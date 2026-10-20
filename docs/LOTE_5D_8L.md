# Social Wars — Lote 5D.8L: cinco direções do Bushwacker

**Resultado: extração concluída e validada em CI.**
**Escopo:** sprite original, análise da estrutura e GIFs de prévia do
ataque. Não houve edição de SWF, envio artificial de comandos ao jogo
nem utilização de saves pessoais.

## Integridade e execução

- Fonte: `assets/sprites/1358_bushwacker.swf`, do pacote Social Wars 0.02a.
- SHA-256 conferido: `e9db23f98dcaa5cf81cbcdac85154fcb1da92a205b7d9047a5d420fb9d068c5e`.
- 1.158.582 bytes; **30 FPS** definidos no cabeçalho SWF.
- Timeline principal: **DefineSprite 1092**, rótulo `ATAQUE` iniciado
  no frame 11.
- [GitHub Actions — 39357276115](https://github.com/Acccelll/Social_wars_test/actions/runs/39357276115) passou
  nos testes de parser, vínculo de IDs e exportação de GIFs.
- [Artefato com os GIFs, atlas, JSON e linhas de dependência](https://github.com/Acccelll/Social_wars_test/actions/runs/39357276115/artifacts/12235179182).

## Cinco símbolos de ataque original

| Variante | Frame no sprite 1092 | DefineSprite | Frames declarados | Frames exportados no GIF | Imagens visualmente distintas* | Filhos diretos |
|---|---:|---:|---:|---:|---:|---:|
| `E_attack` | 11 | 643 | 60 | 60 | 3 | 27 |
| `TE_attack` | 12 | 675 | 60 | 60 | 5 | 29 |
| `P_attack` | 13 | 716 | 60 | 60 | 3 | 31 |
| `T_attack` | 14 | 752 | 60 | 60 | 3 | 27 |
| `F_attack` | 15 | 786 | 60 | 60 | 10 | 25 |

\* Contagem por SHA-256 dos pixels RGBA de cada quadro do GIF
renderizado pelo FFDec, **não** número de poses únicas do arquivo SWF.
Todas as 5 variantes foram extraídas com 60 quadros de GIF.
Nas prévias, `E`, `P`, `T` e `F` mostraram um ciclo
repetido a cada 18 frames; `TE` apresentou cinco imagens distintas
sem período exato detectado nesse recorte.
**O período de prévia não é necessariamente a duração da ação em runtime.**

## Elementos gráficos e dependências

Os cinco nomes são provenientes da `SymbolClass` original:

- `_1358_bushwacker_fla.E_attack_133`
- `_1358_bushwacker_fla.TE_attack_141`
- `_1358_bushwacker_fla.P_attack_145`
- `_1358_bushwacker_fla.T_attack_153`
- `_1358_bushwacker_fla.F_attack_159`

A análise de eventos `PlaceObject/RemoveObject` confirmou cada
um nos frames 11–15, profundidade 1, do sprite principal 1092.
Em conjunto, as cinco variantes referenciam **123 IDs diretos**,
dos quais **3, 611, 621, 642** aparecem em todas as variantes.
O ID **611** possui o nome simbólico
`_1358_bushwacker_fla.cascus_135`; isso não o torna projétil.
Os detalhes por frame, IDs individuais e posicionamentos estão no
`attack_timelines.json.gz` do artefato.

**Não identificamos com segurança** um `DefineSprite` de projétil
ou impacto. A presença de um filho específico de uma direção
não basta para afirmar que é disparo, arma ou partícula.

## Comparação com combate original 5D.8J

A [gravação confirmada do combate](https://github.com/Acccelll/Social_wars_test/actions/runs/39353491847)
mostra o Bushwacker disparando contra o Reaper Drone, com efeitos
visuais antes do comando `kill` nativo do objeto de mapa 42.
O servidor removeu o alvo do save.

Os GIFs deste lote mostram o mecha em cada uma das cinco
variantes de orientação, permitindo uma **comparação visual
qualitativa** com o vídeo. Ainda não há evidência técnica para
atribuir um frame e ID direcional exatos a cada instante da
gravação, pois orientação, escala, frame interno e o efeito
do tiro podem ser controlados dinamicamente pelo ActionScript.

O código original distingue `IsoUnit.playGunAnimation`,
`IsoFightingElement.shootProjectile` e
`IsoFightingElement.doProjectileDamage`. Isso reforça a
necessidade de seguir as definições de projétil e o carregamento
dos efeitos, além da timeline de corpo recuperada aqui.

## Arquivos criados/atualizados no repositório

- `tools/directional_attack_5d8l.py`
- `tools/directional_attack_5d8l_test.py`
- `.github/workflows/directional-attack-5d8l.yml`
- `data/visual/directional_attack_5d8l.json`
- `docs/LOTE_5D_8L.md`

O workflow produz artefatos, **não comita animações licenciadas
diretamente ao Git**. Inclui:
- cinco `frames.gif` de 60 quadros;
- `attack_direction_atlas.png`, usando quadros 1, 6, 7, 12,
  13, 16 e 19 para expor alterações reais de pose;
- `attack_timelines.json.gz` com eventos estáticos;
- `report.json` com hashes, status e diversidade visual.

## Próximo microlote 5D.8M

Rastrear `ProjectileDefinition` e o carregamento de FX no
ActionScript original. Localizar arquivos e símbolos das
partículas de disparo/impacto, exportar candidatos de modo
controlado, e só associar IDs aos eventos da gravação quando
existir evidência suficiente. A recriação completa do
cliente independente ainda não está concluída.
