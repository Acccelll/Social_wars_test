/** Independent deterministic RNG for tests; NOT the original Flash PRNG. */
import type {RandomSource} from './model.js';
export function seededRng(seed:number):RandomSource {
  if(!Number.isInteger(seed)||seed<0||seed>0xffffffff)throw new RangeError('uint32 seed required');
  let value=seed||0x6d2b79f5;
  return ()=>{
    value^=value<<13;
    value^=value>>>17;
    value^=value<<5;
    return (value>>>0)/0x100000000;
  };
}
export function sequenceRng(values:readonly number[]):RandomSource {
  let i=0;
  return ()=>{if(i>=values.length)throw new RangeError('RNG exhausted');return values[i++]!;};
}
