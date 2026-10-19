# Lote 5D.5 - Galeria visual de animações

Este lote usa timelines persistentes de seis fontes analisadas no 5D.4 e seleciona dois sprites animados por SWF, quando disponíveis. O exportador usa o FFDec com sprite:gif e -selectid, reduzindo a prévia para no máximo 256 pixels e 20 quadros.

Fontes iniciais: Tetrapod Mech, Splinter Mech, torre, centro de comando e good_10_m.

O resultado é uma galeria HTML offline com GIFs, identificadores de sprite, quadros declarados, quadros renderizados, dependências de character ID e manifesto CSV/JSON. O arquivo index.html deve ser aberto junto da pasta previews.

O lote não recria as animações controladas pelo código ActionScript e não publica imagens originais no Git. Somente ferramentas e documentação são versionadas. O pacote de prévias fica temporariamente em GitHub Actions.

O script tools/visual_preview_catalog.py também pode ser executado no Windows após a instalação de Python 3, Pillow, Java e JPEXS FFDec.

## Resultado inicial confirmado em 19/10/2026

Workflow [39301011532](https://github.com/Acccelll/Social_wars_test/actions/runs/39301011532)
aprovado: oito sprites de cinco SWFs exportados pelo FFDec 26.3.0
em GIF, **8/8 prévias animadas validadas**.

| SWF | Character IDs | Quadros renderizados |
|---|---|---|
| 1212_tetrapod_mech | 362, 393 | 20 + 20 |
| 1313_splinterMech | 188, 189 | 20 + 20 |
| 0022_tower_1_m | 85, 52 | 20 + 18 |
| 0026_command_center_1_m | 21 | 2 |
| good_10_m | 11 | 4 |

O [pacote com galeria HTML/GIF/CSV/JSON](https://github.com/Acccelll/Social_wars_test/actions/runs/39301011532/artifacts/12211297019)
tem tamanho comprimido de 1.264.939 bytes e retenção de 14 dias.
O repositório recebe os **metadados CSV/JSON** permanentemente, sem
incorporar os GIFs.

**O catálogo completo de todas as unidades e animações segue pendente.**
