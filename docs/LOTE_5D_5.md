# Lote 5D.5 - Galeria visual de animações

Este lote usa timelines persistentes de seis fontes analisadas no 5D.4 e seleciona dois sprites animados por SWF, quando disponíveis. O exportador usa o FFDec com sprite:gif e -selectid, reduzindo a prévia para no máximo 256 pixels e 20 quadros.

Fontes iniciais: Tetrapod Mech, Splinter Mech, torre, centro de comando e good_10_m.

O resultado é uma galeria HTML offline com GIFs, identificadores de sprite, quadros declarados, quadros renderizados, dependências de character ID e manifesto CSV/JSON. O arquivo index.html deve ser aberto junto da pasta previews.

O lote não recria as animações controladas pelo código ActionScript e não publica imagens originais no Git. Somente ferramentas e documentação são versionadas. O pacote de prévias fica temporariamente em GitHub Actions.

O script tools/visual_preview_catalog.py também pode ser executado no Windows após a instalação de Python 3, Pillow, Java e JPEXS FFDec.
