# Aplica o padrao do site a um HTML vNN ja no formato v29+ e grava private/full.html e private/full_info.html
import re,sys
import os
HERE=os.path.dirname(os.path.abspath(__file__))
SC=HERE+'/'
R=os.path.join(os.path.dirname(HERE),'private')+'/'
o=open(sys.argv[1],encoding='utf8').read()
OUT=sys.argv[2] if len(sys.argv)>2 else 'full.html'
NOINFO=len(sys.argv)>3 and sys.argv[3]=='noinfo'
if o.lstrip().startswith('<!--'): o=o[o.index('-->')+3:].lstrip()
o=re.sub(r'<title>(Mapa 3D [^<]*?) v\d+',r'<title>\1',o,count=1)
# notas -> aba Informacao
if '<!--ADMIN_START' in o:
    i=o.index('<!--ADMIN_START');e=o.index('<!--ADMIN_END-->')
    blk=o[o.index('-->',i)+3:e];o=o[:i]+o[e+len('<!--ADMIN_END-->'):]
    blk=re.sub(r'<summary>',r'<summary>3D HPB Completa · ',blk)
    if not NOINFO: open(R+'full_info.html','w',encoding='utf8').write('<h3 style="margin:18px 0 6px">3D HPB Completa</h3>'+blk)
# script de filtros/Todas/gaveta
if 'window.__syncAll=' not in o:
    d=open(SC+'drawer_glue.html',encoding='utf8').read()
    k=o.index('var M={');k=o.rindex('<script>',0,k)
    o=o[:k]+d+'\n'+o[k:]
# Perspectiva / Planta: caldeira completa ou conjunto selecionado
a='[].forEach.call(lst.querySelectorAll("button[data-c]"),function(b){b.addEventListener("click",function(){show(b.getAttribute("data-c"))})});'
if a in o and '__frame' not in o:
    o=o.replace('function show(k){var ids=CJ[k];setLayers(ids);','function show(k){CURK=k;var ids=CJ[k];setLayers(ids);',1)
    o=o.replace('(function(){var CJ=','(function(){var CURK=null,CJ=',1)
    o=o.replace(a,a+r'''
function bbox(ids){var box=new THREE.Box3(),tmp=new THREE.Box3(),M4=new THREE.Matrix4(),Z0=new THREE.Matrix4().makeScale(0,0,0),seen=[];
  function add(o){if(seen.indexOf(o)>=0)return;seen.push(o);o.updateMatrixWorld(true);o.traverse(function(n){if(!n.geometry)return;var g=n.geometry;if(!g.boundingBox)g.computeBoundingBox();if(!g.boundingBox||g.boundingBox.isEmpty())return;
    if(n.isInstancedMesh){var cnt=n.count,st=Math.max(1,Math.floor(cnt/400));for(var i=0;i<cnt;i+=st){n.getMatrixAt(i,M4);if(M4.equals(Z0))continue;tmp.copy(g.boundingBox).applyMatrix4(M4).applyMatrix4(n.matrixWorld);box.union(tmp)}}
    else{tmp.copy(g.boundingBox).applyMatrix4(n.matrixWorld);box.union(tmp)}})}
  ids.forEach(function(id){var f=GM[id];if(f)f().forEach(function(o){if(o)add(o)})});return box}
function allIds(){var r=[];Object.keys(CJ).forEach(function(k){CJ[k].forEach(function(i){if(r.indexOf(i)<0)r.push(i)})});return r}
window.__frame=function(mode,instant){var ids=CURK&&CJ[CURK]?CJ[CURK]:allIds(),box=bbox(ids);if(box.isEmpty())return;
  var c=box.getCenter(new THREE.Vector3()),sz=box.getSize(new THREE.Vector3()),a=Math.min(1,cam.aspect),r,ph,th;
  var vf=cam.fov*Math.PI/360,tv=Math.tan(vf),asp=cam.aspect;
  if(mode==="plan"){r=Math.max(sz.z/2/tv,sz.x/2/(tv*asp))*1.12+sz.y/2;ph=0.02;th=Math.PI}
  else{var rad=sz.length()/2;r=rad/Math.sin(Math.atan(tv*Math.min(1,asp)))*0.92;ph=1.0;th=Math.PI*0.86}
  r=Math.min(Math.max(r,2),185);
  if(instant){anim=null;tgt.copy(c);sph.r=r;sph.ph=ph;sph.th=th;updCam();layoutPins()}else flyTo(c,r,ph,th)};''',1)
    o=o.replace('["bPersp","bPlan","bFront","bWalls","bAll"].forEach(function(id){var b=$(id);if(b)b.addEventListener("click",function(){mark(null)})});',
                '["bFront","bWalls","bAll"].forEach(function(id){var b=$(id);if(b)b.addEventListener("click",function(){CURK=null;mark(null)})});',1)
    o=o.replace('$("bSite").addEventListener("click",function(){setLayers(true);mark("site");open(false)});','$("bSite").addEventListener("click",function(){CURK=null;setLayers(true);mark("site");open(false);window.__frame("persp")});',1)
    for v in ('persp','plan'):
        b='$("b%s").addEventListener("click",function(){setView("%s")});'%('Persp' if v=='persp' else 'Plan',v)
        assert o.count(b)==1,b
        o=o.replace(b,b[:-3]+';window.__frame&&window.__frame("%s")});'%v)
# botao Divisorias removido do projeto (fica oculto; id mantido para o script)
o=re.sub(r'<button id="bWalls"(?![^>]*display:none)',r'<button id="bWalls" style="display:none"',o)
# sem bloco "Tipo de cap" e sem "Detalhes da posicao" no visualizador geral
if 'id="geral-ui"' not in o:
    o=o.replace('</head>','<style id="geral-ui">#tipos{display:none!important}section.bottom{display:none!important}@media (max-width:820px),(max-height:500px) and (orientation:landscape){#bPlan,#bFront,#bAll,#bWalls{display:none!important}}#conjList{max-height:calc(100vh - 240px)!important;overflow-y:auto!important;scrollbar-width:thin;padding:4px!important}#conjList button{padding:6px 10px!important;font-size:13px!important}@media (max-width:820px),(max-height:500px){#conjList{max-height:calc(64dvh - 80px)!important}}.csep{margin:2px!important}\n@media (min-width:821px) and (min-height:501px){html,body{height:100%;overflow:hidden}.page{padding-bottom:0}#wrap{height:calc(100vh - 92px)!important;min-height:0!important}.side{position:sticky;top:0;max-height:calc(100vh - 92px);overflow:auto;scrollbar-width:none}.side::-webkit-scrollbar{display:none}}</style>\n</head>',1)
# vista inicial: perspectiva da caldeira completa
m=re.search(r'updCam\(\);layoutPins\(\);\s*\(function loop',o)
if m and '__frame("persp",true)' not in o:
    o=o[:m.start()]+'updCam();layoutPins();if(window.__frame)window.__frame("persp",true);setTimeout(function(){if(window.__syncAll)window.__syncAll()},300);\n(function loop'+o[m.end():]

# conjuntos na lateral direita (arvore com as camadas indentadas)
_a='[].forEach.call(lst.querySelectorAll("button[data-c]"),function(b){b.addEventListener("click",function(){show(b.getAttribute("data-c"))})});'
if _a in o and 'window.__CJ=' not in o:
    o=o.replace(_a,_a+'window.__CJ=CJ;window.__showCJ=function(k){show(k)};',1)
if 'id="cj-tree-ui"' not in o:
    _t=open(os.path.join(HERE,'cj_tree.html'),encoding='utf8').read()
    _k=o.rindex('</body>');o=o[:_k]+_t+'\n'+o[_k:]

# celular, so na 3D HPB Completa: painel de conjuntos abaixo do 3D (no lugar da gaveta Filtros)
if 'id="full-mob"' not in o and OUT=='full.html':
    _m="""<style id="full-mob-css">#layMob{display:none}@media (max-width:820px){#layMob{display:block;padding:10px 10px 90px}#layMob #layers{margin:0}body.laymob #bFilt{display:none!important}}</style>
<script id="full-mob">(function(){if(document.getElementById('rep'))return;var L=document.getElementById('layers'),side=document.querySelector('.side'),st=document.querySelector('.stage');if(!L||!side||!st)return;
var box=document.createElement('div');box.id='layMob';st.parentNode.insertBefore(box,st.nextSibling);var home=L.nextSibling,mq=matchMedia('(max-width:820px)');
function place(){if(mq.matches){if(L.parentNode!==box)box.appendChild(L);document.body.classList.add('laymob');document.body.classList.remove('fopen')}else{document.body.classList.remove('laymob');if(L.parentNode!==side)side.insertBefore(L,home&&home.parentNode===side?home:null)}}
box.addEventListener('click',function(e){if(mq.matches&&(e.target.closest('.cjv')||(e.target.closest('.cjg')&&!e.target.closest('.car')&&e.target.closest('.cjgrp').dataset.k!=='_out')))setTimeout(function(){window.scrollTo(0,0)},60)},true);place();(mq.addEventListener?mq.addEventListener('change',place):mq.addListener(place))})();</script>"""
    _k=o.rindex('</body>');o=o[:_k]+_m+'\n'+o[_k:]

# estilos da arvore de conjuntos no <head> (evita aparecer o painel antigo antes do script montar a arvore)
_m=re.search(r'<style id="cj-tree-ui">.*?</style>',o,re.S)
if _m and o.find('</head>')<_m.start():
    _st=_m.group(0);o=o[:_m.start()]+o[_m.end():]
    if '#layers:not(.cjready)' not in _st: _st=_st.replace('</style>','#layers:not(.cjready){visibility:hidden}</style>')
    o=o.replace('</head>',_st+'\n</head>',1)
if "card.classList.add('cjready')" not in o:
    o=o.replace("card.appendChild(tree);","card.appendChild(tree);card.classList.add('cjready');",1)
# Three.js r128 pelo CDN (mesmo arquivo da pagina principal, ja em cache no navegador) em vez de 600 KB embutidos
o=re.sub(r'<script>\s*/\*\*\s*\n \* @license\s*\n \* Copyright 2010-2021 Three\.js Authors.*?</script>',lambda m:'<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>',o,count=1,flags=re.S)
open(R+OUT,'w',encoding='utf8').write(o)
# pagina publica /fluxos: so o 3D + fluxos da caldeira (esboco v2), ja ligados; o full.html do site fica sem o modulo
if OUT=='full.html':
    f=o
    if 'window.__fx=' not in f:
        _a='window.__bc={v45'
        assert _a in f, 'gancho window.__bc nao encontrado'
        f=f.replace(_a,'window.__fx={scene:scene,cam:cam,renderer:renderer,ezz:ezz,THREE:THREE,mark:function(){dirty=true},G:{gSS:gSS,gSP:gSP,gECO:gECO}};'+_a,1)
    _lp='if(dirty){renderer.render(scene,cam);placeLabels();dirty=false}'
    assert _lp in f, 'laco de desenho nao encontrado'
    f=f.replace(_lp,'if(window.__fxTick)window.__fxTick(now||performance.now());'+_lp,1)
    _k=f.rfind('</body>')
    f=f[:_k]+'<script>window.__fxAuto=1</script>\n'+open(os.path.join(HERE,'fluxos3d.html'),encoding='utf8').read()+'\n'+f[_k:]
    f=re.sub(r'<title>[^<]*</title>','<title>Caldeira HPB – fluxos em 3D</title>',f,count=1)
    # so o 3D: sem o painel de Conjuntos / Tipo de cap (computador e celular) e com o 3D na largura toda
    _css='<style id="fluxos-page">.side,#layers,#tipos,#bFilt,#fclose{display:none!important}.grid{grid-template-columns:minmax(0,1fr)!important}#wrap{height:clamp(480px,78vh,900px)!important}@media (max-width:820px),(max-height:500px) and (orientation:landscape){#wrap{height:calc(100dvh - 70px)!important}}</style>\n'
    _k=f.rfind('</body>')
    f=f[:_k]+_css+f[_k:]
    open(os.path.join(os.path.dirname(HERE),'public','fluxos.html'),'w',encoding='utf8').write(f)
    print('fluxos.html',len(f))
print('ok',len(o),'loopinit' ,bool(m))
