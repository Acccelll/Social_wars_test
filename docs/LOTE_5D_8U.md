# Social Wars — lote 5D.8U: mechas reais no catálogo e primeira arena 2D própria

**Estado: concluído, com validação no GitHub Actions.** Este lote usa os atributos cadastrados dos dois personagens no servidor comunitário AcidCaos e apresenta uma arena 2D própria, com disparos, impacto, HP e vitória calculados pelo motor TypeScript do [lote 5D.8T](LOTE_5D_8T.md). **Não é um cliente Flash recompilado.**

## 1. Proveniência dos atributos

Os valores foram extraídos de quatro arquivos em `AcidCaos/socialwarriors`:
- `config/main.json`;
- `config/patch/unit_patch.json`;
- `config/patch/patches.txt` (confirma que `unit_patch` está ativo);
- `tools/sw_unit_patch.csv` (confirma vida, ataque, alcance, velocidade e intervalo).

O script [`tools/extract_unit_stats_5d8u.py`](../tools/extract_unit_stats_5d8u.py) confere os IDs, parseia `properties`, valida o patch ativo, verifica os valores do CSV e registra os hashes SHA-256 dos quatro arquivos.

**Descoberta importante:** os IDs **1358** e **1376** **não aparecem em `config/main.json` sem patch**. São introduzidos em `unit_patch.json` da reconstrução comunitária. Portanto os números abaixo são confirmados para o **servidor comunitário efetivo**; a autenticidade histórica dos números nos servidores originais da Social Point ainda não foi demonstrada.

| Campo | Bushwacker 1358 | Reaper Drone 1376 |
|---|---:|---:|
| Nome do asset | `1358_bushwacker` | `1376_reaperDrone` |
| Tipo | `ROBOT` | `AIR_VEHICLE` |
| `life` | **6500** | **700** |
| `attack` | **138** | **36** |
| `defense` | **1** | **1** |
| `attack_range` | **10** | **11** |
| `velocity` | **7** | **8** |
| `attack_interval` | **35** | **30** |
| `best_against` | `ft_ground` | `ft_ground` |
| `best_against_mult` | 1 | 1 |

Artefato de extração independente, incluindo atributos adicionais e hashes: [GitHub Actions — valores verificados](https://github.com/Acccelll/Social_wars_test/actions/runs/39428441819/artifacts/12267150974). Registro permanente: [`data/rebuild/unit_stats_5d8u.json`](../data/rebuild/unit_stats_5d8u.json).

## 2. Arena 2D totalmente independente

A cena nova está em `rebuild/combat/demo/arena.html` e `arena.js`, com a lógica de simulação TypeScript em `rebuild/combat/src/scene.ts`, o catálogo auditável em `unitCatalog.ts` e as funções de HP/dano do 5D.8T.

A interface mostra:
- Bushwacker e Reaper Drone desenhados diretamente em **Canvas 2D**, sem sprites Flash; HUD com estatísticas confirmadas do patch;
- projéteis próprios em formato de bala e laser, com movimento na tela;
- **dano somente na chegada do projétil**, calculado por `receiveAttack()` (defesa, críticos e variação aleatória);
- atualização da barra do inimigo após o impacto; números de dano, efeito de acerto e desaparecimento do drone ao morrer;
- ataque manual clicando nos botões ou nos mechas, partida automática, pausa, avanço por frame e reinício determinístico;
- temporizador de ataque usando os valores `attack_interval` do patch, **interpretados como frames apenas para esta demo**, uma simplificação que ainda não estabelece os tempos reais do Flash;
- estado de combate serializável para verificações automáticas e eventos com origem identificável.

A distância visual inicial escolhida é de **9 tiles**, para que as duas unidades consigam disparar sem acrescentar a IA de perseguição, que ainda não foi reconstruída. Os personagens vetoriais são placeholders próprios, não reprodução 1:1 dos sprites oficiais.

### Execução local

Requer Node.js 22+:

```bash
cd rebuild/combat
npm install
npm test
npm run demo
```

Abrir **http://127.0.0.1:5179/arena** para a arena nova. A rota principal `/` continua oferecendo a demonstração básica do 5D.8T.

O servidor HTTP aceita somente loopback e não requer SWF, back-end Flask ou autenticação.

## 3. Verificação automatizada

Workflow [`combat-units-5d8u.yml`](../.github/workflows/combat-units-5d8u.yml):

1. Clona a configuração original do servidor comunitário em ambiente descartável; extrai as duas unidades e valida a origem.
2. Compila o módulo TypeScript em modo estrito; executa **25 testes unitários**, incluindo todos os 16 do 5D.8T e 9 para o catálogo/cena.
3. Baixa o JSON auditado e compara, campo a campo, os números do código TypeScript compilado com os números reais de `unit_patch`.
4. Abre `/arena` com Playwright/Chromium real, confirma Canvas não vazio, testa disparo manual, aguarda o impacto antes de confirmar a perda de HP e simula um combate automático até a vitória do Bushwacker.
5. Gera capturas `arena-ready.png`, `arena-hit-manual.png`, `arena-victory.png` e arquiva o código, JS compilado e imagens, sem incluir SWFs.

Na execução de referência [39428441819](https://github.com/Acccelll/Social_wars_test/actions/runs/39428441819), a extração da fonte, os **25 testes**, a compilação TypeScript e o navegador real passaram sem erros de JavaScript. A workflow definitiva adicionou a comparação binária de valores e a publicação do pacote completo de código-fonte, testada na execução final do lote.

## 4. Limitações explícitas

**O que está funcionando:** catálogo de unidades, HP real do servidor comunitário, dano/defesa e críticos no motor próprio, tiros visuais, transições de vida, morte e interação na arena.

**O que permanece pendente:** sprites e timelines originais integrados ao Canvas, IA de aquisição e perseguição fiel ao ActionScript, colisões e caminho A*, semântica exata de `attack_interval`, efeitos do `best_against`, projéteis Flash autênticos, outros tipos de unidades, infraestrutura de missões/economia, áudio, mapa isométrico completo, persistência e ligação ao jogo principal.

O disparo **bala versus laser**, seu tempo de percurso e o movimento nos sprites vetoriais são simulações visuais próprias. O RNG de testes `xorshift32` não replica o `Math.random` do Flash. Nem o cliente original nem os recursos SWF foram modificados.

## 5. Próximo lote: 5D.8V

Substituir os mechas vetoriais por **frames originais já extraídos e validados** no 5D.8K/5D.8L (Bushwacker e Reaper Drone), alinhando QUIETO/ANDAR/ATAQUE/MUERTE e as direções quando possível. Integrar os efeitos do 5D.8M, com atlas e offsets documentados, mantendo a possibilidade de alternar para placeholders até a verificação do enquadramento e da escala. Só depois evoluir a aquisição de alvo e deslocamento pela IA original.
