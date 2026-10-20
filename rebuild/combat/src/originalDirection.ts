/**
 * Source-derived 8-direction to 5-sprite-frame mapping of Social Wars 0.02a.
 * core.Constants.ORIENTATION_*, core.isoengine.IsoUnit.updateUnitDirectionTilePixel()
 * and updateAnimation(). Reproduces the DIRECTION logic, not a 3D hitbox.
 * Source evidence: docs/LOTE_5D_8X.md.
 */
export const ORIGINAL_DIRECTION = Object.freeze({
 UP:1,UP_RIGHT:2,RIGHT:3,DOWN_RIGHT:4,DOWN:5,
 UP_LEFT:6,LEFT:7,DOWN_LEFT:8
} as const);
export type OriginalDirection=1|2|3|4|5|6|7|8;
export type OriginalAnimation=0|1|2|3|4;
export type Point={readonly x:number;readonly y:number};
function finite(p:Point):void{
 if(!Number.isFinite(p.x)||!Number.isFinite(p.y))throw new RangeError('finite coordinates required');
}
export interface FacingFrame {
 readonly logicalDirection:OriginalDirection;
 readonly poseIndex:0|1|2|3|4;
 readonly oneBasedPose:1|2|3|4|5;
 readonly mirrored:boolean;
 readonly scaleX:1|-1;
}
/** Exact IsoUnit.updateAnimation folding:
 * if (currentDirection > 5) {frameDirection -= 4; scaleX=-1;}
 * gotoAndStop(iAnimation*5 + frameDirection).
 */
export function originalFacingFrame(direction:OriginalDirection):FacingFrame{
 if(!Number.isInteger(direction)||direction<1||direction>8)throw new RangeError('direction 1..8');
 const mirrored=direction>5;
 const pose=(mirrored?direction-4:direction) as 1|2|3|4|5;
 return {logicalDirection:direction,poseIndex:(pose-1) as 0|1|2|3|4,
   oneBasedPose:pose,mirrored,scaleX:mirrored?-1:1};
}
export function originalSpriteFrame(animation:OriginalAnimation,direction:OriginalDirection):number{
 if(!Number.isInteger(animation)||animation<0||animation>4)throw new RangeError('animation 0..4');
 return animation*5+originalFacingFrame(direction).oneBasedPose;
}
/** Screen (not tile) coordinates: literal sign comparison in IsoUnit.
 * The original early return preserves the existing direction when both
 * x and y differences are smaller than tile pixel width/height divided by 3.
 */
export function originalDirectionToward(
 current:Point,target:Point,previous:OriginalDirection,
 options:{tileWidthPx?:number;tileHeightPx?:number;applyOriginalDeadZone?:boolean}={}
):OriginalDirection{
 finite(current);finite(target);
 const dx=target.x-current.x,dy=target.y-current.y;
 if(options.applyOriginalDeadZone){
   const width=options.tileWidthPx,height=options.tileHeightPx;
   if(width===undefined||height===undefined||width<=0||height<=0||
      !Number.isFinite(width)||!Number.isFinite(height))
     throw new RangeError('original tile pixel dimensions required for dead-zone');
   if(Math.abs(dx)<width/3&&Math.abs(dy)<height/3)return previous;
 }
 if(dx>0) return dy<0?2:dy>0?4:3;
 if(dx<0) return dy<0?6:dy>0?8:7;
 if(dy<0)return 1;
 if(dy>0)return 5;
 return previous;
}
/** AS3 getProjectilePoint("projectilePoint") branch. The parent-space
 * result of localToGlobal/globalToLocal must be supplied explicitly.
 * Without proven marker, fall back to (x, y-bmd.height*.6) or (x,y).
 * Asset-marker existence is determined separately, not guessed.
 */
export function originalProjectileStart(input:{
 readonly worldPosition:Point;
 readonly resolvedMarkerInParent?:Point|null;
 readonly displayHeight?:number|null;
}):Point{
 finite(input.worldPosition);
 if(input.resolvedMarkerInParent){
   finite(input.resolvedMarkerInParent);
   return {...input.resolvedMarkerInParent};
 }
 const h=input.displayHeight;
 if(h===undefined||h===null)return {...input.worldPosition};
 if(!Number.isFinite(h)||h<0)throw new RangeError('nonnegative display height required');
 return {x:input.worldPosition.x,y:input.worldPosition.y-h*.6};
}
/** Original getHitPoint(): named marker (if proven) or
 * ghostBuilding.getBounds(this) using projectile.verticalOffset.
 */
export function originalProjectileHitPoint(input:{
 readonly worldPosition:Point;
 readonly resolvedHitMarkerOffset?:Point|null;
 readonly boundsInTarget?:{readonly y:number;readonly height:number}|null;
 readonly verticalOffset?:number;
}):Point{
 finite(input.worldPosition);
 if(input.resolvedHitMarkerOffset){
   finite(input.resolvedHitMarkerOffset);
   return {x:input.worldPosition.x+input.resolvedHitMarkerOffset.x,
     y:input.worldPosition.y+input.resolvedHitMarkerOffset.y};
 }
 if(!input.boundsInTarget)return {...input.worldPosition};
 const {y,height}=input.boundsInTarget;
 const verticalOffset=input.verticalOffset??0;
 if(![y,height,verticalOffset].every(Number.isFinite)||height<0)
   throw new RangeError('invalid target bounds');
 return {x:input.worldPosition.x,
  y:input.worldPosition.y+y+height-height*verticalOffset};
}
