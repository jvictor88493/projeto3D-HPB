const fs = require('fs');
const path = require('path');
const { readEmail } = require('./_auth');
module.exports = (req, res) => {
  res.setHeader('Cache-Control', 'private, no-store');
  res.setHeader('X-Robots-Tag', 'noindex, nofollow');
  if (!readEmail(req)) { res.statusCode = 302; res.setHeader('Location', '/login'); return res.end(); }
  const html = fs.readFileSync(path.join(process.cwd(), 'private', 'index.html'));
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.end(html);
};
