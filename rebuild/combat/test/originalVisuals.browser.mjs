import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir} from 'node:fs/promises';
const base='http://127.0.0.1:5179';
await mkdir('test/screenshots',{recursive:true});
const browser=await chromium.launch({headless:true,args:['--enable-webgl','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
try{
 const page=await browser.newPage({viewport:{width:1360,height:960},deviceScaleFactor:1});
 const errors=[];page.on('pageerror',err=>errors.push(err.message));
 let response=await page.goto(base+'/arena',{waitUntil:'load'});
 assert.equal(response.status(),200);
 await page.waitForFunction(()=>window.__swArenaDebug?.getState()?.visual?.ready===true,{timeout:20000});
 const initial=await page.evaluate(()=>window.__swArenaDebug.getState());
 assert.equal(initial.visual.mode,'original');
 assert.equal(initial.visual.loaded,12);
 assert.equal(initial.units.bushwacker.maxLife,6500);
 assert.equal(initial.units.reaperDrone.maxLife,700);
 await page.screenshot({path:'test/screenshots/5d8v-original-initial.png',fullPage:true});
 await page.click('#auto');
 await page.click('#b-fire');
 for(let n=0;n<11;n++)await page.click('#step');
 const afterHit=await page.evaluate(()=>window.__swArenaDebug.getState());
 assert.ok(afterHit.units.reaperDrone.health<700);
 await page.screenshot({path:'test/screenshots/5d8v-original-hit.png',fullPage:true});
 await page.click('#visual-mode');
 assert.equal((await page.evaluate(()=>window.__swArenaDebug.getState().visual)).mode,'vector');
 await page.screenshot({path:'test/screenshots/5d8v-vector-fallback.png',fullPage:true});
 await page.click('#visual-mode');
 assert.equal((await page.evaluate(()=>window.__swArenaDebug.getState().visual)).mode,'original');
 const manifest=await (await page.request.get(base+'/original-visual/manifest.json')).json();
 assert.equal(manifest.lot,'5D.8V');
 assert.equal(manifest.originalSWFModified,false);
 assert.equal(manifest.units.reaper_drone.states.ataque.distinctRenderedFrames,1);
 assert.ok(manifest.units.bushwacker.states.ataque.distinctRenderedFrames>1);
 assert.equal((await page.request.get(base+'/original-visual/fx/bazooka.png')).status(),200);
 assert.equal((await page.request.get(base+'/original-visual/../package.json')).status(),404);
 await page.click('#reset');await page.click('#run');
 await page.waitForFunction(()=>window.__swArenaDebug?.getState().winner==='bushwacker',{timeout:35000});
 await page.screenshot({path:'test/screenshots/5d8v-original-death.png',fullPage:true});
 assert.deepEqual(errors,[]);
 console.log('ORIGINAL_SPRITE_ARENA_5D8V',JSON.stringify({
  visible_assets:initial.visual.loaded,original_scene_loaded:true,manual_hit:true,
  vector_fallback:true,auto_victory:true,source_untouched:true,errors
 }));
}finally{await browser.close();}
