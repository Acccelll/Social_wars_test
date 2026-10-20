import test from 'node:test';
import assert from 'node:assert/strict';
import {
 BUSH_ATTACK_MARKERS,bushMuzzleLocal,bushMuzzleForDirection,
 calibratedBushMuzzle,multiplyAffine,transformPoint
} from '../dist/index.js';
const expected=[
 [1,11,643,116.15,-371.7],
 [2,12,675,254.55,-299.2],
 [3,13,716,186.55,-182.5],
 [4,14,752,89.7,-78.25],
 [5,15,786,-93.9,-109.7]
];
test('Bushwacker original five root attack marker paths are deterministic',()=>{
 assert.equal(BUSH_ATTACK_MARKERS.length,5);
 for(const [pose,frame,sprite,x,y] of expected){
  const v=bushMuzzleLocal(pose);
  assert.deepEqual([v.pose,v.rootFrame,v.spriteId],[pose,frame,sprite]);
  assert.ok(Math.abs(v.xPx-x)<1e-9);
  assert.ok(Math.abs(v.yPx-y)<1e-9);
 }
});
test('SWF child placement includes original -1 scaleX, not a sign guess',()=>{
 const p=BUSH_ATTACK_MARKERS[0];
 const m=multiplyAffine(p.rootPlacement,p.markerPlacement);
 assert.deepEqual([...m],[-1,0,0,1,2323,-7434]);
 assert.deepEqual(transformPoint(m,{x:0,y:0}),{x:2323,y:-7434});
});
test('static 8-way direction mirror applies outside nested sprite chain',()=>{
 for(const [direction,pose,mirror] of [
  [1,1,false],[2,2,false],[3,3,false],[4,4,false],[5,5,false],
  [6,2,true],[7,3,true],[8,4,true]]){
  const r=bushMuzzleForDirection(direction);
  const local=bushMuzzleLocal(pose);
  assert.equal(r.mirrored,mirror);
  assert.equal(r.local.pose,pose);
  assert.equal(r.xPx,mirror?-local.xPx:local.xPx);
  assert.equal(r.yPx,local.yPx);
 }
});
test('screen muzzle conversion explicitly requires measured origin and scale',()=>{
 const p=calibratedBushMuzzle({direction:3,measuredRootOrigin:{x:500,y:600},
  measuredPixelsPerOriginalPx:.5});
 assert.deepEqual(p,{x:593.275,y:508.75});
 assert.throws(()=>calibratedBushMuzzle({direction:3,
  measuredRootOrigin:{x:0,y:0},measuredPixelsPerOriginalPx:0}),RangeError);
});
test('invalid frame, affine and missing measured origin rejected',()=>{
 assert.throws(()=>bushMuzzleLocal(6),RangeError);
 assert.throws(()=>multiplyAffine([1,0,0,1,0,NaN],[1,0,0,1,0,0]),RangeError);
 assert.throws(()=>transformPoint([1,0,0,1,0,0],{x:NaN,y:0}),RangeError);
});
