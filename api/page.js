const fs = require('fs');
const path = require('path');
const { readEmail, fullEmails } = require('./_auth');
// Quem ve a aba "Informacao" (padrao: so o e-mail principal). Pode ser sobrescrito pela variavel INFO_EMAILS.
function infoEmails() {
  return (process.env.INFO_EMAILS || 'jvictor88493@gmail.com').split(/[,;\s]+/).map(s => s.trim().toLowerCase()).filter(Boolean);
}
const FULL_UI = `<button id="bFull" class="cta alt" type="button" title="Abrir o 3D completo da caldeira"><svg class="i" viewBox="0 0 24 24"><path d="M12 3l8 4.5v9L12 21l-8-4.5v-9z"/><path d="M12 12l8-4.5M12 12L4 7.5M12 12v9"/></svg><span>3D HPB Completa</span></button>`;
const FULL_OVERLAY = `<div id="fullOv" hidden><div class="fbar"><button id="fullBack" type="button">&larr; Voltar</button><b>3D HPB Completa</b></div><iframe id="fullFr" title="3D HPB Completa" allow="fullscreen"></iframe></div>
<script>(function(){var b=document.getElementById('bFull'),o=document.getElementById('fullOv'),f=document.getElementById('fullFr'),k=document.getElementById('fullBack');if(!b||!o)return;
function open(){if(!f.getAttribute('src'))f.setAttribute('src','/api/full');o.hidden=false;document.documentElement.style.overflow='hidden'}
function close(){o.hidden=true;document.documentElement.style.overflow=''}
b.addEventListener('click',open);k.addEventListener('click',close);document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!o.hidden)close()})})();</script>`;
const TAB_JS = `<script>(function(){var v=document.getElementById("vizPane"),p=document.getElementById("infoPanel"),T={viz:document.getElementById("tViz"),acomp:document.getElementById("tAcomp"),info:document.getElementById("tInfo")};
function show(n){if(v)v.hidden=n==="info";if(p)p.hidden=n!=="info";Object.keys(T).forEach(function(k){var b=T[k];if(!b)return;b.classList.toggle("on",k===n);b.setAttribute("aria-current",k===n?"page":"false")});
if(window.__acompMode)window.__acompMode(n==="acomp");window.scrollTo(0,0)}
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
      (full ? '<button class="tab" id="tAcomp" type="button">Acompanhamento</button>' : '') +
      (info ? '<button class="tab" id="tInfo" type="button">Informação</button>' : '') + '</nav>';
  }
  html = html.replace('<!--INFO_NAV-->', () => nav).replace('<!--INFO_PANEL-->', () => panel + TAB_JS)
    .replace('<!--FULL_BTN-->', () => full ? FULL_UI : '').replace('<!--FULL_OVERLAY-->', () => full ? FULL_OVERLAY : '');
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.end(html);
};
