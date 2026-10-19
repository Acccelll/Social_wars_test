import {chromium} from "../ruffle/node_modules/playwright/index.mjs";
import path from "node:path";
import {fileURLToPath} from "node:url";
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"../..");
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage();
 const events=[];
 await page.exposeFunction("__swHostRecord",x=>events.push(x));
 await page.setContent('<object id="fake" style="width:760px;height:500px;display:block"></object>');
 await page.addScriptTag({path:path.join(root,"tests/original/observer.js")});
 await page.locator("#sw-action").selectOption("movement");
 await page.locator("#sw-start").click();
 await page.locator("#fake").click({position:{x:35,y:44}});
 await page.locator("#sw-stop").click();
 await page.waitForTimeout(100);
 const report=await page.evaluate(()=>window.__swObserver.snapshot());
 const kinds=report.events.map(e=>e.type);
 if(!["observer_ready","begin_action","pointer","end_action"].every(x=>kinds.includes(x)))
   throw Error("Missing events: "+JSON.stringify(kinds));
 if(!report.user_labels_only)throw Error("False runtime inference");
 console.log("OBSERVER_TEST_SUCCESS",JSON.stringify({events:events.length,kinds}));
}finally{await browser.close()}