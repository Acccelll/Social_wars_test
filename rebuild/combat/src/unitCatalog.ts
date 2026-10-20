/** 5D.8U: server-verified COMMUNITY unit catalog, not historical production proof.
 * Sources: AcidCaos/socialwarriors config/patch/unit_patch.json and
 * tools/sw_unit_patch.csv (active via config/patch/patches.txt).
 */
export interface UnitCatalogEntry {
  readonly id:1358|1376;
  readonly name:string;
  readonly assetName:string;
  readonly type:'ROBOT'|'AIR_VEHICLE';
  readonly maxLife:number;
  readonly attack:number;
  readonly defense:number;
  readonly attackRange:number;
  readonly velocity:number;
  readonly attackInterval:number;
  readonly bestAgainst:string;
  readonly bestAgainstMultiplier:number;
  readonly source:'AcidCaos-active-unit-patch';
}
export const UNIT_CATALOG:Readonly<Record<'bushwacker'|'reaperDrone',UnitCatalogEntry>>=Object.freeze({
  bushwacker:Object.freeze({
    id:1358,name:'Bushwacker',assetName:'1358_bushwacker',type:'ROBOT',
    maxLife:6500,attack:138,defense:1,attackRange:10,velocity:7,attackInterval:35,
    bestAgainst:'ft_ground',bestAgainstMultiplier:1,source:'AcidCaos-active-unit-patch'
  }),
  reaperDrone:Object.freeze({
    id:1376,name:'Reaper Drone',assetName:'1376_reaperDrone',type:'AIR_VEHICLE',
    maxLife:700,attack:36,defense:1,attackRange:11,velocity:8,attackInterval:30,
    bestAgainst:'ft_ground',bestAgainstMultiplier:1,source:'AcidCaos-active-unit-patch'
  })
});
export type UnitKey=keyof typeof UNIT_CATALOG;
export function unitCatalogById(itemId:number):UnitCatalogEntry|undefined {
  return Object.values(UNIT_CATALOG).find(x=>x.id===itemId);
}
