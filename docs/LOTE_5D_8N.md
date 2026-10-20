# Lote 5D.8N — FX pré-carregados e combate automático original comprovado

**Resultado: concluído.** O SWF original carregou 14 arquivos de efeitos
na inicialização (todos HTTP 200). Em uma vila descartável com Bushwacker
(aliado) e Reaper Drone (inimigo), o cliente executou combate, dano e
eliminação **sem nenhum clique manual nas unidades**.

## Contexto do experimento

Este lote sucede os [efeitos recuperados no 5D.8M](LOTE_5D_8M.md).
O executável é **o Social Wars 0.02a original no Ruffle/Chromium**,
não um jogo recompilado. O servidor Flask AcidCaos original foi executado
em `127.0.0.1:5055`, com saves temporários independentes.

Fixture: vila original com 40 objetos, à qual foram adicionados:
- Bushwacker — item 1358, índice de mapa 41, `PlayerID=1`, tile (55,45).
- Reaper Drone — item 1376, índice de mapa 42, `PlayerID=2`, tile (55,40).

O SWF e os arquivos de usuário **não foram alterados**. Os testes não
fabricaram POSTs `kill`, `attack` ou `move`; os comandos foram emitidos
pelo próprio navegador com o cliente original.

## 1. Resultado da captura HTTP

O instrumentador `tests/original/client_fx_timing_5d8n.mjs` coletou
requests e responses para arquivos `fx/*.swf`, timestamps de
cliques, eventos `command.php`, snapshots e vídeo.

**14/14 solicitações dos FX ocorreram na fase `original_swf_boot`,
todas por HTTP GET e com resposta 200**. Os recursos vieram de
`/static/socialwars/fx/`.

| FX identificado no 5D.8M | GET antes do primeiro clique no inimigo | GET após esse clique | Resposta |
|---|---:|---:|---:|
| `p.bulletAirBig.swf` | 1 | 0 | 200 |
| `b.bazookaSmall.swf` | 1 | 0 | 200 |
| `p.laserMassiveDrone.swf` | 1 | 0 | 200 |
| `b.laserBlue.swf` | 1 | 0 | 200 |

Outros dez FX foram pré-carregados na mesma fase:
`p.bullet`, `b.bullet2`, `p.laserBeamBlueFat`, `b.earth`,
`p.missileM`, `b.bazooka2`, `b.smokeSmall`,
`p.bulletBig`, `p.rocketM` e `b.missile`.
O fato de um FX ter sido solicitado na inicialização **não confirma
que tenha sido mostrado durante o combate deste cenário**.

[Run 39361613405](https://github.com/Acccelll/Social_wars_test/actions/runs/39361613405);
[artefato de requisições e vídeo](https://github.com/Acccelll/Social_wars_test/actions/runs/39361613405/artifacts/12237283795).

## 2. Descoberta: `kill` antes do clique manual

A instrumentação produziu esta ordem no primeiro ensaio:

| Evento | Tempo desde o início da captura |
|---|---:|
| GET dos 14 FX | 3.943–3.944 ms |
| `kill(42,"u")` originado pelo cliente | 23.645 ms |
| Primeiro clique manual no Reaper Drone | 29.253 ms |

Assim, **a eliminação precedeu o clique manual por 5.608 ms**.
O alvo foi removido do save do servidor. O primeiro ensaio não
permitia atribuir causalidade ao clique.

Isso é uma correção importante na leitura dos lotes 5D.8I/5D.8J:
eles comprovaram a operação do combate original, mas não que
a seleção manual iniciou a troca de tiros.

## 3. Teste de controle SEM cliques nas unidades

Foi criado um segundo registrador:
`tests/original/client_auto_combat_control_5d8n.mjs`.
Ele fecha apenas os dois avisos iniciais necessários para acessar
o cenário, **não seleciona o Bushwacker, não clica no Reaper Drone
e não ordena movimento ou ataque**.

**Resultado da execução aprovada:**
- **0** cliques manuais nas unidades, **0** comandos de ataque injetados.
- **14** FX pré-carregados no boot, todos HTTP 200.
- Comando nativo `kill`, objeto **42**, motivo `u`,
  no timestamp **40.765 ms** desta segunda execução independente.
- Reaper Drone **removido do save**; nenhum erro de página.
- **16 capturas** da fase de entrada e de combate, com timestamps.
- Os screenshots mostram o Bushwacker disparando, números de
  dano sobre o Reaper Drone, efeitos luminosos, desaparecimento do
  alvo e indicadores posteriores de XP e recompensa.

[CI com controle 39362157076](https://github.com/Acccelll/Social_wars_test/actions/runs/39362157076);
[artefato do controle sem cliques](https://github.com/Acccelll/Social_wars_test/actions/runs/39362157076/artifacts/12237713271).

**Conclusão limitada e comprovada:** nessa configuração
`near_north`, o cliente original pode atacar e eliminar
automaticamente uma unidade hostil a curta distância.
Ainda não está demonstrado o alcance máximo de aggro ou
quais classes de unidade e terreno seguem o mesmo comportamento.

## 4. O que a cronologia dos GIFs e FX NÃO prova

O jogo pediu os SWFs de efeitos antes do combate.
Portanto, a ausência de um novo GET durante o tiro é
compatível com uso de recursos pré-carregados e **não é
evidência de ausência de projétil**.

Os screenshots comprovam **efeitos visuais, números de dano
e eliminação**, mas ainda não há instrumentação frame a frame
de `DefineSprite` ou correspondência inequívoca de pixels que
associe um gráfico específico ao `p.bulletAirBig` e
`b.bazookaSmall` durante um instante do vídeo. A definição
estática desses nomes no delegado original permanece válida,
com escopo distinto da observação dinâmica.

Além disso, capturas obtidas com Ruffle em CI sofrem
latência de renderização; os timestamps reais do relatório
devem ser priorizados sobre os nomes de screenshot
`after-200ms`, `after-650ms` etc.

## 5. Implementação e evidências

- `tests/original/client_fx_timing_5d8n.mjs` — HTTP GET,
  fases, comandos originais e snapshots.
- `tests/original/client_auto_combat_control_5d8n.mjs`
  — controle com **zero cliques em unidades**.
- `.github/workflows/original-fx-timing-5d8n.yml`
  — execução de observação e controle em vilas independentes.
- `.github/workflows/native-hostile-combat-5d8j.yml`
  — job adicional de verificação de regressão.
- `data/visual/runtime_fx_autocombat_5d8n.json` — resumo
  verificável dos eventos, tempos e limites.
- `docs/LOTE_5D_8N.md` (este documento).

Os ZIPs de capturas e vídeos ficam em artefatos e no
pacote de continuidade, não incorporados permanentemente ao
repositório de código.

## Próximo microlote — 5D.8O

Testar o **alcance e as regras de auto-aggro** do original,
com cenários descartáveis e sem cliques de combate:
variação da distância entre inimigos, atacante e terreno,
registrando se ocorre ataque, tempo até o primeiro golpe,
emissão de `kill` e persistência. Evitar inferir
distância de ataque apenas de um único exemplo.
