const { NAME } = require('./_auth');
module.exports = (req, res) => {
  res.setHeader('Set-Cookie', `${NAME}=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0`);
  res.statusCode = 302; res.setHeader('Location', '/login'); res.end();
};
