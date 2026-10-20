/** Local-only demo server for independent rebuilt combat. */
import http from 'node:http';
import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=path.dirname(fileURLToPath(import.meta.url));
const host='127.0.0.1',port=Number(process.env.PORT||5179);
const types={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json; charset=utf-8','.png':'image/png'};
const allow=new Map([
 ['/','demo/index.html'],['/arena','demo/arena.html'],['/muzzle','demo/muzzle.html'],['/demo/muzzle.js','demo/muzzle.js'],['/demo/main.js','demo/main.js'],['/demo/arena.js','demo/arena.js'],['/demo/originalVisuals.js','demo/originalVisuals.js'],
 ['/dist/index.js','dist/index.js'],['/dist/model.js','dist/model.js'],
 ['/dist/healthBar.js','dist/healthBar.js'],['/dist/rng.js','dist/rng.js'],
 ['/dist/scene.js','dist/scene.js'],['/dist/unitCatalog.js','dist/unitCatalog.js'],['/dist/originalDirection.js','dist/originalDirection.js'],['/dist/bushMuzzle.js','dist/bushMuzzle.js']
]);
http.createServer(async(req,res)=>{
 const urlPath=new URL(req.url??'/',`http://${host}:${port}`).pathname;
 let file=allow.get(urlPath);
 // Closed list of optional original visual files. No directory traversal.
 if(!file&&/^\/original-visual\/(manifest\.json|(?:units\/(?:bushwacker|reaper_drone)\/(?:quieto|andar|ataque|muerte|picar)|fx\/(?:bullet|bazooka|laser|laserBlue))\.png)$/.test(urlPath))file=urlPath.slice(1);
 if(!file){res.writeHead(404);res.end('not found');return;}
 try{
  const data=await readFile(path.join(root,file));
  res.writeHead(200,{'content-type':types[path.extname(file)]||'application/octet-stream',
   'x-content-type-options':'nosniff','cache-control':'no-store'});res.end(data);
 }catch{res.writeHead(500);res.end('build not found');}
}).listen(port,host,()=>console.log(`Independent combat demo: http://${host}:${port}`));
