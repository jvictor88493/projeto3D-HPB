#!/usr/bin/env python3
"""Ensina/corrige a localização de uma recomendação e grava na base de conhecimento (tools/rep_locais.json).

Uso:
  python3 tools/rep_aprender.py N 'LOC_JSON' "Zona legível" [--regra 'regex_no_titulo' [--zona-regra "Zona genérica"]] [--obs "texto"] [--fora "motivo"]
Exemplos:
  python3 tools/rep_aprender.py 38 '{"t":"wall","w":"frente","el":48500,"tubos":[]}' "Penthouse · fechamento Oeste · perto da BV Norte"
  python3 tools/rep_aprender.py 57 '{"t":"grp","g":"vMDC","el":36000}' "Multiciclone · capela · ciclone 4 fileira 18" --regra 'multiciclone.*capela'
  python3 tools/rep_aprender.py 9 null "" --fora "Duto de ar secundário ainda não modelado"

Efeito:
  - memória confirmada para o item (chave = nota SAP ou título+recomendação): próximos reports com o mesmo item já saem com conf "alta";
  - se --regra for dada, cria/atualiza uma regra por palavra-chave (vale para itens novos parecidos);
  - atualiza o item no report atual (tools/out/rep_<N>.json e private/rec.html) e registra no histórico.
"""
import sys,os,json,re,datetime,glob
HERE=os.path.dirname(os.path.abspath(__file__));ROOT=os.path.dirname(HERE)
sys.path.insert(0,HERE);import rep_report as rr
args=sys.argv[1:]
def opt(k):
    if k in args: i=args.index(k);v=args[i+1];del args[i:i+2];return v
regra=opt('--regra');zregra=opt('--zona-regra');obs=opt('--obs');fora=opt('--fora')
n=int(args[0]);loc=json.loads(args[1]) if len(args)>1 else None;zona=args[2] if len(args)>2 else None
kb=json.load(open(rr.KB_PATH,encoding='utf8'))
js=sorted(glob.glob(os.path.join(HERE,'out','rep_*.json')),key=lambda f:int(re.search(r'rep_(\d+)',f).group(1)))
data=json.load(open(js[-1],encoding='utf8'));it=[x for x in data['itens'] if x['n']==n][0]
key=rr.sig(it)
gm={'vWB':'Fornalha','vCF':'Fornalha','vSW3':'Fornalha','vFT':'Fornalha','vMDC':'Multiciclone','vMDJ':'Multiciclone','vDTM':'Multiciclone','vDTE':'Multiciclone','vECO':'Economizador','vTT':'Penthouse','vDR':'Penthouse','vCL':'Penthouse','vWW':'Wingwall','vUB':'U-beam','vSP':'Superaquecedor primário','vSS':'Superaquecedor secundário','vDEA':'Desaerador'}
cj=None
if loc: cj='Fornalha' if loc['t'] in ('wall','div','piso') else gm.get(loc.get('g'))
mem={'loc':loc,'zona':zona or None,'conf':'alta' if loc else None,'conjunto':cj,'nota':obs,'fora':fora if not loc else None,
     'confirmado':True,'origem':'confirmado na conversa em '+datetime.date.today().isoformat(),'titulo':it['titulo'],'report':data['meta'].get('report')}
kb['memoria'][key]=mem
if regra:
    rid='u_'+re.sub(r'\W+','_',regra)[:30]
    kb['regras']=[r for r in kb['regras'] if r['id']!=rid]
    base={k:mem[k] for k in ('loc','zona','conjunto','nota','fora')};base['conf']='média' if loc else None
    base['zona']=zregra or (zona.split(' · ')[0] if zona else None);base['nota']=obs or 'Posição aprendida de item parecido: confirmar'
    kb['regras'].insert(0,dict(id=rid,padrao=regra,texto=False,**base))
kb['historico'].append({'data':datetime.datetime.now().isoformat(timespec='minutes'),'report':data['meta'].get('report'),'n':n,'chave':key,
    'antes':{'loc':it.get('loc'),'conf':it.get('conf'),'zona':it.get('zona')},'depois':{'loc':loc,'zona':zona},'regra':regra})
json.dump(kb,open(rr.KB_PATH,'w',encoding='utf8'),ensure_ascii=False,indent=1)
for k in ('loc','zona','conf','conjunto','nota','fora'): it[k]=mem[k]
json.dump(data,open(js[-1],'w',encoding='utf8'),ensure_ascii=False)
REC=os.path.join(ROOT,'private','rec.html');s=open(REC,encoding='utf8').read()
a=s.index('/*REPDATA*/')+len('/*REPDATA*/');b=s.index('/*ENDREPDATA*/');cur=json.loads(s[a:b])
for x in cur['itens']:
    if x['n']==n:
        for k in ('loc','zona','conf','conjunto','nota','fora'): x[k]=mem[k]
open(REC,'w',encoding='utf8').write(s[:a]+json.dumps(cur,ensure_ascii=False,separators=(',',':'))+s[b:])
print('aprendido:',n,key,json.dumps(loc,ensure_ascii=False),zona,'| regra' if regra else '')
