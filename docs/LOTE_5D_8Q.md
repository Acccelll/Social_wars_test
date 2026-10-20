# Social Wars — 5D.8Q: influência da câmera no combate automático

**Estado: teste controlado concluído, três jobs de CI aprovados.**

Objetivo: investigar por que, na vila original, o Bushwacker (item **1358**, `PlayerID=1`) eliminou automaticamente o Reaper Drone (item **1376**, `PlayerID=2`) a **15 tiles ao norte**, mas não o eliminou a **15 tiles a leste** nas janelas observadas anteriormente.

## 1. Preparação e integridade

- **Cliente:** SWF original `Basesec_1.5.4.swf`, SHA-256 `e4ce0218920a30fceee85ba750df3eedffa3f90e977bd117655704e297e0dc77`, Chromium + Ruffle, servidor original Flask em loopback.
- **Fixture descartável:** Bushwacker índice **41**, tile **(55,45)**; Reaper Drone hostil índice **42**, tile **(70,45)**. A distância inicial entre os tiles permanece em **15**.
- Não há **nenhum clique em unidade** ou POST sintético de movimento, dano ou ataque.
- Os únicos cliques são para fechar os avisos de entrada, como nos testes anteriores.
- Repetição do cenário em três jobs independentes, diferenciando somente as teclas que movimentam a visão.

[Workflow 5D.8Q — CI 39411986093, três jobs aprovados](https://github.com/Acccelll/Social_wars_test/actions/runs/39411986093).

## 2. Código original confirma que as setas movem o mapa

O decompilado ActionScript 0.02a, `core.Base`, mostra:

- `UpdateGame1()` verifica `Key.isDown(Constants.KEY_RIGHT)` e chama `moveMap(-50,0)`;
- `Key.isDown(Constants.KEY_LEFT)` chama `moveMap(50,0)`;
- `moveMap()` altera a posição de exibição dos elementos da cena, sem solicitar por si só um ataque ou modificar o tile persistido das unidades;
- `IsoEngine.getNearestTarget()` percorre arrays de unidades e usa o cálculo de distância/validade em coordenadas do mapa; esse método, isoladamente, não consulta a posição da câmera;
- `core.Config.AGGRO_RANGE` original é **10**, conforme recuperado no [5D.8P](LOTE_5D_8P.md).

**Limite:** mesmo que o helper de seleção não utilize a câmera diretamente, outras partes do motor podem ativar/carregar unidades por área visível. Portanto o código não basta para excluir toda dependência da câmera.

## 3. Execução controlada

O script `tests/original/client_camera_aggro_5d8q.mjs` repetiu o cenário `east_15` com três tratamentos:

| Tratamento | Comando de câmera | Câmera mudou nas capturas? | `kill(42)`? | Movimento persistido do Bushwacker? | Janela monitorada |
|---|---|---|---|---|---:|
| Sem pan | Nenhum | Não | **Não observado** | **Não** | 23,024 s |
| Pan direita | `ArrowRight` pressionada 280 ms | **Sim** | **Não observado** | **Não** | 21,440 s |
| Pan esquerda | `ArrowLeft` pressionada 280 ms | **Sim** | **Não observado** | **Não** | 21,619 s |

Os três jobs produziram:
- `session.webm` do cliente original;
- `camera-before.png`, `camera-after.png`, imagens da fase de controle e da situação final;
- `report.json` com timestamps das teclas, eventos HTTP originais, eventos `command.php`, estado do save e captura de vídeo;
- **zero erros de página** e nenhuma remoção do Reaper Drone.

Artefatos Actions:
- [Sem pan](https://github.com/Acccelll/Social_wars_test/actions/runs/39411986093/artifacts/12259612902)
- [Pan direita](https://github.com/Acccelll/Social_wars_test/actions/runs/39411986093/artifacts/12260010994)
- [Pan esquerda](https://github.com/Acccelll/Social_wars_test/actions/runs/39411986093/artifacts/12260535389)

## 4. Interpretação e limite principal

As imagens demonstram a mudança da paisagem entre `camera-before` e `camera-after`, confirmando que o comando de pan foi efetivo. Em todas as rodadas o Reaper Drone **continuou no save em (70,45)** e o Bushwacker em **(55,45)**, sem `move(41)` ou `kill(42)`.

**Entretanto, não foi possível verificar que o inimigo tenha ficado visível após o deslocamento horizontal.** A translação da câmera altera o enquadramento, mas **não equivale a posicionar a câmera precisamente sobre o alvo**. A ausência de `kill` também não prova ausência de danos voláteis, aquisição sem movimento ou impossibilidade de ataque em outro intervalo.

Portanto:
- **Confirmado:** panorâmicas horizontais opostas, nas condições testadas, **não foram suficientes** para produzir combate persistido.
- **Não confirmado:** que a posição da câmera nunca influencia a ativação da IA ou que o alcance dependa exclusivamente da orientação/posição no mapa.
- **Em aberto:** região ativa, visibilidade real do inimigo, obstáculos/caminho A*, direção, disparos não letais, regras de missão.

Os resultados do [5D.8P](LOTE_5D_8P.md), inclusive `kill` norte a 17 tiles e ausência de `kill` leste a 15, permanecem válidos dentro de suas janelas e cenários.

## 5. Arquivos versionados

- `tests/original/client_camera_aggro_5d8q.mjs`
- `.github/workflows/camera-aggro-5d8q.yml`
- `data/visual/camera_aggro_5d8q.json`
- `docs/LOTE_5D_8Q.md`

Os arquivos SWF, vídeos, screenshots e saves não foram comitados ao Git.

## Próximo microlote — 5D.8R

Criar um **controle com o inimigo comprovadamente dentro do enquadramento** e outro teste com os dois mechas deslocados em conjunto para uma região diferente, mantendo os mesmos 15 tiles de separação. Instrumentar deslocamento de câmera em dois eixos e confirmar visualmente a presença do alvo. Só então comparar os resultados de detecção, aproximação, ataque e eliminação e separar a influência da região/terreno da influência da câmera.
