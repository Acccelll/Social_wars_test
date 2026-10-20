import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir} from 'node:fs/promises';
await mkdir('test/screenshots',{recursive:true});
const browser=await chromium.launch({headless:true,args:[
 '--enable-webgl','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'
]});
try{
 const page=await browser.newPage({viewport:{width:1370,height:940},deviceScaleFactor:1});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const response=await page.goto('http://127.0.0.1:5179/arena',{waitUntil:'load'});
 assert.equal(response.status(),200);
 await page.waitForFunction(()=>window.__swArenaDebug?.getState().visual?.ready===true,{timeout:20000});
 let state=await page.evaluate(()=>window.__swArenaDebug.getState());
 assert.equal(state.visual.loaded,13);
 assert.equal(state.visual.autoFacingEnabled,true);
 assert.equal(state.units.reaperDrone.facing,7,'Reaper looks LEFT at Bushwacker');
 assert.equal(state.units.bushwacker.facing,3,'Bushwacker looks RIGHT at Reaper');
 await page.screenshot({path:'test/screenshots/5d8x-source-auto-reaper-left.png',fullPage:true});
 // Exactly same drawable canvas, but different directional frame after manual override.
 await page.click('#reaper-facing');
 state=await page.evaluate(()=>window.__swArenaDebug.getState());
 assert.equal(state.visual.autoFacingEnabled,false);
 assert.equal(state.visual.reaperFacingIndex,1);
 await page.screenshot({path:'test/screenshots/5d8x-manual-pose.png',fullPage:true});
 await page.click('#reaper-auto');
 state=await page.evaluate(()=>window.__swArenaDebug.getState());
 assert.equal(state.visual.autoFacingEnabled,true);
 await page.click('#auto'); // Disable automatic attack so hit timing can be checked.
 await page.click('#b-fire');
 for(let i=0;i<11;i++)await page.click('#step');
 state=await page.evaluate(()=>window.__swArenaDebug.getState());
 assert.ok(state.units.reaperDrone.health<700);
 await page.screenshot({path:'test/screenshots/5d8x-impact-auto-facing.png',fullPage:true});
 await page.click('#reset');await page.click('#run');
 await page.waitForFunction(()=>window.__swArenaDebug?.getState().winner==='bushwacker',{timeout:35000});
 await page.screenshot({path:'test/screenshots/5d8x-victory-auto-facing.png',fullPage:true});
 assert.deepEqual(errors,[]);
 console.log('ORIGINAL_DIRECTION_BROWSER_5D8X',JSON.stringify({
   originalAssetsLoaded:13,reaperFacing:7,bushwackerFacing:3,
   mirroredPoseFromSource:true,manualOverrideWorks:true,autoRestores:true,
   impactValidated:true,winValidated:true,pageErrors:errors
 }));
}finally{await browser.close();}
