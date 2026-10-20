/** 5D.8Z strict conversion from source sprite-root coordinates to FFDec
 * PNG and Canvas pixels. Requires MEASURED root registration and scale.
 * Never silently uses image center, alpha bbox, or feet as the root origin.
 */
import {bushMuzzleForDirection} from './bushMuzzle.js';
import type {OriginalDirection,Point} from './originalDirection.js';
export interface Bounds2D { readonly x:number;readonly y:number;
  readonly width:number;readonly height:number; }
export interface BushRegistration {
 readonly ffdecImageRootOriginPx:Point;
 /** Scale applied from sprite-local original pixel to FFDec exported image
  * pixel (not proven 1 unless independently measured). */
 readonly ffdecPxPerSpriteLocalPx:number;
 readonly imageSize:{readonly width:number;readonly height:number};
 readonly canvasRect:Bounds2D;
}
function assertPoint(p:Point){if(!Number.isFinite(p.x)||!Number.isFinite(p.y))throw new RangeError('Invalid registered point');}
export function validateRegistration(cal:BushRegistration):void {
 assertPoint(cal.ffdecImageRootOriginPx);
 if(!Number.isFinite(cal.ffdecPxPerSpriteLocalPx)||cal.ffdecPxPerSpriteLocalPx<=0)
   throw new RangeError('Measured source pixel ratio is required');
 const {width,height}=cal.imageSize;
 const rect=cal.canvasRect;
 if(![width,height,rect.x,rect.y,rect.width,rect.height].every(Number.isFinite)||
   width<=0||height<=0||rect.width<=0||rect.height<=0)
   throw new RangeError('Positive measured PNG and Canvas dimensions required');
}
export function localBushMarkerInFfdecImage(
 direction:OriginalDirection,cal:BushRegistration
):Point{
 validateRegistration(cal);
 const point=bushMuzzleForDirection(direction);
 return {
  x:cal.ffdecImageRootOriginPx.x+point.xPx*cal.ffdecPxPerSpriteLocalPx,
  y:cal.ffdecImageRootOriginPx.y+point.yPx*cal.ffdecPxPerSpriteLocalPx
 };
}
export function sourcePixelInCanvas(source:Point,cal:BushRegistration):Point {
 validateRegistration(cal);assertPoint(source);
 return {x:cal.canvasRect.x+source.x*cal.canvasRect.width/cal.imageSize.width,
         y:cal.canvasRect.y+source.y*cal.canvasRect.height/cal.imageSize.height};
}
export function calibratedFfdecBushShot(
 direction:OriginalDirection,cal:BushRegistration
):{readonly source:Point;readonly canvas:Point;readonly inSourceBounds:boolean}{
 const source=localBushMarkerInFfdecImage(direction,cal);
 const canvas=sourcePixelInCanvas(source,cal);
 return {source,canvas,inSourceBounds:
   source.x>=0&&source.x<=cal.imageSize.width&&
   source.y>=0&&source.y<=cal.imageSize.height};
}
