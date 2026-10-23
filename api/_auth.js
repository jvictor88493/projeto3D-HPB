const crypto = require('crypto');
const NAME = 'bc_auth';
function allowed() {
  return (process.env.ALLOWED_EMAILS || '').split(/[,;\s]+/).map(s => s.trim().toLowerCase()).filter(Boolean);
}
function sign(v) {
  return crypto.createHmac('sha256', process.env.AUTH_SECRET || '').update(v).digest('base64url');
}
function makeToken(email) {
  const p = Buffer.from(JSON.stringify({ e: email, x: Date.now() + 30 * 86400000 })).toString('base64url');
  return p + '.' + sign(p);
}
function readEmail(req) {
  if (!process.env.AUTH_SECRET) return null;
  const m = (req.headers.cookie || '').split(/;\s*/).find(c => c.startsWith(NAME + '='));
  if (!m) return null;
  const tok = m.slice(NAME.length + 1);
  const [p, sig] = tok.split('.');
  if (!p || !sig) return null;
  const good = Buffer.from(sign(p));
  const got = Buffer.from(sig);
  if (good.length !== got.length || !crypto.timingSafeEqual(good, got)) return null;
  try {
    const d = JSON.parse(Buffer.from(p, 'base64url').toString());
    if (!d.e || d.x < Date.now()) return null;
    return allowed().includes(d.e) ? d.e : null;
  } catch (e) { return null; }
}
module.exports = { NAME, allowed, makeToken, readEmail };
