/** Local-only demo server for independent rebuilt combat. */
import http from 'node:http';
import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=path.dirname(fileURLToPath(import.meta.url));
const host='127.0.0.1',port=Number(process.env.PORT||5179);
const types={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8'};
const allow=new Map([
 ['/','demo/index.html'],['/demo/main.js','demo/main.js'],
 ['/dist/index.js','dist/index.js'],['/dist/model.js','dist/model.js'],
 ['/dist/healthBar.js','dist/healthBar.js'],['/dist/rng.js','dist/rng.js']
]);
http.createServer(async(req,res)=>{
 const file=allow.get(new URL(req.url??'/',`http://${host}:${port}`).pathname);
 if(!file){res.writeHead(404);res.end('not found');return;}
 try{
  const data=await readFile(path.join(root,file));
  res.writeHead(200,{'content-type':types[path.extname(file)]||'application/octet-stream',
   'x-content-type-options':'nosniff','cache-control':'no-store'});res.end(data);
 }catch{res.writeHead(500);res.end('build not found');}
}).listen(port,host,()=>console.log(`Independent combat demo: http://${host}:${port}`));
