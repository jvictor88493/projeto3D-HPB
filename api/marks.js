// Marcacoes de bubble caps (retirado / montado), gravadas no Neon.
// GET: lotes ativos (todos os usuarios logados veem). POST: novo lote ou desfazer (so MARK_EMAILS; desfazer so o autor).
const { neon } = require('@neondatabase/serverless');
const { readEmail, fullEmails } = require('./_auth');

function markEmails() {
  return (process.env.MARK_EMAILS || 'hpb@timitecnologia.com,jvictor88493@gmail.com').split(/[,;\s]+/).map(s => s.trim().toLowerCase()).filter(Boolean);
}
function send(res, code, obj) {
  res.statusCode = code;
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('Cache-Control', 'private, no-store');
  res.end(JSON.stringify(obj));
}
async function readBody(req) {
  if (req.body && typeof req.body === 'object') return req.body;
  if (typeof req.body === 'string') { try { return JSON.parse(req.body); } catch (e) { return {}; } }
  return await new Promise(r => { let b = ''; req.on('data', d => { b += d; if (b.length > 2e6) req.destroy(); }); req.on('end', () => { try { r(JSON.parse(b || '{}')); } catch (e) { r({}); } }); });
}
const CELL = /^(\d{1,2}),(\d{1,3})$/;

module.exports = async (req, res) => {
  const email = readEmail(req);
  if (!email) return send(res, 401, { erro: 'Sessão expirada. Entre de novo.' });
  if (!fullEmails().includes(email)) return send(res, 403, { erro: 'Acesso restrito.' });
  if (!process.env.DATABASE_URL) return send(res, 500, { erro: 'Banco de dados não configurado.' });
  const sql = neon(process.env.DATABASE_URL);
  const canMark = markEmails().includes(email);
  try {
    if (req.method === 'GET') {
      const rows = await sql`SELECT id, acao, email, celulas, qtd, criado_em FROM bc_lotes WHERE desfeito_em IS NULL ORDER BY criado_em, id`;
      return send(res, 200, { me: email, canMark, lotes: rows });
    }
    if (req.method !== 'POST') return send(res, 405, { erro: 'Método não permitido.' });
    if (!canMark) return send(res, 403, { erro: 'Seu e-mail não tem permissão para marcar.' });
    const b = await readBody(req);
    if (b.desfazer != null) {
      const id = parseInt(b.desfazer, 10);
      if (!(id > 0)) return send(res, 400, { erro: 'Lote inválido.' });
      const r = await sql`UPDATE bc_lotes SET desfeito_em = now(), desfeito_por = ${email} WHERE id = ${id} AND email = ${email} AND desfeito_em IS NULL RETURNING id`;
      if (!r.length) return send(res, 403, { erro: 'Só quem fez a marcação pode desfazê-la.' });
      return send(res, 200, { ok: true, id });
    }
    const acao = b.acao;
    if (acao !== 'removido' && acao !== 'montado') return send(res, 400, { erro: 'Ação inválida.' });
    const seen = new Set();
    for (const c of Array.isArray(b.celulas) ? b.celulas : []) {
      const m = CELL.exec(String(c));
      if (!m) continue;
      const r = +m[1], k = +m[2];
      if (r < 79 && k < 125) seen.add(r + ',' + k);
    }
    const cells = [...seen];
    if (!cells.length) return send(res, 400, { erro: 'Nenhum bubble cap selecionado.' });
    if (cells.length > 4508) return send(res, 400, { erro: 'Seleção grande demais.' });
    const r = await sql`INSERT INTO bc_lotes (acao, email, celulas, qtd) VALUES (${acao}, ${email}, ${JSON.stringify(cells)}::jsonb, ${cells.length}) RETURNING id, acao, email, celulas, qtd, criado_em`;
    return send(res, 200, { ok: true, lote: r[0] });
  } catch (e) {
    console.error(e);
    return send(res, 500, { erro: 'Falha ao acessar o banco de dados. Tente de novo.' });
  }
};
