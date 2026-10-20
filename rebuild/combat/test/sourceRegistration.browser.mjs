import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir} from 'node:fs/promises';
await mkdir('test/screenshots',{recursive:true});
const browser=await chromium.launch({headless:true,args:['--enable-webgl','--use-gl=angle',
 '--use-angle=swiftshader','--enable-unsafe-swiftshader']});
try{
 const page=await browser.newPage({viewport:{width:1420,height:1000},deviceScaleFactor:1});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const res=await page.goto('http://127.0.0.1:5179/calibration',{waitUntil:'load'});
 assert.equal(res.status(),200);
 await page.waitForFunction(()=>window.__swCalibration?.getState().ready===true,{timeout:20000});
 let state=await page.evaluate(()=>window.__swCalibration.getState());
 assert.equal(state.pose,3);assert.equal(state.meta.lot,'5D.8Z');
 assert.equal(state.meta.rootKnown,false);
 assert.equal(state.meta.distinct,5);
 assert.equal(state.calibrated,false);
 assert.equal(state.source,null);
 await page.screenshot({path:'test/screenshots/5d8z-attack-pose-3-uncalibrated.png',fullPage:true});
 await page.getByRole('button',{name:'Pose 1'}).click();
 state=await page.evaluate(()=>window.__swCalibration.getState());
 assert.equal(state.pose,1);
 await page.screenshot({path:'test/screenshots/5d8z-attack-pose-1.png',fullPage:true});
 await page.getByRole('button',{name:'Pose 5'}).click();
 state=await page.evaluate(()=>window.__swCalibration.getState());
 assert.equal(state.pose,5);
 await page.screenshot({path:'test/screenshots/5d8z-attack-pose-5.png',fullPage:true});
 await page.locator('#root-frame').click({position:{x:320,y:260}});
 state=await page.evaluate(()=>window.__swCalibration.getState());
 assert.equal(state.calibrated,true);
 assert.ok(Number.isFinite(state.source.x)&&Number.isFinite(state.source.y));
 await page.screenshot({path:'test/screenshots/5d8z-experimental-marker-overlay.png',fullPage:true});
 await page.getByRole('button',{name:'Limpar ajuste'}).click();
 state=await page.evaluate(()=>window.__swCalibration.getState());
 assert.equal(state.calibrated,false);
 assert.equal(state.source,null);
 const imgs=await page.request.get('http://127.0.0.1:5179/original-visual/registration/bush_attack_root_11_15.png');
 assert.equal(imgs.status(),200);
 assert.equal((await page.request.get('http://127.0.0.1:5179/../../package.json')).status(),404);
 await page.locator('a[href="/arena"]').click();
 await page.waitForFunction(()=>window.__swArenaDebug?.getState().visual?.ready===true,{timeout:20000});
 const arena=await page.evaluate(()=>window.__swArenaDebug.getState());
 assert.equal(arena.visual.loaded,13);
 assert.deepEqual(errors,[]);
 console.log('BUSH_REGISTRATION_BROWSER_5D8Z',JSON.stringify({
  nativeRootFrames:5,rootRegistrationKnown:false,
  manualCalibrationIsOptional:true,unmodifiedArena:true,
  assets:arena.visual.loaded,jsErrors:errors
 }));
}finally{await browser.close();}
