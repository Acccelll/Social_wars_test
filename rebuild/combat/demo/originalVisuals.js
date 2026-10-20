/** 5D.8V original FFDec sprite/FX atlases. Optional; keep Canvas placeholders.
 * GIF sources are limited nested-timeline subframes, not every original frame.
 */
import {originalFacingFrame} from '/dist/originalDirection.js';
const UNIT_KEYS={bushwacker:'bushwacker',reaperDrone:'reaper_drone'};
const imageCache=new Map();
let manifest=null,mode='original',status='loading',error=null,tick=0;
let reaperFacingIndex=0; // Optional manual pose override, retained from 5D.8W.
let manualReaperPose=null; // null = source-derived automatic 8-direction facing.
const deadAt=new Map();
function paintFrame(ctx,rec,x,y,w,h,frame,angle=0,flipX=false){
 const img=imageCache.get(rec?.url);
 if(!img||!rec?.frames||!rec.frameWidth||!rec.frameHeight)return false;
 const f=((Math.floor(frame)%rec.frames)+rec.frames)%rec.frames;
 ctx.save();ctx.translate(x,y);ctx.rotate(angle);if(flipX)ctx.scale(-1,1);
 ctx.drawImage(img,(f%rec.columns)*rec.frameWidth,Math.floor(f/rec.columns)*rec.frameHeight,
   rec.frameWidth,rec.frameHeight,-w/2,-h/2,w,h);
 ctx.restore();return true;
}
export function visualInfo(){return {mode,status,error,loaded:imageCache.size,ready:status==='ready',
 reaperFacingIndex,manualReaperPose,autoFacingEnabled:manualReaperPose===null};}
export function resetReaperFacing(){manualReaperPose=null;}
export function nextReaperFacing(){reaperFacingIndex=(reaperFacingIndex+1)%5;manualReaperPose=reaperFacingIndex;return reaperFacingIndex;}
export function setVisualMode(next){
 if(!['original','vector'].includes(next))throw Error('Invalid visual mode');
 mode=next;
}
export function nextVisualTick(){tick++;}
export async function initOriginalVisuals(){
 try{
  const response=await fetch('/original-visual/manifest.json',{cache:'no-store'});
  if(!response.ok)throw Error('Opcional sprite pack indisponível ('+response.status+')');
  const m=await response.json();
  if(!['5D.8V','5D.8W'].includes(m.lot)||m.originalSWFModified!==false)throw Error('Manifest incompatible');
  const urls=[];
  for(const key of Object.values(UNIT_KEYS)){
   const u=m.units?.[key];
   if(!u||!['quieto','ataque','muerte'].every(n=>u.states?.[n]))throw Error('Missing unit states '+key);
   urls.push(...Object.values(u.states).map(r=>r.url));
  }
  for(const key of ['bullet','laser','bazooka','laserBlue']){
   if(!m.effects?.[key])throw Error('Missing projectile/impact '+key);
   urls.push(m.effects[key].url);
  }
  await Promise.all([...new Set(urls)].map(url=>new Promise((resolve,reject)=>{
   const img=new Image();img.onload=()=>{imageCache.set(url,img);resolve();};
   img.onerror=()=>reject(Error('Sprite file failed: '+url));img.src=url;
  })));
  manifest=m;status='ready';error=null;
 }catch(e){manifest=null;status='missing';error=String(e?.message||e);}
 return visualInfo();
}
export function drawOriginalUnit(ctx,key,u,p){
 if(mode!=='original'||status!=='ready')return false;
 const recs=manifest.units[UNIT_KEYS[key]].states;
 const state=u.hp.dead?'muerte':u.poseFrames>0?'ataque':'quieto';
 const rec=recs[state];if(!rec)return false;
 if(!u.hp.dead)deadAt.delete(key);
 else if(!deadAt.has(key))deadAt.set(key,tick);
 // The 25 Reaper root frames include 5 different orientation poses in
 // QUIETO/ANDAR/ATAQUE; they must not be cycled as a temporal animation.
 const autoDirection=originalFacingFrame(u.facing??(key==='reaperDrone'?7:3));
 const frame=key==='reaperDrone'
   ? (u.hp.dead?0:Math.min(rec.frames-1,
       manualReaperPose===null?autoDirection.poseIndex:manualReaperPose))
   : (u.hp.dead?Math.min(rec.frames-1,Math.floor((tick-deadAt.get(key))/3))
     :u.poseFrames>0?(8-u.poseFrames)*2:Math.floor(tick/2));
 // Flash ghostBuilding.scaleX mirrors about its registration point.
 // Canvas export anchoring is provisional and not claimed pixel-perfect.
 const flip=key==='reaperDrone'&&manualReaperPose===null&&autoDirection.mirrored;
 const height=key==='bushwacker'?238:161;
 return paintFrame(ctx,rec,p.x,p.y-(key==='bushwacker'?92:64),
   height*rec.frameWidth/rec.frameHeight,height,frame,0,flip);
}
export function drawOriginalShot(ctx,shot,progress,from,to){
 if(mode!=='original'||status!=='ready')return false;
 const rec=manifest.effects[shot.effect==='bullet'?'bullet':'laser'];
 if(!rec)return false;
 const x=from.x+(to.x-from.x)*progress,y=from.y-26+(to.y-from.y)*progress;
 const angle=Math.atan2(to.y-from.y,to.x-from.x);
 return paintFrame(ctx,rec,x,y,shot.effect==='bullet'?74:105,
   shot.effect==='bullet'?24:12,Math.floor(tick*rec.fps/30),angle);
}
export function drawOriginalImpact(ctx,hit,p){
 if(mode!=='original'||status!=='ready'||hit.kind!=='hit')return false;
 const rec=manifest.effects[hit.x<=6?'laserBlue':'bazooka'];
 if(!rec)return false;
 const frame=Math.min(rec.frames-1,Math.floor((15-hit.remaining)*rec.fps/30));
 const h=85;
 return paintFrame(ctx,rec,p.x,p.y-26,h*rec.frameWidth/rec.frameHeight,h,frame);
}
