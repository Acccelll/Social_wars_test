#!/usr/bin/env node
// 5D.8G: Only browser mouse input can issue move; original server on loopback.
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
if(!Array.isArray(expected)||expected.length!==4)throw Error("Unexpected fixture");
const out=path.resolve(opt("--out",path.join(root,"dist/client-move-5d8g")));
await fs.mkdir(out,{recursive:true});
const ruffleRoot=path.join(root,"tests/ruffle/node_modules/@ruffle-rs/ruffle");
const start=Date.now(), requests=[],errors=[],shots=[],actions=[];
const sha=b=>crypto.createHash("sha256").update(b).digest("hex");
function parsed(r){
 if(r.method()!=="POST")return [];
 try{
  const raw=new URLSearchParams(r.postData()||"").get("data")||"";
  const data=JSON.parse(raw.slice(raw.indexOf(";")+1));
  return (Array.isArray(data.commands)?data.commands:[]).map(cmd=>{
   const action=typeof cmd?.[1]==="string"?cmd[1]:"unknown";
   const a=Array.isArray(cmd?.[2])?cmd[2]:[];
   return {action,...(action==="move"?{
    map_index:Number.isInteger(a[0])?a[0]:null,
    destination:a.slice(1,3).length===2&&a.slice(1,3).every(Number.isInteger)?a.slice(1,3):null
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
  if(!u||u[0]!==s.item_id||u[7]!==s.player_id)throw Error("Test fixture not present");
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
 page.on("request",r=>{
  try{const u=new URL(r.url());if(u.origin===host&&u.pathname==="/dynamic/menvswomen/srvsexwars/command.php"){
   requests.push({at_ms:Date.now()-start,method:r.method(),commands:parsed(r),source:"original_browser_client"});
  }}catch{errors.push("request_observer_failed")}
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
  [[190,350],[560,270]],[[380,415],[570,290]],[[255,452],[490,280]],
  [[375,370],[620,320]],[[180,425],[590,380]],[[450,445],[500,260]],
  [[390,470],[555,335]],[[275,400],[675,240]],[[230,350],[505,385]],
  [[330,420],[610,220]],[[160,465],[635,285]],[[425,350],[530,370]]
 ];
 let after=before,attempts=0;
 for(let i=0;i<probes.length;i++){
  const [unit,dest]=probes[i],n=String(i+1).padStart(2,"0");
  const was=requests.length;
  await player.click({position:{x:unit[0],y:unit[1]},timeout:10000});
  await page.waitForTimeout(600);
  await screenshot(page,"probe-"+n+"-selected.png");
  await player.click({position:{x:dest[0],y:dest[1]},timeout:10000});
  await page.waitForTimeout(1500);
  await screenshot(page,"probe-"+n+"-destination.png");
  attempts++;
  actions.push({probe:attempts,unit_local:unit,dest_local:dest,requests_since:requests.length-was});
  after=await currentSave();
  const moved=expected.some(s=>{
   const a=before.items[String(s.index)],c=after.items[String(s.index)];
   return a[1]!==c[1]||a[2]!==c[2];
  });
  if(moved&&requests.some(r=>r.commands.some(c=>c.action==="move")))break;
 }
 await page.waitForTimeout(1200);
 await screenshot(page,"final.png");
 after=await currentSave();
 const changes=Object.keys(before.items).filter(k=>JSON.stringify(before.items[k])!==JSON.stringify(after.items[k]));
 const moved=expected.filter(s=>{
  const a=before.items[String(s.index)],c=after.items[String(s.index)];
  return a[1]!==c[1]||a[2]!==c[2];
 }).map(s=>({index:s.index,unit_item_id:s.item_id,from:before.items[String(s.index)].slice(1,3),to:after.items[String(s.index)].slice(1,3)}));
 const browserMoves=requests.flatMap(r=>r.commands.filter(c=>c.action==="move"));
 const matched=moved.some(m=>browserMoves.some(c=>c.map_index===m.index&&JSON.stringify(c.destination)===JSON.stringify(m.to)));
 const report={
  lot:"5D.8G",original_swf_untouched:true,source:"original browser mouse clicks on isolated Flask and Ruffle",
  no_synthetic_move_posts:true,modal_ok_clicks:2,modal_dismissal_independently_reviewed:false,
  original_stage:{x:Math.round(b.x),y:Math.round(b.y),width:Math.round(b.width),height:Math.round(b.height)},
  attempts,probes:actions,request_count:requests.length,requests,
  browser_move_count:browserMoves.length,moved_seeded_units:moved,
  changed_map_object_count:changes.length,
  save_changed:before.hash!==after.hash,before_sha256:before.hash,after_sha256:after.hash,
  browser_move_and_save_persistence_matched:matched,
  animation_visual_confirmed:false,sprite_define_id_confirmed:null,
  screenshots:shots,errors,limits:"Screenshots and video require review; HTTP move plus save change alone is not animation proof."
 };
 await fs.writeFile(path.join(out,"report.json"),JSON.stringify(report,null,2)+"\n");
 console.log("CLIENT_MOVE_5D8G",JSON.stringify({attempts,requests:requests.length,moves:browserMoves.length,moved:moved.length,matched,errors}));
}finally{
 if(context){await context.close().catch(()=>{});if(page?.video())await page.video().saveAs(path.join(out,"session.webm")).catch(()=>{})}
 if(browser)await browser.close().catch(()=>{});
}
