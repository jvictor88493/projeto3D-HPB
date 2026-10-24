const fs = require('fs');
const path = require('path');
const { readEmail, fullEmails, infoEmails } = require('./_auth');
module.exports = (req, res) => {
  res.setHeader('Cache-Control', 'private, no-store');
  res.setHeader('X-Robots-Tag', 'noindex, nofollow');
  const email = readEmail(req);
  if (!email) { res.statusCode = 302; res.setHeader('Location', '/login'); return res.end(); }
  if (!fullEmails().includes(email)) { res.statusCode = 403; res.setHeader('Content-Type', 'text/plain; charset=utf-8'); return res.end('Acesso restrito.'); }
  let html = fs.readFileSync(path.join(process.cwd(), 'private', 'full.html'), 'utf8');
  // Notas de conferencia/pendencias e lista de desenhos: so para quem tem acesso a aba Informacao.
  if (!infoEmails().includes(email)) html = html.replace(/<!--ADMIN_START-->[\s\S]*?<!--ADMIN_END-->/, '');
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.end(html);
};
