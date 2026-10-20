import {bushMuzzleLocal,calibratedFfdecBushShot} from '/dist/index.js';
const $=id=>document.getElementById(id),canvas=$('root-frame'),ctx=canvas.getContext('2d');
const image=new Image();let meta=null,ready=false,pose=3,calibrated=false;
let viewport=null,readout={};const fmt=n=>Number(n).toFixed(2);
async function init(){
 try{
  const res=await fetch('/original-visual/registration/registration_5d8z.json');
  if(!res.ok)throw Error('Diagnóstico de quadros não disponível');
  meta=await res.json();
  if(meta.lot!=='5D.8Z'||meta.registration.known!==false||meta.frames.length!==5)
    throw Error('Manifesto inválido');
  image.onload=()=>{ready=true;draw();};
  image.onerror=()=>{$('readout').textContent='Erro no PNG raiz';};
  image.src='/original-visual/registration/bush_attack_root_11_15.png';
 }catch(err){$('readout').textContent=String(err.message);}
}
function fields(){const x=Number($('root-x').value),y=Number($('root-y').value),scale=Number($('scale-ratio').value);
 if(!calibrated||!Number.isFinite(x)||!Number.isFinite(y)||!Number.isFinite(scale)||scale<=0)return null;
 return {x,y,scale};
}
function renderLabel(){
 const r=meta.frames[pose-1],m=bushMuzzleLocal(pose);
 const c=fields();
 let text='Pose: '+pose+' · Root frame: '+r.rootFrame+'\n'+
   'PNG: '+r.pngCanvas.join('×')+' px\n'+
   'Alpha bbox: '+r.alphaBounds.join(', ')+'\n'+
   'Muzzle original: '+fmt(m.xPx)+' ; '+fmt(m.yPx)+' px';
 if(c){
  const cal={
   ffdecImageRootOriginPx:{x:c.x,y:c.y},ffdecPxPerSpriteLocalPx:c.scale,
   imageSize:{width:meta.frameWidth,height:meta.frameHeight},
   canvasRect:viewport.rect
  };
  const shot=calibratedFfdecBushShot(pose,cal);
  readout={pose,source:shot.source,canvas:shot.canvas,inside:shot.inSourceBounds,
   origin:{x:c.x,y:c.y},scale:c.scale};
  text+='\nMuzzle FFDec candidato: '+fmt(shot.source.x)+' ; '+fmt(shot.source.y)+
      '\nDentro do PNG: '+(shot.inSourceBounds?'sim':'não')+
      '\nESTADO: AJUSTE EXPERIMENTAL';
 }else{readout={pose,source:null};text+='\nESTADO: ORIGEM NÃO MEDIDA';}
 $('readout').textContent=text;
 $('calibration-status').textContent=c?'Calibração manual não validada':'Origem desconhecida — nenhum marcador projetado';
}
function draw(){
 if(!ready)return;
 const frame=meta.frames[pose-1];
 const fullW=meta.frameWidth,fullH=meta.frameHeight;
 canvas.width=640;canvas.height=560;
 ctx.clearRect(0,0,640,560);
 const fit=Math.min(615/fullW,515/fullH);
 const w=fullW*fit,h=fullH*fit,x=(640-w)/2,y=(560-h)/2;
 viewport={fit,rect:{x,y,width:w,height:h}};
 ctx.fillStyle='#213844';ctx.fillRect(0,0,640,560);
 ctx.drawImage(image,(pose-1)*fullW,0,fullW,fullH,x,y,w,h);
 const a=frame.alphaBounds;
 ctx.strokeStyle='#80e5e4';ctx.lineWidth=1.5;
 ctx.strokeRect(x+a[0]*fit,y+a[1]*fit,(a[2]-a[0])*fit,(a[3]-a[1])*fit);
 const c=fields();
 if(c){
  const ox=x+c.x*fit,oy=y+c.y*fit;
  ctx.strokeStyle='#b2e5a5';ctx.lineWidth=2;
  ctx.beginPath();ctx.moveTo(ox-11,oy);ctx.lineTo(ox+11,oy);
  ctx.moveTo(ox,oy-11);ctx.lineTo(ox,oy+11);ctx.stroke();
  const shot=calibratedFfdecBushShot(pose,{
   ffdecImageRootOriginPx:{x:c.x,y:c.y},ffdecPxPerSpriteLocalPx:c.scale,
   imageSize:{width:fullW,height:fullH},canvasRect:viewport.rect
  });
  ctx.beginPath();ctx.arc(shot.canvas.x,shot.canvas.y,7,0,Math.PI*2);
  ctx.fillStyle='#ffd87e';ctx.fill();ctx.strokeStyle='#212f36';ctx.stroke();
  ctx.beginPath();ctx.moveTo(ox,oy);ctx.lineTo(shot.canvas.x,shot.canvas.y);
  ctx.strokeStyle='#ffe58aa0';ctx.lineWidth=1;ctx.stroke();
 }
 ctx.fillStyle='#c9e7f4';ctx.font='600 13px system-ui';
 ctx.fillText('ATTACK FRAME '+frame.rootFrame+'  ·  SOURCE ALPHA BOUNDS',18,25);
 renderLabel();
}
function setPose(n){pose=n;for(const b of $('poses').querySelectorAll('button'))b.classList.toggle('active',Number(b.dataset.pose)===n);draw();}
$('poses').addEventListener('click',e=>{const b=e.target.closest('[data-pose]');if(b)setPose(Number(b.dataset.pose));});
canvas.addEventListener('click',e=>{
 if(!viewport)return;
 const r=canvas.getBoundingClientRect(),px=(e.clientX-r.left)*canvas.width/r.width,py=(e.clientY-r.top)*canvas.height/r.height;
 $('root-x').value=fmt((px-viewport.rect.x)/viewport.fit);
 $('root-y').value=fmt((py-viewport.rect.y)/viewport.fit);
 calibrated=true;draw();
});
for(const id of ['root-x','root-y','scale-ratio'])
 $(id).addEventListener('input',()=>{
  if($('root-x').value!==''&&$('root-y').value!=='')calibrated=true;
  draw();
 });
$('reset-cal').onclick=()=>{calibrated=false;$('root-x').value='';$('root-y').value='';draw();};
window.__swCalibration={getState:()=>({ready,pose,calibrated,meta:meta?{
 lot:meta.lot,rootKnown:meta.registration.known,distinct:meta.distinctImages}:null,...readout})};
init();