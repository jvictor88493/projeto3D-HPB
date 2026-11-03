const fs = require('fs');
const path = require('path');
const { readEmail, fullEmails } = require('./_auth');
// Quem ve a aba "Informacao" (padrao: so o e-mail principal). Pode ser sobrescrito pela variavel INFO_EMAILS.
function infoEmails() {
  return (process.env.INFO_EMAILS || 'jvictor88493@gmail.com').split(/[,;\s]+/).map(s => s.trim().toLowerCase()).filter(Boolean);
}
const FULL_PANE = `<section id="fullPane" hidden><iframe id="fullFr" title="3D HPB Completa" allow="fullscreen"></iframe></section>`;
const TAB_JS = `<script>(function(){var v=document.getElementById("vizPane"),p=document.getElementById("infoPanel"),f=document.getElementById("fullPane"),fr=document.getElementById("fullFr"),T={viz:document.getElementById("tViz"),full:document.getElementById("tFull"),info:document.getElementById("tInfo")};
function show(n){if(v)v.hidden=n!=="viz";if(p)p.hidden=n!=="info";if(f){f.hidden=n!=="full";if(n==="full"&&fr&&!fr.getAttribute("src"))fr.setAttribute("src","/api/full")}
Object.keys(T).forEach(function(k){var b=T[k];if(!b)return;b.classList.toggle("on",k===n);b.setAttribute("aria-current",k===n?"page":"false")});document.body.classList.remove("fopen");document.body.classList.toggle("tabfull",n==="full");window.scrollTo(0,0)}
Object.keys(T).forEach(function(k){if(T[k])T[k].onclick=function(){show(k)}});window.__showViz=function(){show("viz")}})();</script>`;
module.exports = (req, res) => {
  res.setHeader('Cache-Control', 'private, no-store');
  res.setHeader('X-Robots-Tag', 'noindex, nofollow');
  const email = readEmail(req);
  if (!email) { res.statusCode = 302; res.setHeader('Location', '/login'); return res.end(); }
  const dir = path.join(process.cwd(), 'private');
  let html = fs.readFileSync(path.join(dir, 'index.html'), 'utf8');
  const info = infoEmails().includes(email);
  const full = fullEmails().includes(email);
  let panel = '';
  if (info) {
    panel = fs.readFileSync(path.join(dir, 'info.html'), 'utf8');
    let extra = '';
    try { extra = fs.readFileSync(path.join(dir, 'full_info.html'), 'utf8').replace(/id="desenhos"/g, 'id="desenhosFull"'); } catch (e) {}
    const k = panel.lastIndexOf('</section>');
    if (extra && k >= 0) panel = panel.slice(0, k) + '<style>.t-ok{color:#2e8b57;font-weight:600}.t-dv{color:#d9822b;font-weight:600}.t-pe{color:#d9423a;font-weight:600}</style>' + extra + panel.slice(k);
  }
  let nav = '';
  if (info || full) {
    nav = '<nav class="tabs"><button class="tab on" id="tViz" aria-current="page" type="button">Visualização</button>' +
      (full ? '<button class="tab" id="tFull" type="button">3D HPB Completa</button>' : '') +
      (info ? '<button class="tab" id="tInfo" type="button">Informação</button>' : '') + '</nav>';
  }
  html = html.replace('<!--INFO_NAV-->', () => nav).replace('<!--FULL_PANE-->', () => full ? FULL_PANE : '').replace('<!--INFO_PANEL-->', () => panel + TAB_JS);
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.end(html);
};
