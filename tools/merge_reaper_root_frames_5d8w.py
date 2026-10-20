#!/usr/bin/env python3
"""Merge validated Reaper root-frame atlas into optional 5D.8V visual manifest."""
import argparse, json,hashlib
from pathlib import Path
def main():
 p=argparse.ArgumentParser()
 p.add_argument('--baseline',required=True)
 p.add_argument('--root25',required=True)
 p.add_argument('--out',required=True)
 a=p.parse_args()
 base=Path(a.baseline);source=Path(a.root25);dest=Path(a.out)
 visual=json.loads((base/'manifest.json').read_text())
 root=json.loads((source/'reaper_root25_manifest.json').read_text())
 if visual['lot']!='5D.8V' or root['lot']!='5D.8W':raise ValueError('Mixed versions')
 if root['originalSWFModified'] or root['rootFrameCount']!=25:raise ValueError('Bad source')
 key='reaper_drone'
 states=root['states']
 for state in ('quieto','andar','ataque','muerte','picar'):
  rec=states[state]
  if rec['frames']!=5:
   raise ValueError('Invalid root frame count: '+state)
  # QUIETO, ANDAR, ATAQUE have multiple orientations; MUERTE/PICAR
  # have no new placements after their first frame and may be static/blank.
  if state in ('quieto','andar','ataque') and rec['distinctRenderedFrames']<2:
   raise ValueError('No directional diversity: '+state)
  src=source/'units'/key/(state+'.png')
  if hashlib.sha256(src.read_bytes()).hexdigest()!=rec['atlasSha256']:
   raise ValueError('PNG source corrupt')
  destFile=dest/'units'/key/(state+'.png')
  destFile.parent.mkdir(parents=True,exist_ok=True)
  destFile.write_bytes(src.read_bytes())
 visual['units'][key]['states']={
  state:{"url":rec['url'],"frames":rec['frames'],"columns":rec['columns'],
          "frameWidth":rec['frameWidth'],"frameHeight":rec['frameHeight'],
          "fps":rec['fps'],"distinctRenderedFrames":rec['distinctRenderedFrames'],
          "rootFrameLabelStart":rec['sourceRootFrames'][0],
          "sourceRootFrames":rec['sourceRootFrames'],
          "alphaBounds":rec['alphaBounds'],
          "pngSha256":rec['atlasSha256']} for state,rec in states.items()
 }
 visual['lot']='5D.8W'
 visual['reaperAnimationSource']='25 individual SWF root frames, not sublength subframes'
 visual['rootTimelineAnalysis']={'rootTransformTwips':root['rootTransformTwips'],
     'rootFrameCount':25,'states':root['keyframeEventsByState']}
 visual['limitations']=[x for x in visual.get('limitations',[])
       if 'Reaper Drone' not in x and 'Reaper' not in x]
 visual['limitations']+=['Source Reaper still-image issue corrected by explicit root frame selection',
   'SWF stage registration and rendered alpha bounds are not a verified gameplay muzzle/foot pivot',
   'Independent projectile speed and frame sync are still approximate']
 dest.mkdir(parents=True,exist_ok=True)
 (dest/'manifest.json').write_text(json.dumps(visual,indent=2,ensure_ascii=False)+'\n')
 print('REAPER_DYNAMIC_MERGE_5D8W',json.dumps({
    'frames':sum(x['frames'] for x in visual['units'][key]['states'].values()),
    'distinct':{k:v['distinctRenderedFrames'] for k,v in visual['units'][key]['states'].items()},
    'spriteAssets':len(visual['units'][key]['states'])}))
if __name__=='__main__':main()
