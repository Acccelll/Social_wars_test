# Lote 5D.6 — Galeria categorizada

Objetivo: ampliar o lote 5D.5 (oito GIFs) com nove SWFs adicionais, separados em unidades, construções e interface/telas. Seleção pelos nomes confirmados no catálogo e inspeção de sprites via visual_timelines.py.

Unidades: Bushwacker, Reaper Drone e Megatank. Construções: Tower 2, Workshop 1 e Laboratory. Interface/telas: popupResearchCenter_buildingProcess, popupResearchCenter_buildingProcess_2 e crossDCi.

O HTML gerado tem botões de categoria e pesquisa por nome/ID. Cada cartão informa o arquivo SWF, sprite ID, quadros declarados e GIF efetivamente renderizado. As categorias são preliminares, derivadas do nome/caminho dos recursos, e não revisão visual definitiva.

Os recursos GIF ficam em artefato temporário do GitHub Actions. Apenas CSV/JSON técnico será registrado em data/visual, protegendo o repositório de binários e arquivos de terceiros. A execução não altera o jogo instalado nem os salvamentos.

Ainda NÃO reproduz os estados e transições de animações dependentes de ActionScript em runtime.

## Resultado conferido

[GitHub Actions 39303077044](https://github.com/Acccelll/Social_wars_test/actions/runs/39303077044)
aprovado com **17/17 prévias renderizadas, 17 animadas e zero erros**,
abrangendo **14 arquivos SWF**.

| Categoria | Prévia GIF |
|---|---:|
| Unidades | 8 |
| Construções | 6 |
| Interface e telas | 3 |
| **Total** | **17** |

Nove SWFs novos foram adicionados aos cinco anteriores, mantendo as oito
prévias do 5D.5. IDs novos:

- `1358_bushwacker.swf`: 327, 20 quadros de prévia.
- `1376_reaperDrone.swf`: 1654, 20 quadros.
- `1037_megatank.swf`: 132, 20 quadros.
- `0039_tower_2_m.swf`: 74, 20 quadros.
- `0040_workshop_1_m.swf`: 52, 18 quadros.
- `0118_laboratory_m.swf`: 11, 20 quadros.
- `popupResearchCenter_buildingProcess.swf`: 74, 20 quadros.
- `popupResearchCenter_buildingProcess_2.swf`: 73, 20 quadros.
- `crossDCi.swf`: 123, 20 quadros.

[Artefato temporário social-wars-gallery-5d6](https://github.com/Acccelll/Social_wars_test/actions/runs/39303077044/artifacts/12212183676)
contém `index.html`, pasta `previews/` e manifestos. Validade até
02/11/2026. Metadados persistentes no repositório:
[`data/visual/gallery_5d6.json`](../data/visual/gallery_5d6.json).

**O catálogo completo de 1.118 SWFs não foi renderizado.**
Categorias, frames e GIFs ainda precisam de verificação visual e
comparação com a execução original do jogo.
