import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdir} from 'node:fs/promises';
import path from 'node:path';
const dir=path.resolve('test/screenshots');
await mkdir(dir,{recursive:true});
const browser=await chromium.launch({headless:true,args:['--enable-webgl','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
let pageErrors=[];
try{
 const page=await browser.newPage({viewport:{width:1360,height:930},deviceScaleFactor:1});
 page.on('pageerror',e=>pageErrors.push(e.message));
 const response=await page.goto('http://127.0.0.1:5179/arena',{waitUntil:'load',timeout:30000});
 assert.equal(response.status(),200);
 await page.locator('#battle').waitFor();
 await page.waitForFunction(()=>typeof window.__swArenaDebug?.getState==='function',{timeout:10000});
 let state=await page.evaluate(()=>window.__swArenaDebug.getState());
 assert.equal(state.frame,0);
 assert.equal(state.units.bushwacker.health,6500);
 assert.equal(state.units.reaperDrone.health,700);
 assert.ok((await page.locator('body').textContent()).includes('Arena de combate'));
 assert.equal(await page.locator('#battle').evaluate(el=>el.width),960);
 await page.screenshot({path:path.join(dir,'arena-ready.png'),fullPage:true});
 const backdrop=await page.evaluate(()=>[...document.querySelector('#battle').getContext('2d').getImageData(12,12,1,1).data]);
 assert.equal(backdrop[3],255);
 // Manual projectile, discrete frames and hit before death.
 await page.click('#auto'); // switch off auto firing
 await page.click('#b-fire');
 state=await page.evaluate(()=>window.__swArenaDebug.getState());
 assert.equal(state.units.bushwacker.shotsFired,1);
 assert.equal(state.units.reaperDrone.health,700);
 for(let i=0;i<11;i++)await page.click('#step');
 state=await page.evaluate(()=>window.__swArenaDebug.getState());
 assert.ok(state.units.reaperDrone.health<700);
 assert.equal(state.units.bushwacker.health,6500);
 assert.ok((await page.locator('#events').textContent()).includes('recebeu'));
 await page.screenshot({path:path.join(dir,'arena-hit-manual.png'),fullPage:true});
 await page.click('#reset');
 await page.click('#run');
 await page.waitForFunction(()=>window.__swArenaDebug?.getState().winner==='bushwacker',{timeout:35000});
 state=await page.evaluate(()=>window.__swArenaDebug.getState());
 assert.equal(state.units.reaperDrone.health,0);
 assert.equal(state.winner,'bushwacker');
 assert.ok(state.units.bushwacker.shotsFired>=5);
 assert.ok((await page.locator('#status').textContent()).includes('Vitória'));
 await page.screenshot({path:path.join(dir,'arena-victory.png'),fullPage:true});
 assert.deepEqual(pageErrors,[]);
 console.log('ARENA_2D_BROWSER_5D8U',JSON.stringify({
   first_frame:0,manual_hit:true,auto_win:state.winner,
   bush_shots:state.units.bushwacker.shotsFired,
   enemy_hp_at_finish:state.units.reaperDrone.health,
   canvas_valid:true,errors:pageErrors,
   screenshots:['arena-ready.png','arena-hit-manual.png','arena-victory.png']
 }));
}finally{await browser.close();}
