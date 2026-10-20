# Social Wars — 5D.8P: limite observado de auto-aggro e `Config.AGGRO_RANGE`

**Resultado:** concluído. **11 cenários originais** executados sem selecionar nem comandar as unidades; recuperado o valor de configuração **`Config.AGGRO_RANGE:uint = 10`** diretamente do ActionScript 0.02a.

Os resultados **não** estabelecem um raio de agressividade universal de 10 ou 17 tiles: há diferenças entre posições no mapa e caminhos de decisão que não se resumem à constante.

## Integridade / evidências

- Cliente: `assets/flash/Basesec_1.5.4.swf` original (SHA-256 `e4ce0218920a30fceee85ba750df3eedffa3f90e977bd117655704e297e0dc77`) em Ruffle/Chromium, servidor Flask original.
- Vila inicial original: 40 objetos; Bushwacker amigo **1358** no objeto 41, tile **(55,45)**, `PlayerID=1`; Reaper Drone inimigo **1376** no objeto 42, `PlayerID=2`.
- A única variável controlada em cada grupo foi a posição do inimigo. **Saves e servidores reinicializados por cenário**, sem editar SWF, sem ataques sintéticos, sem cliques nas unidades. Foram realizados somente cliques para fechar os diálogos necessários à tela inicial.
- [CI principal 39409756959 — 3 jobs aprovados](https://github.com/Acccelll/Social_wars_test/actions/runs/39409756959), [CI de controles orientais 39410457546 — aprovado](https://github.com/Acccelll/Social_wars_test/actions/runs/39410457546).
- [Decompilação original](https://github.com/Acccelll/Social_wars_test/actions/runs/39409756959/artifacts/12258752179) · [GIF/capturas/vídeos norte](https://github.com/Acccelll/Social_wars_test/actions/runs/39409756959/artifacts/12258747905) · [leste](https://github.com/Acccelll/Social_wars_test/actions/runs/39409756959/artifacts/12259700246) · [controles leste](https://github.com/Acccelll/Social_wars_test/actions/runs/39410457546/artifacts/12258858595).

## 1. Tabela consolidada da execução

Na tabela, **Sim** significa comando nativo `kill(42)` e remoção persistida do inimigo do save. **Não observado** significa ausência de `kill` e de movimento persistido durante o período medido, não prova de inexistência de detecção de alvo.

| Distância inicial em tiles | Norte — alvo em (55,45−d) | Leste — alvo em (55+d,45) |
|---:|---|---|
| 5 | **Sim**, sem movimento persistido (5D.8O) | **Sim**, sem movimento persistido (controle 5D.8P) |
| 10 | **Sim**, sem movimento persistido (5D.8O) | **Sim**, sem movimento persistido (controle 5D.8P) |
| 15 | **Sim**, Bushwacker avançou 5 tiles (5D.8O) | **Não observado**, por ~23,2 s |
| 16 | **Sim**, com movimento nativo | **Não observado**, por ~23,3 s |
| 17 | **Sim**, com movimento nativo | **Não observado**, por ~23,2 s |
| 18 | **Não observado**, por ~23,0 s | **Não observado**, por ~23,2 s |
| 19 | **Não observado**, por ~23,3 s | **Não observado**, por ~23,2 s |
| 20 | **Não observado**, por ~25,3 s (5D.8O) | Não testado |

Todos os 8 cenários intermediários foram repetidos em outra execução; o padrão de presença ou ausência do `kill` foi o mesmo. Em norte 16, o Bushwacker foi persistido em **(54,42)** numa execução e em **(53,42)** na outra: a trajetória exata variou, embora o alvo tenha morrido nas duas. Em norte 17, houve movimento para **(53,42)**.

O controle do leste mostra que não existe um impedimento geral de atacar nessa direção: a **5** e **10 tiles** houve `kill` normal. Entretanto, a **15 tiles** o comportamento difere do resultado norte na mesma distância inicial.

### Cuidados com a cronometragem

Nos cenários que eliminaram o inimigo, o combate pôde ocorrer durante a inicialização e o fechamento dos diálogos, antes de começar a janela de amostragem. Os tempos de `kill` nos relatórios contam desde a abertura do navegador, **não desde o primeiro disparo**.

Em distâncias sem `kill`, observaram-se ~23 segundos de amostras após os diálogos, com saves sem mudança de posição. Não conseguimos confirmar visualmente o inimigo distante em todos os screenshots, porque ele pode ficar **fora da região de câmera**. Portanto, os registros persistidos e os comandos capturados são a principal evidência.

## 2. ActionScript original: o que está realmente codificado

**`core.Config.as`, linha 116:**

```actionscript
public static const AGGRO_RANGE:uint = 10;
```

O FFDec exportou também `core.isoengine.IsoEngine`, `IsoFightingElement`, `IsoUnit` e `isoUtils.CheckFunctions`, com hashes e P-code no artefato.

- **`IsoFightingElement.acquireNewTarget()`**: quando nenhum raio é passado, usa `Math.max(Config.AGGRO_RANGE, this.iAttackRange)`.
- **`IsoEngine.bucleNearestUnits()`**: calcula distância entre centros dos objetos por raiz quadrada, convertida para `int`, e só mantém candidatos dentro do raio fornecido.
- **`IsoEngine.getElementScore()`**: pontuação base `1000 - distancia`; aplica +150 a unidades, +100 a prefeitura, +75 a produtores, +50 a edificações armadas; candidatos sem valor podem ter `score=-1`. **`getNearestTarget`** ordena e aplica a verificação de elegibilidade.
- **`IsoEngine.fCheckNearestTarget()`**: exige time correspondente, alvo vivo, atacável, marcado como elegível e não carregado em contêiner.
- **`IsoUnit.IA_Attack()`**: quando o alvo está além de `iAttackRange`, tenta deslocar a unidade para uma formação de ataque.
- **Uma chamada específica de `IsoUnit`** usa `acquireNewTarget(tx,ty,iAttackRange + 2)`; não assumimos que essa chamada controla todas as circunstâncias.

Os atributos do catálogo original identificam **`attack_range=10`** para Bushwacker 1358 e **`attack_range=11`** para Reaper Drone 1376. Isso descreve configuração, não a distância de aquisição observada sob todos os gatilhos.

## 3. Interpretação responsável

Os dados oferecem um **limite experimental dependente da região/orientação**, não uma regra universal de que o máximo é 17 tiles:

- O norte registrou combate com 17 tiles de separação inicial, e ausência de `kill` com 18 tiles.
- O leste registrou combate a 10 tiles, e ausência de `kill` com 15.
- Terrain/pathfinding, inicialização da unidade, área ativa/câmera, propriedades de time e sequências automáticas do próprio jogo são explicações ainda abertas.
- Em eixos ortogonais a distância Manhattan coincide com a distância euclidiana entre os centros das células. Não implica, porém, caminho A* livre ou visibilidade garantida.
- Ausência de eventos persistidos **não exclui ataques sem morte**, danos voláteis nem aquisição sem aproximação dentro do período observado.

**Não alterar o `Config.AGGRO_RANGE` original para 17** nem reconstruir artificialmente um raio anisotrópico com base apenas nestes dados.

## 4. Arquivos versionados

- `tools/seed_auto_aggro_5d8p.py` e `tools/seed_aggro_east_control_5d8p.py`: fixtures determinísticos e isolados.
- `tests/original/client_aggro_threshold_5d8p.mjs` e `client_aggro_east_control_5d8p.mjs`: gravação, amostras do save e comandos nativos, sem cliques em unidades. As leituras de JSON de save tentam novamente quando há escrita simultânea pelo servidor original.
- `tools/original_aggro_as3_5d8p.py`: extração da constante e fluxo de aquisição.
- `.github/workflows/aggro-boundary-5d8p.yml` e `aggro-east-controls-5d8p.yml`.
- `data/visual/aggro_boundary_5d8p.json`: valores, resultados reproduzidos e limites.
- `docs/LOTE_5D_8P.md`: relatório atual.

## Próximo microlote — 5D.8Q

Investigar **ativação por região/câmera versus regras de IA**, mantendo a mesma distância em pontos diferentes da vila. Medir o momento de criação/ativação do alvo, a linha de visão e a origem dos eventos `IA_Attack`, evitando converter as observações desta etapa em um raio artificial. A reconstrução independente do cliente permanece trabalho separado.
