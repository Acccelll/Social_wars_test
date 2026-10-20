import {
 createCombatant,receiveAttack,healthBarView,seededRng,
 advanceFrames,finishDamageParticle
} from '/dist/index.js';
const byId=id=>document.getElementById(id);
let rng,bush,drone,lines;
function render(key,state){
 const v=healthBarView(state),percent=Math.round(v.ratio*100);
 byId(key+'-stat').textContent=`HP ${state.health}/${state.maxLife} (${percent}%)${state.dead?' — MORTO':''}`;
 byId(key+'-fill').style.width=percent+'%';
 byId(key+'-fill').style.background=v.color;
 byId(key+'-bar').textContent=`Barra: ${v.divisions} divisões, ${v.width}×4 px, cor ${v.color}, ${v.visible?'visível':'oculta'}`;
}
function update(){
 render('b',bush);render('r',drone);
 byId('b-attack').disabled=drone.dead;byId('r-attack').disabled=bush.dead;
 byId('auto').disabled=bush.dead||drone.dead;
}
function log(msg){lines.push(msg);if(lines.length>60)lines.shift();byId('events').textContent=lines.join('\n');}
function attack(side){
 const target=side==='b'?drone:bush;
 if(target.dead)return;
 // Demo-only frame step to expose damage particle gate.
 const rested=advanceFrames(target,15);
 const ready=finishDamageParticle(rested);
 const outcome=receiveAttack(ready.state,side==='b'?32:23,rng);
 if(side==='b')drone=outcome.state;else bush=outcome.state;
 log(`${side==='b'?'Bushwacker':'Reaper Drone'}: ${outcome.roll.damage} de dano ${outcome.roll.critical?'(CRÍTICO)':''}; perda real ${outcome.actualLoss}; alvo HP=${outcome.state.health}`);
 for(const ev of outcome.events.filter(e=>['near-death','death','damage-number'].includes(e.type)))
   log(`  · ${ev.type}${ev.type==='damage-number'?' '+ev.amount:''}`);
 update();
}
function reset(){
 rng=seededRng(1358);
 bush=createCombatant({id:'Bushwacker',maxLife:200,defense:5});
 drone=createCombatant({id:'Reaper Drone',maxLife:220,defense:7});
 lines=[];log('Simulação independente iniciada. Sem comandos de combate HTTP.');update();
}
byId('b-attack').onclick=()=>attack('b');
byId('r-attack').onclick=()=>attack('r');
byId('auto').onclick=()=>{for(let i=0;i<5&&!bush.dead&&!drone.dead;i++){attack('b');if(!drone.dead)attack('r')}};
byId('reset').onclick=reset;reset();
