# Social Wars — Lote 5D.8K: timelines, estados e exportação de animações originais

**Resultado: extração concluída.** Foram identificadas e exportadas
amostras animadas dos estados originais de Bushwacker e Reaper Drone,
preservando os SWFs sem edição e sem introduzi-los no repositório Git.

## Fontes e integridade

| Item gameplay | Unidade | Caminho no ZIP 0.02a | Bytes | SHA-256 |
|---|---|---|---:|---|
| 1358 | Bushwacker | `assets/sprites/1358_bushwacker.swf` | 1.158.582 | `e9db23f98dcaa5cf81cbcdac85154fcb1da92a205b7d9047a5d420fb9d068c5e` |
| 1376 | Reaper Drone | `assets/sprites/1376_reaperDrone.swf` | 201.043 | `c26e398f5f2209eb9ba8fc3ef84ed243b1032240c3e2f543a879330e77b64b83` |

A distribuição original 0.02a de 492.630.085 bytes foi baixada pelo CI.
Os scripts exigiram caminhos inequívocos em `assets/sprites/`, tamanhos
e hashes reproduzidos. Os dois SWFs possuem **30 FPS**.

**Inventário:** Bushwacker tem **258 DefineSprite internos e 2.125
frames declarados** somados; Reaper Drone tem **554 DefineSprite e 578
frames**. Isso é contagem estrutural estática, **não duração contínua
de animação do jogo**.

## Estados originais comprovados por FrameLabel

Os `FrameLabel` e `DefineSprite` foram recuperados diretamente da
estrutura SWF, com o parser `tools/visual_timelines.py`.

| Frame inicial | Bushwacker (DefineSprite **1092**) | Reaper Drone (DefineSprite **1654**) |
|---:|---|---|
| 1 | `QUIETO` (1–5) | `QUIETO` (1–5) |
| 6 | `ANDAR` (6–10) | `ANDAR` (6–10) |
| 11 | `ATAQUE` (11–15) | `ATAQUE` (11–15) |
| 16 | `MUERTE` (16–30) | `MUERTE` (16–20) |
| 21 | — | `PICAR` (21–25) |
| 31 | `01` (31–35) | — |
| 36 | `02` (36–40) | — |
| 41 | `03` (41–50) | — |

A correspondência entre raiz SWF e símbolo principal foi verificada
pela única referência do primeiro frame da timeline raiz.

### Ataques direcionais Bushwacker — descoberta adicional

O estado `ATAQUE` do sprite **1092** não é um único clipe. Seus frames
11–15 substituem o filho na profundidade 1 por estes
símbolos originais, também recuperados da `SymbolClass`:

| Frame principal | ID interno | Nome simbólico recuperado |
|---:|---:|---|
| 11 | 643 | `_1358_bushwacker_fla.E_attack_133` |
| 12 | 675 | `_1358_bushwacker_fla.TE_attack_141` |
| 13 | 716 | `_1358_bushwacker_fla.P_attack_145` |
| 14 | 752 | `_1358_bushwacker_fla.T_attack_153` |
| 15 | 786 | `_1358_bushwacker_fla.F_attack_159` |

Esses cinco símbolos contêm **60 frames cada**. Eles demonstram a
estrutura de variantes de ataque, mas ainda não foi verificado qual
orientação aparece em cada instante do combate gravado no 5D.8J.

## Recursos visuais exportados

Foram concluídos dois workflows:

- [Original Combat Animation 5D.8K — CI 39355691232](https://github.com/Acccelll/Social_wars_test/actions/runs/39355691232):
  inventário e linhas de dependência completas, hashes e exportação de
  **3 GIFs** dos candidatos de ataque Bushwacker mais **1 GIF**
  da timeline principal Reaper Drone.
- [Original Combat Frame States — CI 39355945927](https://github.com/Acccelll/Social_wars_test/actions/runs/39355945927):
  exportação específica dos rótulos **QUIETO, ANDAR, ATAQUE e MUERTE**
  de ambas as unidades e também **PICAR** do Reaper Drone: **9 GIFs**
  independentes, com até 15 subframes de composição por amostra.
  [Baixar artefato dos estados](https://github.com/Acccelll/Social_wars_test/actions/runs/39355945927/artifacts/12235636024).

**Ressalva verificada:** na saída FFDec, as amostras de `QUIETO`,
`ANDAR` e `ATAQUE` do Reaper Drone ficaram **idênticas em bytes**.
Isso não apaga os rótulos originais, mas impede alegar uma diferença
visual entre esses três estados a partir desses GIFs. A amostra
`PICAR` aparenta não desenhar a unidade na prévia.
Sua função exata também permanece pendente.

As amostras estão em artefatos temporários, **não publicadas como
assets reescritos/alterados no Git**. O repositório guarda somente
scripts reprodutíveis e metadados minimizados.

## Correlação com o 5D.8J e limites

O 5D.8J já comprovou o combate em runtime do SWF original:
Bushwacker (`PlayerID=1`) matou Reaper Drone
(`PlayerID=2`) e emitiu `kill` para objeto 42, removido
do save original.

**Neste lote**, identificamos em qual timeline/intervalo os
estados `ATAQUE` e `MUERTE` são definidos e extraímos prévias
originais. **Ainda não identificamos**:
- o `DefineSprite` do projétil, impacto ou partícula de dano;
- quais subframes exatos estavam ativos em cada instante no Ruffle;
- comportamento de `ATAQUE` do Reaper no renderizador FFDec, que
  exibiu saída idêntica a `QUIETO`/`ANDAR`;
- recompilação integral do cliente independente do SWF original.

## Arquivos versionados

- `tools/combat_animation_probe_5d8k.py`
- `.github/workflows/combat-animation-5d8k.yml`
- `tools/combat_frame_states_5d8k.py`
- `.github/workflows/combat-frame-states-5d8k.yml`
- `data/visual/combat_animations_5d8k.json`
- `docs/LOTE_5D_8K.md` (este arquivo)

**Próximo microlote 5D.8L:** exportar em detalhe as cinco
variantes direcionais de `ATAQUE` do Bushwacker e relacionar
projéteis e impactos com o vídeo original. Manter os limites de
prova separados: sprite estático, quadro exportado e execução runtime.
