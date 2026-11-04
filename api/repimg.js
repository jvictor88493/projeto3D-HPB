const fs = require('fs');
const path = require('path');
const { readEmail, fullEmails } = require('./_auth');
// Fotos (antes/depois) das recomendações dos reports — mesmo acesso da aba Recomendações.
module.exports = (req, res) => {
  const email = readEmail(req);
  if (!email || !fullEmails().includes(email)) { res.statusCode = 403; return res.end(); }
  const f = String((new URL(req.url, 'http://x')).searchParams.get('f') || '');
  if (!/^r\d+_\d+_[ad]\.jpg$/.test(f)) { res.statusCode = 400; return res.end(); }
  const p = path.join(process.cwd(), 'private', 'rep_img', f);
  if (!fs.existsSync(p)) { res.statusCode = 404; return res.end(); }
  res.setHeader('Content-Type', 'image/jpeg');
  res.setHeader('Cache-Control', 'private, max-age=86400');
  res.end(fs.readFileSync(p));
};
