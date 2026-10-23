const fs = require('fs');
const path = require('path');
const { readEmail } = require('./_auth');
// Quem ve a aba "Informacao" (padrao: so o e-mail principal). Pode ser sobrescrito pela variavel INFO_EMAILS.
function infoEmails() {
  return (process.env.INFO_EMAILS || 'jvictor88493@gmail.com').split(/[,;\s]+/).map(s => s.trim().toLowerCase()).filter(Boolean);
}
module.exports = (req, res) => {
  res.setHeader('Cache-Control', 'private, no-store');
  res.setHeader('X-Robots-Tag', 'noindex, nofollow');
  const email = readEmail(req);
  if (!email) { res.statusCode = 302; res.setHeader('Location', '/login'); return res.end(); }
  const dir = path.join(process.cwd(), 'private');
  let html = fs.readFileSync(path.join(dir, 'index.html'), 'utf8');
  let nav = '', panel = '';
  if (infoEmails().includes(email)) {
    const parts = fs.readFileSync(path.join(dir, 'info.html'), 'utf8').split('<!--SPLIT-->');
    nav = parts[0] || ''; panel = parts[1] || '';
  }
  html = html.replace('<!--INFO_NAV-->', () => nav).replace('<!--INFO_PANEL-->', () => panel);
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.end(html);
};
