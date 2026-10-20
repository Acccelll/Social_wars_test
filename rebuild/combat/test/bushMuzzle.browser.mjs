import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir} from 'node:fs/promises';
await mkdir('test/screenshots',{recursive:true});
const browser=await chromium.launch({headless:true,args:[
 '--enable-webgl','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'
]});
try{
 const page=await browser.newPage({viewport:{width:1280,height:880},deviceScaleFactor:1});
 const errors=[];page.on('pageerror',x=>errors.push(x.message));
 const response=await page.goto('http://127.0.0.1:5179/muzzle',{waitUntil:'load'});
 assert.equal(response.status(),200);
 await page.waitForFunction(()=>typeof window.__swMuzzleDebug?.getSelected==='function');
 let selected=await page.evaluate(()=>window.__swMuzzleDebug.getSelected());
 assert.equal(selected.direction,3);
 assert.equal(selected.local.spriteId,716);
 assert.ok(Math.abs(selected.xPx-186.55)<1e-8);
 assert.ok(Math.abs(selected.yPx+182.5)<1e-8);
 const markers=await page.evaluate(()=>window.__swMuzzleDebug.getAll());
 assert.equal(markers.length,5);
 await page.screenshot({path:'test/screenshots/5d8y-bush-five-muzzles.png',fullPage:true});
 await page.getByRole('button',{name:'← Esquerda'}).click();
 selected=await page.evaluate(()=>window.__swMuzzleDebug.getSelected());
 assert.equal(selected.direction,7);
 assert.equal(selected.local.pose,3);
 assert.equal(selected.mirrored,true);
 assert.ok(Math.abs(selected.xPx+186.55)<1e-8);
 await page.screenshot({path:'test/screenshots/5d8y-bush-mirrored.png',fullPage:true});
 await page.getByRole('button',{name:'↑ Cima',exact:true}).click();
 selected=await page.evaluate(()=>window.__swMuzzleDebug.getSelected());
 assert.equal(selected.local.spriteId,643);
 await page.screenshot({path:'test/screenshots/5d8y-bush-pose-one.png',fullPage:true});
 const link=await page.locator('a[href="/arena"]').getAttribute('href');
 assert.equal(link,'/arena');
 await page.locator('a[href="/arena"]').click();
 await page.waitForFunction(()=>window.__swArenaDebug?.getState().visual?.ready===true,{timeout:20000});
 const arena=await page.evaluate(()=>window.__swArenaDebug.getState());
 assert.equal(arena.visual.loaded,13);
 assert.equal(arena.units.bushwacker.health,6500);
 assert.equal(arena.units.reaperDrone.health,700);
 assert.deepEqual(errors,[]);
 console.log('BUSH_MUZZLE_INSPECTOR_BROWSER_5D8Y',JSON.stringify({
  plottedMarkers:markers.length,mirroredDirection:7,
  sourceRootSprite:1092,unmodifiedArena:true,spriteAssets:13,jsErrors:errors
 }));
}finally{await browser.close();}
