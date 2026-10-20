import test from 'node:test';
import assert from 'node:assert/strict';
import {
 ORIGINAL_DIRECTION,originalDirectionToward,originalFacingFrame,
 originalSpriteFrame,originalProjectileStart,originalProjectileHitPoint,
 createScene,fireSceneWeapon,unitCatalogById
} from '../dist/index.js';
const here={x:0,y:0};
test('original eight logical directions have their exact 1..8 enum values',()=>{
 assert.deepEqual(Object.values(ORIGINAL_DIRECTION),[1,2,3,4,5,6,7,8]);
});
test('all eight facing directions fold to five native root poses plus mirror',()=>{
 const expected=[
  [1,1,false],[2,2,false],[3,3,false],[4,4,false],[5,5,false],
  [6,2,true],[7,3,true],[8,4,true]
 ];
 for(const [direction,pose,mirror] of expected){
  const f=originalFacingFrame(direction);
  assert.equal(f.oneBasedPose,pose);
  assert.equal(f.poseIndex,pose-1);
  assert.equal(f.mirrored,mirror);
  assert.equal(f.scaleX,mirror?-1:1);
  assert.equal(originalSpriteFrame(0,direction),pose);
  assert.equal(originalSpriteFrame(1,direction),5+pose);
  assert.equal(originalSpriteFrame(2,direction),10+pose);
  assert.equal(originalSpriteFrame(3,direction),15+pose);
 }
});
test('eight-way direction selected by signed screen-space coordinate deltas',()=>{
 const samples=[
  [{x:0,y:-15},1],[{x:1,y:-1},2],[{x:12,y:0},3],
  [{x:1,y:1},4],[{x:0,y:15},5],
  [{x:-1,y:-1},6],[{x:-12,y:0},7],[{x:-1,y:1},8]
 ];
 for(const [point,dir] of samples)
  assert.equal(originalDirectionToward(here,point,5),dir);
});
test('original near-target dead-zone preserves preceding facing',()=>{
 const opts={applyOriginalDeadZone:true,tileWidthPx:60,tileHeightPx:30};
 assert.equal(originalDirectionToward(here,{x:19.999,y:9.999},7,opts),7);
 assert.equal(originalDirectionToward(here,{x:20,y:9.999},7,opts),4);
 assert.equal(originalDirectionToward(here,{x:0,y:0},5,opts),5);
});
test('native attack frames are 11..15 and death frames 16..20',()=>{
 assert.deepEqual([1,2,3,4,5].map(d=>originalSpriteFrame(2,d)),[11,12,13,14,15]);
 assert.deepEqual([1,2,3,4,5].map(d=>originalSpriteFrame(3,d)),[16,17,18,19,20]);
});
test('source getProjectilePoint resolves supplied marker in parent coordinates',()=>{
 assert.deepEqual(originalProjectileStart({
  worldPosition:{x:80,y:140},resolvedMarkerInParent:{x:112,y:83},displayHeight:200
 }),{x:112,y:83});
});
test('source getProjectilePoint fallback subtracts 60% sprite height',()=>{
 assert.deepEqual(originalProjectileStart({
  worldPosition:{x:80,y:140},displayHeight:200
 }),{x:80,y:20});
 assert.deepEqual(originalProjectileStart({worldPosition:{x:80,y:140}}),{x:80,y:140});
});
test('source getHitPoint uses marker offset if known, otherwise bounds and verticalOffset',()=>{
 assert.deepEqual(originalProjectileHitPoint({
  worldPosition:{x:200,y:300},resolvedHitMarkerOffset:{x:3,y:-44},
  boundsInTarget:{y:-100,height:100},verticalOffset:.5
 }),{x:203,y:256});
 assert.deepEqual(originalProjectileHitPoint({
  worldPosition:{x:200,y:300},
  boundsInTarget:{y:-100,height:100},verticalOffset:.5
 }),{x:200,y:250});
 assert.deepEqual(originalProjectileHitPoint({worldPosition:{x:200,y:300}}),{x:200,y:300});
});
test('origin and target coordinate guards reject invalid input',()=>{
 assert.throws(()=>originalFacingFrame(0),RangeError);
 assert.throws(()=>originalSpriteFrame(8,3),RangeError);
 assert.throws(()=>originalDirectionToward(here,{x:NaN,y:10},3),RangeError);
 assert.throws(()=>originalProjectileStart({worldPosition:here,displayHeight:-5}),RangeError);
});
test('independent scene automatically faces opponent on spawn and firing',()=>{
 let s=createScene();
 assert.equal(s.units.bushwacker.facing,3);
 assert.equal(s.units.reaperDrone.facing,7);
 s=fireSceneWeapon(s,'bushwacker');
 s=fireSceneWeapon(s,'reaperDrone');
 assert.equal(s.units.bushwacker.facing,3);
 assert.equal(s.units.reaperDrone.facing,7);
 assert.equal(s.projectiles.length,2);
 assert.equal(unitCatalogById(1376)?.attackRange,11);
});
