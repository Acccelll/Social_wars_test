import test from 'node:test';
import assert from 'node:assert/strict';
import {
 calibratedFfdecBushShot,localBushMarkerInFfdecImage,
 sourcePixelInCanvas,validateRegistration
} from '../dist/index.js';
const cal={
 ffdecImageRootOriginPx:{x:640,y:840},
 ffdecPxPerSpriteLocalPx:1,
 imageSize:{width:1255,height:1140},
 canvasRect:{x:20,y:30,width:251,height:228}
};
test('root-local marker uses explicitly measured PNG registration, not alpha center',()=>{
 assert.deepEqual(localBushMarkerInFfdecImage(3,cal),{x:826.55,y:657.5});
});
test('FFDec source pixel to drawn Canvas rectangle scales both axes',()=>{
 assert.deepEqual(sourcePixelInCanvas({x:200,y:300},cal),{x:60,y:90});
});
test('measured Bush projectile point conversion preserves original affine marker',()=>{
 const shot=calibratedFfdecBushShot(3,cal);
 assert.deepEqual(shot.source,{x:826.55,y:657.5});
 assert.ok(Math.abs(shot.canvas.x-185.31)<.001);
 assert.ok(Math.abs(shot.canvas.y-161.5)<.001);
 assert.equal(shot.inSourceBounds,true);
});
test('mirrored logical direction also mirrors source muzzle relative to root point',()=>{
 const left=calibratedFfdecBushShot(7,cal);
 const right=calibratedFfdecBushShot(3,cal);
 assert.equal(right.source.y,left.source.y);
 assert.ok(Math.abs((right.source.x+left.source.x)/2-640)<1e-9);
});
test('registration missing or invalid measured scale is rejected',()=>{
 for(const factor of [0,-1,NaN]){
  assert.throws(()=>validateRegistration({...cal,ffdecPxPerSpriteLocalPx:factor}),RangeError);
 }
 assert.throws(()=>validateRegistration({...cal,canvasRect:{x:0,y:0,width:0,height:20}}),RangeError);
 assert.throws(()=>validateRegistration({...cal,ffdecImageRootOriginPx:{x:NaN,y:0}}),RangeError);
});
