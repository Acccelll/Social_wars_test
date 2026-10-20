#!/usr/bin/env node
// 5D.8I: native client interaction with one friendly and one hostile test unit. No injected attack POSTs.
// Never persist request bodies, cookies, credentials, user IDs, or whole saves.
import {chromium} from "../ruffle/node_modules/playwright/index.mjs";
import fs from "node:fs/promises";
import path from "node:path";
import crypto from "node:crypto";
import {fileURLToPath} from "node:url";
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"../..");
const args=process.argv.slice(2);
const opt=(k,d)=>{const i=args.indexOf(k);return i<0?d:args[i+1]};
const host=opt("--server","http://127.0.0.1:5055").replace(/\/$/,"");
const url=new URL(host);
if(url.protocol!=="http:"||!["localhost","127.0.0.1"].includes(url.hostname)||!url.port)throw Error("Loopback only");
const saveDir=path.resolve(opt("--save-dir",""));
const fixture=JSON.parse(await fs.readFile(opt("--fixture",""),"utf8"));
const expected=fixture.seeded_units;
if(!Array.isArray(expected)||expected.length!==2)throw Error('Exactly two seeded units required');
if(fixture.original_items!==40||!['near_east','near_north','near_west'].includes(fixture.scenario))throw Error('Unexpected 5D.8I fixture');
if(expected[0].index!==41||expected[0].item_id!==1358||expected[0].owner!==1||expected[1].index!==42||expected[1].item_id!==1376||expected[1].owner!==3)throw Error('Unit IDs or sides unexpected');
const out=path.resolve(opt("--out",path.join(root,"dist/native-combat-5d8i")));
await fs.mkdir(out,{recursive:true});
const ruffleRoot=path.join(root,"tests/ruffle/node_modules/@ruffle-rs/ruffle");
const start=Date.now(), requests=[],otherApi=[],errors=[],shots=[],actions=[];
const sha=b=>crypto.createHash("sha256").update(b).digest("hex");
function parsed(r){
 if(r.method()!=="POST")return [];
 try{
  const raw=new URLSearchParams(r.postData()||"").get("data")||"";
  const data=JSON.parse(raw.slice(raw.indexOf(";")+1));
  return (Array.isArray(data.commands)?data.commands:[]).map(cmd=>{
   const action=typeof cmd?.[1]==="string"?cmd[1]:"unknown";
   const a=Array.isArray(cmd?.[2])?cmd[2]:[];
   return {action,...(action==='move'?{
    map_index:Number.isInteger(a[0])?a[0]:null,
    destination:a.slice(1,3).length===2&&a.slice(1,3).every(Number.isInteger)?a.slice(1,3):null
   }:['sell','kill','kill_iid','batch_remove','orient'].includes(action)?{
    object_reference:typeof a[0]==='number'?a[0]:null,
    reason:typeof a[1]==='string'&&a[1].length<=40?a[1]:null
   }:{})};
  });
 }catch{return []}
}
async function currentSave(){
 const entries=(await fs.readdir(saveDir)).filter(n=>n.endsWith(".save.json"));
 if(entries.length!==1)throw Error("Expected exactly one disposable save; got "+entries.length);
 const bytes=await fs.readFile(path.join(saveDir,entries[0]));
 const data=JSON.parse(bytes.toString("utf8")), items=data.maps?.[0]?.items;
 if(!items)throw Error("Invalid original save");
 for(const s of expected){
  const u=items[String(s.index)];
  if(u&&(u[0]!==s.item_id||u[7]!==s.owner))throw Error('Seeded object identity changed');
 }
 return {hash:sha(bytes),items};
}
const screenshot=async(page,name)=>{await page.screenshot({path:path.join(out,name),timeout:25000,animations:"disabled"});shots.push(name)};
if((await fs.readdir(saveDir)).some(n=>n.endsWith(".save.json")))throw Error("Refusing to use populated save folder");
let browser,context,page;
try{
 browser=await chromium.launch({headless:true,args:["--enable-webgl","--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"]});
 context=await browser.newContext({viewport:{width:1280,height:900},recordVideo:{dir:out,size:{width:1280,height:900}}});
 page=await context.newPage();
 await page.route("**/__sw_ruffle/**",async route=>{
  const name=new URL(route.request().url()).pathname.slice("/__sw_ruffle/".length);
  if(!name||name.includes("..")||name.includes("\\")||name.startsWith("/"))return route.fulfill({status:400,body:"Invalid"});
  const file=path.resolve(ruffleRoot,name);
  if(!file.startsWith(ruffleRoot+path.sep))return route.fulfill({status:403,body:"Forbidden"});
  try{await route.fulfill({status:200,contentType:file.endsWith(".wasm")?"application/wasm":file.endsWith(".js")?"application/javascript":"application/octet-stream",body:await fs.readFile(file)})}
  catch{await route.fulfill({status:404,body:"Not found"})}
 });
 await page.route("**/play.html",async route=>{
  const response=await route.fetch();let body=await response.text();
  const inject='<script>window.RufflePlayer=window.RufflePlayer||{};window.RufflePlayer.config={publicPath:"/__sw_ruffle/",polyfills:true,autoplay:"on",unmuteOverlay:"hidden",logLevel:"warn"};</script><script src="/__sw_ruffle/ruffle.js"></script>';
  if(!body.includes("</head>"))throw Error("Unexpected play.html");
  await route.fulfill({response,body:body.replace("</head>",inject+"</head>")});
 });
 page.on('request',r=>{
  try{const u=new URL(r.url());if(u.origin!==host)return;
   if(u.pathname==='/dynamic/menvswomen/srvsexwars/command.php'){
    requests.push({at_ms:Date.now()-start,method:r.method(),commands:parsed(r),source:'original_browser_client'});
   }else if(u.pathname.startsWith('/dynamic/menvswomen/srvsexwars/')){
    otherApi.push({at_ms:Date.now()-start,method:r.method(),path:u.pathname});
   }
  }catch{errors.push('request_observer_failed')}
 });
 page.on("pageerror",()=>errors.push("page_error"));
 page.on("requestfailed",r=>{try{if(new URL(r.url()).origin===host)errors.push("local_request_failed")}catch{}});
 const h=await fetch(host+"/health",{signal:AbortSignal.timeout(7000)});
 if(!h.ok)throw Error("Original server unavailable");
 await page.goto(host+"/new.html",{waitUntil:"domcontentloaded",timeout:30000});
 await page.goto(host+"/play.html",{waitUntil:"domcontentloaded",timeout:30000});
 await page.waitForTimeout(9000);
 const player=page.locator("ruffle-embed").first();
 if(await player.count()!==1)throw Error("Ruffle stage missing");
 await player.evaluate(el=>{el.style.width="760px";el.setAttribute("width","760")});
 await page.waitForTimeout(1000);
 const b=await player.boundingBox();
 if(!b||b.width<700||b.height<500)throw Error("SWF stage invisible");
 const before=await currentSave();
 await screenshot(page,"01-dialog.png");
 for(let n=1;n<=2;n++){
  await page.mouse.click(b.x+385,b.y+568,{delay:280});
  await page.waitForTimeout(n===1?850:2200);
  await screenshot(page,"0"+(n+1)+"-ok-"+n+".png");
 }
 const probes=[
  // Test coordinates are local to the original 760x600 SWF stage.
  // All moves or attacks are performed with real pointer clicks by Playwright.
  [[380,415],[440,385]],[[380,415],[460,420]],[[380,415],[500,365]],
  [[255,452],[440,315]],[[380,415],[375,355]],[[380,415],[395,310]],
  [[255,452],[510,405]],[[380,415],[330,390]],[[380,415],[315,300]],
  [[255,452],[540,350]],[[380,415],[260,430]],[[380,415],[565,290]],
  [[380,415],[570,420]],[[255,452],[600,365]]
 ];
 const initialTarget=before.items[String(expected[1].index)];
 if(!initialTarget)throw Error('Enemy target absent before input');
 let after=before,attempts=0;
 for(let i=0;i<probes.length;i++){
  const [unit,dest]=probes[i],n=String(i+1).padStart(2,'0');
  const beforeCount=requests.length;
  const savedBefore=await currentSave();
  await player.click({position:{x:unit[0],y:unit[1]},timeout:10000});
  await page.waitForTimeout(420);
  if(i<4)await screenshot(page,'probe-'+n+'-selected.png');
  await player.click({position:{x:dest[0],y:dest[1]},timeout:10000});
  await page.waitForTimeout(300);
  if(i<5)await screenshot(page,'probe-'+n+'-after-300ms.png');
  await page.waitForTimeout(1600);
  if(i<5)await screenshot(page,'probe-'+n+'-after-1900ms.png');
  attempts++;
  after=await currentSave();
  const stepCommands=requests.slice(beforeCount).flatMap(r=>r.commands);
  actions.push({
    probe:attempts,unit_local:unit,target_local:dest,
    commands:stepCommands,
    target_exists:!!after.items[String(expected[1].index)],
    target_object_changed:JSON.stringify(savedBefore.items[String(expected[1].index)])!==JSON.stringify(after.items[String(expected[1].index)]),
    attacker_tile:after.items[String(expected[0].index)]?.slice(1,3)||null
  });
  const decisive=stepCommands.some(c=>['kill','sell','end_attack'].includes(c.action));
  if(decisive || !after.items[String(expected[1].index)])break;
 }
 await page.waitForTimeout(1200);
 await screenshot(page,"final.png");
 after=await currentSave();
 const allCommands=requests.flatMap(r=>r.commands);
 const changes=Object.keys(before.items).filter(k=>JSON.stringify(before.items[k])!==JSON.stringify(after.items[k]));
 const objectView=(items,s)=>{
  const r=items[String(s.index)];
  if(!r)return {exists:false};
  const meta=r[6]&&typeof r[6]==='object'?r[6]:{};
  const healthKeys=Object.fromEntries(Object.entries(meta).filter(([k,v])=>/hp|life|health|damage|injur/i.test(k)&&['number','string','boolean'].includes(typeof v)).slice(0,12));
  return {exists:true,item_id:r[0],tile:r.slice(1,3),owner:r[7],health_keys:healthKeys,meta_keys:Object.keys(meta).slice(0,15)};
 };
 const unitSummaries=expected.map(s=>({
   name:s.name,index:s.index,item_id:s.item_id,
   before:objectView(before.items,s),after:objectView(after.items,s),
   changed:JSON.stringify(before.items[String(s.index)])!==JSON.stringify(after.items[String(s.index)])
 }));
 const combatActions=allCommands.filter(c=>['kill','sell','kill_iid','end_attack','end_quest','batch_remove'].includes(c.action));
 const targetChanged=unitSummaries[1].changed;
 const attackObserved=combatActions.some(c=>['kill','sell','end_attack'].includes(c.action));
 const report={
  lot:'5D.8I',scenario:fixture.scenario,original_swf_untouched:true,
  no_synthetic_combat_posts:true,source:'Original SWF input only',
  fixture_seeded_units:expected,modal_ok_clicks:2,
  original_stage:{x:Math.round(b.x),y:Math.round(b.y),width:Math.round(b.width),height:Math.round(b.height)},
  attempts,probes:actions,
  request_count:requests.length,requests,other_api_paths:otherApi,
  command_names:allCommands.map(c=>c.action),combat_actions:combatActions,
  native_combat_command_seen:attackObserved,
  target_object_changed:targetChanged,
  target_removed_from_save:!after.items[String(expected[1].index)],
  unit_summaries:unitSummaries,
  changed_existing_map_objects:changes,
  save_changed:before.hash!==after.hash,before_sha256:before.hash,after_sha256:after.hash,
  visual_attack_confirmed:false,damage_amount_confirmed:false,
  screenshots:shots,errors,
  limits:'The original server does not expose each hit as a persisted attack command. No image assertion is automated. Any native combat must be correlated manually with the recording.'
 };
 await fs.writeFile(path.join(out,"report.json"),JSON.stringify(report,null,2)+"\n");
 console.log('NATIVE_COMBAT_5D8I',JSON.stringify({scenario:fixture.scenario,attempts,requests:requests.length,combat:combatActions.map(c=>c.action),target_changed:targetChanged,target_removed:report.target_removed_from_save,errors}));
}finally{
 if(context){await context.close().catch(()=>{});if(page?.video())await page.video().saveAs(path.join(out,"session.webm")).catch(()=>{})}
 if(browser)await browser.close().catch(()=>{});
}
