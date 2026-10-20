import test from 'node:test';
import assert from 'node:assert/strict';
import {
 UNIT_CATALOG,unitCatalogById,createScene,stepScene,fireSceneWeapon,
 setSceneAutoFire,setSceneRunning,seededRng,sequenceRng,healthBarView
} from '../dist/index.js';

test('community active patch stats for exact historical unit IDs',()=>{
 assert.deepEqual([UNIT_CATALOG.bushwacker.id,UNIT_CATALOG.reaperDrone.id],[1358,1376]);
 assert.deepEqual([UNIT_CATALOG.bushwacker.maxLife,UNIT_CATALOG.reaperDrone.maxLife],[6500,700]);
 assert.deepEqual([UNIT_CATALOG.bushwacker.attack,UNIT_CATALOG.reaperDrone.attack],[138,36]);
 assert.deepEqual([UNIT_CATALOG.bushwacker.defense,UNIT_CATALOG.reaperDrone.defense],[1,1]);
 assert.deepEqual([UNIT_CATALOG.bushwacker.attackRange,UNIT_CATALOG.reaperDrone.attackRange],[10,11]);
 assert.deepEqual([UNIT_CATALOG.bushwacker.velocity,UNIT_CATALOG.reaperDrone.velocity],[7,8]);
 assert.deepEqual([UNIT_CATALOG.bushwacker.attackInterval,UNIT_CATALOG.reaperDrone.attackInterval],[35,30]);
 assert.equal(UNIT_CATALOG.bushwacker.source,'AcidCaos-active-unit-patch');
 assert.equal(unitCatalogById(1376),UNIT_CATALOG.reaperDrone);
 assert.equal(unitCatalogById(1375),undefined);
});
test('independent 2D stage creates real unit HP and no SWF runtime',()=>{
 const s=createScene();
 assert.equal(s.units.bushwacker.hp.health,6500);
 assert.equal(s.units.reaperDrone.hp.health,700);
 assert.deepEqual([s.units.bushwacker.x,s.units.reaperDrone.x],[3,12]);
 assert.equal(s.projectiles.length,0);
 assert.equal(s.winner,null);
});
test('auto fire launches separate bullet and beam with no immediate damage',()=>{
 const s=stepScene(createScene(),sequenceRng([]),1);
 assert.equal(s.projectiles.length,2);
 assert.deepEqual(s.projectiles.map(p=>p.effect),['bullet','beam']);
 assert.equal(s.units.reaperDrone.hp.health,700);
 assert.equal(s.units.bushwacker.hp.health,6500);
});
test('damage only applies after projectile arrival',()=>{
 const rng=sequenceRng(Array(20).fill(.5));
 let s=stepScene(createScene(),rng,7);
 assert.equal(s.units.reaperDrone.hp.health,700);
 assert.equal(s.units.bushwacker.hp.health,6500);
 s=stepScene(s,rng,5);
 assert.ok(s.units.bushwacker.hp.health<6500);
 assert.ok(s.units.reaperDrone.hp.health<700);
 assert.equal(s.units.bushwacker.hp.defense,1);
 assert.equal(healthBarView(s.units.reaperDrone.hp).visible,true);
});
test('cooldown honors patch fields as *demo* frame intervals',()=>{
 let s=createScene();
 s=fireSceneWeapon(s,'bushwacker');
 assert.equal(s.projectiles.length,1);
 assert.equal(fireSceneWeapon(s,'bushwacker').projectiles.length,1);
 const rng=seededRng(1358);
 s=stepScene(setSceneAutoFire(s,false),rng,34);
 assert.equal(s.units.bushwacker.cooldown,1);
 s=stepScene(s,rng,1);
 assert.equal(s.units.bushwacker.cooldown,0);
 s=fireSceneWeapon(s,'bushwacker');
 assert.equal(s.units.bushwacker.shotsFired,2);
});
test('manual shot works with auto disabled, without any movement or server',()=>{
 let s=setSceneAutoFire(createScene(),false);
 s=stepScene(s,sequenceRng([]),100);
 assert.equal(s.projectiles.length,0);
 s=fireSceneWeapon(s,'bushwacker');
 assert.equal(s.projectiles.length,1);
 s=stepScene(s,sequenceRng([.5,.5]),10);
 assert.equal(s.units.reaperDrone.hp.health,700-137);
 assert.equal(s.units.reaperDrone.x,12);
});
test('winning side, death visuals, and no attack after death',()=>{
 let s=createScene();
 s=stepScene(s,seededRng(1358),340);
 assert.equal(s.winner,'bushwacker');
 assert.equal(s.units.reaperDrone.hp.health,0);
 assert.equal(s.units.reaperDrone.hp.dead,true);
 assert.equal(fireSceneWeapon(s,'reaperDrone'),s);
 assert.ok(s.log.some(line=>line.includes('venceu')));
 assert.equal(s.frame<340,true);
});
test('scene states are immutable across simulation steps',()=>{
 const prev=createScene();
 const now=stepScene(prev,sequenceRng([]),1);
 assert.equal(prev.frame,0);
 assert.equal(prev.projectiles.length,0);
 assert.equal(prev.units.bushwacker.shotsFired,0);
 assert.equal(now.units.bushwacker.shotsFired,1);
});
test('step count input validation',()=>{
 assert.throws(()=>stepScene(createScene(),seededRng(1),-1),RangeError);
 assert.throws(()=>stepScene(createScene(),seededRng(1),.5),RangeError);
 assert.throws(()=>stepScene(createScene(),seededRng(1),5001),RangeError);
 assert.equal(setSceneRunning(createScene(),true).running,true);
});
