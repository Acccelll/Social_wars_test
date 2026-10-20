/** Standalone 2D combat scene for the 5D.8U demo.
 * Uses confirmed active community server stats. Timings, projectile motion,
 * positions and drawn units below are independent visual approximations,
 * NOT extracted original movement/FX/sprite behavior.
 */
import {UNIT_CATALOG,type UnitKey} from './unitCatalog.js';
import {originalDirectionToward,type OriginalDirection} from './originalDirection.js';
import {
 createCombatant,receiveAttack,advanceFrames,finishDamageParticle,
 type CombatantState,type RandomSource
} from './model.js';

export interface SceneUnit {
 readonly key:UnitKey;readonly x:number;readonly y:number;
 readonly hp:CombatantState;readonly cooldown:number;readonly poseFrames:number;
 readonly shotsFired:number;readonly facing:OriginalDirection;
}
export interface SceneProjectile {
 readonly id:number;readonly from:UnitKey;readonly to:UnitKey;
 readonly x0:number;readonly y0:number;readonly x1:number;readonly y1:number;
 readonly remaining:number;readonly duration:number;readonly effect:'bullet'|'beam';
}
export interface SceneImpact {
 readonly id:number;readonly x:number;readonly y:number;readonly amount:number;
 readonly critical:boolean;readonly remaining:number;readonly kind:'hit'|'death'|'number';
}
export interface SceneState {
 readonly frame:number;readonly running:boolean;readonly autoFire:boolean;readonly nextId:number;
 readonly units:Readonly<Record<UnitKey,SceneUnit>>;
 readonly projectiles:readonly SceneProjectile[];
 readonly impacts:readonly SceneImpact[];
 readonly log:readonly string[];
 readonly winner:UnitKey|null;
}
const keys:readonly UnitKey[]=['bushwacker','reaperDrone'];
const target=(key:UnitKey):UnitKey=>key==='bushwacker'?'reaperDrone':'bushwacker';
const label=(key:UnitKey)=>UNIT_CATALOG[key].name;
const LOG_LIMIT=32;
function append(s:SceneState,line:string):SceneState {
 return {...s,log:[...s.log,line].slice(-LOG_LIMIT)};
}
export function createScene():SceneState {
 const mk=(key:UnitKey,x:number):SceneUnit=>({
  key,x,y:5,hp:createCombatant({
   id:key,maxLife:UNIT_CATALOG[key].maxLife,defense:UNIT_CATALOG[key].defense
  }),cooldown:0,poseFrames:0,shotsFired:0,facing:key==='bushwacker'?3:7
 });
 return {frame:0,running:false,autoFire:true,nextId:1,
  units:{bushwacker:mk('bushwacker',3),reaperDrone:mk('reaperDrone',12)},
  projectiles:[],impacts:[],
  log:['Cena própria 2D iniciada; atributos do patch comunitário verificados.'],
  winner:null};
}
export function setSceneRunning(s:SceneState,running:boolean):SceneState {
 return {...s,running};
}
export function setSceneAutoFire(s:SceneState,autoFire:boolean):SceneState {
 return {...s,autoFire};
}
/** One projectile per permitted fire. Attack interval is treated as frames
 * FOR THIS DEMO; the original animation/action cadence has not been recovered.
 */
export function fireSceneWeapon(s:SceneState,from:UnitKey):SceneState {
 const u=s.units[from],t=s.units[target(from)],cfg=UNIT_CATALOG[from];
 if(u.hp.dead||t.hp.dead||u.cooldown>0)return s;
 const tileDistance=Math.hypot(u.x-t.x,u.y-t.y);
 if(tileDistance>cfg.attackRange)return s;
 const duration=from==='bushwacker'?10:7;
 const shot:SceneProjectile={
  id:s.nextId,from,to:target(from),x0:u.x,y0:u.y,
  x1:t.x,y1:t.y,remaining:duration,duration,
  effect:from==='bushwacker'?'bullet':'beam'
 };
 // Original IsoUnit.updateDirection() faces the target before attack.
 // This 2D demo uses its screen-space tile axes as an affine projection;
 // orientation rules are source-derived, but isometric tile conversion is pending.
 const facing=originalDirectionToward(
   {x:u.x,y:u.y},{x:t.x,y:t.y},u.facing);
 const u2={...u,cooldown:cfg.attackInterval,poseFrames:8,
   shotsFired:u.shotsFired+1,facing};
 return append({...s,nextId:s.nextId+1,
  units:{...s.units,[from]:u2},
  projectiles:[...s.projectiles,shot]},`${label(from)} disparou (frame ${s.frame}).`);
}
function applyHit(s:SceneState,shot:SceneProjectile,rng:RandomSource):SceneState {
 const u=s.units[shot.to];if(u.hp.dead)return s;
 const result=receiveAttack(u.hp,UNIT_CATALOG[shot.from].attack,rng);
 const nextUnit={...u,hp:result.state};
 const amount=result.actualLoss;
 const critical=result.roll?.critical??false;
 const damageNumbers=result.events.filter(e=>e.type==='damage-number');
 const impacts:SceneImpact[]=[
  {id:s.nextId,x:u.x,y:u.y,amount,critical,remaining:15,kind:'hit'},
  ...damageNumbers.map((e,i):SceneImpact=>({
    id:s.nextId+i+1,x:u.x,y:u.y,amount:e.amount,
    critical,remaining:28,kind:'number'
  }))
 ];
 let next:SceneState={...s,nextId:s.nextId+impacts.length,
   units:{...s.units,[shot.to]:nextUnit},
   impacts:[...s.impacts,...impacts]};
 next=append(next,`${label(shot.to)} recebeu ${amount} dano${critical?' CRÍTICO':''}: HP ${nextUnit.hp.health}/${nextUnit.hp.maxLife}.`);
 if(nextUnit.hp.dead){
  next={...next,winner:shot.from,impacts:[
   ...next.impacts,{id:next.nextId,x:u.x,y:u.y,amount:0,
    critical:false,remaining:34,kind:'death'}],nextId:next.nextId+1};
  next=append(next,`Derrota de ${label(shot.to)}; ${label(shot.from)} venceu.`);
 }
 return next;
}
export function stepScene(input:SceneState,rng:RandomSource,frames=1):SceneState {
 if(!Number.isInteger(frames)||frames<0||frames>5000)throw new RangeError('frames must be integer 0..5000');
 let s=input;
 for(let i=0;i<frames;i++){
  if(s.winner)break;
  s={...s,frame:s.frame+1,
   units:Object.fromEntries(keys.map(key=>{
    const u=s.units[key];
    const cooled=advanceFrames(u.hp,1);
    const done=cooled.particleCooldownFrames===0&&cooled.pendingDamageToDisplay>0
      ?finishDamageParticle(cooled):null;
    return [key,{...u,hp:done?.state??cooled,
      cooldown:Math.max(0,u.cooldown-1),poseFrames:Math.max(0,u.poseFrames-1)}];
   })) as Record<UnitKey,SceneUnit>,
   impacts:s.impacts.map(x=>({...x,remaining:x.remaining-1})).filter(x=>x.remaining>0)};
  if(s.autoFire)for(const key of keys)s=fireSceneWeapon(s,key);
  const remaining:SceneProjectile[]=[];
  const hits:SceneProjectile[]=[];
  for(const shot of s.projectiles){
   if(shot.remaining<=1)hits.push(shot);
   else remaining.push({...shot,remaining:shot.remaining-1});
  }
  s={...s,projectiles:remaining};
  for(const hit of hits)s=applyHit(s,hit,rng);
 }
 return s;
}
