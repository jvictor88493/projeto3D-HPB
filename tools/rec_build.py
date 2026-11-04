# Gera private/rec.html = private/full.html (modelo atual do 3D HPB Completa) + modulo "Reparos do report"
# extraido de um arquivo de reparos (vN) por diferenca contra a base 3D que ele usou.
import difflib,re,sys,json
SC='/tmp/claude-0/-home-claude/a9cf151c-8bb3-5936-89bb-628d4d806cb3/scratchpad/full/'
R='/home/claude/projeto3d-hpb/private/'
base=open(sys.argv[1],encoding='utf8').read()   # base 3D usada pelo arquivo de reparos
rep=open(sys.argv[2],encoding='utf8').read()    # arquivo de reparos
tgt=open(R+'full.html',encoding='utf8').read()
def toks(s): return re.split(r'(?<=[;}>\n])',s)
A=toks(base);B=toks(rep)
sm=difflib.SequenceMatcher(None,A,B,autojunk=False)
patches=[]
for op,i1,i2,j1,j2 in sm.get_opcodes():
    if op=='equal':continue
    old=''.join(A[i1:i2]);new=''.join(B[j1:j2])
    pre=''.join(B[max(0,j1-6):j1])
    patches.append((op,old,new,pre))
skip_old=('MAPA 3D','</title>','Desaerador','gDEA','vDEA','Montado (v35)','v35: desaerador','window.__bc={v35')
out=tgt;applied=0;skipped=[]
for op,old,new,pre in patches:
    if op=='delete': skipped.append(('del',old[:60]));continue
    if any(k in old for k in skip_old) and op!='insert':
        # trechos que existem so na base (ex.: desaerador) ou cabecalho: tratar caso a caso
        if op=='replace' and 'forEach(function(id){$(id).addEve' in old:
            out=re.sub(r'(\]\.forEach\(function\(id\)\{\$\(id\)\.addEventListener\("change",vis\)\}\);)',lambda m:',"vREP"'+m.group(1),out,count=1) if '"vREP"' not in out else out
            applied+=1;continue
        if op=='replace' and 'var CJ=' in old:
            continue
        skipped.append(('rep',old[:60]));continue
    if new.startswith('<li><span class="t-ok">Montado (v1).') or 'Montado (v1).' in new[:200]: skipped.append(('note','v1'));continue
    if op=='replace':
        if old in out and out.count(old)==1: out=out.replace(old,new);applied+=1;continue
        if 'forEach(function(id){$(id).addEve' in old:
            out=re.sub(r'(\]\.forEach\(function\(id\)\{\$\(id\)\.addEventListener\("change",vis\)\}\);)',lambda m:',"vREP"'+m.group(1),out,count=1);applied+=1;continue
        if 'var CJ=' in old: continue
        if 'window.__bc=' in old: continue
        skipped.append(('rep?',old[:80]));continue
    # insert: achar ancora (fim do trecho anterior) unica no alvo
    ok=False
    for L in (200,120,80,50,30):
        a=pre[-L:]
        if a and out.count(a)==1:
            k=out.index(a)+len(a);out=out[:k]+new+out[k:];ok=True;applied+=1;break
    if not ok: skipped.append(('ins',pre[-80:],new[:80]))
# CJ + GM do modulo de reparos (vale para qualquer CJ)
m=re.search(r'GM=\{.*?\}\}?,NM=\{\}',out)
if 'GM.vREP=' not in out:
    out=out.replace(',NM={};',',NM={};Object.keys(CJ).forEach(function(k){CJ[k].push("vREP")});GM.vREP=function(){return [gREP]};',1)
out=re.sub(r'<title>[^<]*','<title>Mapa 3D reparos HPB',out,count=1)
open(R+'rec.html','w',encoding='utf8').write(out)
print('aplicados',applied);[print(' pulado',x) for x in skipped]
for k in ('gREP.visible','"vREP"','id="rep"','repShow','GM.vREP','REPDATA'): print(k,out.count(k))
