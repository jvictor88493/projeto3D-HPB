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
// Quem ve o botao "3D HPB Completa" (padrao abaixo; pode ser sobrescrito pela variavel FULL_EMAILS).
const FULL_DEFAULT = 'jvictor88493@gmail.com,hpb@timitecnologia.com,thiago.morais@hydro.com,luana@luanaandrade.com,emanuel.rosario@hydro.com,maviano.silva@hydro.com,mario.mendes.neto@hydro.com,nerio.pereira@hydro.com';
function fullEmails() {
  return (process.env.FULL_EMAILS || FULL_DEFAULT).split(/[,;\s]+/).map(s => s.trim().toLowerCase()).filter(Boolean);
}
// Quem ve a aba "Informacao" e as notas tecnicas do 3D completo (padrao: so o e-mail principal; variavel INFO_EMAILS).
function infoEmails() {
  return (process.env.INFO_EMAILS || 'jvictor88493@gmail.com').split(/[,;\s]+/).map(s => s.trim().toLowerCase()).filter(Boolean);
}
module.exports = { NAME, allowed, makeToken, readEmail, fullEmails, infoEmails };
