const saleHouses = [
  {n:"Modern Hillside Villa", l:"Beverly Hills, CA", p:"$4,200,000", img:"images/houses/sale/house1.jpg"},
  {n:"Glass Forest Retreat", l:"Aspen, CO", p:"$3,750,000", img:"images/houses/sale/house2.jpg"},
  {n:"Colonial Estate", l:"Greenwich, CT", p:"$2,900,000", img:"images/houses/sale/house3.jpg"},
  {n:"Mountain Cabin Lodge", l:"Lake Tahoe, NV", p:"$1,850,000", img:"images/houses/sale/house4.jpg"},
  {n:"Beachfront Mansion", l:"Malibu, CA", p:"$8,500,000", img:"images/houses/sale/house5.jpg"},
  {n:"Spanish Hacienda", l:"Santa Fe, NM", p:"$2,400,000", img:"images/houses/sale/house6.jpg"},
  {n:"Country Farmhouse", l:"Hudson Valley, NY", p:"$1,650,000", img:"images/houses/sale/house7.jpg"},
  {n:"Grand Mansion", l:"Atlanta, GA", p:"$5,300,000", img:"images/houses/sale/house8.jpg"},
  {n:"Scandinavian House", l:"Portland, OR", p:"$1,290,000", img:"images/houses/sale/house9.jpg"},
  {n:"Tudor Manor", l:"Boston, MA", p:"$3,100,000", img:"images/houses/sale/house10.jpg"},
  {n:"Glass Cliff House", l:"Big Sur, CA", p:"$6,800,000", img:"images/houses/sale/house11.jpg"},
  {n:"Craftsman Bungalow", l:"Seattle, WA", p:"$1,150,000", img:"images/houses/sale/house12.jpg"},
  {n:"Downtown Penthouse", l:"Chicago, IL", p:"$2,750,000", img:"images/houses/sale/house13.jpg"},
  {n:"Lakeside Estate", l:"Austin, TX", p:"$3,400,000", img:"images/houses/sale/house14.jpg"},
  {n:"Desert Modern", l:"Scottsdale, AZ", p:"$2,100,000", img:"images/houses/sale/house15.jpg"},
];
const rentHouses = [
  {n:"Cozy Studio Loft", l:"Brooklyn, NY", p:"$2,400/mo", img:"images/houses/rent/rent1.jpg"},
  {n:"Modern Townhouse", l:"San Francisco, CA", p:"$5,800/mo", img:"images/houses/rent/rent2.jpg"},
  {n:"Industrial Loft", l:"Los Angeles, CA", p:"$4,200/mo", img:"images/houses/rent/rent3.jpg"},
  {n:"Suburban Home", l:"Denver, CO", p:"$3,100/mo", img:"images/houses/rent/rent4.jpg"},
  {n:"Sky Penthouse", l:"Miami, FL", p:"$7,500/mo", img:"images/houses/rent/rent5.jpg"},
  {n:"Charming Cottage", l:"Portland, ME", p:"$1,900/mo", img:"images/houses/rent/rent6.jpg"},
  {n:"Urban Duplex", l:"Washington, DC", p:"$3,600/mo", img:"images/houses/rent/rent7.jpg"},
  {n:"Luxury Condo", l:"Seattle, WA", p:"$4,800/mo", img:"images/houses/rent/rent8.jpg"},
  {n:"Beachside Bungalow", l:"San Diego, CA", p:"$3,950/mo", img:"images/houses/rent/rent9.jpg"},
  {n:"Garden Apartment", l:"Austin, TX", p:"$2,200/mo", img:"images/houses/rent/rent10.jpg"},
];

function render(id, list){
  document.getElementById(id).innerHTML = list.map(h=>`
    <div class="card">
      <img src="${h.img}" alt="${h.n}" loading="lazy">
      <div class="card-body">
        <h3>${h.n}</h3>
        <div class="loc">${h.l}</div>
        <div class="price">${h.p}</div>
      </div>
    </div>`).join('');
}
render('grid-sale', saleHouses);
render('grid-rent', rentHouses);

document.querySelectorAll('.tab').forEach(t=>{
  t.onclick = ()=>{
    document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
    t.classList.add('active');
    const tab = t.dataset.tab;
    document.getElementById('grid-sale').classList.toggle('hidden', tab!=='sale');
    document.getElementById('grid-rent').classList.toggle('hidden', tab!=='rent');
  };
});

// Scroll fade for cards
const io = new IntersectionObserver(es=>es.forEach(e=>{
  if(e.isIntersecting){e.target.style.opacity=1;e.target.style.transform='translateY(0)';}
}),{threshold:.1});
setTimeout(()=>document.querySelectorAll('.card').forEach(c=>{
  c.style.opacity=0;c.style.transform='translateY(30px)';c.style.transition='all .6s ease';
  io.observe(c);
}),50);
