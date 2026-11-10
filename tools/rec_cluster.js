/*REPCL*/
/* Marcação das recomendações: pontos pequenos + agrupamento numerado por proximidade na tela (substitui os cones) */
var repGrp=null,repClEls=[],REPCL_R=30;
(function(){
  var st=document.createElement("style");
  st.textContent="#repCl{position:absolute;left:0;top:0;width:100%;height:100%;z-index:5;pointer-events:none;overflow:hidden}"
  +"#repCl .d{position:absolute;pointer-events:auto;cursor:pointer;width:14px;height:14px;transform:translate(-50%,-50%);display:flex;align-items:center;justify-content:center}"
  +"#repCl .d i{display:block;width:6px;height:6px;border-radius:50%;box-shadow:0 0 0 1px rgba(255,255,255,.85)}"
  +"#repCl .d:hover i{width:10px;height:10px}#repCl .d.sel{width:22px;height:22px}#repCl .d.sel i{width:14px;height:14px;background:#ffc400!important;border:2px solid #111;box-shadow:0 0 0 3px #ffc400}"
  +"#repCl .pl{position:absolute;pointer-events:auto;cursor:pointer;transform:translate(-50%,-50%);display:flex;align-items:center;gap:5px;background:#0f1b2d;color:#fff;border-radius:14px;padding:3px 5px 3px 10px;font:600 12px/1 system-ui,sans-serif;white-space:nowrap;box-shadow:0 2px 8px rgba(0,0,0,.4)}"
  +"#repCl .pl:hover{background:#1d3557}#repCl .pl b{min-width:20px;height:18px;padding:0 5px;box-sizing:border-box;border-radius:9px;display:inline-flex;align-items:center;justify-content:center;font:700 11px/1 system-ui;color:#fff}"
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
function repSetGrp(set,nome){
  repGrp=set;var bar=repGrpBarEl();
  if(bar){if(set){var k=Object.keys(set).length;document.getElementById("repGrpTxt").textContent="Conjunto: "+(nome||"região")+" · "+k+" recomendações";bar.style.display="flex"}else bar.style.display="none"}
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
  var w=wrap.clientWidth,h=wrap.clientHeight,v=new THREE.Vector3(),cj={},pills=[];
  repMeshes.forEach(function(m){m.visible=false});
  REP.itens.forEach(function(it){
    if(!it._mesh)return;var sel=repSel===it.n;if(!sel&&!repFilt(it))return;
    v.copy(it._mesh.userData.base).project(cam);if(v.z>1||v.z<-1)return;
    var x=(v.x*0.5+0.5)*w,y=(-v.y*0.5+0.5)*h;if(x<-20||y<-20||x>w+20||y>h+20)return;
    var k=it.conjunto||"Outros",g=cj[k]||(cj[k]={k:k,m:[],x:0,y:0});g.m.push(it);g.x+=x;g.y+=y;
    var d=document.createElement("div");d.className="d"+(sel?" sel":"");d.style.left=x+"px";d.style.top=y+"px";
    d.innerHTML="<i style='background:"+repHex(repColor(it))+"'></i>";d.title="#"+it.n+" · "+it.titulo;
    d.onclick=function(ev){ev.stopPropagation();repShow(it.n,true)};L.appendChild(d);
  });
  Object.keys(cj).forEach(function(k){
    var g=cj[k],n=g.m.length,ab=g.m.filter(function(i){return i.stt<100}).length,fe=n-ab;
    var e=document.createElement("div");e.className="pl";
    e.innerHTML="<span>"+esc(k)+"</span>"+(ab?"<b style='background:#e5322d'>"+ab+"</b>":"")+(fe?"<b style='background:#2b8a3e'>"+fe+"</b>":"");
    e.title=n+" recomendações ("+ab+" abertas, "+fe+" concluídas) · clique para aproximar e listar";
    e.onclick=function(ev){ev.stopPropagation();repClGo(g.m,k)};
    L.appendChild(e);pills.push({e:e,x:g.x/n,y:g.y/n-18,w:e.offsetWidth||90,h:22});
  });
  pills.sort(function(a,b){return a.y-b.y});
  for(var i=0;i<pills.length;i++){var p=pills[i];p.x=Math.max(p.w/2+4,Math.min(w-p.w/2-4,p.x));p.y=Math.max(14,Math.min(h-14,p.y));
    for(var j=0;j<i;j++){var q=pills[j];if(Math.abs(p.x-q.x)<(p.w+q.w)/2+4&&Math.abs(p.y-q.y)<p.h+3){p.y=q.y+p.h+3;j=-1}}
    p.y=Math.min(h-14,p.y)}
  pills.forEach(function(p){p.e.style.left=p.x+"px";p.e.style.top=p.y+"px"});
}
function repClGo(its,nome){
  var c=new THREE.Vector3(),k=0;its.forEach(function(i){c.add(i._mesh.userData.base);k++});c.multiplyScalar(1/k);
  var rad=0;its.forEach(function(i){rad=Math.max(rad,i._mesh.userData.base.distanceTo(c))});
  var set={};its.forEach(function(i){set[i.n]=1});
  repSetGrp(set,nome);
  flyTo(c,Math.max(5,Math.min(sph.r*0.9,rad*2.6+4)),sph.ph,sph.th);
}
var _rl2=repLayout;repLayout=function(){_rl2();repClDraw()};
var _pl2=placeLabels;placeLabels=function(){_pl2();repClDraw()};
var _rb=repBack;repBack=function(){_rb()};
window.addEventListener("keydown",function(e){if(e.key==="Escape"&&repView==="list"&&repGrp)repSetGrp(null)});
/*ENDREPCL*/
