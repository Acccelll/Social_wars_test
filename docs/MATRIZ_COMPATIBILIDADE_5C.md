# Matriz de correspondência 5C — AVM2 original vs protótipo

Esta matriz **não** significa que o jogo original foi recompilado. A coluna
'Resultado' indica execução dentro do **ContractProbe test double**, usando
os nomes de classe originais em uma árvore separada.

| Contrato observado no SWF original | Verificação no protótipo | Resultado | Limitação |
|---|---|---|---|
| `NodesPath` usa `flash.utils.Proxy` | `proxy_index`, `proxy_shift_unshift`, `splice_removes_tile` | 3 PASS | Nomes coincidem, bytecode da classe não |
| Tipo nominal `com.socialpoint.astar.NodesPath` | `nominal_type`, `typed_setter_getter` | 2 PASS | Um SWF distinto compila o double, não o tipo original |
| Setter `IsoUnit.aNodes` aceita `NodesPath` | `typed_setter_getter` | PASS | Somente compila contra o double |
| Caminho vazio não inicia movimento | `empty_no_event`, `cleared_route_no_event` | 2 PASS | Observador double |
| Caminho manual chama `onMoveStart(false)` | `manual_event` | PASS | Efeitos reais (som/IA) não testados |
| `isAI` é consultado na atribuição da rota | `no_event_on_flag_mutation`, `reassignment_uses_isAI` | 2 PASS | O `IA_Move` original não foi invocado |
| `IA_Move` define `isAI=true` antes do setter | `adapter_preserves_isAI`, `adapter_assignment_ai_event` | 2 PASS | Ordem verificada apenas no adaptador |
| Converter rota preserva posições | `adapter_copies_coordinates`, `adapter_is_independent_copy` | 2 PASS | Sem integração à unidade real |
| O setter permite `null` sem evento | `nullable_setter` | PASS | Simulação baseada no P-code |

## Escopo original ainda SEM comparação de runtime

- Sequência dos tiles `x,y` de caminhos longos e diagonais.
- Desvios por colisão, água, terreno intransponível ou unidade ocupando tile.
- A* original: custo `g`, ordenação `sortOn('f')`, `ResolvePath`,
  `paintedNodes` e cancelamento por tempo.
- `IsoUnit.updateMove`: velocidade, pixel, eventos e fim de movimento.
- Ações em subclasses específicas de `AbstractUnitDelegate` (`JunkBot`,
  `RedBaron`).

## Critério necessário para declarar paridade

Executar **a mesma entrada** em:
1. cliente SWF original de referência (`Basesec_1.5.4.swf`);
2. implementação `AStarRecovered`.

Comparar listas completas de tiles, sinalizadores `isAI`, eventos,
destino efetivo e status da busca. Divergências devem ser registradas
como regressões reais; resultados do double não substituem essa etapa.

## Evidências de 5C.1

GitHub Actions: https://github.com/Acccelll/Social_wars_test/actions/runs/39262967632

- `AS3Probe.swf`: **8 PASS / 0 FAIL**.
- `ContractProbe.swf`: **15 PASS / 0 FAIL**.
- Dois SWFs compilados pelo `mxmlc` e executados no Chromium/Ruffle 0.7.1.
- Nenhum arquivo do jogo original ou salvamento foi modificado.
