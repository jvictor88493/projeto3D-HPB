const fs = require('fs');
const path = require('path');
const sendHtml = require('./_send');
const { readEmail, fullEmails } = require('./_auth');
// Quem ve a aba "Informacao" (padrao: so o e-mail principal). Pode ser sobrescrito pela variavel INFO_EMAILS.
function infoEmails() {
  return (process.env.INFO_EMAILS || 'jvictor88493@gmail.com').split(/[,;\s]+/).map(s => s.trim().toLowerCase()).filter(Boolean);
}
// As abas 3D ficam na mesma pagina (iframes carregados no primeiro clique e mantidos abertos):
// voltar a uma aba ja aberta e instantaneo. /completa e /recomendacoes abrem a pagina ja na aba.
const FULL_PANE = `<section id="fullPane" class="fpane" hidden><iframe id="fullFr" title="3D HPB Completa" allow="fullscreen"></iframe></section><section id="recPane" class="fpane" hidden><iframe id="recFr" title="Recomendações" allow="fullscreen"></iframe></section><section id="acPane" class="fpane" hidden><iframe id="acFr" title="Acompanhamento" allow="fullscreen"></iframe></section>`;
const TAB_JS = `<script>(function(){var v=document.getElementById("vizPane"),p=document.getElementById("infoPanel"),f=document.getElementById("fullPane"),fr=document.getElementById("fullFr"),g=document.getElementById("recPane"),gr=document.getElementById("recFr"),a=document.getElementById("acPane"),ar=document.getElementById("acFr"),T={viz:document.getElementById("tViz"),full:document.getElementById("tFull"),rec:document.getElementById("tRec"),ac:document.getElementById("tAc"),info:document.getElementById("tInfo")},U={viz:"/",full:"/completa",rec:"/recomendacoes",ac:"/#ac",info:"/#info"};
function show(n){if(!T[n])n="viz";if(v)v.hidden=n!=="viz";if(p)p.hidden=n!=="info";if(f){f.hidden=n!=="full";if(n==="full"&&fr&&!fr.getAttribute("src"))fr.setAttribute("src","/api/full")}if(g){g.hidden=n!=="rec";if(n==="rec"&&gr&&!gr.getAttribute("src"))gr.setAttribute("src","/api/rec")}if(a){a.hidden=n!=="ac";if(n==="ac"&&ar&&!ar.getAttribute("src"))ar.setAttribute("src","/api/acomp")}
Object.keys(T).forEach(function(k){var b=T[k];if(!b)return;b.classList.toggle("on",k===n);b.setAttribute("aria-current",k===n?"page":"false")});document.body.classList.remove("fopen");document.body.classList.toggle("tabfull",n==="full"||n==="rec"||n==="ac");
try{history.replaceState(null,"",U[n])}catch(e){}window.scrollTo(0,0)}
Object.keys(T).forEach(function(k){if(T[k])T[k].onclick=function(){show(k)}});window.__showViz=function(){show("viz")};
// Aba inicial (/completa, /recomendacoes, /#ac, /#info): so depois de montar o mapa principal (montado escondido ele quebra).
function initTab(){var n=window.__initTab||(location.hash||"").slice(1);if(n&&T[n])show(n)}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",initTab);else initTab()})();</script>`;
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
  const init = full && (view === 'full' || view === 'rec') ? view : '';
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
    nav = '<nav class="tabs"><button class="tab on" id="tViz" aria-current="page" type="button">Mapa bubble caps</button>' +
      (full ? '<button class="tab" id="tFull" type="button">3D HPB Completa</button><button class="tab" id="tRec" type="button">Recomendações</button><button class="tab" id="tAc" type="button">Acompanhamento</button>' : '') +
      (info ? '<button class="tab" id="tInfo" type="button">Informação</button>' : '') + '</nav>';
  }
  const initJs = init ? `<script>window.__initTab=${JSON.stringify(init)}</script>` : '';
  html = html.replace('<!--INFO_NAV-->', () => nav).replace('<!--FULL_PANE-->', () => full ? FULL_PANE : '').replace('<!--INFO_PANEL-->', () => panel + initJs + TAB_JS);
  sendHtml(req, res, html);
};
