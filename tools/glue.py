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
    o=o.replace('</head>','<style id="geral-ui">#tipos{display:none!important}section.bottom{display:none!important}\n@media (min-width:821px) and (min-height:501px){html,body{height:100%;overflow:hidden}.page{padding-bottom:0}#wrap{height:calc(100vh - 92px)!important;min-height:0!important}.side{position:sticky;top:0;max-height:calc(100vh - 92px);overflow:auto;scrollbar-width:none}.side::-webkit-scrollbar{display:none}}</style>\n</head>',1)
# vista inicial: perspectiva da caldeira completa
m=re.search(r'updCam\(\);layoutPins\(\);\s*\(function loop',o)
if m and '__frame("persp",true)' not in o:
    o=o[:m.start()]+'updCam();layoutPins();if(window.__frame)window.__frame("persp",true);setTimeout(function(){if(window.__syncAll)window.__syncAll()},300);\n(function loop'+o[m.end():]
open(R+OUT,'w',encoding='utf8').write(o)
print('ok',len(o),'loopinit' ,bool(m))
