// API Client
const T = () => localStorage.getItem('token');
const H = () => T() ? {'Content-Type':'application/json','Authorization':`Bearer ${T()}`} : {'Content-Type':'application/json'};

async function api(path, opts={}) {
  const r = await fetch(path, {...opts, headers:{...H(),...(opts.headers||{})}});
  if (!r.ok) { const e = await r.json().catch(()=>({detail:'Hata'})); throw new Error(e.detail||'Hata'); }
  return r.json();
}

const API = {
  login: d => api('/auth/login',{method:'POST',body:JSON.stringify(d)}),
  register: d => api('/auth/register',{method:'POST',body:JSON.stringify(d)}),
  me: () => api('/auth/me'),
  trending: cat => api('/products/trending'+(cat?`?category=${cat}`:'')),
  categories: () => api('/products/categories'),
  history: id => api(`/products/${id}/history`),
  watchlist: () => api('/watchlist'),
  wlAdd: (pid,tp) => api('/watchlist',{method:'POST',body:JSON.stringify({product_id:pid,target_price:tp||null})}),
  wlDel: id => api(`/watchlist/${id}`,{method:'DELETE'}),
  notifs: () => api('/notifications'),
  unread: () => api('/notifications/unread-count'),
  markRead: id => api(`/notifications/${id}/read`,{method:'PATCH'}),
  markAll: () => api('/notifications/read-all',{method:'PATCH'}),
};

// State
let user = null;
let unreadCount = 0;
let theme = localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');

function setTheme(value) {
  theme = value;
  document.documentElement.dataset.theme = value;
  localStorage.setItem('theme', value);
}

function toggleTheme() {
  setTheme(theme === 'dark' ? 'light' : 'dark');
  route();
}

// Router
const ROUTES = {'#/':pageAgent,'#/welcome':pageLanding,'#/trends':pageTrends,'#/watchlist':pageWatchlist,'#/notifications':pageNotifs,'#/login':pageLogin,'#/register':pageRegister};

window.addEventListener('hashchange', route);
window.addEventListener('DOMContentLoaded', init);

async function init() {
  setTheme(theme);
  const tok = T();
  if (tok) { try { user = await API.me(); } catch { localStorage.removeItem('token'); } }
  if (user) refreshUnread();
  route();
}

function route() {
  const h = location.hash||'#/welcome';
  if (user && h === '#/welcome') { location.hash = '#/'; return; }
  if (!user && ['#/','#/trends','#/watchlist','#/notifications'].includes(h)) { location.hash = '#/welcome'; return; }
  const fn = ROUTES[h];
  fn ? fn() : (location.hash='#/welcome');
}

function go(h) { location.hash = h; }

async function refreshUnread() {
  if (!user) return;
  try { const r = await API.unread(); unreadCount=r.count; renderSidebar(); } catch {}
}

// Sidebar
function renderSidebar() {
  const nav = [
    {h:'#/',i:'📊',l:'Ürün Araştırması'},
    {h:'#/trends',i:'📈',l:'Trend Ürünler'},
    {h:'#/watchlist',i:'🔖',l:'Takip Listesi',auth:true},
    {h:'#/notifications',i:'🔔',l:'Bildirimler',auth:true,badge:true},
  ];
  const cur = location.hash||'#/';
  return `<aside class="sidebar">
    <a class="sb-logo" href="#/"><span class="sb-dot"></span>DropAgent</a>
    <nav class="sb-nav">
      <div class="sb-lbl">Menü</div>
      ${nav.filter(n=>!n.auth||user).map(n=>`
        <a class="sb-item${cur===n.h?' active':''}" href="${n.h}">
          <span>${n.i}</span>${n.l}
          ${n.badge&&unreadCount>0?`<span class="sb-badge">${unreadCount>9?'9+':unreadCount}</span>`:''}
        </a>`).join('')}
    </nav>
    <div class="sb-footer">
      ${user?`
        <div class="sb-user">
          <div class="sb-avatar">${user.name[0].toUpperCase()}</div>
          <div><div class="sb-uname">${user.name}</div><div class="sb-uemail">${user.email}</div></div>
        </div>
        <button class="sb-item" onclick="logout()"><span>🚪</span>Çıkış Yap</button>
      `:`<div style="display:grid;gap:8px">
        <a class="sb-item" href="#/login"><span>👤</span>Giriş Yap</a>
      </div>`}
    </div>
  </aside>`;
}

function layout(title, sub, content) {
  document.getElementById('app').innerHTML = renderSidebar() + `
    <main class="main">
      <div class="ph">
        <div class="topbar">
          <div>
            <h1 class="pt">${title}</h1>
            <p class="ps">${sub}</p>
          </div>
          <button class="btn btn-s btn-sm theme-toggle" onclick="toggleTheme()">${theme==='dark'?'☀️ Aydınlık Mod':'🌙 Karanlık Mod'}</button>
        </div>
      </div>
      <div class="pc" id="pc">${content}</div>
    </main>`;
}

function logout() { localStorage.removeItem('token'); user=null; unreadCount=0; go('#/welcome'); }

// Product card helper
function compBadge(c) {
  if(c==='Düşük') return `<span class="badge b-low">✅ ${c}</span>`;
  if(c==='Yüksek') return `<span class="badge b-high">🔴 ${c}</span>`;
  return `<span class="badge b-mid">⚠️ ${c}</span>`;
}

function shopLinks(p) {
  return `<div class="links">
    ${p.ebay_url?`<a class="link" href="${p.ebay_url}" target="_blank">🛒 eBay</a>`:''}
    ${p.amazon_url?`<a class="link" href="${p.amazon_url}" target="_blank">📦 Amazon</a>`:''}
    ${p.aliexpress_url?`<a class="link" href="${p.aliexpress_url}" target="_blank">🛍️ AliExpress</a>`:''}
    ${p.trendyol_url?`<a class="link" href="${p.trendyol_url}" target="_blank">🏷️ Trendyol</a>`:''}
  </div>`;
}

function productCard(p, watchBtn=true) {
  return `<div class="pcard glass">
    <img class="pimg" src="${p.image_url||'https://images.unsplash.com/photo-1518717758536-85ae29035b6d?w=400&q=80'}" alt="${p.name}" onerror="this.src='https://images.unsplash.com/photo-1518717758536-85ae29035b6d?w=400&q=80'">
    <div class="pb">
      <div class="pcat">${p.category}</div>
      <div class="pname">${p.name}</div>
      <div class="badges">
        <span class="badge b-roi">📊 %${(p.roi_percent||0).toFixed(0)} ROI</span>
        <span class="badge b-trend">🔥 ${p.trend_score}/100</span>
        ${compBadge(p.competition)}
      </div>
      <div class="prices">
        <div><div class="plbl">Tedarik</div><div class="psup">$${(p.supplier_price||0).toFixed(2)}</div></div>
        <div style="text-align:right"><div class="plbl">Pazar</div><div class="pval">$${(p.market_price||0).toFixed(2)}</div></div>
      </div>
    </div>
    ${shopLinks(p)}
    ${watchBtn?`<div class="pactions"><button class="btn btn-s btn-sm wf" onclick="addToWatch(${p.id},'${p.name}',${p.market_price})">+ Takip Listesine Ekle</button></div>`:''}
  </div>`;
}

// Add to watchlist modal
window.addToWatch = function(pid, name, price) {
  if (!user) { go('#/login'); return; }
  document.body.insertAdjacentHTML('beforeend', `
    <div class="modal-ov" id="wl-modal" onclick="closeModal(event)">
      <div class="modal glass">
        <div class="modal-t">Takip Listesine Ekle</div>
        <p style="font-size:13px;color:var(--txt-m);margin-bottom:16px"><strong>${name}</strong> — Hedef fiyat belirlerseniz düşünce bildirim alırsınız.</p>
        <div class="fg"><label class="fl">Hedef Fiyat (opsiyonel)</label>
          <input id="tp-input" class="fi" type="number" step="0.01" placeholder="Mevcut: $${price.toFixed(2)}">
        </div>
        <div id="wl-err"></div>
        <div class="flex g2"><button class="btn btn-s wf" onclick="document.getElementById('wl-modal').remove()">İptal</button>
          <button class="btn btn-p wf" onclick="confirmWatch(${pid})">Ekle</button></div>
      </div>
    </div>`);
};

window.closeModal = function(e) { if(e.target.classList.contains('modal-ov')) e.target.remove(); };

window.confirmWatch = async function(pid) {
  const tp = parseFloat(document.getElementById('tp-input').value)||null;
  try {
    await API.wlAdd(pid, tp);
    document.getElementById('wl-modal').remove();
  } catch(e) {
    document.getElementById('wl-err').innerHTML = `<div class="alert alert-e">${e.message}</div>`;
  }
};

// === PAGE: AGENT ===
const CATS = [{k:'genel',l:'Genel',e:'🌐'},{k:'elektronik',l:'Elektronik',e:'📱'},{k:'spor',l:'Spor',e:'🏋️'},{k:'ev',l:'Ev',e:'🏠'},{k:'güzellik',l:'Güzellik',e:'💄'},{k:'evcil',l:'Evcil',e:'🐾'}];
let selCat = 'genel';

function pageAgent() {
  layout('Ürün Araştırması','Dropshipping için en karlı ürünleri keşfedin',`
    <div class="agent-wrap">
      <div id="agent-panel">
        <div class="card glass mb4">
          <div class="ch"><span class="ct">Kategori Seç</span></div>
          <div class="cb">
            <div class="cat-grid">${CATS.map(c=>`<button class="cat-btn${c.k===selCat?' sel':''}" onclick="selectCat('${c.k}')"><span class="cat-em">${c.e}</span>${c.l}</button>`).join('')}</div>
            <button id="start-btn" class="btn btn-p wf" onclick="startAgent()">⚡ Araştırmayı Başlat</button>
          </div>
        </div>
        <div id="steps-card"></div>
      </div>
      <div id="agent-results">
        <div class="card glass center"><div style="font-size:40px;margin-bottom:12px">⚡</div>
          <div style="font-size:15px;font-weight:600;margin-bottom:6px">Araştırma Hazır</div>
          <div style="font-size:13px;color:var(--txt-m);max-width:280px;margin:0 auto">Kategori seçin ve en karlı ürünleri hızlıca keşfedin.</div>
        </div>
      </div>
    </div>`);
}

window.selectCat = function(k) {
  selCat = k;
  document.querySelectorAll('.cat-btn').forEach(b=>b.classList.remove('sel'));
  event.target.closest('.cat-btn').classList.add('sel');
};

window.startAgent = function() {
  const btn = document.getElementById('start-btn');
  btn.disabled = true; btn.innerHTML = '<span class="spin"></span> Analiz Yapılıyor...';
  document.getElementById('agent-results').innerHTML = `<div class="card glass center"><span class="spin" style="width:32px;height:32px"></span><div style="font-size:13px;color:var(--txt-m);margin-top:16px">Agent ürünleri analiz ediyor...</div></div>`;
  document.getElementById('steps-card').innerHTML = `<div class="card glass"><div class="ch"><span class="ct">Agent Adımları</span></div><div class="cb" style="padding-top:8px"><div class="steps" id="steps-list"></div></div></div>`;
  const steps = {};
  const src = new EventSource(`/agent/research?category=${selCat}`);
  src.onmessage = e => {
    if (e.data==='[DONE]') { src.close(); btn.disabled=false; btn.innerHTML='⚡ Araştırmayı Başlat'; return; }
    try {
      const d = JSON.parse(e.data);
      if (d.step==='result') {
        const prods = d.products||[];
        document.getElementById('agent-results').innerHTML = `
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
            <div><div style="font-weight:600;font-size:15px">${prods.length} Ürün Bulundu</div><div style="font-size:12px;color:var(--txt-m);margin-top:2px">ROI değerine göre sıralandı</div></div>
            <span style="font-size:12px;color:var(--ok);background:var(--ok-l);padding:4px 10px;border-radius:12px;font-weight:500">✅ Tamamlandı</span>
          </div>
          <div class="pgrid">${prods.map(p=>productCard(p)).join('')}</div>`;
      } else if (d.step && d.step !== 'error') {
        steps[d.step] = d;
        const list = document.getElementById('steps-list');
        if (list) list.innerHTML = Object.values(steps).map(s=>`
          <div class="step ${s.status}">
            <div class="step-ind">${s.status==='done'?'✓':s.step}</div>
            <div class="step-body"><div class="step-title">${s.title}</div>${s.detail?`<div class="step-detail">${s.detail}</div>`:''}</div>
          </div>`).join('');
      }
    } catch {}
  };
  src.onerror = () => { src.close(); btn.disabled=false; btn.innerHTML='⚡ Araştırmayı Başlat'; };
};

// === PAGE: TRENDS ===
async function pageTrends() {
  layout('Trend Ürünler','En yüksek talep gören ürünler — alışveriş sitelerinde anında görüntüle',`<div class="center"><span class="spin" style="width:32px;height:32px"></span></div>`);
  const [prods, cats] = await Promise.all([API.trending(), API.categories()]).catch(()=>[[],[]]);
  const top = prods[0];
  const avgT = prods.length ? (prods.reduce((s,p)=>s+(p.trend_score||0),0)/prods.length).toFixed(0) : 0;
  document.getElementById('pc').innerHTML = `
    ${top?`<div class="stats">
      <div class="stat glass"><div class="sl">Toplam Ürün</div><div class="sv">${prods.length}</div></div>
      <div class="stat glass"><div class="sl">En Yüksek ROI</div><div class="sv">%${Math.max(...prods.map(p=>p.roi_percent||0)).toFixed(0)}</div></div>
      <div class="stat glass"><div class="sl">Düşük Rekabet</div><div class="sv" style="color:var(--ok)">${prods.filter(p=>p.competition==='Düşük').length}</div></div>
      <div class="stat glass"><div class="sl">Ort. Trend Skoru</div><div class="sv">${avgT}</div></div>
    </div>`:''}
    <div class="fbar" id="fbar">
      <button class="chip act" onclick="filterTrend(null,this)">Tümü</button>
      ${cats.map(c=>`<button class="chip" onclick="filterTrend('${c}',this)">${c}</button>`).join('')}
    </div>
    <div id="tgrid" class="pgrid">${prods.map(p=>productCard(p)).join('')}</div>`;
  window._tprods = prods;
}

window.filterTrend = async function(cat, el) {
  document.querySelectorAll('.chip').forEach(c=>c.classList.remove('act'));
  el.classList.add('act');
  document.getElementById('tgrid').innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:40px"><span class="spin" style="width:24px;height:24px"></span></div>`;
  const prods = await API.trending(cat).catch(()=>[]);
  document.getElementById('tgrid').innerHTML = prods.map(p=>productCard(p)).join('');
};

// === PAGE: WATCHLIST ===
async function pageWatchlist() {
  if (!user) { go('#/login'); return; }
  layout('Takip Listesi','Fiyat takibi yaptığınız ürünler — hedef fiyata düşünce bildirim alırsınız',`<div class="center"><span class="spin" style="width:32px;height:32px"></span></div>`);
  const items = await API.watchlist().catch(()=>[]);
  if (!items.length) {
    document.getElementById('pc').innerHTML = `<div class="card glass"><div class="empty"><div class="empty-ico">🔖</div><div class="empty-t">Takip listesi boş</div><div class="empty-s">Trend ürünlerden ürün ekleyebilirsiniz.</div><a class="btn btn-p" href="#/trends">Trend Ürünlere Git</a></div></div>`;
    return;
  }
  const avgROI = (items.reduce((s,i)=>s+(i.product?.roi_percent||0),0)/items.length).toFixed(0);
  const hit = items.filter(i=>i.target_price&&i.product?.market_price<=i.target_price).length;
  document.getElementById('pc').innerHTML = `
    <div class="stats">
      <div class="stat glass"><div class="sl">Takip Edilen</div><div class="sv">${items.length}</div></div>
      <div class="stat glass"><div class="sl">Hedefe Ulaşan</div><div class="sv" style="color:var(--ok)">${hit}</div></div>
      <div class="stat glass"><div class="sl">Ort. ROI</div><div class="sv">%${avgROI}</div></div>
    </div>
    <div class="card glass">${items.map(i=>{
      const p=i.product; const reached=i.target_price&&p.market_price<=i.target_price;
      return `<div class="wl-item">
        <img class="wl-img" src="${p.image_url}" onerror="this.src='https://images.unsplash.com/photo-1518717758536-85ae29035b6d?w=400&q=80'" alt="${p.name}">
        <div class="wl-info">
          <div class="wl-name">${p.name}</div>
          <div class="wl-cat">${p.category}</div>
          <div class="links" style="padding:6px 0 0">
            ${p.ebay_url?`<a class="link" href="${p.ebay_url}" target="_blank">🛒 eBay</a>`:''}
            ${p.amazon_url?`<a class="link" href="${p.amazon_url}" target="_blank">📦 Amazon</a>`:''}
            ${p.trendyol_url?`<a class="link" href="${p.trendyol_url}" target="_blank">🏷️ Trendyol</a>`:''}
          </div>
        </div>
        <div class="wl-price">
          <div class="wl-cur">$${p.market_price.toFixed(2)}</div>
          ${i.target_price?`<div class="wl-tgt${reached?' hit':''}">${reached?'✅':'🎯'} Hedef: $${i.target_price.toFixed(2)}</div>`:''}
          <button class="btn btn-d btn-sm" style="margin-top:6px" onclick="removeWatch(${i.id})">Kaldır</button>
        </div>
      </div>`;
    }).join('')}</div>`;
}

window.removeWatch = async function(id) {
  await API.wlDel(id).catch(()=>{});
  pageWatchlist();
};

// === PAGE: NOTIFICATIONS ===
async function pageNotifs() {
  if (!user) { go('#/login'); return; }
  layout('Bildirimler','Fiyat düşüşü ve ürün uyarıları',`<div class="center"><span class="spin" style="width:32px;height:32px"></span></div>`);
  const notifs = await API.notifs().catch(()=>[]);
  const unread = notifs.filter(n=>!n.is_read).length;
  document.getElementById('pc').innerHTML = `
    <div class="flex ic jb mb4">
      <span style="font-size:13px;color:var(--txt-m)">${unread>0?`${unread} okunmamış bildirim`:'Tüm bildirimler okundu'}</span>
      ${unread>0?`<button class="btn btn-g btn-sm" onclick="markAllRead()">Tümünü Okundu İşaretle</button>`:''}
    </div>
    <div class="card glass">
      ${!notifs.length?`<div class="empty"><div class="empty-ico">🔔</div><div class="empty-t">Henüz bildirim yok</div><div class="empty-s">Takip listenizdeki ürünler düşünce burada görünür.</div></div>`
      :notifs.map(n=>`
        <div class="notif-item${n.is_read?'':' unread'}" onclick="readNotif(${n.id},this)">
          <div class="ndot ${n.is_read?'old':'new'}"></div>
          <div class="nmsg">${n.message}${n.product_name?`<div style="font-size:11px;color:var(--txt-m);margin-top:3px">📦 ${n.product_name}</div>`:''}</div>
          <div class="ntime">${timeAgo(n.created_at)}</div>
        </div>`).join('')}
    </div>`;
  unreadCount = unread; renderSidebar();
}

window.readNotif = async function(id, el) {
  await API.markRead(id).catch(()=>{});
  el.classList.remove('unread');
  el.querySelector('.ndot').className='ndot old';
};

window.markAllRead = async function() {
  await API.markAll().catch(()=>{});
  pageNotifs();
};

function timeAgo(s) {
  const m = Math.floor((Date.now()-new Date(s))/60000);
  if(m<1) return 'az önce'; if(m<60) return `${m} dk önce`;
  const h=Math.floor(m/60); if(h<24) return `${h} saat önce`;
  return `${Math.floor(h/24)} gün önce`;
}

// === PAGE: LOGIN ===
function pageLanding() {
  document.getElementById('app').innerHTML = `
    <div class="landing-wrap">
      <div class="landing-card glass">
        <div class="landing-hero">
          <div class="sb-logo" style="font-size:26px;">DropAgent</div>
          <div class="landing-title">Dropshipping ara, kârını büyüt.</div>
          <div class="landing-sub">AI destekli ürün araştırması, trend keşfi ve fiyat takibi tek panelde. Kaydol veya giriş yap, sana özel fırsatları görmeye başla.</div>
          <div class="landing-actions">
            <button class="btn btn-p" onclick="go('#/login')">Giriş Yap</button>
            <button class="btn btn-s" onclick="go('#/register')">Kayıt Ol</button>
          </div>
        </div>
        <div class="landing-visual">
          <img src="/assets/images/Gemini_Generated_Image_anpnhyanpnhyanpn.png" alt="DropAgent alışveriş görseli">
        </div>
      </div>
    </div>`;
}

function pageLogin() {
  document.getElementById('app').innerHTML = `
    <div class="auth-wrap">
      <div class="auth-card glass">
        <div class="auth-toolbar">
          <div class="auth-logo" onclick="go('#/welcome')"><span class="sb-dot"></span>DropAgent</div>
          <button class="btn btn-s btn-sm" onclick="toggleTheme()">${theme==='dark'?'☀️ Aydınlık Mod':'🌙 Karanlık Mod'}</button>
        </div>
        <div class="at">Giriş Yap</div>
        <div class="as">Hesabınıza giriş yapın</div>
        <div id="auth-err"></div>
        <div class="fg"><label class="fl">E-posta</label><input id="l-email" class="fi" type="email" placeholder="ornek@email.com"></div>
        <div class="fg"><label class="fl">Şifre</label><input id="l-pass" class="fi" type="password" placeholder="••••••••" onkeydown="if(event.key==='Enter')doLogin()"></div>
        <button class="btn btn-p wf" style="margin-top:8px" onclick="doLogin()" id="l-btn">Giriş Yap</button>
        <div style="text-align:center;font-size:13px;color:var(--txt-m);margin-top:16px">
          Hesabınız yok mu? <span class="alink" onclick="go('#/register')">Kayıt Ol</span>
        </div>
      </div>
    </div>`;
}

window.doLogin = async function() {
  const email=document.getElementById('l-email').value, pass=document.getElementById('l-pass').value;
  const btn=document.getElementById('l-btn'); btn.disabled=true; btn.innerHTML='<span class="spin"></span>';
  document.getElementById('auth-err').innerHTML='';
  try {
    const r = await API.login({email,password:pass});
    localStorage.setItem('token',r.access_token); user=r.user;
    await refreshUnread(); go('#/');
  } catch(e) {
    document.getElementById('auth-err').innerHTML=`<div class="alert alert-e">${e.message}</div>`;
    btn.disabled=false; btn.innerHTML='Giriş Yap';
  }
};

// === PAGE: REGISTER ===
function pageRegister() {
  document.getElementById('app').innerHTML = `
    <div class="auth-wrap">
      <div class="auth-card glass">
        <div class="auth-toolbar">
          <div class="auth-logo" onclick="go('#/')"><span class="sb-dot"></span>DropAgent</div>
          <button class="btn btn-s btn-sm" onclick="toggleTheme()">${theme==='dark'?'☀️ Aydınlık Mod':'🌙 Karanlık Mod'}</button>
        </div>
        <div class="at">Kayıt Ol</div>
        <div class="as">Ücretsiz hesap oluşturun</div>
        <div id="auth-err"></div>
        <div class="fg"><label class="fl">Ad Soyad</label><input id="r-name" class="fi" type="text" placeholder="Ahmet Yılmaz"></div>
        <div class="fg"><label class="fl">E-posta</label><input id="r-email" class="fi" type="email" placeholder="ornek@email.com"></div>
        <div class="fg"><label class="fl">Şifre</label><input id="r-pass" class="fi" type="password" placeholder="En az 6 karakter" onkeydown="if(event.key==='Enter')doRegister()"></div>
        <button class="btn btn-p wf" style="margin-top:8px" onclick="doRegister()" id="r-btn">Kayıt Ol</button>
        <div style="text-align:center;font-size:13px;color:var(--txt-m);margin-top:16px">
          Hesabınız var mı? <span class="alink" onclick="go('#/login')">Giriş Yap</span>
        </div>
      </div>
    </div>`;
}

window.doRegister = async function() {
  const name=document.getElementById('r-name').value, email=document.getElementById('r-email').value, pass=document.getElementById('r-pass').value;
  if(pass.length<6){document.getElementById('auth-err').innerHTML='<div class="alert alert-e">Şifre en az 6 karakter olmalı</div>';return;}
  const btn=document.getElementById('r-btn'); btn.disabled=true; btn.innerHTML='<span class="spin"></span>';
  document.getElementById('auth-err').innerHTML='';
  try {
    const r = await API.register({name,email,password:pass});
    localStorage.setItem('token',r.access_token); user=r.user;
    await refreshUnread(); go('#/');
  } catch(e) {
    document.getElementById('auth-err').innerHTML=`<div class="alert alert-e">${e.message}</div>`;
    btn.disabled=false; btn.innerHTML='Kayıt Ol';
  }
};
