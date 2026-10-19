# Lote 5D.8C — Unidade original em cenário reproduzível

## Objetivo

Abrir o **cliente original Social Wars 0.02a**, no Chromium/Ruffle com
servidor Flask verdadeiro e vila de teste, e avançar da mera observação de
inicialização para uma vila contendo unidades com IDs confirmados na
configuração do jogo. O objetivo de longo prazo é associar estados de
animação (espera, movimentação, ataque, dano e destruição) aos sprites
Flash identificados no inventário de 1.118 SWFs.

## Cenário descartável

O script `tools/seed_original_units_5d8c.py` transforma apenas a cópia
temporária de `villages/initial.json` do runner GitHub Actions, **antes**
de iniciar o servidor. A distribuição original, seus SWFs e os saves
existentes do usuário não são alterados.

| Unidade (config original) | Item ID | Jogador | Posição no mapa (tiles) |
|---|---:|---:|---|
| Splinter Mech | 1313 | 1 | (52,45) |
| Bushwacker | 1358 | 1 | (55,45) |
| Reaper Drone | 1376 | 1 | (58,45) |
| Splinter Mech (adversário de teste) | 1313 | 3 | (61,45) |

Esses são **IDs de item do jogo**, e não IDs `DefineSprite` internos
dos SWFs. A configuração original `config/patch/unit_patch.json`
identifica os três tipos como unidades `type=u`.

O teste é determinístico, recusa colisão com os objetos da vila
inicial, emite um manifesto JSON e pode ser repetido isoladamente.

## Instrumentação

O gravador `tests/original/record.mjs` oferece `--unit-probe`, que
executa três cliques exploratórios em coordenadas relativas do
`ruffle-embed` na vila descartável, com captura antes/depois,
vídeo WebM e registro dos SWFs requisitados. As sondagens são
identificadas como `center_selection_probe`,
`offset_destination_probe` e `offset_target_probe`.

**Esses nomes descrevem a intenção do ensaio, não uma ação de
gameplay validada.** Todas as marcações têm categoria `other`.
Não é possível afirmar que uma unidade andou, atacou ou recebeu
dano apenas por um clique ou mudança visual. O teste nunca preenche
a fila de estados confirmados do lote 5D.7 sem evidência adicional.

## Critérios de aceite

- Servidor Python, SWLoader e Flash principal carregados no Ruffle.
- Quatro unidades adicionadas ao snapshot temporário sem alterar a
  template original remota.
- Três eventos de sonda, três pares de PNGs, vídeo WebM e análise de
  diferenças visuais com área de comparação válida.
- Manifesto com SWFs requisitados e contagens reais da execução.
- **Zero ações e zero `character_id` confirmados automaticamente.**

Artefatos visuais completos ficam temporariamente no GitHub Actions;
o repositório recebe somente metadados técnicos.

## Próximo passo

Após a validação do cenário na CI, confrontar imagens do vídeo com os
sprites GIF existentes e instrumentar interações de unidade
reconhecidas visualmente. Somente observações corroboradas devem
entrar no mapeamento de `source_swf` + `character_id` + ação.

## Resultado confirmado — 19/10/2026

A primeira execução [39312898050](https://github.com/Acccelll/Social_wars_test/actions/runs/39312898050)
encontrou timeouts de screenshots em três sondagens. **Foi reprovada**
corretamente e as capturas foram serializadas para a repetição.

A execução final [39313160511](https://github.com/Acccelll/Social_wars_test/actions/runs/39313160511)
terminou com **success**, sem etapas reprovadas:

- **4 unidades** no snapshot da vila: Splinter aliado e oponente,
  Bushwacker e Reaper Drone;
- **3 eventos exploratórios** e **3 pares válidos de capturas PNG**;
- **3 mudanças visuais** medidas dentro do player Ruffle;
- **3 SWFs de unidade efetivamente requisitados**:
  `1313_splinterMech.swf`, `1358_bushwacker.swf` e
  `1376_reaperDrone.swf`;
- **0 ações específicas de gameplay confirmadas** e
  **0 `DefineSprite character_id` confirmados**.

Os quatro objetos iniciais usam os índices 41–44 e posicionamentos
indicados neste documento. O manifesto comprova a inclusão das
unidades na cópia descartável; a rede comprova a requisição de seus
SWFs pelo cliente original. Isso não constitui prova de que
movimentação, ataque ou dano tenham sido acionados.

[Baixar vídeo WebM, seis capturas, manifestos e logs do 5D.8C](https://github.com/Acccelll/Social_wars_test/actions/runs/39313160511/artifacts/12217206551)
(cerca de 10,3 MB comprimidos, expiração prevista em 02/11/2026).

[Resumo persistente do ensaio](../data/visual/original_unit_probe_5d8c.json).

**Status:** cenário preparado e captura exploratória **concluídos**;
validação de ações por unidade ainda **pendente**. Próximo
micro-lote 5D.8D: utilizar evidência de quadro para descobrir
quais unidades são visíveis e quais ações do jogo são efetivamente
disparadas, comparando as sequências com os GIFs exportados.
