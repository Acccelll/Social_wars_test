import {UNIT_CATALOG,createScene,setSceneRunning,setSceneAutoFire,stepScene,fireSceneWeapon,healthBarView,seededRng} from '/dist/index.js';
import {initOriginalVisuals,visualInfo,setVisualMode,nextVisualTick,drawOriginalUnit,drawOriginalShot,drawOriginalImpact} from '/demo/originalVisuals.js';
const canvas=document.querySelector('#battle'), ctx=canvas.getContext('2d');
const $=id=>document.getElementById(id), units=['bushwacker','reaperDrone'];
const fmt=n=>new Intl.NumberFormat('pt-BR').format(n);
const clamp=(x,a,b)=>Math.min(b,Math.max(a,x));
let state,rng,accumulator=0,lastTime=0;
const pos=u=>({x:116+53*u.x,y:95+44*u.y});
function path(points,color,stroke='#102b37'){
 ctx.beginPath();ctx.moveTo(points[0][0],points[0][1]);
 for(const p of points.slice(1))ctx.lineTo(p[0],p[1]);
 ctx.closePath();ctx.fillStyle=color;ctx.fill();ctx.strokeStyle=stroke;ctx.lineWidth=2;ctx.stroke();
}
function rect(x,y,w,h,color){ctx.fillStyle=color;ctx.fillRect(x,y,w,h);}
function round(x,y,w,h,r,color,outline){
 ctx.beginPath();ctx.roundRect(x,y,w,h,r);ctx.fillStyle=color;ctx.fill();
 if(outline){ctx.strokeStyle=outline;ctx.lineWidth=2;ctx.stroke();}
}
function line(x1,y1,x2,y2,color,width=1){ctx.beginPath();ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);ctx.strokeStyle=color;ctx.lineWidth=width;ctx.stroke();}
function ellipse(x,y,rx,ry,color){
 ctx.beginPath();ctx.ellipse(x,y,rx,ry,0,0,2*Math.PI);ctx.fillStyle=color;ctx.fill();
}
function text(t,x,y,size=11,color='#e1f4ef',align='center'){
 ctx.fillStyle=color;ctx.textAlign=align;ctx.font='600 '+size+'px system-ui,Segoe UI,sans-serif';ctx.fillText(t,x,y);
}
function ground(){
 let g=ctx.createLinearGradient(0,0,0,540);g.addColorStop(0,'#142838');g.addColorStop(.48,'#254352');g.addColorStop(1,'#13272e');
 rect(0,0,960,540,g);
 ellipse(770,120,260,110,'#2c526078');ellipse(145,114,330,100,'#37576946');
 path([[0,226],[115,212],[210,228],[352,203],[502,217],[653,202],[820,224],[960,206],[960,540],[0,540]],'#18343e','#18343e');
 path([[0,319],[281,299],[490,318],[960,296],[960,540],[0,540]],'#273f42','#273f42');
 for(let i=-550;i<1400;i+=74){
  line(i,335,i+352,540,'#8da6a423');
  line(i+352,335,i,540,'#8da6a426');
 }
 for(const [x,y,s] of [[76,267,.75],[194,248,.64],[875,278,.74]]){
  ellipse(x,y+22,26*s,8*s,'#071920a0');
  round(x-14*s,y-30*s,28*s,48*s,3,'#3b626b','#93ada7');
  round(x-8*s,y-48*s,16*s,18*s,2,'#557887');
  line(x,y-48*s,x,y-62*s,'#9fccc4',2);
 }
 for(let i=0;i<55;i++)ellipse((i*131+15)%960,355+(i*73)%170,3+(i%3),2,'#81908630');
 for(const key of units){
  const u=state.units[key],p=pos(u);
  ctx.strokeStyle=key==='bushwacker'?'#95cfab44':'#79bfe944';ctx.lineWidth=2;
  ctx.beginPath();ctx.ellipse(p.x,p.y+36,68,22,0,0,2*Math.PI);ctx.stroke();
 }
 round(14,497,235,29,5,'#091c27b8','#45616b');
 text('SIMULAÇÃO INDEPENDENTE / 30 FPS',25,516,10,'#b0d0ce','left');
}
function bar(u,p){
 const v=healthBarView(u.hp);if(!v.visible)return;
 const x=p.x-43,y=p.y-91,w=86;
 round(x-3,y-3,w+6,13,3,'#07141b','#a2bcc0');
 rect(x,y,w,7,'#8f9797');rect(x,y,w*v.ratio,7,v.color);
 for(let i=1;i<v.divisions;i++)line(x+i*w/v.divisions,y,x+i*w/v.divisions,y+7,'#17222a',1);
}
function bush(u){
 const p=pos(u);
 if(drawOriginalUnit(ctx,'bushwacker',u,p)){
  text('BUSHWACKER · 1358',p.x,p.y-137,11,'#cbf1dd');bar(u,p);return;
 }ctx.save();ctx.translate(p.x,p.y);
 ellipse(0,40,61,14,'#081018a0');
 if(u.hp.dead){ctx.globalAlpha=.25;ctx.translate(0,25);ctx.rotate(.23);}
 for(const x of [-22,20]){
  path([[x-10,9],[x+10,11],[x+9,37],[x-5,43]],'#427568');
  round(x-15,33,38,12,3,'#315449','#a1caa4');
 }
 round(-36,-41,75,58,7,'#24504e','#b1d5be');
 path([[-36,-32],[-18,-50],[24,-50],[42,-29],[30,6],[-28,6]],'#568b7d','#214650');
 round(-30,-29,60,23,4,'#305a60','#b3d9ac');
 for(let i=0;i<4;i++)round(-24+i*14,-23,8,10,1,'#9cd4ad');
 round(-22,-69,44,24,4,'#86bfae','#235461');
 round(-16,-61,31,11,2,u.poseFrames>0?'#ffe79c':'#9be5e4','#173442');
 path([[16,-38],[37,-45],[57,-39],[57,-28],[18,-27]],'#68988e');
 round(50,-42,33,13,2,'#aec8b0','#213b47');
 if(u.poseFrames>0){ellipse(83,-36,10,7,'#ffd994');path([[83,-37],[105,-48],[95,-32],[107,-23]],'#ffc85a','#ffc85a');}
 ctx.restore();text('BUSHWACKER · 1358',p.x,p.y-107,11,'#cbf1dd');bar(u,p);
}
function drone(u){
 const p=pos(u);
 if(drawOriginalUnit(ctx,'reaperDrone',u,p)){
  text('REAPER DRONE · 1376',p.x,p.y-143,11,'#c3e8ff');bar(u,p);return;
 }ctx.save();ctx.translate(p.x,p.y-16);
 ellipse(0,55,61,15,'#050f1caa');
 ctx.translate(0,u.hp.dead?28:Math.sin(state.frame/10)*4);
 if(u.hp.dead)ctx.globalAlpha=.2;
 path([[-57,-5],[-32,-22],[-21,-10],[-40,8]],'#48859a');
 path([[21,-10],[32,-22],[57,-5],[40,8]],'#48859a');
 for(const x of [-55,55]){
  ellipse(x,-7,18,5,'#b6e7e49a');ellipse(x,-3,14,3,'#38698c');
  line(x-12,-12,x+12,-12,'#b2ebff',2);
 }
 path([[-40,-8],[-18,-29],[23,-29],[42,-6],[29,20],[-27,20]],'#4b89a5');
 path([[-25,-14],[0,-27],[25,-14],[18,8],[-18,8]],'#1b4159','#a1dcec');
 ellipse(0,-8,14,11,u.poseFrames>0?'#f5f6fb':'#60badb');
 ellipse(0,-8,7,5,'#112b41');
 for(const x of [-29,29])round(x-7,3,14,15,2,'#4e9eb5','#1b3a52');
 ctx.restore();text('REAPER DRONE · 1376',p.x,p.y-107,11,'#c3e8ff');bar(u,p);
}
function shots(){
 for(const s of state.projectiles){
  const a=pos({x:s.x0,y:s.y0}),b=pos({x:s.x1,y:s.y1});
  const t=1-s.remaining/s.duration,x=a.x+(b.x-a.x)*t,y=a.y-27+(b.y-a.y)*t;
  if(drawOriginalShot(ctx,s,t,a,b))continue;
  ctx.save();ctx.shadowBlur=18;
  if(s.effect==='bullet'){
   ctx.shadowColor='#ffdf8c';ellipse(x,y,8,4,'#fff0aa');
   line(x-24*Math.sign(b.x-a.x),y+3,x,y,'#f8a638',3);
  } else {
   ctx.shadowColor='#89f2ff';line(a.x,a.y-27,x,y,'#5fd2fdaa',8);
   line(a.x,a.y-27,x,y,'#e6ffff',2);ellipse(x,y,6,6,'#b8efff');
  }
  ctx.restore();
 }
}
function impacts(){
 for(const v of state.impacts){
  const p=pos(v),max=v.kind==='number'?28:v.kind==='death'?34:15;
  const t=1-v.remaining/max;
  if(drawOriginalImpact(ctx,v,p))continue;
  ctx.save();ctx.globalAlpha=clamp(1-t,0,1);
  if(v.kind==='number')text(String(v.amount),p.x+(v.id%3-1)*10,p.y-72-t*28,v.critical?25:19,v.critical?'#ffe290':'#ffac87');
  else if(v.kind==='hit'){
   ctx.beginPath();ctx.arc(p.x,p.y-30,7+t*35,0,Math.PI*2);ctx.strokeStyle=v.critical?'#fff4a9':'#92dcf9';ctx.lineWidth=3;ctx.stroke();
  }else{ellipse(p.x,p.y-26,25+t*40,17+t*23,'#dba66b99');text('DESTROYED',p.x,p.y-79,18,'#ffe0a2');}
  ctx.restore();
 }
}
function draw(){
 nextVisualTick();ground();bush(state.units.bushwacker);drone(state.units.reaperDrone);shots();impacts();
 if(state.winner){
  round(324,35,312,65,9,'#0c222ce8','#88c5b8');
  text('VITÓRIA · '+UNIT_CATALOG[state.winner].name.toUpperCase(),480,75,18,'#cefce5');
 }
}
function hud(){
 for(const [prefix,key] of [['b','bushwacker'],['r','reaperDrone']]){
  const u=state.units[key],v=healthBarView(u.hp),c=UNIT_CATALOG[key];
  $(prefix+'-health').textContent=fmt(u.hp.health)+' / '+fmt(u.hp.maxLife);
  $(prefix+'-fill').style.width=(v.ratio*100)+'%';$(prefix+'-fill').style.background=v.color;
  $(prefix+'-attack').textContent=c.attack;$(prefix+'-defense').textContent=c.defense;
  $(prefix+'-range').textContent=c.attackRange+' tiles';$(prefix+'-interval').textContent=c.attackInterval+' (config.)';
 }
 $('frame').textContent=fmt(state.frame);$('projectiles').textContent=state.projectiles.length;
 $('status').textContent=state.winner?'Vitória':state.running?'Em combate':'Pausado';
 $('run').textContent=state.running?'Ⅱ Pausar':'▶ Iniciar combate';
 $('auto').textContent='IA: '+(state.autoFire?'ligada':'desligada');
 $('events').textContent=[...state.log].reverse().join('\n');
 $('b-fire').disabled=state.units.bushwacker.hp.dead||state.units.reaperDrone.hp.dead;
 $('r-fire').disabled=state.units.bushwacker.hp.dead||state.units.reaperDrone.hp.dead;
 $('step').disabled=Boolean(state.winner);
 const vi=visualInfo();
 $('visual-mode').textContent=vi.mode==='original'?'Estilo: original':'Estilo: vetorial';
 $('visual-status').textContent=vi.ready?'Sprites FFDec carregados (amostras limitadas)':vi.status==='loading'?'Carregando visuais…':'Pacote original não encontrado; desenhos vetoriais ativos';
}
function repaint(){draw();hud();}
function fire(which){state=fireSceneWeapon(state,which);repaint();}
function reset(){state=createScene();rng=seededRng(1358);accumulator=0;repaint();}
$('reset').onclick=reset;
$('visual-mode').onclick=()=>{const vi=visualInfo();setVisualMode(vi.mode==='original'?'vector':'original');repaint();};
$('run').onclick=()=>{state=setSceneRunning(state,!state.running);repaint();};
$('auto').onclick=()=>{state=setSceneAutoFire(state,!state.autoFire);repaint();};
$('step').onclick=()=>{state=stepScene(state,rng,1);repaint();};
$('b-fire').onclick=()=>fire('bushwacker');
$('r-fire').onclick=()=>fire('reaperDrone');
canvas.addEventListener('click',ev=>{
 const b=canvas.getBoundingClientRect();
 const x=(ev.clientX-b.left)*canvas.width/b.width;
 fire(x<480?'bushwacker':'reaperDrone');
});
function tick(now){
 if(!lastTime)lastTime=now;
 const dt=Math.min(120,now-lastTime);lastTime=now;
 if(state.running){
  accumulator+=dt;let count=0;
  while(accumulator>=1000/30&&count<5&&!state.winner){
   state=stepScene(state,rng,1);accumulator-=1000/30;count++;
  }
  if(state.winner)state=setSceneRunning(state,false);
 }
 repaint();requestAnimationFrame(tick);
}
reset();
initOriginalVisuals().then(()=>repaint());
window.__swArenaDebug={getState:()=>({
 frame:state.frame,winner:state.winner,projectiles:state.projectiles.length,visual:visualInfo(),
 units:Object.fromEntries(units.map(key=>[key,{
  id:UNIT_CATALOG[key].id,health:state.units[key].hp.health,
  maxLife:state.units[key].hp.maxLife,shotsFired:state.units[key].shotsFired
 }]))
})};
requestAnimationFrame(tick);
