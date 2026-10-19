# 5D.3C — Construções: bitmaps de 12 SWFs confirmados

Os 12 arquivos foram selecionados pelo **catálogo persistente de nomes**
[`data/visual/building_candidates.csv`](../data/visual/building_candidates.csv).
São nomes de construções plausíveis, mas a classificação definitiva exige
prévia visual e revisão de uso dentro do jogo.

| Fonte | Tipo identificado pelo nome |
|---|---|
| `0022_tower_1_m.swf` | tower 1 m |
| `0026_command_center_1_m.swf` | command center 1 m |
| `0028_hospital_1_m.swf` | hospital 1 m |
| `0040_workshop_1_m.swf` | workshop 1 m |
| `0050_bunker_1_m.swf` | bunker 1 m |
| `0080_fortress_1_m.swf` | fortress 1 m |
| `0089_nuclear_plant_m.swf` | nuclear plant m |
| `0118_laboratory_m.swf` | laboratory m |
| `0170_giant_walker_factory_m.swf` | giant walker factory m |
| `0195_orc_headquarters.swf` | orc headquarters |
| `0202_orc_resource_building.swf` | orc resource building |
| `10032_silo_1.swf` | silo 1 |

A workflow [Visual Buildings Bitmap Batch 5D.3](../.github/workflows/visual-buildings-bitmap.yml)
exporta inicialmente somente **bitmaps embutidos** (`--types images`).
Isso evita gerar novamente gigabytes de frames renderizados.

Os SWFs podem conter somente vetores: `EMPTY_CATEGORY` é um resultado
legítimo do filtro bitmap, não uma falha do FFDec. O manifesto registra
todos os estados separadamente.

**Limite:** isso não extrai animações completas nem garante que os
bitmaps sejam suficientes para recriar as construções.
