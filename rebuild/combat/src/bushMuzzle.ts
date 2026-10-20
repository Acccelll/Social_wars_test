/** 5D.8Y — genuine nested SWF projectilePoint transforms (Bushwacker 1358).
 * Raw static tags are verified against the SHA-pinned unmodified original SWF.
 * These points are in DefineSprite1092 LOCAL space, not CSS/canvas pixels.
 * A registered root origin + actual scale/zoom is required for world output.
 */
import {originalFacingFrame,type OriginalDirection,type Point} from './originalDirection.js';
export type AffineTwips=readonly [number,number,number,number,number,number];
export interface BushMarkerRecord {
 readonly pose:1|2|3|4|5;
 readonly attackRootFrame:number;
 readonly childSpriteId:number;
 readonly rootPlacement:AffineTwips;
 readonly markerPlacement:AffineTwips;
 readonly markerName:'projectilePoint';
}
/** Positions directly taken from PlaceObject tags. a,b,c,d,tx,ty in twips. */
export const BUSH_ATTACK_MARKERS:readonly BushMarkerRecord[]=Object.freeze([
 {pose:1,attackRootFrame:11,childSpriteId:643,
  rootPlacement:[-1,0,0,1,173,469],markerPlacement:[1,0,0,1,-2150,-7903],markerName:'projectilePoint'},
 {pose:2,attackRootFrame:12,childSpriteId:675,
  rootPlacement:[-1,0,0,1,1148,926],markerPlacement:[1,0,0,1,-3943,-6910],markerName:'projectilePoint'},
 {pose:3,attackRootFrame:13,childSpriteId:716,
  rootPlacement:[-1,0,0,1,1180,1008],markerPlacement:[1,0,0,1,-2551,-4658],markerName:'projectilePoint'},
 {pose:4,attackRootFrame:14,childSpriteId:752,
  rootPlacement:[-1,0,0,1,1144,904],markerPlacement:[1,0,0,1,-650,-2469],markerName:'projectilePoint'},
 {pose:5,attackRootFrame:15,childSpriteId:786,
  rootPlacement:[-1,0,0,1,319,416],markerPlacement:[1,0,0,1,2197,-2610],markerName:'projectilePoint'}
]);
export function multiplyAffine(parent:AffineTwips,child:AffineTwips):AffineTwips {
 const [a,b,c,d,tx,ty]=parent,[e,f,g,h,u,v]=child;
 for(const n of [...parent,...child])
  if(!Number.isFinite(n))throw new RangeError('Finite affine matrix required');
 return [a*e+c*f,b*e+d*f,a*g+c*h,b*g+d*h,
         a*u+c*v+tx,b*u+d*v+ty];
}
export function transformPoint(m:AffineTwips,p:Point):Point{
 if(!Number.isFinite(p.x)||!Number.isFinite(p.y))throw new RangeError('Invalid point');
 const [a,b,c,d,tx,ty]=m;
 return {x:a*p.x+c*p.y+tx,y:b*p.x+d*p.y+ty};
}
export function bushMuzzleLocal(pose:1|2|3|4|5):{
 readonly pose:1|2|3|4|5;readonly rootFrame:number;
 readonly spriteId:number;readonly xTwips:number;readonly yTwips:number;
 readonly xPx:number;readonly yPx:number;
}{
 const entry=BUSH_ATTACK_MARKERS[pose-1];
 if(!entry||entry.pose!==pose)throw new RangeError('Bushwacker pose must be 1..5');
 const m=multiplyAffine(entry.rootPlacement,entry.markerPlacement);
 const p=transformPoint(m,{x:0,y:0});
 return {pose,rootFrame:entry.attackRootFrame,spriteId:entry.childSpriteId,
  xTwips:p.x,yTwips:p.y,xPx:p.x/20,yPx:p.y/20};
}
/** Apply original outer scaleX flip for logical directions 6..8.
 * The result remains sprite-root local; it is NOT a calibrated canvas muzzle.
 */
export function bushMuzzleForDirection(direction:OriginalDirection):{
 readonly local:ReturnType<typeof bushMuzzleLocal>;
 readonly xPx:number;readonly yPx:number;readonly mirrored:boolean;
}{
 const facing=originalFacingFrame(direction),local=bushMuzzleLocal(facing.oneBasedPose);
 return {local,xPx:local.xPx*facing.scaleX,yPx:local.yPx,mirrored:facing.mirrored};
}
/** Convert to screen coordinates ONLY when caller supplies a MEASURED
 * Sprite1092 root anchor on screen and an independently determined scale.
 * We deliberately do not provide default values for these unknowns.
 */
export function calibratedBushMuzzle(input:{
 readonly direction:OriginalDirection;
 readonly measuredRootOrigin:Point;
 readonly measuredPixelsPerOriginalPx:number;
}):Point{
 const {measuredRootOrigin:origin,measuredPixelsPerOriginalPx:scale}=input;
 if(!Number.isFinite(scale)||scale<=0||!Number.isFinite(origin.x)||!Number.isFinite(origin.y))
  throw new RangeError('Measured anchor and positive scale required');
 const marker=bushMuzzleForDirection(input.direction);
 return {x:origin.x+marker.xPx*scale,y:origin.y+marker.yPx*scale};
}
