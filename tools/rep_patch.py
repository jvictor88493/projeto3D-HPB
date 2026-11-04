# Aplica em private/rec.html: fotos "depois" vindas do report (tools/rep_depois/dep_<n>.jpg) e remove o "Anexar foto".
import json,base64,glob,os,re
HERE=os.path.dirname(os.path.abspath(__file__))
R=os.path.join(HERE,'..','private','rec.html')
s=open(R,encoding='utf8').read()
k=s.index('var REP=/*REPDATA*/')+len('var REP=/*REPDATA*/');o,end=json.JSONDecoder().raw_decode(s[k:])
dep={}
for f in glob.glob(os.path.join(HERE,'rep_depois','dep_*.jpg')):
    n=int(re.search(r'dep_(\d+)',f).group(1));dep[n]='data:image/jpeg;base64,'+base64.b64encode(open(f,'rb').read()).decode()
for it in o['itens']:
    if it['n'] in dep: it['depois']=dep[it['n']]
    else: it.pop('depois',None)
s=s[:k]+json.dumps(o,ensure_ascii=False,separators=(',',':'))+s[k+end:]
def rep(a,b):
    global s
    if a in s: s=s.replace(a,b)
    elif b not in s: raise SystemExit('trecho nao encontrado: '+a[:60])
rep('function depGet(n){if(repDep[n])return repDep[n];try{return localStorage.getItem(depKey(n))}catch(e){return null}}',
    'function depGet(n){var it=repItem(n);return it&&it.depois||null}')
rep("""(dep?"<img src='"+dep+"' alt='Foto depois do reparo'><div style='margin-top:6px'><button type='button' class='chip' id='rdDel'>Remover foto</button></div>":"<div class='rempty'>Ainda sem foto do depois<label class='chip'>Anexar foto<input type='file' accept='image/*' id='rdFile' hidden></label></div>")""",
    """(dep?"<img src='"+dep+"' alt='Foto depois do reparo'>":"<div class='rempty'>Sem foto do depois no report</div>")""")
open(R,'w',encoding='utf8').write(s)
print('depois aplicados:',sorted(dep))
