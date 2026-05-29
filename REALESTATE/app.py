import os, sqlite3, uuid, smtplib
from email.mime.text import MIMEText
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify

app = Flask(__name__)
app.secret_key = "change-this-secret"
DB = "database.db"

# ---------- EMAIL CONFIG (fill in to actually send mail) ----------
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "kkgadashin@gmail.com"
SMTP_PASS = "ykas mmdi sbow szxf"
SEND_EMAILS = False   # set True after filling SMTP_USER/SMTP_PASS

def send_email(to, subject, body):
    if not SEND_EMAILS:
        print(f"[EMAIL DISABLED] To:{to} | {subject}\n{body}")
        return
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = to
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.starttls()
        s.login(SMTP_USER, SMTP_PASS)
        s.send_message(msg)

# ---------- DATABASE ----------
def db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = db()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY,
        first_name TEXT, last_name TEXT,
        email TEXT UNIQUE, unique_id TEXT UNIQUE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS companies(
        id INTEGER PRIMARY KEY,
        company_name TEXT, residents INTEGER, units_in_use INTEGER,
        email TEXT, unique_id TEXT UNIQUE, discount REAL DEFAULT 0.15
    );
    CREATE TABLE IF NOT EXISTS properties(
        id INTEGER PRIMARY KEY,
        title TEXT, listing_type TEXT,  -- sale | rent | shortlet
        property_type TEXT,             -- flat | villa | self-contained...
        location TEXT, price REAL,
        bedrooms INTEGER, bathrooms INTEGER,
        furnished INTEGER, serviced INTEGER, sharing INTEGER,
        features TEXT, image TEXT,
        status TEXT DEFAULT 'available' -- available | occupied
    );
    CREATE TABLE IF NOT EXISTS requests(
        id INTEGER PRIMARY KEY,
        user_email TEXT, message TEXT,
        status TEXT DEFAULT 'pending',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    # seed sample properties
    if c.execute("SELECT COUNT(*) FROM properties").fetchone()[0] == 0:
        seed = [
            ("Modern Villa with Pool","sale","villa","Lekki, Lagos",450000,4,5,1,1,0,"pool,jacuzzi,garden","h1.jpg","available"),
            ("Luxury Penthouse","sale","flat","Victoria Island",380000,3,3,1,1,0,"pool,gym","h2.jpg","available"),
            ("Cozy Self-Contained","rent","self-contained","Yaba",1200,1,1,1,0,1,"wifi","h3.jpg","available"),
            ("Family Apartment","rent","flat","Ikeja",2500,3,2,0,0,0,"parking","h4.jpg","occupied"),
            ("Short-Let Studio","shortlet","flat","Ikoyi",150,1,1,1,1,0,"pool","h5.jpg","available"),
            ("Beach House","sale","villa","Eko Atlantic",980000,5,6,1,1,0,"pool,jacuzzi,beach","h6.jpg","available"),
        ]
        c.executemany("""INSERT INTO properties
            (title,listing_type,property_type,location,price,bedrooms,bathrooms,
             furnished,serviced,sharing,features,image,status)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""", seed)
    c.commit(); c.close()

init_db()

# ---------- ROUTES ----------
@app.route("/")
def home():
    featured = db().execute("SELECT * FROM properties LIMIT 6").fetchall()
    return render_template("home.html", featured=featured)

@app.route("/search")
def search():
    q = request.args
    try:
        pmin = float(q.get("min_price") or 0)
        pmax = float(q.get("max_price") or 1e12)
    except ValueError:
        return jsonify({"error":"Invalid price"}), 400
    if pmin == pmax and pmin != 0:
        return jsonify({"error":"Minimum and maximum price cannot be equal"}), 400
    if pmin > pmax:
        return jsonify({"error":"Minimum price greater than maximum"}), 400

    sql = "SELECT * FROM properties WHERE price BETWEEN ? AND ?"
    args = [pmin, pmax]
    for f,col in [("listing_type","listing_type"),("property_type","property_type"),
                  ("location","location"),("bedrooms","bedrooms")]:
        v = q.get(f)
        if v:
            sql += f" AND {col} LIKE ?"
            args.append(f"%{v}%")
    if q.get("furnished"): sql += " AND furnished=1"
    if q.get("serviced"):  sql += " AND serviced=1"
    if q.get("sharing"):   sql += " AND sharing=1"
    kw = q.get("keywords")
    if kw:
        sql += " AND features LIKE ?"; args.append(f"%{kw}%")
    rows = db().execute(sql, args).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/sale")
def sale():
    rows = db().execute("SELECT * FROM properties WHERE listing_type='sale'").fetchall()
    return render_template("sale.html", properties=rows)

@app.route("/rent")
def rent():
    rows = db().execute("SELECT * FROM properties WHERE listing_type IN ('rent','shortlet')").fetchall()
    return render_template("rent.html", properties=rows)

# ---- COMPANY ----
@app.route("/company", methods=["GET","POST"])
def company():
    if request.method == "POST":
        uid = "CMP-" + uuid.uuid4().hex[:8].upper()
        c = db()
        c.execute("""INSERT INTO companies(company_name,residents,units_in_use,email,unique_id)
                     VALUES (?,?,?,?,?)""",
                  (request.form["company_name"], request.form["residents"],
                   request.form["units"], request.form["email"], uid))
        c.commit(); c.close()
        send_email(request.form["email"], "Your Company ID",
                   f"Welcome! Your company ID is {uid}. You get 15% discount on listings.")
        flash(f"Company registered. Your unique ID: {uid} (also emailed).","ok")
        return redirect(url_for("company"))
    return render_template("company.html")

# ---- REQUESTS ----
@app.route("/request", methods=["GET","POST"])
def user_request():
    if request.method == "POST":
        c = db()
        c.execute("INSERT INTO requests(user_email,message) VALUES (?,?)",
                  (request.form["email"], request.form["message"]))
        c.commit(); c.close()
        flash("Request submitted — status: pending.","ok")
        return redirect(url_for("user_request"))
    rows = db().execute("SELECT * FROM requests ORDER BY created_at DESC").fetchall()
    return render_template("request.html", requests=rows)

# ---- MARKET TRENDS ----
@app.route("/trends")
def trends():
    # simple computed analytics
    c = db()
    total = c.execute("SELECT COUNT(*) FROM properties").fetchone()[0]
    avg_sale = c.execute("SELECT AVG(price) FROM properties WHERE listing_type='sale'").fetchone()[0] or 0
    avg_rent = c.execute("SELECT AVG(price) FROM properties WHERE listing_type='rent'").fetchone()[0] or 0
    occupied = c.execute("SELECT COUNT(*) FROM properties WHERE status='occupied'").fetchone()[0]
    # fictional "issues" stats per request: properties with broken/spoilt items
    damaged_pct = 22  # placeholder analytic
    return render_template("trends.html",
        total=total, avg_sale=avg_sale, avg_rent=avg_rent,
        occupied=occupied, damaged_pct=damaged_pct)

# ---- REGISTER ----
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        uid = "USR-" + uuid.uuid4().hex[:8].upper()
        try:
            c = db()
            c.execute("""INSERT INTO users(first_name,last_name,email,unique_id)
                         VALUES (?,?,?,?)""",
                      (request.form["first_name"], request.form["last_name"],
                       request.form["email"], uid))
            c.commit(); c.close()
        except sqlite3.IntegrityError:
            flash("Email already registered.","err")
            return redirect(url_for("register"))
        send_email(request.form["email"], "Your Unique ID",
                   f"Hi {request.form['first_name']}, your sign-in ID is: {uid}")
        flash(f"Registered! Your unique ID: {uid} (sent to your email). Please sign in.","ok")
        return redirect(url_for("signin"))
    return render_template("register.html")

# ---- SIGN IN ----
@app.route("/signin", methods=["GET","POST"])
def signin():
    if request.method == "POST":
        uid = request.form["unique_id"].strip()
        user = db().execute("SELECT * FROM users WHERE unique_id=?", (uid,)).fetchone()
        if user:
            session["user"] = dict(user)
            flash(f"Welcome back, {user['first_name']}!","ok")
            return redirect(url_for("home"))
        flash("Invalid unique ID.","err")
    return render_template("signin.html")

@app.route("/logout")
def logout():
    session.clear(); return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
3. templates/base.html