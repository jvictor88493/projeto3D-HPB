const fs = require('fs');
const path = require('path');
const sendHtml = require('./_send');
const { readEmail, fullEmails } = require('./_auth');
// Aba "Recomendacoes": mapa 3D de reparos (mesmo acesso da aba 3D HPB Completa).
module.exports = (req, res) => {
  res.setHeader('Cache-Control', 'private, no-store'); // respostas de erro/redirecionamento; a pagina usa sendHtml (ETag)
  res.setHeader('X-Robots-Tag', 'noindex, nofollow');
  const email = readEmail(req);
  if (!email) { res.statusCode = 302; res.setHeader('Location', '/login'); return res.end(); }
  if (!fullEmails().includes(email)) { res.statusCode = 403; res.setHeader('Content-Type', 'text/plain; charset=utf-8'); return res.end('Acesso restrito.'); }
  sendHtml(req, res, fs.readFileSync(path.join(process.cwd(), 'private', 'rec.html'), 'utf8'));
};
