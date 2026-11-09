# Gera private/acomp.html (aba Acompanhamento) = private/index.html (mesmo 3D da aba Visualizacao)
# + modulo de andamento do overhaul lido do cronograma MS Project (XML).
# Uso: python3 tools/acomp_build.py CRONOGRAMA.xml
#   - le as tarefas da FORNALHA pelo NOME (nao pelo WBS), grava tools/out/acomp_tasks.json
#   - se o XML nao for passado, reaproveita tools/out/acomp_tasks.json (ex.: apos atualizar o full.html)
import sys, os, re, json
import xml.etree.ElementTree as ET
HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(os.path.dirname(HERE), 'private') + '/'
OUTJ = os.path.join(HERE, 'out', 'acomp_tasks.json')
NS = {'p': 'http://schemas.microsoft.com/project'}

def norm(s):
    s = (s or '').upper()
    for a, b in (('Á','A'),('Â','A'),('Ã','A'),('À','A'),('É','E'),('Ê','E'),('Í','I'),('Ó','O'),('Ô','O'),('Õ','O'),('Ú','U'),('Ç','C')):
        s = s.replace(a, b)
    return re.sub(r'\s+', ' ', s).strip()

def parse(xml):
    r = ET.parse(xml).getroot()
    g = lambda e, k: (e.find('p:' + k, NS).text if e.find('p:' + k, NS) is not None else None)
    st = g(r, 'StatusDate') or g(r, 'CurrentDate')
    T = []
    for e in r.find('p:Tasks', NS).findall('p:Task', NS):
        if not g(e, 'WBS') or not g(e, 'Start'): continue
        T.append(dict(w=g(e, 'WBS'), n=(g(e, 'Name') or '').strip(), lv=int(g(e, 'OutlineLevel') or 0), s=g(e, 'Start')[:16], f=g(e, 'Finish')[:16],
                      p=int(float(g(e, 'PercentComplete') or 0)), sum=g(e, 'Summary') == '1'))
    return dict(start=g(r, 'StartDate')[:16], finish=g(r, 'FinishDate')[:16], status=st[:16], title=g(r, 'Title'), saved=(g(r, 'LastSaved') or '')[:16]), T

def kids(T, w):
    return [t for t in T if t['w'].startswith(w + '.') and t['w'].count('.') == w.count('.') + 1]
def under(T, w):
    return [t for t in T if t['w'].startswith(w + '.')]
def find(L, pat, summ=None):
    for t in L:
        if re.search(pat, norm(t['n'])) and (summ is None or t['sum'] == summ): return t
    return None

def build_cfg(meta, T):
    forn = find([t for t in T if t['lv'] == 2], r'^FORNALHA$')
    assert forn, 'tarefa resumo FORNALHA nao encontrada'
    F = under(T, forn['w'])
    miss = []
    def need(t, what):
        if not t: miss.append(what)
        return t['w'] if t else None
    cfg = {'caps': {}, 'f2': [], 'front': {}, 'rear': {}, 'div': [], 'floor': []}
    # fase 01: CAMARA INTERNA DA FORNALHA C1..C6 -> 6 etapas
    STEPS = [r'CORTE', r'CASQUILHO', r'LUVA', r'MONTAGEM DE NOVOS', r'SOLDAGEM', r'INSPECAO']
    for t in F:
        m = re.search(r'CAMARA ?INTERNA DA FORNALHA C(\d)', norm(t['n']))
        if m and t['sum']:
            K = kids(T, t['w'])
            cfg['caps'][m.group(1)] = [need(find(K, p), 'C%s %s' % (m.group(1), p)) for p in STEPS]
    if len(cfg['caps']) != 6: miss.append('camaras C1..C6 (achadas: %s)' % sorted(cfg['caps']))
    # fase 02 (216 caps, posicao nao informada)
    f2 = find(F, r'BUBLE CAPS FASE 02|BUBBLE CAPS FASE 02', True)
    if f2:
        K = kids(T, f2['w'])
        rem, cas, mon, sol, ins = (find(K, r'^REMOVER BUBBLE'), find(K, r'CASQUILHO'), find(K, r'^MONTAR BUBBLE'), find(K, r'^SOLDAR BUBBLE'), find(K, r'INSPECAO POR EV DO PISO'))
        cfg['f2'] = [need(rem, 'F2 remover'), need(cas, 'F2 casquilho'), need(cas, 'F2 casquilho'), need(mon, 'F2 montar'), need(sol, 'F2 soldar'), need(ins, 'F2 inspecao')]
        m = re.search(r'(\d+)', norm(rem['n'])) if rem else None
        cfg['f2n'] = int(m.group(1)) if m else 216
    # tubos RDZ 25k
    fr = find(F, r'^PAREDE FRONTAL 25K', True)
    if fr:
        K = kids(T, fr['w'])
        cfg['front'] = dict(cut=need(find(K, r'^CORTE DOS TUBOS'), 'frontal corte'), mount=need(find(K, r'^MONTAR TUBOS'), 'frontal montar'),
                            us=need(find(K, r'^FAZER US'), 'frontal US'), aleta=need(find(K, r'ALETA'), 'frontal aleta'),
                            tubes=[[int(re.search(r'TUBO (\d+)', norm(k['n'])).group(1)), k['w']] for k in K if re.search(r'^SOLDAGEM TUBO \d+', norm(k['n']))])
    else: miss.append('PAREDE FRONTAL 25K')
    rr = find(F, r'^PAREDE TRASEIRA 25K', True)
    if rr:
        K = kids(T, rr['w'])
        c = find(K, r'^CORTAR TUBO'); mt = find(K, r'^MONTAR TUBOS')
        n0 = int(re.search(r'TUBO (\d+)', norm(c['n'])).group(1)) if c else 35
        nt = int(re.search(r'\((\d+) TUBOS\)', norm(mt['n'])).group(1)) if mt and re.search(r'\((\d+) TUBOS\)', norm(mt['n'])) else 13
        cfg['rear'] = dict(cut=need(c, 'traseira corte'), mount=need(mt, 'traseira montar'), weld=need(find(K, r'^SOLDAR TUBOS'), 'traseira soldar'),
                           us=need(find(K, r'^FAZER US'), 'traseira US'), aleta=need(find(K, r'ALETA'), 'traseira aleta'), first=n0, n=nt)
    else: miss.append('PAREDE TRASEIRA 25K')
    dv = find(F, r'^PAREDE DIVISORIA 25K', True)
    if dv:
        for k in kids(T, dv['w']):
            nm = norm(k['n']); m = re.search(r'TUBO (\d+)', nm); d = re.search(r'DIVISORIA (\d)', nm)
            if m: cfg['div'].append([int(m.group(1)), int(d.group(1)) if d else 3, k['w'], 0 if d else 1])
    for k in F:
        m = re.search(r'^SUBSTITUIR (\d+) TUBOS DO PISO', norm(k['n']))
        if m and not k['sum']: cfg['floor'].append([k['w'], int(m.group(1))])
    # tarefas exibidas na lista "em curso": todas as folhas da fornalha
    used = set(F_['w'] for F_ in F if not F_['sum'])
    tasks = {t['w']: [t['n'], t['s'], t['f'], t['p']] for t in F if not t['sum']}
    sumn = {t['w']: t['n'] for t in F if t['sum']}
    return dict(meta=meta, cfg=cfg, tasks=tasks, sumn=sumn), miss

if len(sys.argv) > 1:
    meta, T = parse(sys.argv[1])
    data, miss = build_cfg(meta, T)
    os.makedirs(os.path.dirname(OUTJ), exist_ok=True)
    json.dump(data, open(OUTJ, 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
    print('cronograma:', meta['title'], '| status', meta['status'], '| tarefas da fornalha:', len(data['tasks']))
    for m in miss: print('  NAO ENCONTRADO:', m)
data = json.load(open(OUTJ, encoding='utf8'))

# base: a aba Visualizacao (private/index.html), sem o cabecalho/abas do site (a aba abre dentro de um iframe)
o = open(R + 'index.html', encoding='utf8').read()
mod = open(os.path.join(HERE, 'acomp_mod.html'), encoding='utf8').read()
part = dict(re.findall(r'@@(\w+)\n(.*?)(?=\n@@\w+\n|\Z)', mod, re.S))
for ph in ('<!--INFO_NAV-->', '<!--FULL_PANE-->', '<!--INFO_PANEL-->'):
    o = o.replace(ph, '')
o = o.replace('<script defer src="/_vercel/insights/script.js"></script>', '')
o = re.sub(r'<title>[^<]*', '<title>Acompanhamento do overhaul HPB · Bubble caps', o, count=1)
o = o.replace('</head>', part['CSS'] + '\n</head>', 1)
k = o.index('<main class="grid">'); o = o[:k] + part['BAR'] + '\n' + o[k:]
a = '<aside class="side"><button id="fclose" type="button">Fechar ✕</button>'
assert o.count(a) == 1, 'painel lateral da Visualizacao mudou'
o = o.replace(a, a + '\n' + part['CARD'], 1)
init = 'setClip();layoutCaps();colorCaps();vis();'
assert o.count(init) == 1, 'linha de inicializacao do 3D mudou'
js = part['JS'].replace('/*ACDATA*/', json.dumps(data, ensure_ascii=False, separators=(',', ':')))
o = o.replace(init, js + '\n' + init, 1)
open(R + 'acomp.html', 'w', encoding='utf8').write(o)
print('ok private/acomp.html', len(o))
