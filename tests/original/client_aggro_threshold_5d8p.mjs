#!/usr/bin/env node
// 5D.8P: north/east acquisition comparison at 16–19 tiles, no manual unit clicks.
// Never inject commands; distinguish resource preloading from visible attack effects.
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
if(fixture.original_items!==40||!['north_16','north_17','north_18','north_19','east_16','east_17','east_18','east_19'].includes(fixture.scenario))throw Error('Unexpected 5D.8I fixture');
if(expected[0].index!==41||expected[0].item_id!==1358||expected[0].owner!==1||expected[1].index!==42||expected[1].item_id!==1376||expected[1].owner!==2)throw Error('Unit IDs or sides unexpected');
const out=path.resolve(opt("--out",path.join(root,"dist/aggro-threshold-5d8p")));
await fs.mkdir(out,{recursive:true});
const ruffleRoot=path.join(root,"tests/ruffle/node_modules/@ruffle-rs/ruffle");
const start=Date.now(),requests=[],otherApi=[],errors=[],shots=[],actions=[],stateSamples=[];
const fxRequests=[],fxResponses=[],timedShots=[],phases=[],relevantFx=[
  'p.bulletAirBig.swf','b.bazookaSmall.swf',
  'p.laserMassiveDrone.swf','b.laserBlue.swf'
];
let phase='setup';
function markPhase(name){
 phase=name;phases.push({phase:name,at_ms:Date.now()-start});
}
function classifyFx(u){
 const path=decodeURIComponent(u.pathname);
 const m=path.match(/(?:^|\/)fx\/([^/]+\.swf)$/i);
 if(!m)return null;
 const basename=m[1];
 return {basename,known_effect:relevantFx.some(x=>x.toLowerCase()===basename.toLowerCase())};
}
const safeRequestPath=u=>decodeURIComponent(u.pathname).slice(0,200);

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
 let bytes,data;
 for(let attempt=0;attempt<10;attempt++){
  bytes=await fs.readFile(path.join(saveDir,entries[0]));
  try {
   data=JSON.parse(bytes.toString("utf8"));
   break;
  }catch(e){
   if(!(e instanceof SyntaxError) || attempt===9)throw e;
   // Flask save persistence may temporarily be mid-write. Only retry the
   // read; do not change any game state or fabricate command responses.
   await new Promise(resolve=>setTimeout(resolve,90));
  }
 }
 const items=data.maps?.[0]?.items;
 if(!items)throw Error("Invalid original save");
 for(const s of expected){
  const u=items[String(s.index)];
  if(u&&(u[0]!==s.item_id||u[7]!==s.owner))throw Error('Seeded object identity changed');
 }
 return {hash:sha(bytes),items};
}
const screenshot=async(page,name)=>{
 await page.screenshot({path:path.join(out,name),timeout:25000,animations:"disabled"});
 shots.push(name);
 timedShots.push({file:name,at_ms:Date.now()-start,phase});
};
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
  try{
   const u=new URL(r.url());
   if(u.origin!==host)return;
   const fx=classifyFx(u);
   if(fx && fxRequests.length<500){
    fxRequests.push({at_ms:Date.now()-start,phase,method:r.method(),
      resource:fx.basename,known_effect:fx.known_effect,source:'browser_request',
      path:safeRequestPath(u)});
   }
   if(u.pathname==='/dynamic/menvswomen/srvsexwars/command.php'){
    requests.push({at_ms:Date.now()-start,phase,method:r.method(),commands:parsed(r),source:'original_browser_client'});
   }else if(u.pathname.startsWith('/dynamic/menvswomen/srvsexwars/')){
    otherApi.push({at_ms:Date.now()-start,method:r.method(),path:u.pathname});
   }
  }catch{errors.push('request_observer_failed')}
 });
 page.on('response',response=>{
  try{
   const u=new URL(response.url());
   if(u.origin!==host)return;
   const fx=classifyFx(u);
   if(fx&&fxResponses.length<500){
    fxResponses.push({at_ms:Date.now()-start,phase,resource:fx.basename,
                      http_status:response.status(),path:safeRequestPath(u)});
   }
  }catch{errors.push('fx_response_observer_failed')}
 });
 page.on("pageerror",()=>errors.push("page_error"));
 page.on("requestfailed",r=>{try{if(new URL(r.url()).origin===host)errors.push("local_request_failed")}catch{}});
 const h=await fetch(host+"/health",{signal:AbortSignal.timeout(7000)});
 if(!h.ok)throw Error("Original server unavailable");
 markPhase('new_page');
 await page.goto(host+"/new.html",{waitUntil:"domcontentloaded",timeout:30000});
 markPhase('original_swf_boot');
 await page.goto(host+"/play.html",{waitUntil:"domcontentloaded",timeout:30000});
 await page.waitForTimeout(9000);
 const player=page.locator("ruffle-embed").first();
 if(await player.count()!==1)throw Error("Ruffle stage missing");
 await player.evaluate(el=>{el.style.width="760px";el.setAttribute("width","760")});
 await page.waitForTimeout(1000);
 const b=await player.boundingBox();
 if(!b||b.width<700||b.height<500)throw Error("SWF stage invisible");
 markPhase('boot_complete_pre_modal');
 const before=await currentSave();
 await screenshot(page,"01-dialog.png");
 for(let n=1;n<=2;n++){
  markPhase('dismiss_modal_'+n);
  await page.mouse.click(b.x+385,b.y+568,{delay:280});
  if(n===1){
   await page.waitForTimeout(850);
  }else{
   // Closely spaced snapshots of the window where native auto-combat
   // previously emitted its kill *before* any unit-selection click.
   for(const [delta,wait] of [[350,350],[1100,750],[2300,1200]]){
    await page.waitForTimeout(wait);
    await screenshot(page,'modal-2-after-'+delta+'ms.png');
   }
  }
  await screenshot(page,"0"+(n+1)+"-ok-"+n+".png");
 }
 markPhase('control_no_unit_clicks');
 await screenshot(page,'control-first.png');
 const initialTarget=before.items[String(expected[1].index)];
 if(!initialTarget)throw Error('Enemy target absent before control');
 let after=before,attempts=0;
 const observeStart=Date.now()-start;
 // Time-limited observational window; snapshots are conditional and
 // no user unit clicks, movement calls or synthetic POSTs are performed.
 let nextScreenshotAt=0,firstTargetMissingAt=null;
 for(let t=0;t<=16;t++){
  const now=Date.now()-start;
  const view=await currentSave();
  const attacker=view.items[String(expected[0].index)];
  const target=view.items[String(expected[1].index)];
  const seenKill=requests.flatMap(r=>r.commands).some(
    c=>c.action==='kill'&&c.object_reference===42);
  stateSamples.push({
    at_ms:now,elapsed_since_control_ms:now-observeStart,
    attacker_tile:attacker?attacker.slice(1,3):null,
    target_tile:target?target.slice(1,3):null,
    attacker_exists:!!attacker,target_exists:!!target,
    native_kill_seen:seenKill
  });
  if(!target && firstTargetMissingAt===null)firstTargetMissingAt=now;
  if(t===0||t===5||t===16||(!target&&nextScreenshotAt<16)){
     await screenshot(page,'distance-'+String(t).padStart(2,'0')+'.png');
     nextScreenshotAt=16;
  }
  if(!target&&seenKill&&t>=1)break;
  if(t<16)await page.waitForTimeout(1200);
 }
 after=await currentSave();
 await page.waitForTimeout(1200);
 markPhase('post_combat');
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
 const firstEnemyClickAt=actions[0]?.enemy_click_at_ms??null;
 const preClickFx=fxRequests.filter(r=>firstEnemyClickAt!==null&&r.at_ms<firstEnemyClickAt);
 const postClickFx=fxRequests.filter(r=>firstEnemyClickAt!==null&&r.at_ms>=firstEnemyClickAt);
 const fxByResource=Object.fromEntries(relevantFx.map(file=>[file,{
   pre_click_requests:preClickFx.filter(x=>x.resource.toLowerCase()===file.toLowerCase()).length,
   post_click_requests:postClickFx.filter(x=>x.resource.toLowerCase()===file.toLowerCase()).length,
   response_statuses:fxResponses.filter(x=>x.resource.toLowerCase()===file.toLowerCase()).map(x=>x.http_status)
 }]));
 const attackObserved=combatActions.some(c=>['kill','sell','end_attack'].includes(c.action));
 const report={
  lot:'5D.8P-two-axis-aggro',scenario:fixture.scenario,
  manhattan_distance_tiles:fixture.manhattan_distance_tiles,axis:fixture.axis,
  control_no_unit_clicks:true,manual_unit_click_count:0,
  original_swf_untouched:true,
  no_synthetic_combat_posts:true,source:'Original SWF input only; PlayerID 2 real enemy (3 was neutral)',
  fixture_seeded_units:expected,modal_ok_clicks:2,
  original_stage:{x:Math.round(b.x),y:Math.round(b.y),width:Math.round(b.width),height:Math.round(b.height)},
  attempts,probes:actions,control_start_at_ms:observeStart,
  native_command_kill_times_ms:requests.filter(r=>r.commands.some(c=>c.action==='kill'&&c.object_reference===42)).map(r=>r.at_ms),
  native_move_commands:requests.flatMap(r=>r.commands).filter(c=>c.action==='move'),
  state_samples:stateSamples,observed_first_missing_target_at_ms:firstTargetMissingAt,
  initial_attacker_tile:expected[0].tile,initial_hostile_tile:expected[1].tile,
  dynamic_visual_attack_verified:false,
  request_count:requests.length,requests,other_api_paths:otherApi,
  command_names:allCommands.map(c=>c.action),combat_actions:combatActions,
  native_combat_command_seen:attackObserved,
  original_enemy_player_id:2,previous_5d8i_side_3_was_neutral:true,
  target_object_changed:targetChanged,
  target_removed_from_save:!after.items[String(expected[1].index)],
  unit_summaries:unitSummaries,
  changed_existing_map_objects:changes,
  save_changed:before.hash!==after.hash,before_sha256:before.hash,after_sha256:after.hash,
  visual_attack_confirmed:false,damage_amount_confirmed:false,
  fx_http_requests:fxRequests,fx_http_responses:fxResponses,
  fx_requests_pre_first_enemy_click:preClickFx.length,
  fx_requests_after_first_enemy_click:postClickFx.length,
  fx_requests_with_zero_unit_clicks:fxRequests.length,
  fx_by_resource:fxByResource,
  timing_phases:phases,shot_timestamps:timedShots,
  first_enemy_click_at_ms:firstEnemyClickAt,
  interpretation_rules:{
    pre_attack_loading:'Any FX requested before the first enemy click is a preload / initialization candidate, not a shot confirmation.',
    post_attack_loading:'A network request after an enemy click is evidence of loading only, not proof the particle was drawn.',
    missing_post_attack_get:'Cached FX or preloaded SWF may render without new network GET; no request does not imply no projectile.',
    status:'Runtime FX per-frame identity is not exposed by HTTP instrumentation.'},
  screenshots:shots,errors,
  limits:'The original server does not expose each hit as a persisted attack command. No image assertion is automated. Any native combat must be correlated manually with the recording.'
 };
 await fs.writeFile(path.join(out,"report.json"),JSON.stringify(report,null,2)+"\n");
 console.log('AUTO_AGGRO_THRESHOLD_5D8P',JSON.stringify({
  scenario:fixture.scenario,tile_distance:fixture.manhattan_distance_tiles,
  manual_unit_clicks:0,control_samples:stateSamples.length,axis:fixture.axis,
  native_kill:combatActions.some(c=>c.action==='kill'&&c.object_reference===42),
  kill_at_ms:requests.filter(r=>r.commands.some(c=>c.action==='kill'&&c.object_reference===42)).map(r=>r.at_ms),
  target_removed:report.target_removed_from_save,
  attacker_tiles:[...new Set(stateSamples.map(x=>JSON.stringify(x.attacker_tile)))],
  target_tiles:[...new Set(stateSamples.map(x=>JSON.stringify(x.target_tile)))],
  errors
 }));
}finally{
 if(context){await context.close().catch(()=>{});if(page?.video())await page.video().saveAs(path.join(out,"session.webm")).catch(()=>{})}
 if(browser)await browser.close().catch(()=>{});
}
