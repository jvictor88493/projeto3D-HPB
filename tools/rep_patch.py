# Aplica em private/rec.html: fotos "depois" vindas do report (tools/rep_depois/dep_<n>.jpg) e remove o "Anexar foto".
import json,base64,glob,os,re
HERE=os.path.dirname(os.path.abspath(__file__))
R=os.path.join(HERE,'..','private','rec.html')
s=open(R,encoding='utf8').read()
k=s.index('var REP=/*REPDATA*/')+len('var REP=/*REPDATA*/');o,end=json.JSONDecoder().raw_decode(s[k:])
dep={}
for f in glob.glob(os.path.join(HERE,'rep_depois','r%s_dep_*.jpg'%o['meta'].get('report',''))):
    n=int(re.search(r'_dep_(\d+)',f).group(1));rp=o['meta'].get('report','');d=os.path.join(HERE,'..','private','rep_img');os.makedirs(d,exist_ok=True)
    open(os.path.join(d,'r%s_%d_d.jpg'%(rp,n)),'wb').write(open(f,'rb').read());dep[n]='/api/repimg?f=r%s_%d_d.jpg'%(rp,n)
for it in o['itens']:
    if it['n'] in dep: it['depois']=dep[it['n']]   # foto enviada na conversa tem prioridade sobre a do PDF
s=s[:k]+json.dumps(o,ensure_ascii=False,separators=(',',':'))+s[k+end:]
def rep(a,b):
    global s
    if a in s: s=s.replace(a,b)
    elif b not in s: raise SystemExit('trecho nao encontrado: '+a[:60])
rep('function depGet(n){if(repDep[n])return repDep[n];try{return localStorage.getItem(depKey(n))}catch(e){return null}}',
    'function depGet(n){var it=repItem(n);return it&&it.depois||null}')
rep("""(dep?"<img src='"+dep+"' alt='Foto depois do reparo'><div style='margin-top:6px'><button type='button' class='chip' id='rdDel'>Remover foto</button></div>":"<div class='rempty'>Ainda sem foto do depois<label class='chip'>Anexar foto<input type='file' accept='image/*' id='rdFile' hidden></label></div>")""",
    """(dep?"<img src='"+dep+"' alt='Foto depois do reparo'>":"<div class='rempty'>Sem foto do depois no report</div>")""")
if 'id="rec-ui"' not in s:
    s=s.replace('</head>','<style id="rec-ui">@media (min-width:821px){.repmode .grid{grid-template-columns:minmax(0,1fr) minmax(360px,32%)!important}.repmode .side{order:0!important;top:0;max-height:calc(100vh - 92px)!important}.repmode #wrap{height:calc(100vh - 92px)!important}.repmode #rep .rl{max-height:calc(100vh - 330px)}}</style>\n</head>',1)
open(R,'w',encoding='utf8').write(s)
print('depois aplicados:',sorted(dep))
