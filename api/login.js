const { NAME, allowed, makeToken } = require('./_auth');
module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('Content-Type', 'application/json');
  if (req.method !== 'POST') { res.statusCode = 405; return res.end('{}'); }
  if (!process.env.AUTH_SECRET) { res.statusCode = 500; return res.end('{"ok":false,"erro":"config"}'); }
  let b = req.body;
  if (typeof b === 'string') { try { b = JSON.parse(b); } catch (e) { b = {}; } }
  const email = String((b && b.email) || '').trim().toLowerCase();
  await new Promise(r => setTimeout(r, 400));
  if (!email || !allowed().includes(email)) { res.statusCode = 401; return res.end('{"ok":false}'); }
  res.setHeader('Set-Cookie', `${NAME}=${makeToken(email)}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=2592000`);
  res.end('{"ok":true}');
};
