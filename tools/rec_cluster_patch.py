#!/usr/bin/env python3
"""Injeta (ou atualiza) o modulo de pontos + agrupamento numerado (tools/rec_cluster.js) em private/rec.html.
Idempotente. Chamado ao final de rec_build.py; pode ser rodado sozinho."""
import os,re
HERE=os.path.dirname(os.path.abspath(__file__));P=os.path.join(os.path.dirname(HERE),'private','rec.html')
js=open(os.path.join(HERE,'rec_cluster.js'),encoding='utf8').read()
s=open(P,encoding='utf8').read()
s=re.sub(r'/\*REPCL\*/.*?/\*ENDREPCL\*/\n?','',s,flags=re.S)
anc='var _pl=placeLabels;placeLabels=function(){_pl();repArrowPlace()};'
assert s.count(anc)==1,'ancora nao encontrada'
s=s.replace(anc,anc+'\n'+js,1)
open(P,'w',encoding='utf8').write(s);print('cluster injetado')
