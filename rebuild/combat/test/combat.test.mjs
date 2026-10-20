import test from 'node:test';
import assert from 'node:assert/strict';
import {
 ORIGINAL_DAMAGE,createCombatant,receiveAttack,calculateDamage,sequenceRng,
 seededRng,originalHealthColor,healthBarView,healthBarDivisions,
 advanceFrames,finishDamageParticle,shouldShowHealthBar
} from '../dist/index.js';
const unit=(extra={})=>createCombatant({id:'target',maxLife:200,...extra});
test('reference constants from original 0.02a',()=>{
 assert.deepEqual(ORIGINAL_DAMAGE,{critPercent:10,critMultiplier:1.5,variance:8,damageParticleIntervalFrames:15});
});
test('critical RNG sampled before variance, at strictly below 10 percent',()=>{
 const crit=calculateDamage(30,0,sequenceRng([.099999,0]));
 const normal=calculateDamage(30,0,sequenceRng([.1,0]));
 assert.deepEqual([crit.critical,crit.variance,crit.damage],[true,-4,51]);
 assert.deepEqual([normal.critical,normal.variance,normal.damage],[false,-4,26]);
});
test('critical uses absolute variance and defense',()=>{
 assert.equal(calculateDamage(30,2,sequenceRng([0,.875])).damage,48);
 assert.equal(calculateDamage(30,2,sequenceRng([.5,.875])).damage,31);
});
test('defense cannot reduce damage below one',()=>{
 assert.equal(calculateDamage(1,100,sequenceRng([.5,.5])).damage,1);
 assert.equal(calculateDamage(20.5,0,sequenceRng([.5,.5])).damage,21);
});
test('life reduced, native-like health-bar event, immutable original state',()=>{
 const old=unit();
 const outcome=receiveAttack(old,40,sequenceRng([.5,.5]));
 assert.equal(outcome.state.health,160);
 assert.equal(old.health,200);
 assert.equal(outcome.actualLoss,40);
 assert.equal(shouldShowHealthBar(old),false);
 assert.equal(shouldShowHealthBar(outcome.state),true);
 assert.ok(outcome.events.some(e=>e.type==='damage-number'&&e.amount===40));
 assert.equal(outcome.state.particleCooldownFrames,15);
});
test('nearDeath threshold occurs before death, death separate event',()=>{
 const before=unit({health:30});
 const first=receiveAttack(before,15,sequenceRng([.5,.5]));
 assert.equal(first.state.health,15);
 assert.ok(first.events.some(e=>e.type==='near-death'));
 assert.ok(!first.events.some(e=>e.type==='death'));
 const last=receiveAttack(first.state,50,sequenceRng([.5,.5]));
 assert.ok(last.state.dead);
 assert.ok(last.events.some(e=>e.type==='death'));
 assert.ok(last.events.some(e=>e.type==='health-bar'&&!e.visible));
});
test('delegate rejection/dead do not consume RNG',()=>{
 const bad=()=>{throw new Error('should not be called')};
 assert.equal(receiveAttack(unit({health:0}),20,bad).events[0].reason,'dead');
 assert.equal(receiveAttack(unit(),20,bad,{delegateAllows:false}).events[0].reason,'delegate-rejected');
});
test('invincible receives immune event but does not lose HP',()=>{
 const r=receiveAttack(unit({isInvincible:true}),90,sequenceRng([.5,.5]));
 assert.equal(r.actualLoss,0);
 assert.equal(r.state.health,200);
 assert.ok(r.events.some(e=>e.type==='immune'));
});
test('canDie and debugCanDie clamp at 1 HP',()=>{
 for(const options of [{canDie:false},{debugCanDie:false}]){
  const r=receiveAttack(unit({health:10,...options}),50,sequenceRng([.5,.5]));
  assert.equal(r.state.health,1);
  assert.equal(r.state.dead,false);
 }
});
test('original shield int-coercion comes before attack multiplier',()=>{
 const r=receiveAttack(unit({shieldMultiplier:.25}),7,sequenceRng([.5,.5]),{attackMultiplier:2});
 assert.equal(r.roll.damage,2);
});
test('damage number queue aggregates while a particle is alive',()=>{
 const a=receiveAttack(unit(),10,sequenceRng([.5,.5]));
 const b=receiveAttack(a.state,20,sequenceRng([.5,.5]));
 assert.equal(b.state.pendingDamageToDisplay,20);
 assert.ok(b.events.some(e=>e.type==='damage-queued'));
 const flushed=finishDamageParticle(b.state);
 assert.equal(flushed.events[0].amount,20);
 assert.equal(flushed.state.pendingDamageToDisplay,0);
 assert.equal(finishDamageParticle(flushed.state).state.damageParticleReady,true);
 assert.equal(advanceFrames(flushed.state,15).particleCooldownFrames,0);
});
test('bar segments at original maxLife bounds',()=>{
 for(const [life,divs] of [[1,4],[200,4],[201,8],[400,8],[401,12],[600,12],[601,16],[800,16],[801,20]])
  assert.equal(healthBarDivisions(life),divs);
});
test('health bar color interpolation matches original anchors',()=>{
 for(const [ratio,color] of [[0,'#800000'],[.25,'#ff0000'],[.5,'#ffff00'],[.75,'#00ff00'],[1,'#008000']])
  assert.equal(originalHealthColor(ratio),color);
 assert.equal(originalHealthColor(.125),'#bf0000');
});
test('bar geometry and visible rules',()=>{
 const b=healthBarView(unit({health:100}),2);
 assert.deepEqual([b.divisions,b.width,b.height,b.fillWidth,b.color,b.visible,b.zoomScale],[4,16,4,8,'#ffff00',true,.5]);
 assert.equal(b.greyBackground,'#a0a0a0');
 assert.equal(healthBarView(unit({health:0})).visible,false);
});
test('seeded independent PRNG is reproducible',()=>{
 const a=seededRng(1358),b=seededRng(1358);
 assert.deepEqual(Array.from({length:10},()=>a()),Array.from({length:10},()=>b()));
});
test('invalid health, random and zoom rejected',()=>{
 assert.throws(()=>unit({maxLife:0}),RangeError);
 assert.throws(()=>unit({health:-1}),RangeError);
 assert.throws(()=>calculateDamage(10,0,()=>1),RangeError);
 assert.throws(()=>healthBarView(unit(),0),RangeError);
 assert.throws(()=>advanceFrames(unit(),-.25),RangeError);
});
