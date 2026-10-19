# Lote 5C — Compatibilidade nominal e contrato de movimentação

## Natureza deste lote

Há dois tipos diferentes de verificação:

1. **Semântica original fundamentada em AVM2:** os resultados recuperados do cliente
   `Basesec_1.5.4.swf`, especialmente `IsoUnit.aNodes` setter #1788,
   `IsoUnit.IA_Move` #1741 e `NodesPath` Proxy.
2. **Execução do nosso código em Ruffle:** apenas em tipos de **teste** que
   reproduzem os nomes e interfaces analisados; ainda NÃO é teste executando
   o `IsoUnit` binário real original.

### Base original de referência

| Item | Fonte / evidência | Comportamento conhecido |
|---|---|---|
| `com.socialpoint.astar.NodesPath` | AS3 original em P-code de NodesPath | herda Proxy, guarda Array interno, tem `isAI` |
| `core.isoengine.IsoUnit.aNodes` | AVM2 getter #1787, setter #1788 (54 bytes) | propriedade nominal `NodesPath`; ao receber caminho não-vazio chama `delegate.onMoveStart(route.isAI)` |
| `core.isoengine.IsoUnit.IA_Move` | AVM2 método #1741 | seta `walkPath.isAI=true` ANTES de atribuir `aNodes` |
| `core.isoengine.IsoUnit.setMove` | AVM2 método #1723 | lê ponto inicial, usa `TileToPixel`, consome `splice(0,1)` |
| `core.isoengine.delegates.AbstractUnitDelegate` | AVM2 método `onMoveStart` #2179 | executa lógica associada a início de movimento |

Essas afirmações são observações anteriores do P-code, **não** equivalência
binária provada pela nossa compilação.

## Implementação deste lote

O diretório `as3/contract_harness/` contém **doubles isolados** com nomes
nominais iguais aos do SWF real para testar tipagem, acesso ao Proxy e ordem
`isAI -> aNodes -> onMoveStart`.

- `NodesPath.as`: tipo nominal fictício `com.socialpoint.astar.NodesPath`.
- `IsoUnit.as`: tipo nominal fictício `core.isoengine.IsoUnit`.
- `AbstractUnitDelegate.as`: observador fictício dos eventos.
- `RecoveredRouteAdapter.as`: faz cópia explícita da rota experimental
  `NodesPathRecovered` ao tipo nominal de teste.
- `ContractProbe.as`: testa 14 casos de contrato em runtime ActionScript 3.

**Nunca empacotar essas classes homônimas com o SWF original**: provocariam
colisões de tipos. A integração real deverá usar o `NodesPath` original,
por exemplo com biblioteca SWC ou compilação de fonte integral recuperada,
sem incluir a implementação fictícia.

## Aceite e limitações

A CI compila `ContractProbe.swf` separadamente de `AS3Probe.swf`.
O mesmo player Ruffle 0.7.1 e Chromium devem executar os cenários.
Resultados são comunicados por `ExternalInterface`.

Os testes validam **compatibilidade de interfaces no sandbox**, não paridade
de caminhos e animação com o jogo real. A fase seguinte precisa extrair os
dados e/ou instrumentar execução do SWF original e comparar:
- sequência de pontos da rota (`x,y`),
- obstáculos, terreno, diagonais e destinos bloqueados,
- `isAI`, `aNodes`, `onMoveStart`,
- eventos de atualização e conclusão do movimento.

O jogo do usuário e seus salvamentos permanecem intocados.
