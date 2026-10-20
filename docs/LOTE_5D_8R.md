# Social Wars — Lote 5D.8R: região ativa, câmera e combate não letal

> **Atualização posterior — 5D.8S:** o cenário `east_midshift`, que aqui permaneceu vivo durante o período monitorado, **terminou com `kill(42)` numa nova execução**. Veja [5D.8S](LOTE_5D_8S.md). Logo, a prova deste lote é a possibilidade de **dano antes da morte e ataque sem comando `kill` imediato**; não afirmar que este cenário seja definitivamente não letal.

**Estado: concluído.** Execução original no Chromium/Ruffle, 2 jobs de GitHub Actions aprovados. O principal achado é que **pode haver disparos e danos entre as unidades mesmo que não seja emitido o comando persistido `kill`.**

Este lote corrige uma interpretação dos controles negativos dos lotes [5D.8P](LOTE_5D_8P.md) e [5D.8Q](LOTE_5D_8Q.md): **sem `kill` não significa automaticamente sem combate**.

## 1. Integridade do cenário

- Cliente original 0.02a, arquivo `assets/flash/Basesec_1.5.4.swf`, SHA-256 `e4ce0218920a30fceee85ba750df3eedffa3f90e977bd117655704e297e0dc77`.
- Execução isolada: servidor AcidCaos Flask original em loopback, Ruffle e Chromium.
- Vila inicial original com **40 objetos**, clonada em save descartável a cada rodada.
- Duas unidades originais: **Bushwacker 1358**, objeto 41 e `PlayerID 1`; **Reaper Drone 1376**, objeto 42 e `PlayerID 2`.
- Distância Manhattan inicial de **15 tiles** em todos os cenários, com posições desocupadas verificadas contra o inventário original.
- Zero cliques nas unidades e zero ataques/baixas fabricados por teste. O script apenas fecha os diálogos de entrada, executa opcionalmente teclas de pan e observa comandos HTTP, capturas e saves.
- [GitHub Actions 39413489925 — sucesso (2 jobs)](https://github.com/Acccelll/Social_wars_test/actions/runs/39413489925).

## 2. Translação dos pares pelo mapa

| Cenário | Bushwacker | Reaper Drone | Movimento persistido | `kill(42)` | Verificação visual |
|---|---|---|---|---|---|
| `east_original` | (55,45) | (70,45) | Não | Não | Alvo distante não confirmado na tela |
| `north_original` | (55,45) | (55,30) | **Sim, para (55,40)** | **Sim** | Controle positivo da eliminação |
| `east_westshift` | (40,45) | (55,45) | Não | Não | Alvo aparece na tela, atacante fora da região central |
| `east_northshift` | (55,35) | (70,35) | Não | Não | Atacante aparece na tela, alvo fora da região capturada |
| `east_midshift` | (45,43) | (60,43) | Não | Não | **Ambos visíveis, disparos e danos nos dois sentidos** |

- Os quatro cenários voltados para leste não apresentaram `kill` ou `move` persistidos durante cerca de 22,8–23,3 segundos de amostragem após os modais.
- No controle norte, o cliente gerou `move(41,55,40)` e `kill(42)`, persistindo a eliminação.
- A descrição correta dos resultados negativos do leste é **sem eliminação e sem deslocamento persistidos na janela**. Não é correto rotular esses cenários em conjunto como "sem ataque".

[Artefato da translação com cinco `report.json`, screenshots e sessões webm originais](https://github.com/Acccelll/Social_wars_test/actions/runs/39413489925/artifacts/12261080426).

### Descoberta decisiva: combate não letal em `east_midshift`

O cenário coloca atacante em **(45,43)** e inimigo em **(60,43)**. Os dois aparecem simultaneamente na área visível. A sequência de screenshots mostra:

- o Bushwacker apontando e **disparando repetidamente contra o Reaper Drone**;
- projétil/efeito luminoso entre as unidades;
- números de dano **32** e **28** sobre a unidade inimiga;
- número **36** sobre o Bushwacker, indicando contra-ataque/dano recebido;
- os dois objetos **permaneceram no save ao final**, sem `kill(42)`.

Esses valores numéricos são **observações visuais** em capturas selecionadas, não deltas de HP obtidos em um log de danos do servidor. A indicação exata da instância que causou cada efeito não foi instrumentada.

É uma distinção fundamental para reproduzir corretamente a jogabilidade: as **ações de ataque e a barra de vida podem permanecer apenas na simulação do cliente durante o combate**; comandos como `kill` documentam a eliminação, **não cada disparo**.

Portanto, os controles negativos de leste dos lotes 5D.8P e 5D.8Q não permitem afirmar ausência absoluta de aggro/combate; o padrão de ausência de `kill` foi medido, mas o dano parcial **precisa de instrumentação visual**.

## 3. Controle de câmera em dois eixos

Foi repetido `east_original` com o par em **(55,45)** e **(70,45)**, mantendo as unidades imóveis e adicionando apenas inputs de navegação:

- oito pressões de **`ArrowRight`** de 170 ms;
- cinco pressões de **`ArrowDown`** de 170 ms;
- capturas intermediárias `camera-ArrowRight-checkpoint.png`,
  `camera-ArrowDown-checkpoint.png` e `camera-after.png`.

O movimento do mapa é visualmente evidente: a câmera percorre construções mais distantes e uma região de lago/floresta. Porém, **o inimigo não foi identificado na área visível**, mesmo após o pan.

Nenhum `kill` ou `move` persistido ocorreu nesse experimento durante cerca de **22,8 segundos** de controle. Isso **não isola a hipótese de visibilidade**, porque a meta de mostrar o alvo ainda não foi satisfeita.

[Artefato completo do controle de câmera](https://github.com/Acccelll/Social_wars_test/actions/runs/39413489925/artifacts/12260198346).

## 4. Verificação adicional no ActionScript original

O arquivo original `core.isoengine.IsoEngine` contém:

- `addElement()`: insere instâncias de `IsoFightingElement` nas listas de aliados ou inimigos, conforme `PlayerID`; essa rotina **não testa explicitamente o viewport**.
- `getNearestTarget()`: seleciona a lista do time desejado, solicita os candidatos a `bucleNearestUnits()`, ordena e valida a elegibilidade.
- `bucleNearestUnits()`: calcula distância euclidiana entre coordenadas `buildingReference.tx/ty` e filtra pelo raio solicitado.
- `core.Config.AGGRO_RANGE:uint=10` permanece o valor original de configuração.

Esses trechos estáticos ajudam a explicar o mecanismo de seleção, mas **não excluem** culling, carregamento por região ativa, obstáculos ou eventos de ataque iniciados em outras partes do cliente.

## 5. Artefatos e arquivos versionados

- `tools/seed_translated_pairs_5d8r.py` — posiciona pares em cinco locais com distância fixa, verificando ocupação.
- `tests/original/client_translated_pairs_5d8r.mjs` — grava sessão, eventos, saves e capturas sem comandos sintéticos; permite foco de câmera opcional.
- `.github/workflows/translated-pairs-5d8r.yml` — dois jobs isolados: cinco translações e foco de câmera com 13 comandos.
- `data/visual/translated_pairs_combat_5d8r.json` — evidência e caveats.
- `docs/LOTE_5D_8R.md` (este relatório).

A distribuição original permanece imutável. Assets, vídeos e screenshots não foram adicionados ao histórico do Git.

## Próximo microlote — 5D.8S

**Separar agressividade, disparos, dano e morte**, com capturas temporizadas e controle do enquadramento. Comparar configurações com **ambos os mechas visíveis**, incluindo variantes de 10 e 15 tiles. Inspecionar as barras de vida e os disparos mesmo sem `kill`, para não interpretar erroneamente novos resultados negativos. Avaliar posteriormente o critério original de pathfinding/terreno e a seleção de alvos, sem inventar um raio de aggro universal.
