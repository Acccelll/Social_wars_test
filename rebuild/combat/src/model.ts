/** Independent subset of Social Wars 0.02a IsoFightingElement damage lifecycle.
 * SHA-pinned reference and limitations: docs/LOTE_5D_8S.md.
 * Never calls the original server, manipulates original saves or loads SWF.
 */
export const ORIGINAL_DAMAGE = Object.freeze({
  critPercent: 10, critMultiplier: 1.5, variance: 8, damageParticleIntervalFrames: 15
});
export type RandomSource=()=>number;
export interface CombatantState {
  readonly id:string; readonly maxLife:number; readonly health:number;
  readonly defense:number; readonly shieldMultiplier:number;
  readonly isInvincible:boolean; readonly canDie:boolean; readonly debugCanDie:boolean;
  readonly displayHealthBar:boolean; readonly dead:boolean;
  readonly pendingDamageToDisplay:number; readonly damageParticleReady:boolean;
  readonly particleCooldownFrames:number;
}
export interface CreateCombatantOptions {
  id:string; maxLife:number; health?:number; defense?:number; shieldMultiplier?:number;
  isInvincible?:boolean; canDie?:boolean; debugCanDie?:boolean; displayHealthBar?:boolean;
}
function finite(n:number,label:string){if(!Number.isFinite(n))throw new RangeError(label+' must be finite');}
function random(rng:RandomSource){
  const r=rng();if(!Number.isFinite(r)||r<0||r>=1)throw new RangeError('RNG must return 0<=x<1');
  return r;
}
export function createCombatant(o:CreateCombatantOptions):CombatantState {
  if(!o.id?.trim())throw new RangeError('id required');
  finite(o.maxLife,'maxLife');
  if(!Number.isInteger(o.maxLife)||o.maxLife<=0)throw new RangeError('positive integer maxLife required');
  const health=o.health??o.maxLife, defense=o.defense??0,shieldMultiplier=o.shieldMultiplier??1;
  finite(health,'health');finite(defense,'defense');finite(shieldMultiplier,'shieldMultiplier');
  if(!Number.isInteger(health)||health<0||health>o.maxLife)throw new RangeError('invalid health');
  if(defense<0||shieldMultiplier<0)throw new RangeError('negative defense/shield');
  return {id:o.id,maxLife:o.maxLife,health,defense,shieldMultiplier,
    isInvincible:o.isInvincible??false,canDie:o.canDie??true,debugCanDie:o.debugCanDie??true,
    displayHealthBar:o.displayHealthBar??true,dead:health===0,pendingDamageToDisplay:0,
    damageParticleReady:true,particleCooldownFrames:0};
}
export interface DamageRoll {
  readonly damage:number;readonly critical:boolean;readonly variance:number;
  readonly criticalRoll:number;readonly varianceRoll:number;readonly defense:number;
}
/** Original calculateDamage: crit RNG first, variance RNG second. */
export function calculateDamage(baseAttack:number,defense:number,rng:RandomSource):DamageRoll {
  finite(baseAttack,'attack');finite(defense,'defense');
  const criticalRoll=random(rng),varianceRoll=random(rng);
  const critical=criticalRoll*100<ORIGINAL_DAMAGE.critPercent;
  const variance=varianceRoll*ORIGINAL_DAMAGE.variance-ORIGINAL_DAMAGE.variance/2;
  const raw=critical?(baseAttack+Math.abs(variance))*ORIGINAL_DAMAGE.critMultiplier:baseAttack+variance;
  return {damage:Math.max(1,Math.round(raw-defense)),critical,variance,criticalRoll,varianceRoll,defense};
}
export type CombatEvent=
 | {type:'ignored';reason:'dead'|'delegate-rejected'}
 | {type:'near-death';entityId:string;threshold:number}
 | {type:'damage-calculated';entityId:string;amount:number;critical:boolean}
 | {type:'damage-applied';entityId:string;before:number;after:number;actualLoss:number}
 | {type:'damage-number';entityId:string;amount:number}
 | {type:'damage-queued';entityId:string;total:number}
 | {type:'immune';entityId:string}
 | {type:'health-bar';entityId:string;visible:boolean;ratio:number}
 | {type:'death';entityId:string};
export interface ReceiveAttackOptions {
  delegateAllows?:boolean;attackMultiplier?:number;bonusAttack?:number;displayDamageParticle?:boolean;
}
export interface AttackOutcome{
  readonly state:CombatantState;readonly events:readonly CombatEvent[];
  readonly roll:DamageRoll|null;readonly actualLoss:number;
}
export function shouldShowHealthBar(s:CombatantState):boolean {
  return s.displayHealthBar&&!s.dead&&s.health>0&&s.health<s.maxLife;
}
/** Own immutable model of recibirAtaque. Deliberately excludes best_against,
 * siege, XP, unit AI and projectile routing. attackMultiplier/bonusAttack
 * are delegate inputs, not internally invented original unit stats.
 */
export function receiveAttack(
  state:CombatantState,baseAttack:number,rng:RandomSource,options:ReceiveAttackOptions={}
):AttackOutcome{
  if(state.dead)return {state,events:[{type:'ignored',reason:'dead'}],roll:null,actualLoss:0};
  if(options.delegateAllows===false)return {state,events:[{type:'ignored',reason:'delegate-rejected'}],roll:null,actualLoss:0};
  finite(baseAttack,'attack');
  const mult=options.attackMultiplier??1,bonus=options.bonusAttack??0;
  finite(mult,'attackMultiplier');finite(bonus,'bonusAttack');
  if(mult<0)throw new RangeError('negative attack multiplier');
  // Native _ataque:int *= _shieldMultiplier, then additional modifiers as Number.
  const incoming=Math.trunc(baseAttack*state.shieldMultiplier)*mult+bonus;
  const roll=calculateDamage(incoming,state.defense,rng);
  const events:CombatEvent[]=[{type:'damage-calculated',entityId:state.id,amount:roll.damage,critical:roll.critical}];
  const before=state.health;
  if(before>=state.maxLife*.1&&before-roll.damage<state.maxLife*.1)
    events.push({type:'near-death',entityId:state.id,threshold:.1});
  let health=state.isInvincible?before:before-roll.damage;
  if(health<=0)health=(!state.canDie||!state.debugCanDie)?1:0;
  const dead=health===0,actualLoss=before-health;
  let pending=state.pendingDamageToDisplay,ready=state.damageParticleReady,cooldown=state.particleCooldownFrames;
  if(options.displayDamageParticle!==false){
    if(state.isInvincible)events.push({type:'immune',entityId:state.id});
    else{
      pending+=roll.damage;
      if(cooldown<=0&&ready){
        events.push({type:'damage-number',entityId:state.id,amount:pending});
        pending=0;ready=false;cooldown=ORIGINAL_DAMAGE.damageParticleIntervalFrames;
      } else events.push({type:'damage-queued',entityId:state.id,total:pending});
    }
  }
  events.push({type:'damage-applied',entityId:state.id,before,after:health,actualLoss});
  const next:CombatantState={...state,health,dead,pendingDamageToDisplay:pending,
    damageParticleReady:ready,particleCooldownFrames:cooldown};
  events.push({type:'health-bar',entityId:state.id,visible:shouldShowHealthBar(next),ratio:health/state.maxLife});
  if(dead)events.push({type:'death',entityId:state.id});
  return {state:next,events,roll,actualLoss};
}
export function advanceFrames(s:CombatantState,frames:number):CombatantState {
  if(!Number.isInteger(frames)||frames<0)throw new RangeError('frames must be nonnegative integer');
  return {...s,particleCooldownFrames:Math.max(0,s.particleCooldownFrames-frames)};
}
/** Approximate original _onDamageParticleFinished callback. */
export function finishDamageParticle(s:CombatantState):{state:CombatantState;events:readonly CombatEvent[]}{
  if(s.pendingDamageToDisplay>0)return {state:{...s,pendingDamageToDisplay:0,damageParticleReady:false},
    events:[{type:'damage-number',entityId:s.id,amount:s.pendingDamageToDisplay}]};
  return {state:{...s,damageParticleReady:true},events:[]};
}
