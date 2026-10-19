# Lote 5D.6 — Galeria categorizada

Objetivo: ampliar o lote 5D.5 (oito GIFs) com nove SWFs adicionais, separados em unidades, construções e interface/telas. Seleção pelos nomes confirmados no catálogo e inspeção de sprites via visual_timelines.py.

Unidades: Bushwacker, Reaper Drone e Megatank. Construções: Tower 2, Workshop 1 e Laboratory. Interface/telas: popupResearchCenter_buildingProcess, popupResearchCenter_buildingProcess_2 e crossDCi.

O HTML gerado tem botões de categoria e pesquisa por nome/ID. Cada cartão informa o arquivo SWF, sprite ID, quadros declarados e GIF efetivamente renderizado. As categorias são preliminares, derivadas do nome/caminho dos recursos, e não revisão visual definitiva.

Os recursos GIF ficam em artefato temporário do GitHub Actions. Apenas CSV/JSON técnico será registrado em data/visual, protegendo o repositório de binários e arquivos de terceiros. A execução não altera o jogo instalado nem os salvamentos.

Ainda NÃO reproduz os estados e transições de animações dependentes de ActionScript em runtime.
