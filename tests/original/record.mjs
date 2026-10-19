#!/usr/bin/env node
/* Original-game browser recorder. Run real Flask Social Wars server first.
 * No original SWF, server module or save file is modified by this tool.
 * Local HTTP paths and explicit user markers only; request bodies excluded.
 */
import {chromium} from "../ruffle/node_modules/playwright/index.mjs";
import fs from "node:fs/promises";
import path from "node:path";
import {fileURLToPath} from "node:url";
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"../..");
const args=process.argv.slice(2);
const option=(name,def)=>{const i=args.indexOf(name);return i<0?def:args[i+1]};
const server=option("--server","http://127.0.0.1:5055").replace(/\/$/,"");
const url=new URL(server);
if(!["127.0.0.1","localhost"].includes(url.hostname))throw Error("Only local server allowed");
const duration=Number(option("--duration","90"));
if(!Number.isFinite(duration)||duration<1||duration>600)throw Error("Duration must be 1..600 seconds");
const out=path.resolve(option("--out",path.join(root,"dist","original-observation")));
const headless=args.includes("--headless");
const newVillage=args.includes("--create-test-village");
const recordVideo=!args.includes("--no-video");
const smokeMarkers=args.includes("--smoke-markers");
const unitProbe=args.includes("--unit-probe");
const introProbe=args.includes("--intro-probe");
const buttonEventProbe=args.includes("--button-event-probe");
if(buttonEventProbe&&(introProbe||unitProbe||smokeMarkers))throw Error("Choose one probe mode");
if(introProbe&&(unitProbe||smokeMarkers))throw Error("Choose one probe mode");
if(unitProbe&&smokeMarkers)throw Error("Use one probe mode at a time");
const ruffleRoot=path.join(root,"tests/ruffle/node_modules/@ruffle-rs/ruffle");
const observerPath=path.join(root,"tests/original/observer.js");
await fs.mkdir(out,{recursive:true});
const events=[],requests=[],errors=[],shots=[];
const startedWallClock=Date.now();
let browser,page,context,injected=false,serverVersion=null;
try{
 browser=await chromium.launch({headless,args:["--enable-webgl","--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"]});
 context=await browser.newContext({
   viewport:{width:1280,height:900},
   ...(recordVideo?{recordVideo:{dir:out,size:{width:1280,height:900}}}:{})
 });
 page=await context.newPage();
 await page.exposeFunction("__swHostRecord",async ev=>{
   events.push(ev);
   if(!unitProbe&&(ev.type==="begin_action"||ev.type==="end_action")){
     const file="event-"+String(shots.length+1).padStart(3,"0")+".png";
     try{await page.screenshot({path:path.join(out,file),timeout:5000});
       shots.push({file,event_index:events.length-1});}catch(e){errors.push("screenshot:"+String(e))}
   }
 });
 await page.route("**/__sw_ruffle/**",async route=>{
   const name=new URL(route.request().url()).pathname.slice("/__sw_ruffle/".length);
   if(!name||name.includes("..")||name.includes("\\")||name.startsWith("/")){
      await route.fulfill({status:400,body:"Invalid resource"});return;}
   const file=path.resolve(ruffleRoot,name);
   if(!file.startsWith(ruffleRoot+path.sep)){await route.fulfill({status:403,body:"Forbidden"});return}
   try{await route.fulfill({status:200,
     contentType:file.endsWith(".wasm")?"application/wasm":file.endsWith(".js")?"application/javascript":"application/octet-stream",
     body:await fs.readFile(file)});}
   catch{await route.fulfill({status:404,body:"Resource unavailable"})}
 });
 await page.route("**/__sw_observer/observer.js",async route=>
   route.fulfill({status:200,contentType:"application/javascript",body:await fs.readFile(observerPath)}));
 await page.route("**/play.html",async route=>{
   const response=await route.fetch();
   let body=await response.text();
   const inject='<script>window.RufflePlayer=window.RufflePlayer||{};window.RufflePlayer.config={publicPath:"/__sw_ruffle/",polyfills:true,autoplay:"on",unmuteOverlay:"hidden",logLevel:"warn"};</script>'+
     '<script src="/__sw_ruffle/ruffle.js"></script>'+
     '<script defer src="/__sw_observer/observer.js"></script>';
   if(body.includes("</head>")){body=body.replace("</head>",inject+"</head>");injected=true}
   await route.fulfill({response,body});
 });
 page.on("request",r=>{
   const u=new URL(r.url());
   if(u.origin===server&&(/\/static\/socialwars\/|\/dynamic\/menvswomen\//.test(u.pathname))){
     requests.push({method:r.method(),path:u.pathname,
       observed_at_ms:Date.now()-startedWallClock,wall_clock_ms:Date.now()});
     if(requests.length>2000)requests.shift();
   }
 });
 page.on("pageerror",e=>errors.push("pageerror:"+String(e).slice(0,400)));
 page.on("requestfailed",r=>{
   const u=new URL(r.url());if(u.origin===server)errors.push("requestfailed:"+u.pathname);
 });
 const health=await fetch(server+"/health",{signal:AbortSignal.timeout(6000)});
 if(!health.ok)throw Error("No original server /health: "+health.status);
 const healthJson=await health.json();serverVersion=healthJson.version;
 await page.goto(server+(newVillage?"/new.html":"/"),{waitUntil:"domcontentloaded",timeout:30000});
 // Flask redirects from /new.html to play.html. A second explicit
 // navigation guarantees the intercepted HTML is loaded in Playwright.
 if(newVillage) await page.goto(server+"/play.html",
                               {waitUntil:"domcontentloaded",timeout:30000});
 if(!headless)console.log("Use a janela do Chromium para entrar na vila e marcar as ações no painel lateral.");
 if(buttonEventProbe){
   // In the original AS3 class popups.PopupMissionInfo, btnOk listens to
   // MouseEvent.MOUSE_UP; test a real pointer down/hold/up at its visible
   // center on a 760x600 player. This test does not modify ActionScript.
   const player=page.locator("ruffle-embed").first();
   await page.waitForTimeout(9000);
   await player.evaluate(el=>{
      el.style.width="760px";el.setAttribute("width","760");
   });
   await page.waitForTimeout(1000);
   const box=await player.boundingBox();
   if(!box || box.width<700 || box.height<500)
      throw Error("Ruffle native stage not visible");
   const location={x:box.x+385,y:box.y+568};
   await page.screenshot({path:path.join(out,"event-before.png"),
                          timeout:25000,animations:"disabled"});
   await page.mouse.move(location.x,location.y,{steps:8});
   await page.waitForTimeout(600);
   await page.screenshot({path:path.join(out,"event-hover.png"),
                          timeout:25000,animations:"disabled"});
   await page.mouse.down();
   await page.waitForTimeout(380);
   await page.screenshot({path:path.join(out,"event-down.png"),
                          timeout:25000,animations:"disabled"});
   await page.mouse.up();
   await page.waitForTimeout(1700);
   await page.screenshot({path:path.join(out,"event-up.png"),
                          timeout:25000,animations:"disabled"});
   // First click may only dismiss the Ruffle hardware acceleration warning.
   // Now send an independent SECOND click to the actual Flash OK button.
   // Take a separate frame so the two UI effects cannot be conflated.
   await page.waitForTimeout(650);
   await page.mouse.move(location.x,location.y,{steps:2});
   await page.mouse.down();
   await page.waitForTimeout(280);
   await page.mouse.up();
   await page.waitForTimeout(2400);
   await page.screenshot({path:path.join(out,"event-second-up.png"),
                          timeout:25000,animations:"disabled"});
   await page.evaluate(()=>window.__swHostRecord?.({
     type:"intro_second_click_after_ruffle_overlay",
     action_execution_confirmed:false,
     visual_review_required:true,
     position_local:[385,568],wall_clock_ms:Date.now()
   }));
   const focus=await page.evaluate(()=>{
     const e=document.querySelector("ruffle-embed");
     return {active:document.activeElement?.tagName||null,
             shadowActive:e?.shadowRoot?.activeElement?.tagName||null,
             canvasCount:e?.shadowRoot?.querySelectorAll("canvas").length||0};
   });
   await page.evaluate(info=>window.__swHostRecord?.({
     type:"button_mouseup_event_probe",location_relative:[385,568],
     focus_after:info,action_execution_confirmed:false,
     internal_movieclip_id_confirmed:null,wall_clock_ms:Date.now()
   }),focus);
 }
 if(introProbe){
   // The 5D.8C video showed a "RESCUE YOUR COMRADE!" intro dialog that
   // covered the map. Test its visible OK button before probing units.
   const target=page.locator("ruffle-embed").first();
   await page.waitForTimeout(10000);
   await page.screenshot({path:path.join(out,"intro-before.png"),
                           timeout:25000,animations:"disabled"});
   // Original play.html sets width=1090 even though the SWF's actual
   // stage is 760x600. At native width, click hit testing is unambiguous.
   await target.evaluate(el=>{
     el.style.width="760px";
     el.setAttribute("width","760");
   });
   await page.waitForTimeout(1300);
   await page.screenshot({path:path.join(out,"intro-resized.png"),
                           timeout:25000,animations:"disabled"});
   const hitTest=await page.evaluate(()=>{
     const el=document.querySelector("ruffle-embed");
     const r=el.getBoundingClientRect(),x=r.x+380,y=r.y+568;
     const outer=document.elementFromPoint(x,y);
     const inner=el.shadowRoot?.elementFromPoint(x,y);
     return {
       player_bounds:{x:r.x,y:r.y,width:r.width,height:r.height},
       outer_target:outer?.tagName||null,
       shadow_target:inner?.tagName||null,
       outer_pointer_events:outer?getComputedStyle(outer).pointerEvents:null,
       shadow_pointer_events:inner?getComputedStyle(inner).pointerEvents:null,
       shadow_canvas_count:el.shadowRoot?.querySelectorAll("canvas").length||0,
       active_tag:document.activeElement?.tagName||null
     };
   });
   await page.evaluate(details=>window.__swHostRecord?.({
     type:"intro_hit_test",details,wall_clock_ms:Date.now(),
     confirmed_game_action:false
   }),hitTest);
   await page.evaluate(()=>window.__swHostRecord?.({
     type:"intro_dismiss_attempt",source:"5D.8C screenshot review",
     target:"Rescue Your Comrade dialog OK at 760px native width",
     unit_item_id:null,sprite_character_id:null,
     wall_clock_ms:Date.now(),player_x:380,player_y:568,
     gameplay_action_confirmed:false
   }));
   await target.click({position:{x:380,y:568},timeout:10000});
   await page.waitForTimeout(4000);
   await page.screenshot({path:path.join(out,"intro-after.png"),
                           timeout:25000,animations:"disabled"});
   // Keyboard fallback to check whether input is consumed by the Flash
   // virtual machine. Captured separately to avoid ambiguous attribution.
   await page.keyboard.press("Enter");
   await page.waitForTimeout(1500);
   await page.screenshot({path:path.join(out,"intro-after-enter.png"),
                           timeout:25000,animations:"disabled"});
   await page.evaluate(()=>window.__swHostRecord?.({
     type:"intro_dismiss_capture_complete",
     gameplay_action_confirmed:false,
     sprite_character_id:null,wall_clock_ms:Date.now()
   }));
 }
 if(unitProbe){
   // Controlled exploratory clicks on the ORIGINAL SWF canvas. The "other"
   // label is intentional: no action or SWF child sprite is assumed.
   const target=page.locator("ruffle-embed").first();
   const positions=[
     {name:"center_selection_probe",x:380,y:300},
     {name:"offset_destination_probe",x:430,y:320},
     {name:"offset_target_probe",x:470,y:270},
   ];
   for(const position of positions){
     await page.locator("#sw-action").selectOption("other");
     await page.locator("#sw-start").click();
     await page.waitForTimeout(180);
     const bidx=events.findLastIndex(e=>e.type==="begin_action");
     if(bidx<0)throw Error("Missing beginning of probe "+position.name);
     const prefix=String(shots.length+1).padStart(3,"0");
     const bfile="event-"+prefix+"-begin.png";
     await page.screenshot({path:path.join(out,bfile),timeout:25000,animations:"disabled"});
     shots.push({file:bfile,event_index:bidx});
     await page.evaluate(step=>window.__swHostRecord?.({
       type:"exploratory_probe",step:step.name,expected_game_action:null,
       unit_item_id:null,sprite_character_id:null,
       wall_clock_ms:Date.now(),location:{x:step.x,y:step.y}
     }),position);
     await target.click({position:{x:position.x,y:position.y},timeout:10000});
     await page.waitForTimeout(750);
     await page.locator("#sw-stop").click();
     await page.waitForTimeout(180);
     const eidx=events.findLastIndex(e=>e.type==="end_action");
     if(eidx<0)throw Error("Missing end of probe "+position.name);
     const efile="event-"+prefix+"-end.png";
     await page.screenshot({path:path.join(out,efile),timeout:25000,animations:"disabled"});
     shots.push({file:efile,event_index:eidx});
     await page.waitForTimeout(200);
   }
 }
 if(smokeMarkers){
   // Test only that the overlay works on the original client's page.
   // Kind 'other' is NOT an actual game action.
   await page.locator("#sw-action").selectOption("other");
   await page.locator("#sw-start").click();
   await page.waitForTimeout(500);
   await page.locator("ruffle-embed").click({position:{x:380,y:300}});
   await page.waitForTimeout(900);
   await page.locator("#sw-stop").click();
 }
 await page.waitForTimeout(duration*1000);
 const state=await page.evaluate(()=>({
   pathname:location.pathname,title:document.title,
   observer:Boolean(window.__swObserver),
   ruffle:Boolean(window.RufflePlayer),
   rufflePlayerCount:document.querySelectorAll("ruffle-player,ruffle-embed,ruffle-object").length,
   ruffleTags:[...document.querySelectorAll("ruffle-player,ruffle-embed,ruffle-object")].map(e=>e.tagName.toLowerCase()),
   embeds:document.querySelectorAll("embed").length,
   metadata:[...document.querySelectorAll("ruffle-player,ruffle-embed,ruffle-object")].map(e=>{try{return e.ruffle().metadata}catch{return null}})
 }));
 await page.screenshot({path:path.join(out,"final.png"),timeout:7000});
 const report={kind:"original-game-client-observation",serverVersion,
   state,injected,events,screenshots:shots,
   network_events:requests,
   request_paths:[...new Set(requests.map(r=>r.path))],request_count:requests.length,
   errors,limits:"User labels and clicks are not proof of which original character ID is rendered."};
 await fs.writeFile(path.join(out,"report.json"),JSON.stringify(report,null,2));
 if(recordVideo){
   // Chromium finalizes video on context close; no source game files are touched.
   await context.close();
   const video=page.video();
   if(video){
     await video.saveAs(path.join(out,"session.webm"));
     console.log("ORIGINAL_RUNTIME_VIDEO",path.join(out,"session.webm"));
   }
 }
 console.log("ORIGINAL_RUNTIME_REPORT",JSON.stringify({
   state,swfs:report.request_paths.filter(x=>x.endsWith(".swf")).slice(0,20),
   dynamic:report.request_paths.filter(x=>x.includes("/dynamic/")).slice(0,20),
   events:events.length,errors:errors.slice(0,5)}));
}finally{if(context){try{await context.close()}catch{}}if(browser)await browser.close()}