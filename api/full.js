const fs = require('fs');
const path = require('path');
const { readEmail, fullEmails } = require('./_auth');
// Visual do site aplicado ao 3D completo (so variaveis de cor/forma; a funcionalidade do arquivo nao muda).
const SKIN = `<style id="skin-site">
:root{--bg:#f1f4f8;--panel:#ffffff;--ink:#14233b;--muted:#6b778a;--line:#e1e7ef;--accent:#0f2e57;--accent-bg:#e8eef8;--scene:#dde4ed;--chip:#f1f4f8;--shadow:0 1px 2px rgba(20,35,59,.06),0 4px 14px rgba(20,35,59,.05)}
@media (prefers-color-scheme: dark){:root{--bg:#0e1524;--panel:#16203a;--ink:#e8edf6;--muted:#97a3b8;--line:#26334f;--accent:#9db9e8;--accent-bg:#1d2e50;--scene:#101a2e;--chip:#1b2742;--shadow:none}}
.chip,button,input[type=text]{border-radius:10px}
.chip,button{box-shadow:var(--shadow)}
button.on{background:var(--accent);border-color:var(--accent);color:#fff}
@media (prefers-color-scheme: dark){button.on{color:#0e1524}}
#wrap{border-radius:14px;box-shadow:var(--shadow)}
details{border-radius:14px;box-shadow:var(--shadow)}
input[type=range]{accent-color:#f26a1b}
@media (max-width:820px),(max-height:500px) and (orientation:landscape){
.page{display:flex;flex-direction:column;padding:6px 8px 16px}
h1{order:-2;font-size:13px;margin:2px 2px 6px}
#wrap{order:-1;height:calc(100dvh - 96px);min-height:260px;margin-bottom:8px}
.chip{padding:3px 8px;font-size:11.5px}
button{padding:4px 9px;font-size:12px}
.grp,.bar{gap:6px}
}
</style>`;
module.exports = (req, res) => {
  res.setHeader('Cache-Control', 'private, no-store');
  res.setHeader('X-Robots-Tag', 'noindex, nofollow');
  const email = readEmail(req);
  if (!email) { res.statusCode = 302; res.setHeader('Location', '/login'); return res.end(); }
  if (!fullEmails().includes(email)) { res.statusCode = 403; res.setHeader('Content-Type', 'text/plain; charset=utf-8'); return res.end('Acesso restrito.'); }
  let html = fs.readFileSync(path.join(process.cwd(), 'private', 'full.html'), 'utf8');
  html = html.replace('</head>', () => SKIN + '</head>');
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.end(html);
};
