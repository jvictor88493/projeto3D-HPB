const fs = require('fs');
const path = require('path');
const sendHtml = require('./_send');
const { readEmail, fullEmails } = require('./_auth');
// Quem ve a aba "Informacao" (padrao: so o e-mail principal). Pode ser sobrescrito pela variavel INFO_EMAILS.
function infoEmails() {
  return (process.env.INFO_EMAILS || 'jvictor88493@gmail.com').split(/[,;\s]+/).map(s => s.trim().toLowerCase()).filter(Boolean);
}
// Paginas proprias (cada uma em sua URL): ao trocar de pagina o navegador libera o 3D da anterior.
const PAGES = {
  full: { url: '/completa', api: '/api/full', id: 'tFull', label: '3D HPB Completa', title: '3D HPB Completa' },
  rec: { url: '/recomendacoes', api: '/api/rec', id: 'tRec', label: 'Recomendações', title: 'Recomendações' }
};
const AC_PANE = `<section id="acPane" class="fpane" hidden><iframe id="acFr" title="Acompanhamento" allow="fullscreen"></iframe></section>`;
const TAB_CSS = `<style>a.tab{display:inline-flex;align-items:center;text-decoration:none}.tab.on{cursor:default}</style>`;
const TAB_JS = `<script>(function(){var v=document.getElementById("vizPane"),p=document.getElementById("infoPanel"),a=document.getElementById("acPane"),ar=document.getElementById("acFr"),T={viz:document.getElementById("tViz"),ac:document.getElementById("tAc"),info:document.getElementById("tInfo")};
function show(n){if(!T[n])n="viz";if(v)v.hidden=n!=="viz";if(p)p.hidden=n!=="info";if(a){a.hidden=n!=="ac";if(n==="ac"&&ar&&!ar.getAttribute("src"))ar.setAttribute("src","/api/acomp")}
Object.keys(T).forEach(function(k){var b=T[k];if(!b)return;b.classList.toggle("on",k===n);b.setAttribute("aria-current",k===n?"page":"false")});document.body.classList.remove("fopen");document.body.classList.toggle("tabfull",n==="ac");
try{history.replaceState(null,"",n==="viz"?location.pathname+location.search:"#"+n)}catch(e){}window.scrollTo(0,0)}
Object.keys(T).forEach(function(k){if(T[k])T[k].onclick=function(){show(k)}});window.__showViz=function(){show("viz")};
function fromHash(){var h=(location.hash||"").slice(1);if(h&&T[h])show(h)}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",fromHash);else fromHash()})();</script>`;

// Abas: "here" = pagina atual ('viz' = pagina principal, 'full'/'rec' = paginas proprias).
function buildNav(here, info, full) {
  const onMain = here === 'viz';
  const btn = (id, label, on) => `<button class="tab${on ? ' on' : ''}" id="${id}"${on ? ' aria-current="page"' : ''} type="button">${label}</button>`;
  const link = (id, href, label, on) => `<a class="tab${on ? ' on' : ''}" id="${id}" href="${href}"${on ? ' aria-current="page"' : ''}>${label}</a>`;
  // Abas que vivem na pagina principal: botoes la, links de volta (com #) nas paginas proprias.
  const main = (id, key, label) => onMain ? btn(id, label, key === 'viz') : link(id, key === 'viz' ? '/' : '/#' + key, label, false);
  let nav = '<nav class="tabs">' + main('tViz', 'viz', 'Mapa bubble caps');
  if (full) {
    nav += link(PAGES.full.id, PAGES.full.url, PAGES.full.label, here === 'full') +
      link(PAGES.rec.id, PAGES.rec.url, PAGES.rec.label, here === 'rec') +
      main('tAc', 'ac', 'Acompanhamento');
  }
  if (info) nav += main('tInfo', 'info', 'Informação');
  return nav + '</nav>';
}

module.exports = (req, res) => {
  res.setHeader('Cache-Control', 'private, no-store');
  res.setHeader('X-Robots-Tag', 'noindex, nofollow');
  const email = readEmail(req);
  if (!email) { res.statusCode = 302; res.setHeader('Location', '/login'); return res.end(); }
  const dir = path.join(process.cwd(), 'private');
  let html = fs.readFileSync(path.join(dir, 'index.html'), 'utf8');
  const info = infoEmails().includes(email);
  const full = fullEmails().includes(email);
  const view = String((new URL(req.url, 'http://x')).searchParams.get('v') || '');
  const pg = PAGES[view];

  if (pg) {
    if (!full) { res.statusCode = 302; res.setHeader('Location', '/'); return res.end(); }
    // Pagina leve: so o topo do site (marca + abas) e o 3D da aba em tela cheia; sem o mapa bubble caps.
    const head = html.slice(0, html.indexOf('</head>')).replace(/<title>[^<]*<\/title>/, `<title>${pg.title} - Mapa 3D de Caldeiras</title>`);
    const h0 = html.indexOf('<header class="top">'), h1 = html.indexOf('</header>') + '</header>'.length;
    const header = html.slice(h0, h1).replace('<!--INFO_NAV-->', () => buildNav(view, info, full));
    const out = head + TAB_CSS + '</head>\n<body class="tabfull">\n<div class="app">\n' + header +
      `\n<section id="fullPane" class="fpane"><iframe title="${pg.title}" src="${pg.api}" allow="fullscreen"></iframe></section>\n</div>\n</body>\n</html>\n`;
    return sendHtml(req, res, out);
  }

  let panel = '';
  if (info) {
    panel = fs.readFileSync(path.join(dir, 'info.html'), 'utf8');
    let extra = '';
    try { extra = fs.readFileSync(path.join(dir, 'full_info.html'), 'utf8').replace(/id="desenhos"/g, 'id="desenhosFull"'); } catch (e) {}
    const k = panel.lastIndexOf('</section>');
    if (extra && k >= 0) panel = panel.slice(0, k) + '<style>.t-ok{color:#2e8b57;font-weight:600}.t-dv{color:#d9822b;font-weight:600}.t-pe{color:#d9423a;font-weight:600}</style>' + extra + panel.slice(k);
  }
  const nav = (info || full) ? buildNav('viz', info, full) : '';
  html = html.replace('</head>', () => TAB_CSS + '</head>')
    .replace('<!--INFO_NAV-->', () => nav).replace('<!--FULL_PANE-->', () => full ? AC_PANE : '').replace('<!--INFO_PANEL-->', () => panel + TAB_JS);
  sendHtml(req, res, html);
};
