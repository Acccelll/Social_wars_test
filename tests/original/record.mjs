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
   if(ev.type==="begin_action"||ev.type==="end_action"){
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
 if(smokeMarkers){
   // Test only that the overlay works on the original client's page.
   // Kind 'other' is NOT an actual game action.
   await page.locator("#sw-action").selectOption("other");
   await page.locator("#sw-start").click();
   await page.waitForTimeout(350);
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