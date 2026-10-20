#!/usr/bin/env python3
"""5D.8V: convert original FFDec 5D.8K/5D.8M GIF artifacts to Canvas PNG atlases.
Read-only source assets. No SWF files or licensed sprite atlases committed to Git.
Usage: --states States.zip --fx FX.zip --out rebuild/combat/original-visual
"""
import argparse, hashlib, io, json, math, zipfile
from pathlib import Path
from PIL import Image
UNITS={
 'bushwacker':(1358,1092,'e9db23f98dcaa5cf81cbcdac85154fcb1da92a205b7d9047a5d420fb9d068c5e'),
 'reaper_drone':(1376,1654,'c26e398f5f2209eb9ba8fc3ef84ed243b1032240c3e2f543a879330e77b64b83')
}
STATES={'quieto':1,'andar':6,'ataque':11,'muerte':16}
FX={
 'bullet':('p.bulletAirBig','DefineSprite_4_p.bulletAirBig'),
 'bazooka':('b.bazookaSmall','DefineSprite_16_b.bazookaSmall'),
 'laser':('p.laserMassiveDrone','DefineSprite_3'),
 'laserBlue':('b.laserBlue','DefineSprite_7_b.laserBlue')
}
def decode(raw):
 im=Image.open(io.BytesIO(raw)); frames=[]
 for i in range(im.n_frames):
  im.seek(i);frames.append(im.convert('RGBA').copy())
 return frames
def union(frames):
 boxes=[f.getbbox() for f in frames];boxes=[b for b in boxes if b]
 if not boxes:raise ValueError('Transparent source frames; cannot select visually blank asset')
 return (min(b[0] for b in boxes),min(b[1] for b in boxes),
         max(b[2] for b in boxes),max(b[3] for b in boxes))
def bounds(frames):
 left,top,right,bottom=union(frames);w,h=frames[0].size
 return (max(0,left-7),max(0,top-7),min(w,right+7),min(h,bottom+7))
def sheet(frames,box,file,height,fps):
 w=box[2]-box[0];h=box[3]-box[1];scale=min(1,height/h)
 cw,ch=max(1,round(w*scale)),max(1,round(h*scale))
 cols=5;rows=math.ceil(len(frames)/cols)
 result=Image.new('RGBA',(cw*cols,ch*rows))
 sigs=set()
 for i,f in enumerate(frames):
  sigs.add(hashlib.sha256(f.tobytes()).hexdigest())
  im=f.crop(box).resize((cw,ch),Image.Resampling.LANCZOS)
  result.paste(im,((i%cols)*cw,(i//cols)*ch))
 file.parent.mkdir(parents=True,exist_ok=True)
 result.save(file,optimize=True)
 return {'frames':len(frames),'columns':cols,'frameWidth':cw,'frameHeight':ch,
         'fps':fps,'distinctRenderedFrames':len(sigs),
         'sha256':hashlib.sha256(file.read_bytes()).hexdigest()}
def main():
 a=argparse.ArgumentParser()
 for arg in ('states','fx','out'):a.add_argument('--'+arg,required=True)
 v=a.parse_args();root=Path(v.out)
 m={'lot':'5D.8V','originalSWFModified':False,'runtimeEquivalent':False,
    'source':'Original 0.02a; FFDec 26.3.0 read-only GIF snapshots',
    'limitations':['FFDec GIF frames are bounded nested subframes, not every original root timeline frame',
       'Reaper Drone exports give a single rendered pose per labeled state',
       'Laser sprite uses visible internal DefineSprite_3 rather than transparent public wrapper'],
    'units':{},'effects':{}}
 with zipfile.ZipFile(v.states) as z:
  for name,(ident,root_sprite,sha) in UNITS.items():
   frames={}
   for state in STATES:
    files=[p for p in z.namelist() if p.startswith(name+'/'+state+'/') and p.endswith('/frames.gif')]
    if len(files)!=1:raise ValueError('Missing '+name+'/'+state)
    frames[state]=decode(z.read(files[0]))
    if len(frames[state])!=15:raise ValueError('Unexpected FFDec subframe count')
   common=bounds([f for arr in frames.values() for f in arr])
   rec={'id':ident,'rootSprite':root_sprite,'swfSha256':sha,'states':{}}
   for state,arr in frames.items():
    file=root/'units'/name/(state+'.png')
    entry=sheet(arr,common,file,280,30)
    entry.update({'url':'/original-visual/units/'+name+'/'+state+'.png',
                  'labelRootFrame':STATES[state]})
    rec['states'][state]=entry
   m['units'][name]=rec
 with zipfile.ZipFile(v.fx) as z:
  for name,(folder,sprite) in FX.items():
   paths=[p for p in z.namelist() if p.startswith(folder+'/sprites/'+sprite+'/') and p.endswith('frames.gif')]
   if len(paths)!=1:raise ValueError('FX sprite missing '+name)
   frames=decode(z.read(paths[0]))
   file=root/'fx'/(name+'.png')
   entry=sheet(frames,bounds(frames),file,130,24)
   entry.update({'url':'/original-visual/fx/'+name+'.png',
                 'originalFx':folder,'internalSprite':sprite})
   m['effects'][name]=entry
 root.mkdir(parents=True,exist_ok=True)
 (root/'manifest.json').write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n')
 print('ORIGINAL_ATLAS_5D8V',json.dumps({
  'unitFrames':{k:{st:p['distinctRenderedFrames'] for st,p in v['states'].items()} for k,v in m['units'].items()},
  'fxFrames':{k:v['distinctRenderedFrames'] for k,v in m['effects'].items()}
 }))
if __name__=='__main__':main()
