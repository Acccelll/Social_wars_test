/* 5D.8: user-labelled action observer for original Social Wars.
 * Evidence of user interaction only; no claims about MovieClip IDs. */
(() => {
  if (window.__swObserver) return;
  const entries=[], t0=performance.now();
  const container=document.createElement("aside");
  container.id="sw-observer";
  container.style.cssText="position:fixed;z-index:2147483647;top:8px;right:8px;background:#162638;color:white;border:2px solid #7891a8;border-radius:8px;padding:12px;font:12px system-ui;max-width:250px";
  container.innerHTML='<strong>Social Wars · Observador 5D.8</strong><p>Marque a ação executada. Os IDs dos sprites não são identificados automaticamente.</p><select id="sw-action"><option value="idle">Espera</option><option value="movement">Movimento</option><option value="attack">Ataque</option><option value="damage">Dano</option><option value="destruction">Destruição</option><option value="construction">Construção</option><option value="other">Outra</option></select><p><button id="sw-start">Iniciar</button> <button id="sw-stop" disabled>Finalizar</button></p><small id="sw-result">Sem marcações</small>';
  document.body.appendChild(container);
  const start=container.querySelector("#sw-start"),stop=container.querySelector("#sw-stop");
  const select=container.querySelector("#sw-action"),status=container.querySelector("#sw-result");
  let current=null;
  function bounds(){const el=document.querySelector("ruffle-player,ruffle-embed,ruffle-object,embed,object");
    if(!el)return null;const r=el.getBoundingClientRect();
    return {x:r.x,y:r.y,width:r.width,height:r.height}}
  function record(type,data){
    const x={type,relative_ms:Math.round(performance.now()-t0),wall_clock_ms:Date.now(),...data};
    entries.push(x);
    if(typeof window.__swHostRecord==="function")
      Promise.resolve(window.__swHostRecord(x)).catch(()=>{});
  }
  function begin(){
    if(current)return;
    current={kind:select.value,start_ms:Math.round(performance.now()-t0)};
    record("begin_action",{kind:current.kind,player_bounds:bounds()});
    start.disabled=true;stop.disabled=false;status.textContent="Gravando "+current.kind;
  }
  function end(){
    if(!current)return;
    record("end_action",{kind:current.kind,duration_ms:Math.round(performance.now()-t0)-current.start_ms,
                         player_bounds:bounds()});
    current=null;start.disabled=false;stop.disabled=true;
    status.textContent=entries.length+" eventos";
  }
  start.addEventListener("click",begin);stop.addEventListener("click",end);
  document.addEventListener("pointerdown",ev=>{
    if(container.contains(ev.target))return;
    const b=bounds();
    record("pointer",{x:Math.round(ev.clientX),y:Math.round(ev.clientY),
      relative_x:b?Math.round(ev.clientX-b.x):null,relative_y:b?Math.round(ev.clientY-b.y):null});
  },true);
  window.__swObserver={entries,begin,end,snapshot:()=>({
    type:"social-wars-browser-observation",user_labels_only:true,
    events:[...entries],active:current,player_present:Boolean(bounds())})};
  record("observer_ready",{player_bounds:bounds()});
})();