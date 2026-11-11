const crypto = require('crypto');
// Envia HTML com ETag: o navegador guarda a pagina (cache privado) e, nas proximas visitas,
// so pergunta ao servidor se mudou. Sem mudanca -> resposta 304 vazia (nada e baixado de novo).
// O login continua sendo conferido em toda requisicao, antes de chegar aqui.
module.exports = function sendHtml(req, res, html) {
  const etag = '"' + crypto.createHash('sha1').update(html).digest('base64url') + '"';
  res.setHeader('Cache-Control', 'private, no-cache');
  res.setHeader('ETag', etag);
  res.setHeader('Vary', 'Cookie');
  const inm = String(req.headers['if-none-match'] || '');
  if (inm.split(/\s*,\s*/).some(t => t.replace(/^W\//, '') === etag)) { res.statusCode = 304; return res.end(); }
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.end(html);
};
