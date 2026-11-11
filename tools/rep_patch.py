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
CTK=json.load(open(os.path.join(HERE,'rep_ct.json'),encoding='utf8'))['ct_por_nota'] if os.path.exists(os.path.join(HERE,'rep_ct.json')) else {}
for it in o['itens']:
    if it['n'] in dep: it['depois']=dep[it['n']]   # foto enviada na conversa tem prioridade sobre a do PDF
    if not it.get('ct') and it.get('ref') in CTK: it['ct']=CTK[it['ref']]   # CT conhecido pela nota SAP (rep_ct.json)
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
    s=s.replace('</head>','<style id="rec-ui">#repMob{display:none}@media (max-width:820px){#repMob{display:block;padding:10px 10px 90px}#repMob #rep{margin:0}#repMob #rep .rl{max-height:none!important;overflow:visible}}@media (min-width:821px){.repmode .grid{grid-template-columns:minmax(0,1fr) minmax(360px,32%)!important}.repmode .side{order:0!important;top:0;max-height:calc(100vh - 92px)!important}.repmode #wrap{height:calc(100vh - 92px)!important}.repmode #rep .rl{max-height:calc(100vh - 330px)}}</style>\n</head>',1)
if 'id="rep-mob"' not in s:
    js='''<script id="rep-mob">(function(){var rep=document.getElementById('rep'),side=document.querySelector('.side'),st=document.querySelector('.stage');if(!rep||!side||!st)return;
var box=document.createElement('div');box.id='repMob';st.parentNode.insertBefore(box,st.nextSibling);var home=rep.nextSibling,mq=matchMedia('(max-width:820px)');
function place(){if(mq.matches){if(rep.parentNode!==box)box.appendChild(rep)}else if(rep.parentNode!==side){side.insertBefore(rep,home&&home.parentNode===side?home:side.firstChild)}}
if(mq.matches){var c3=box.querySelector('#repChips [data-f=only3d]')||document.querySelector('#repChips [data-f=only3d]');if(c3&&!c3.classList.contains('on'))c3.click()}
box.addEventListener('click',function(e){if(mq.matches&&e.target.closest('#repRows button,#rdPrev,#rdNext'))setTimeout(function(){window.scrollTo(0,0)},60)},true);place();(mq.addEventListener?mq.addEventListener('change',place):mq.addListener(place))})();</script>'''
    k=s.rindex('</body>');s=s[:k]+js+'\n'+s[k:]
# expoe dados e repShow para o painel (o modulo do 3D roda dentro de uma funcao)
if 'window.__REP=REP' not in s: s=s.replace('/*ENDREPDATA*/;','/*ENDREPDATA*/;window.__REP=REP;window.__repShow=function(n,f){return repShow(n,f)};',1)
# painel de recomendacoes (sub-aba "Painel"): tools/rec_painel.html
P=open(os.path.join(HERE,'rec_painel.html'),encoding='utf8').read()
part={};cur=None
for ln in P.split('\n'):
    if ln.startswith('@@'): cur=ln[2:].strip();part[cur]=[];continue
    if cur: part[cur].append(ln)
part={k:'\n'.join(v).strip() for k,v in part.items()}
s=re.sub(r'<style id="rp-ui">.*?</style>\n?','',s,flags=re.S);s=re.sub(r'<!--rp-html-->.*?<!--/rp-html-->\n?','',s,flags=re.S);s=re.sub(r'<script id="rp-js">.*?</script>\n?','',s,flags=re.S)
s=s.replace('</head>',part['CSS']+'\n</head>',1)
s=s.replace('<div class="page">','<div class="page">\n<!--rp-html-->'+part['HTML']+'<!--/rp-html-->',1)
k=s.rindex('</body>');s=s[:k]+part['JS']+'\n'+s[k:]
open(R,'w',encoding='utf8').write(s)
print('depois aplicados:',sorted(dep))
