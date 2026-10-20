import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir} from 'node:fs/promises';
const root='test/screenshots';
await mkdir(root,{recursive:true});
const browser=await chromium.launch({headless:true,args:['--enable-webgl','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
try{
 const page=await browser.newPage({viewport:{width:1360,height:930},deviceScaleFactor:1});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const response=await page.goto('http://127.0.0.1:5179/arena',{waitUntil:'load'});
 assert.equal(response.status(),200);
 await page.waitForFunction(()=>window.__swArenaDebug?.getState().visual?.ready===true,{timeout:20000});
 const status=await page.evaluate(()=>window.__swArenaDebug.getState());
 assert.equal(status.visual.mode,'original');
 assert.equal(status.visual.reaperFacingIndex,0);
 assert.equal(status.visual.loaded,13);
 const m=await (await page.request.get('http://127.0.0.1:5179/original-visual/manifest.json')).json();
 assert.equal(m.lot,'5D.8W');
 assert.equal(m.rootTimelineAnalysis.rootFrameCount,25);
 assert.equal(m.units.reaper_drone.states.ataque.distinctRenderedFrames,5);
 assert.equal(m.units.reaper_drone.states.quieto.distinctRenderedFrames,5);
 assert.equal(m.units.reaper_drone.states.muerte.distinctRenderedFrames,1);
 assert.equal(m.units.reaper_drone.states.picar.distinctRenderedFrames,1);
 assert.equal((await page.request.get('http://127.0.0.1:5179/original-visual/units/reaper_drone/picar.png')).status(),200);
 await page.screenshot({path:root+'/5d8w-reaper-facing-1.png',fullPage:true});
 const signature=async()=>page.evaluate(()=>{
  const d=document.querySelector('#battle').getContext('2d').getImageData(655,162,225,230).data;
  let result=2166136261>>>0;
  for(let i=0;i<d.length;i+=4){result=Math.imul(result^d[i],16777619)>>>0;
   result=Math.imul(result^d[i+1],16777619)>>>0;
   result=Math.imul(result^d[i+2],16777619)>>>0;
  }
  return result;
 });
 const before=await signature();
 await page.click('#reaper-facing');
 await page.waitForTimeout(100);
 assert.equal((await page.evaluate(()=>window.__swArenaDebug.getState().visual)).reaperFacingIndex,1);
 const after=await signature();
 assert.notEqual(before,after,'Root orientation frame must change rendered pixels');
 await page.screenshot({path:root+'/5d8w-reaper-facing-2.png',fullPage:true});
 for(let k=0;k<3;k++)await page.click('#reaper-facing');
 assert.equal((await page.evaluate(()=>window.__swArenaDebug.getState().visual)).reaperFacingIndex,4);
 await page.screenshot({path:root+'/5d8w-reaper-facing-5.png',fullPage:true});
 await page.click('#visual-mode');
 assert.equal((await page.evaluate(()=>window.__swArenaDebug.getState().visual)).mode,'vector');
 await page.screenshot({path:root+'/5d8w-vector-fallback.png',fullPage:true});
 await page.click('#visual-mode');
 await page.click('#auto');
 await page.click('#b-fire');
 for(let i=0;i<11;i++)await page.click('#step');
 let combat=await page.evaluate(()=>window.__swArenaDebug.getState());
 assert.ok(combat.units.reaperDrone.health<700,'Impact must lower HP after travel');
 await page.screenshot({path:root+'/5d8w-reaper-hit.png',fullPage:true});
 await page.click('#reset');
 await page.click('#run');
 await page.waitForFunction(()=>window.__swArenaDebug?.getState().winner==='bushwacker',{timeout:35000});
 combat=await page.evaluate(()=>window.__swArenaDebug.getState());
 assert.equal(combat.units.reaperDrone.health,0);
 await page.screenshot({path:root+'/5d8w-reaper-death.png',fullPage:true});
 assert.deepEqual(errors,[]);
 console.log('REAPER_DIRECTIONAL_BROWSER_5D8W',JSON.stringify({
  sprites:status.visual.loaded,rootFrames:25,
  orientationPixelsDiffer:before!==after,
  manualImpact:true,vectorFallback:true,winner:combat.winner,errors
 }));
}finally{await browser.close();}
