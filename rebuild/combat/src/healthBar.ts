/** Independent HealthBar model based on battle.HealthBar in SWF 0.02a. */
import type {CombatantState} from './model.js';
import {shouldShowHealthBar} from './model.js';
const COLORS:readonly (readonly [number,number,number])[]=[
  [128,0,0],[255,0,0],[255,255,0],[0,255,0],[0,128,0]
];
export const HEALTH_BAR_DIVISION_WIDTH=4;
export const HEALTH_BAR_HEIGHT=4;
export function healthBarDivisions(maxLife:number):number {
  if(!Number.isFinite(maxLife)||maxLife<0)throw new RangeError('invalid maxLife');
  return maxLife<=200?4:maxLife<=400?8:maxLife<=600?12:maxLife<=800?16:20;
}
const hex=(channel:number)=>Math.trunc(channel).toString(16).padStart(2,'0');
/** Piecewise original getHealthColor interpolation, fraction clamped to [0,1]. */
export function originalHealthColor(ratio:number):string{
  if(!Number.isFinite(ratio))throw new RangeError('invalid ratio');
  const x=Math.max(0,Math.min(1,ratio))*4;
  const low=COLORS[Math.floor(x)]!,high=COLORS[Math.ceil(x)]!;
  const highWeight=x-Math.floor(x),lowWeight=1-highWeight;
  const channel=(i:0|1|2)=>hex(low[i]*lowWeight+high[i]*highWeight);
  return '#'+channel(0)+channel(1)+channel(2);
}
export interface HealthBarView{
  readonly ratio:number;readonly width:number;readonly height:number;
  readonly fillWidth:number;readonly divisions:number;readonly divisionWidth:number;
  readonly color:string;readonly greyBackground:string;readonly borderColor:string;
  readonly visible:boolean;readonly zoomScale:number;
}
export function healthBarView(state:CombatantState,zoom=1):HealthBarView{
  if(!Number.isFinite(zoom)||zoom<=0)throw new RangeError('zoom must be >0');
  const divisions=healthBarDivisions(state.maxLife),width=divisions*HEALTH_BAR_DIVISION_WIDTH;
  const ratio=Math.max(0,Math.min(1,state.health/state.maxLife));
  return {ratio,width,height:HEALTH_BAR_HEIGHT,fillWidth:width*ratio,
    divisions,divisionWidth:HEALTH_BAR_DIVISION_WIDTH,color:originalHealthColor(ratio),
    greyBackground:'#a0a0a0',borderColor:'#000000',
    visible:shouldShowHealthBar(state),zoomScale:1/zoom};
}
