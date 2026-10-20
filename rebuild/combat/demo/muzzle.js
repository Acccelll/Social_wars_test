import {bushMuzzleLocal,bushMuzzleForDirection,originalFacingFrame} from '/dist/index.js';
const $=id=>document.getElementById(id);
const xs=[1,2,3,4,5].map(n=>bushMuzzleLocal(n)),formatter=new Intl.NumberFormat('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2});
const svgNS='http://www.w3.org/2000/svg';
let current=3;
function node(name,attrs,content=''){const el=document.createElementNS(svgNS,name);for(const [key,value] of Object.entries(attrs))el.setAttribute(key,String(value));if(content)el.textContent=content;return el;}
const center={x:315,y:365};
const scale=.65;
const px=x=>center.x+x*scale,py=y=>center.y+y*scale;
const grid=$('gridlines');
for(let x=-400;x<=400;x+=100){
 grid.append(node('line',{x1:px(x),y1:0,x2:px(x),y2:490,class:x===0?'axis':'gridline'}));
 grid.append(node('text',{x:px(x)+4,y:478,fill:'#8fadb7','font-size':10},String(x)));
}
for(let y=-500;y<=100;y+=100){
 grid.append(node('line',{x1:0,y1:py(y),x2:630,y2:py(y),class:y===0?'axis':'gridline'}));
 grid.append(node('text',{x:7,y:py(y)-5,fill:'#8fadb7','font-size':10},String(y)));
}
const points=$('marker-points');
const table=$('pose-table');
for(const p of xs){
 const tr=document.createElement('tr');tr.dataset.pose=p.pose;
 tr.innerHTML='<td>'+p.pose+'</td><td>'+p.spriteId+'</td><td>'+formatter.format(p.xPx)+'</td><td>'+formatter.format(p.yPx)+'</td>';
 table.append(tr);
}
function render(){
 const logical=originalFacingFrame(current);
 const marker=bushMuzzleForDirection(current);
 $('pose-label').textContent='Direção '+current+' → pose '+marker.local.pose+(marker.mirrored?' espelhada':'');
 $('coordinate').textContent=formatter.format(marker.xPx)+' / '+formatter.format(marker.yPx)+' px';
 $('matrix-info').textContent='Sprite interno '+marker.local.spriteId+
  ' · quadro raiz '+marker.local.rootFrame+' · marcador projectilePoint'+
  ' · xTwips='+marker.local.xTwips+' · yTwips='+marker.local.yTwips+
  (marker.mirrored?' · scaleX exterior = −1':' · scaleX exterior = +1');
 for(const button of $('directions').querySelectorAll('button'))
  button.classList.toggle('active',Number(button.dataset.direction)===current);
 for(const tr of table.children)tr.classList.toggle('selected',Number(tr.dataset.pose)===marker.local.pose);
 points.replaceChildren();
 for(const p of xs){
  const isActive=p.pose===marker.local.pose;
  points.append(node('circle',{cx:px(p.xPx),cy:py(p.yPx),r:isActive?8:5,
   fill:isActive?'#ffe0a8':'#78b7c1',stroke:isActive?'#f1f5f9':'none','stroke-width':2}));
  points.append(node('text',{x:px(p.xPx)+12,y:py(p.yPx)-8,fill:'#d6e9ec',
   'font-size':12},'Pose '+p.pose));
 }
 const selected={x:marker.xPx,y:marker.yPx};
 points.append(node('circle',{cx:px(selected.x),cy:py(selected.y),r:12,
  fill:'none',stroke:'#ffe193','stroke-width':2,'stroke-dasharray':'3 3'}));
 points.append(node('line',{x1:px(selected.x),y1:py(selected.y),x2:px(0),y2:py(0),
  stroke:'#f4c77b','stroke-width':1,opacity:.6,'stroke-dasharray':'5 5'}));
}
$('directions').addEventListener('click',e=>{
 const b=e.target.closest('button[data-direction]');
 if(b){current=Number(b.dataset.direction);render();}
});
window.__swMuzzleDebug={getSelected:()=>({...bushMuzzleForDirection(current),direction:current}),getAll:()=>xs};
render();
