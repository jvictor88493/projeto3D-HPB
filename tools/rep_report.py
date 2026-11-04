#!/usr/bin/env python3
"""Lê um report de inspeção (PDF ISQ/Hydro), localiza cada recomendação no 3D da HPB e grava os dados na aba Recomendações.

Uso:
  python3 tools/rep_report.py REPORT.pdf            # gera tools/out/rep_<N>.json + relatório de localização e injeta em private/rec.html
  python3 tools/rep_report.py REPORT.pdf --dry-run  # só gera o JSON e o relatório, sem mexer no site

Localização (em ordem de prioridade):
  1. memória confirmada (tools/rep_locais.json -> "memoria", confirmado=true)      -> conf "alta"
  2. leitura explícita do texto (divisória N, parede X, tubo(s), elevação)          -> conf "alta"/"média"
  3. memória automática de reports anteriores (mesmo item / mesma nota SAP)       -> conf da memória
  4. regras por palavra-chave (tools/rep_locais.json -> "regras")                 -> conf da regra
  5. nada encontrado -> fora do 3D ("Local não identificado: revisar")
"""
import sys,os,re,json,io,base64,unicodedata,datetime
import pdfplumber
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__));ROOT=os.path.dirname(HERE)
KB_PATH=os.path.join(HERE,'rep_locais.json')
REC=os.path.join(ROOT,'private','rec.html')
DEP_DIR=os.path.join(HERE,'rep_depois')

def norm(s):
    s=unicodedata.normalize('NFD',s or '').encode('ascii','ignore').decode().lower()
    return re.sub(r'\s+',' ',s).strip()
def sig(it):
    """chave estável de um item entre reports: nota SAP se houver, senão título+recomendação normalizados"""
    if it.get('ref'): return 'sap:'+it['ref']
    return 'txt:'+norm(it['titulo'])+'|'+norm(it['rec'])[:120]

# ---------------- leitura do PDF ----------------
def words_in(ws,x0,x1,t0,t1,skip=()):
    out=[w for w in ws if w['x0']>=x0-1 and w['x1']<=x1+1 and w['top']>=t0-1 and w['top']<t1 and w['text'] not in skip]
    out.sort(key=lambda w:(round(w['top']/4),w['x0']))
    return ' '.join(w['text'] for w in out).strip()
def find(ws,txt,after=None):
    c=[w for w in ws if w['text']==txt and (after is None or w['top']>after)]
    return c[0] if c else None
IMG_DIR=os.path.join(ROOT,'private','rep_img')
def crop_jpg(pg,ims,maxw=900,res=170):
    x0=min(i['x0'] for i in ims);x1=max(i['x1'] for i in ims);t=min(i['top'] for i in ims);b=max(i['bottom'] for i in ims)
    im=pg.crop((max(0,x0),max(0,t),min(pg.width,x1),min(pg.height,b))).to_image(resolution=res).original.convert('RGB')
    if im.width>maxw: im=im.resize((maxw,int(im.height*maxw/im.width)))
    bio=io.BytesIO();im.save(bio,'JPEG',quality=72,optimize=True);return bio.getvalue()

def parse_pdf(path):
    pdf=pdfplumber.open(path);itens={};meta={}
    for pi,pg in enumerate(pdf.pages):
        t=pg.extract_text() or ''
        if not meta:
            m=re.search(r'REPORT\s+(\d+)',t);d=re.search(r'(\d{2}/\d{2}/\d{4})',t)
            if m: meta['report']=m.group(1)
            if d: meta['data']=d.group(1)
        m=re.search(r'N[ºo°]:\s*#\s*(\d+)',t)
        if not m: continue
        n=int(m.group(1));ws=pg.extract_words(keep_blank_chars=False)
        lab={k:find(ws,k) for k in ('ITEM:','CONDIÇÃO:','RECOMENDAÇÃO:','PRIO.','STATUS','ANTES')}
        notas=find(ws,'NOTAS');dep=find(ws,'DEPOIS')
        first=n not in itens
        it=itens.setdefault(n,{'n':n,'pg':pi+1,'paginas':[],'antes_ims':[],'depois_ims':[]})
        it['paginas'].append(pi+1)
        if first and lab['ITEM:'] and lab['CONDIÇÃO:'] and lab['RECOMENDAÇÃO:']:
            W=pg.width;prio_x=lab['PRIO.']['x0'] if lab['PRIO.'] else W*0.74
            nx=[w for w in ws if w['text']=='NOTA' and w['top']>lab['CONDIÇÃO:']['top']+5 and (not notas or w['top']<notas['top'])]
            nota_top=nx[0]['top'] if nx else lab['RECOMENDAÇÃO:']['top']-5
            nota_x=nx[0]['x0'] if nx else prio_x
            t1=notas['top']-2 if notas else lab['RECOMENDAÇÃO:']['top']+40
            it['titulo']=words_in(ws,lab['ITEM:']['x1']+1,W,lab['ITEM:']['top']-2,lab['ITEM:']['bottom']+3)
            it['condicao']=words_in(ws,lab['CONDIÇÃO:']['x1']+4,prio_x-2,lab['ITEM:']['bottom']+3,nota_top-1,skip=('CONDITION',))
            it['rec']=words_in(ws,lab['RECOMENDAÇÃO:']['x1']+2,nota_x-2,nota_top-1,t1,skip=('RECOMMENDATION',))
            blk=words_in(ws,nota_x-4,W,lab['CONDIÇÃO:']['top']-4,t1)
            p=re.search(r'\b([A-D])\b',words_in(ws,prio_x-4,prio_x+40,lab['CONDIÇÃO:']['top']-4,nota_top-1,skip=('PRIO.',)))
            it['prio']=p.group(1) if p else ''
            d=re.search(r'\b(\d{1,2}/\d{2})\b',blk);it['data']=d.group(1) if d else ''
            st=re.search(r'(\d{1,3})\s*%',blk);it['stt']=int(st.group(1)) if st else 0
            r=re.search(r'\b(\d{8})\b',blk);it['ref']=r.group(1) if r else ''
            a_top=lab['ANTES']['top'] if lab['ANTES'] else pg.height
            it['notas']=words_in(ws,0,W,(notas['bottom'] if notas else t1)+2,a_top-4) if notas else ''
            it['notas']='' if it['notas'] in ('-','') else it['notas']
            # medições: linhas de texto (abaixo de ANTES) que citam tubo e mm
            lines={}
            for w in ws:
                if w['top']>a_top: lines.setdefault(round(w['top']/3),[]).append(w)
            it['medicoes']=[]
            for k in sorted(lines):
                ln=' '.join(x['text'] for x in sorted(lines[k],key=lambda w:w['x0']))
                if re.search(r'tubo',ln,re.I) and re.search(r'\d\s*mm',ln): it['medicoes'].append(ln)
        # fotos: imagens abaixo de ANTES (até DEPOIS) e abaixo de DEPOIS; ignora logotipos do cabeçalho
        a_lab=lab['ANTES'];top_ok=lambda im:im['top']>110
        if dep:
            it['depois_ims'].append((pi,[im for im in pg.images if top_ok(im) and im['top']>dep['bottom']-2]))
        if a_lab or not first:
            lim=dep['top'] if dep else pg.height+1
            start=a_lab['bottom'] if a_lab else 110
            ims=sorted([im for im in pg.images if top_ok(im) and im['top']>=start-2 and im['bottom']<=lim+2],key=lambda i:i['top'])
            # só o primeiro bloco contínuo de fotos (para antes de textos, tabelas e croquis)
            blk=[];bot=None
            for im in ims:
                if bot is not None and im['top']>bot+14: break
                txt=[w for w in ws if bot is not None and w['top']>bot+2 and w['top']<im['top']-2]
                if txt: break
                blk.append(im);bot=max(bot or 0,im['bottom'])
            if blk and not it['antes_ims']: it['antes_ims'].append((pi,blk))
    for n,it in itens.items():
        it['foto']=crop_jpg(pdf.pages[it['antes_ims'][0][0]],it['antes_ims'][0][1]) if it['antes_ims'] else None
        dp=[x for x in it['depois_ims'] if x[1]]
        it['depois']=crop_jpg(pdf.pages[dp[0][0]],dp[0][1]) if dp else None
        del it['antes_ims'],it['depois_ims']
    return meta,[itens[k] for k in sorted(itens)]

# ---------------- localização ----------------
ELEV=re.compile(r'(?:elev(?:acao|\.)?|el\.)\s*(\d{1,2})[.,]?(\d{3})(?:\s*mm|m)?')
def el_of(t):
    m=ELEV.search(t)
    if m: return int(m.group(1)+m.group(2))
    m=re.search(r'\b(\d{2})[.](\d{3})\b',t)
    return int(m.group(1)+m.group(2)) if m and 15000<=int(m.group(1)+m.group(2))<=60000 else None
def tubos_of(t):
    out=[]
    for m in re.finditer(r'tubos?\s*(?:n[ºo°]?\s*)?((?:\d{1,3}\s*(?:,|e|a|-|/)\s*)*\d{1,3})',t):
        for x in re.findall(r'\d{1,3}',m.group(1)): 
            v=int(x)
            if 1<=v<=126 and v not in out: out.append(v)
    return out
def explicit(it,kb):
    t=norm(it['titulo']+' . '+it.get('condicao','')+' . '+it.get('rec',''));tt=norm(it['titulo'])
    el=el_of(tt) or el_of(t)
    tb=[]
    for ln in it.get('medicoes',[]):
        m=re.search(r'tubo\s*(?:n[ºo°]?\s*)?(\d{1,3})',norm(ln))
        if m and 1<=int(m.group(1))<=126 and int(m.group(1)) not in tb: tb.append(int(m.group(1)))
    if not tb: tb=tubos_of(t)
    m=re.search(r'divisoria\s*0?(\d)\b',tt)
    if m and 'envoltoria' not in tt:
        k=int(m.group(1));face='N' if re.search(r'lado\s*a|norte',tt) else ('S' if re.search(r'lado\s*b|sul',tt) else None)
        z='Divisória %d'%k+(' · lado '+('Norte' if face=='N' else 'Sul') if face else '')+(' · El. '+fmt_el(el) if el else '')+(' · tubo'+('s ' if len(tb)>1 else ' ')+', '.join(map(str,tb)) if tb else '')
        conf='alta' if (tb and el) else 'média'
        cf=norm(it.get('condicao',''));fc='N' if re.search(r'lado\s*a|norte',cf) else ('S' if re.search(r'lado\s*b|sul',cf) else None)
        if face and fc and fc!=face: conf='baixa'
        return dict(loc={'t':'div','k':k,'face':face,'el':el,'tubos':tb},zona=z,conf=conf,conjunto='Fornalha',nota=None if conf=='alta' else 'Posição na divisória sem tubo informado: marcador no centro')
    walls=[(r'parede\s*lateral\s*direita|\bpld\b','dir','Parede lateral direita (Sul)'),(r'parede\s*lateral\s*esquerda|\bple\b','esq','Parede lateral esquerda (Norte)'),
           (r'parede\s*frontal|\bpf\b','frente','Parede frontal (Oeste)'),(r'parede\s*traseira|\bpt\b','traseira','Parede traseira (Leste)')]
    if tt.startswith('fornalha') or 'fornalha' in tt:
        for rx,w,nm in walls:
            if re.search(rx,tt):
                z=nm+(' · El. '+fmt_el(el) if el else '')+(' · tubo'+('s ' if len(tb)>1 else ' ')+', '.join(map(str,tb)) if tb else '')
                conf='alta' if (tb and el) else ('média' if el else 'baixa')
                return dict(loc={'t':'wall','w':w,'el':el,'tubos':tb},zona=z,conf=conf,conjunto='Fornalha',nota=None if conf=='alta' else 'Posição aproximada na parede: confirmar tubo/elevação')
    return None
def fmt_el(e): return '{:,}'.format(e).replace(',','.')
def by_rules(it,kb):
    t=norm(it['titulo'])
    full=norm(it['titulo']+' '+it.get('rec','')+' '+it.get('condicao',''))
    for r in kb['regras']:
        if re.search(r['padrao'],t) or (r.get('texto') and re.search(r['padrao'],full)):
            d={k:r.get(k) for k in ('loc','zona','conf','conjunto','nota','fora')}
            if d['loc'] and d['loc'].get('t')=='grp' and d['loc'].get('el') is None:
                e=el_of(t)
                if e: d['loc']=dict(d['loc'],el=e);d['zona']=(d['zona'] or '')+' · El. '+fmt_el(e);d['conf']='média' if d['conf']=='baixa' else d['conf']
            d['regra']=r['id'];return d
    return None
def locate(it,kb):
    mem=kb['memoria'].get(sig(it))
    if mem and mem.get('confirmado'): d=dict(mem);d['conf']='alta';d['origem']='memória confirmada';return d
    e=explicit(it,kb)
    if e: e['origem']='texto do report';return e
    if mem: d=dict(mem);d['origem']='memória ('+mem.get('origem','')+')';return d
    r=by_rules(it,kb)
    if r: r['origem']='regra '+r.pop('regra');return r
    return dict(loc=None,zona=None,conf=None,conjunto=None,nota=None,fora='Local não identificado: revisar',origem='sem regra')

def main():
    args=[a for a in sys.argv[1:] if not a.startswith('--')];dry='--dry-run' in sys.argv
    kb=json.load(open(KB_PATH,encoding='utf8'))
    meta,itens=parse_pdf(args[0])
    out=[];rel=[]
    for it in itens:
        d=locate(it,kb)
        dep=it['depois']
        x={'n':it['n'],'titulo':it.get('titulo',''),'rec':it.get('rec',''),'condicao':it.get('condicao',''),'ref':it.get('ref',''),'prio':it.get('prio',''),
           'stt':it.get('stt',0),'data':it.get('data',''),'pg':it['pg'],'medicoes':it.get('medicoes',[]),'conjunto':d.get('conjunto'),'loc':d.get('loc'),
           'conf':d.get('conf'),'zona':d.get('zona'),'nota':d.get('nota'),'fora':d.get('fora'),'foto':it['foto']}
        rep=meta.get('report','x');os.makedirs(IMG_DIR,exist_ok=True)
        if it['foto']:
            open(os.path.join(IMG_DIR,'r%s_%d_a.jpg'%(rep,it['n'])),'wb').write(it['foto']);x['foto']='/api/repimg?f=r%s_%d_a.jpg'%(rep,it['n'])
        fdep=os.path.join(DEP_DIR,'r%s_dep_%d.jpg'%(rep,it['n']))
        if os.path.exists(fdep): dep=open(fdep,'rb').read()
        if dep:
            open(os.path.join(IMG_DIR,'r%s_%d_d.jpg'%(rep,it['n'])),'wb').write(dep);x['depois']='/api/repimg?f=r%s_%d_d.jpg'%(rep,it['n'])
        out.append(x);rel.append((it['n'],d['origem'],x['conf'],x['zona'] or x['fora'],x['titulo'][:60]))
    data={'meta':{'report':meta.get('report',''),'data':meta.get('data','')},'itens':out}
    os.makedirs(os.path.join(HERE,'out'),exist_ok=True)
    jp=os.path.join(HERE,'out','rep_%s.json'%data['meta']['report'])
    json.dump(data,open(jp,'w',encoding='utf8'),ensure_ascii=False)
    from collections import Counter
    c=Counter(r[2] or 'fora' for r in rel);o=Counter(r[1].split(' (')[0] for r in rel)
    print('Report',data['meta'],'itens',len(out),'| confiança',dict(c),'| origem',dict(o))
    print('com foto depois:',[x['n'] for x in out if x.get('depois')])
    with open(os.path.join(HERE,'out','localizacao_%s.tsv'%data['meta']['report']),'w',encoding='utf8') as f:
        f.write('n\torigem\tconf\tzona/fora\ttitulo\n');[f.write('\t'.join(str(v) for v in r)+'\n') for r in rel]
    if not dry:
        s=open(REC,encoding='utf8').read();a=s.index('/*REPDATA*/')+len('/*REPDATA*/');b=s.index('/*ENDREPDATA*/')
        s=s[:a]+json.dumps(data,ensure_ascii=False,separators=(',',':'))+s[b:]
        open(REC,'w',encoding='utf8').write(s);print('rec.html atualizado')
if __name__=='__main__': main()
