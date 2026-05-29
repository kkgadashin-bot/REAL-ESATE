// ----- TABS -----
document.querySelectorAll('.tab').forEach(t=>{
  t.addEventListener('click',()=>{
    document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
    t.classList.add('active');
    const lt = document.getElementById('listing_type');
    if(lt) lt.value = t.dataset.type;
  });
});

// ----- SEARCH -----
const form = document.getElementById('searchForm');
if(form){
  form.addEventListener('submit', async e=>{
    e.preventDefault();
    const fd = new FormData(form);
    const min = parseFloat(fd.get('min_price')||0);
    const max = parseFloat(fd.get('max_price')||0);
    const box = document.getElementById('searchResults');
    if(min && max && min===max){
      box.innerHTML = `<p style="color:#f87171">⚠ Minimum and maximum price cannot be equal.</p>`;
      return;
    }
    if(min>max && max>0){
      box.innerHTML = `<p style="color:#f87171">⚠ Min price greater than max.</p>`;
      return;
    }
    const params = new URLSearchParams();
    for(const [k,v] of fd.entries()) if(v) params.append(k,v);
    const res = await fetch('/search?'+params.toString());
    const data = await res.json();
    if(data.error){ box.innerHTML = `<p style="color:#f87171">${data.error}</p>`; return; }
    if(!data.length){ box.innerHTML = `<p>No properties match your filters.</p>`; return; }
    box.innerHTML = `<h3 style="margin:18px 0">${data.length} results</h3>
      <div class="grid">${data.map(p=>`
        <article class="card">
          <img src="https://picsum.photos/seed/${p.id}/600/400"/>
          <div class="body">
            <h3>${p.title}</h3>
            <p>${p.location} · ${p.bedrooms} bd</p>
            <strong>$${p.price.toLocaleString()}</strong>
            <span class="badge ${p.status}">${p.status}</span>
          </div>
        </article>`).join('')}</div>`;
  });
}

// ----- SCROLL REVEAL -----
const io = new IntersectionObserver(es=>{
  es.forEach(e=>{ if(e.isIntersecting) e.target.classList.add('visible'); });
},{threshold:.15});
document.querySelectorAll('.reveal').forEach(el=>io.observe(el));

// ----- 3D TILT -----
document.querySelectorAll('.tilt').forEach(card=>{
  card.addEventListener('mousemove',e=>{
    const r = card.getBoundingClientRect();
    const x = (e.clientX-r.left)/r.width - .5;
    const y = (e.clientY-r.top)/r.height - .5;
    card.style.transform = `perspective(900px) rotateY(${x*10}deg) rotateX(${-y*10}deg) translateY(-6px)`;
  });
  card.addEventListener('mouseleave',()=> card.style.transform='');
});

// ----- HERO PARALLAX -----
window.addEventListener('scroll',()=>{
  const hero = document.querySelector('.hero');
  if(hero){
    const y = window.scrollY;
    hero.style.backgroundPosition = `center ${y*0.4}px`;
  }
});