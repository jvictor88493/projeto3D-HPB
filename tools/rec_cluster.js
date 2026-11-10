/*REPCL*/
/* Marcação das recomendações: pontos pequenos + agrupamento numerado por proximidade na tela (substitui os cones) */
var repGrp=null,repClEls=[],REPCL_R=30;
(function(){
  var st=document.createElement("style");
  st.textContent="#repCl{position:absolute;left:0;top:0;width:100%;height:100%;z-index:5;pointer-events:none;overflow:hidden}"
  +"#repCl .d,#repCl .g{position:absolute;pointer-events:auto;cursor:pointer;transform:translate(-50%,-50%);border:2px solid #fff;box-shadow:0 1px 5px rgba(0,0,0,.45);box-sizing:border-box;border-radius:50%}"
  +"#repCl .d{width:14px;height:14px}#repCl .d.sel{width:20px;height:20px;border-color:#111;box-shadow:0 0 0 3px #ffc400,0 1px 6px rgba(0,0,0,.5)}"
  +"#repCl .g{min-width:28px;height:28px;padding:0 5px;display:flex;align-items:center;justify-content:center;color:#fff;font:700 13px/1 system-ui;border-radius:14px}"
  +"#repCl .d:hover,#repCl .g:hover{transform:translate(-50%,-50%) scale(1.15)}"
  +"#repGrpBar{display:none;align-items:center;gap:8px;background:#fff7d6;border:1px solid #e0c200;border-radius:8px;padding:6px 8px;margin:6px 0;font:600 12px system-ui;color:#222}"
  +"#repGrpBar button{margin-left:auto}";
  document.head.appendChild(st);
})();
var repClLayer=document.createElement("div");repClLayer.id="repCl";wrap.appendChild(repClLayer);
function repGrpBarEl(){var bar=document.getElementById("repGrpBar");if(bar)return bar;
  var lv=document.getElementById("repLV"),c=document.getElementById("repCount");if(!lv||!c)return null;
  bar=document.createElement("div");bar.id="repGrpBar";bar.innerHTML="<span id='repGrpTxt'></span><button type='button' class='chip' id='repGrpX'>Mostrar todos</button>";
  lv.insertBefore(bar,c.nextSibling);document.getElementById("repGrpX").onclick=function(){repSetGrp(null)};return bar}
var _rmOrig=repMatch;repMatch=function(it){if(repGrp&&!repGrp[it.n])return false;return _rmOrig(it)};
function repSetGrp(set){
  repGrp=set;var bar=repGrpBarEl();
  if(bar){if(set){var k=Object.keys(set).length;document.getElementById("repGrpTxt").textContent="Região selecionada no 3D · "+k+" recomendações";bar.style.display="flex"}else bar.style.display="none"}
  if(repView!=="list"){repView="list";document.getElementById("repDV").hidden=true;document.getElementById("repLV").hidden=false;repSel=null}
  repRows();dirty=true;
}
function repClColor(its){
  var best=null,pr={A:0,B:1,C:2,D:3};
  its.forEach(function(it){if(it.stt>=100)return;var k=pr[it.prio||"D"];if(best===null||k<best)best=k});
  if(best===null)return REPC.OK;return REPC[["A","B","C","D"][best]];
}
function repHex(c){return "#"+("000000"+c.toString(16)).slice(-6)}
function repClDraw(){
  var L=repClLayer;while(L.firstChild)L.removeChild(L.firstChild);
  if(!document.getElementById("vREP").checked)return;
  var w=wrap.clientWidth,h=wrap.clientHeight,pts=[],v=new THREE.Vector3();
  repMeshes.forEach(function(m){m.visible=false});
  REP.itens.forEach(function(it){
    if(!it._mesh)return;var sel=repSel===it.n;if(!sel&&!repFilt(it))return;
    v.copy(it._mesh.userData.base).project(cam);if(v.z>1||v.z<-1)return;
    var x=(v.x*0.5+0.5)*w,y=(-v.y*0.5+0.5)*h;if(x<-20||y<-20||x>w+20||y>h+20)return;
    pts.push({it:it,x:x,y:y,sel:sel});
  });
  var groups=[],R=REPCL_R;
  pts.sort(function(a,b){return a.y-b.y});
  pts.forEach(function(p){
    if(p.sel){groups.push({m:[p],x:p.x,y:p.y,sel:true});return}
    var g=null,bd=1e9;groups.forEach(function(q){if(q.sel)return;var d=Math.hypot(q.x-p.x,q.y-p.y);if(d<R&&d<bd){bd=d;g=q}});
    if(g){g.m.push(p);var n=g.m.length;g.x+=(p.x-g.x)/n;g.y+=(p.y-g.y)/n}else groups.push({m:[p],x:p.x,y:p.y});
  });
  groups.forEach(function(g){
    var e=document.createElement("div"),its=g.m.map(function(p){return p.it});
    e.style.left=g.x+"px";e.style.top=g.y+"px";
    if(g.m.length===1){
      var it=its[0];e.className="d"+(g.sel?" sel":"");e.style.background=g.sel?"#ffc400":repHex(repColor(it));
      e.title="#"+it.n+" · "+it.titulo;
      e.onclick=function(ev){ev.stopPropagation();repShow(it.n,true)};
    }else{
      e.className="g";e.style.background=repHex(repClColor(its));e.textContent=g.m.length;
      var ab=its.filter(function(i){return i.stt<100}).length;e.title=g.m.length+" recomendações ("+ab+" abertas, "+(g.m.length-ab)+" concluídas) · clique para aproximar";
      e.onclick=function(ev){ev.stopPropagation();repClGo(its)};
    }
    L.appendChild(e);
  });
}
function repClGo(its){
  var c=new THREE.Vector3(),k=0;its.forEach(function(i){c.add(i._mesh.userData.base);k++});c.multiplyScalar(1/k);
  var rad=0;its.forEach(function(i){rad=Math.max(rad,i._mesh.userData.base.distanceTo(c))});
  var set={};its.forEach(function(i){set[i.n]=1});
  repSetGrp(set);
  flyTo(c,Math.max(5,Math.min(sph.r*0.8,rad*2.8+4)),sph.ph,sph.th);
}
var _rl2=repLayout;repLayout=function(){_rl2();repClDraw()};
var _pl2=placeLabels;placeLabels=function(){_pl2();repClDraw()};
var _rb=repBack;repBack=function(){_rb()};
window.addEventListener("keydown",function(e){if(e.key==="Escape"&&repView==="list"&&repGrp)repSetGrp(null)});
/*ENDREPCL*/
