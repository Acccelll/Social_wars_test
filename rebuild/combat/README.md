# Social Wars — Combate independente (5D.8T)

**Protótipo independente em TypeScript.** Port parcial das regras de dano, vida e barra de HP observadas no SWF original Social Wars 0.02a. Isto **não** é uma recompilação do cliente Flash ou reconstrução completa de gameplay.

## Executar

Requer Node.js 22 ou superior e npm:

```bash
cd rebuild/combat
npm install
npm test
npm run demo
```

Abra **http://127.0.0.1:5179/arena** para a primeira arena 2D com unidades desenhadas no Canvas, projéteis, dano e HP. A rota **http://127.0.0.1:5179/** mantém a demonstração simples anterior. O servidor é limitado a loopback e serve apenas os arquivos da demo e o JavaScript compilado. Para apenas gerar os módulos `dist/*.js` e declarações `.d.ts`, use `npm run build`.

## Arena 2D e estatísticas comunitárias

O [5D.8U](../../docs/LOTE_5D_8U.md) recuperou no patch ativo do servidor comunitário AcidCaos as estatísticas de Bushwacker 1358 (6500 HP, ataque 138, defesa 1, alcance 10, intervalo 35, velocidade 7) e Reaper Drone 1376 (700 HP, ataque 36, defesa 1, alcance 11, intervalo 30, velocidade 8). **Não foram confirmadas como valores históricos da Social Point.**

A nova `demo/arena.html`, `demo/arena.js`, `src/scene.ts` e `src/unitCatalog.ts` implementam uma pequena cena própria com mechas vetoriais (placeholders), tiros, contra-ataques, barra e morte calculados por `receiveAttack()`. Também incluem testes determinísticos de modelo e Playwright/Chromium que captura três momentos da arena. `attack_interval` é interpretado como frames **somente nesta demo**, ainda sem paridade do tempo do Flash.

## Conteúdo

- `src/model.ts`: `calculateDamage()`, `receiveAttack()`, `createCombatant()`, `advanceFrames()`, `finishDamageParticle()`, eventos de dano, HP, nearDeath e morte.
- `src/healthBar.ts`: `healthBarDivisions()`, `originalHealthColor()`, `healthBarView()`: propriedades e geometria da barra original, sem reutilizar os arquivos gráficos SWF.
- `src/rng.ts`: `seededRng()` e `sequenceRng()` para testes reproduzíveis. O original usa `Math.random()`; o algoritmo **xorshift32 aqui é próprio do protótipo**.
- `test/combat.test.mjs`: **25 testes automáticos** com Node Test Runner; TypeScript estrito verificado em compilação.
- `demo/` e `serve.mjs`: pequena demonstração no navegador, alimentada pelo módulo próprio.
- `tsconfig.json` e `package.json`: build ESM tipado, sem dependências de runtime, compilador `typescript@5.8.3` em devDependency.

## Mapeamento com código recuperado

SWF verificado `assets/flash/Basesec_1.5.4.swf`, SHA256 `e4ce0218920a30fceee85ba750df3eedffa3f90e977bd117655704e297e0dc77`, análise [5D.8S](../../docs/LOTE_5D_8S.md).

| API independente | Trecho original | Correspondência implementada |
|---|---|---|
| `calculateDamage` | `IsoFightingElement.calculateDamage` | Duas rolagens RNG (crítico antes da variância), 10%, 1,5x, variância 8, defesa, mínimo 1 |
| `receiveAttack` | `recibirAtaque` | Vida, gate delegado, escudo básico, nearDeath, invencibilidade, morte e eventos |
| `finishDamageParticle` | `_onDamageParticleFinished` | Agrupamento de valores de dano e liberação de exibição |
| `healthBarView` | `battle.HealthBar` / `updateVida` | Divisões de 4px, interpolação de cor, ocultação a HP cheio/zero e compensação de zoom |
| `seededRng` | Nenhum equivalente recuperado | Reprodutibilidade de testes apenas, não equivalência do sorteio Flash |

**Fora do escopo atual:** controle de unidades, IA e pathfinding, firing rate, projéteis/FX, terreno, targeting, multiplicadores específicos (`best_against`, bônus XP/cerco/tutorial), áudio, sprites, missões, persistência no servidor e sincronização. `attackMultiplier`/`bonusAttack` são pontos de extensão recebidos do futuro delegado.

Os valores da demo (HP 200/220, ataque 32/23, defesa 5/7) são **ilustrativos** e não foram extraídos das estatísticas originais dos personagens.

## Evidência de execução

[GitHub Actions 5D.8T — compilação, 16 testes e smoke HTTP](https://github.com/Acccelll/Social_wars_test/actions/workflows/independent-combat-5d8t.yml).

O lote 5D.8U entregou os dois parâmetros do servidor e a primeira arena 2D independente. Próximo 5D.8V: integrar sprites e efeitos originais extraídos aos estados de ataque/HP, sem confundir placeholder e efeitos confirmados no SWF.


## Lote 5D.8V — Imagens originais como pacote visual opcional

A rota **http://127.0.0.1:5179/arena** agora aceita sprites e FX PNG extraídos por FFDec dos SWFs originais (Bushwacker 1358, Reaper Drone 1376, bala, laser e impactos). O motor de combate **continua sendo independente do Flash**. Se a pasta opcional `original-visual/` faltar, o navegador mostra automaticamente os desenhos vetoriais e o botão **Estilo** permite comparar os dois modos.

O pacote completo entregue no [lote 5D.8V](../../docs/LOTE_5D_8V.md) já vem com `original-visual/manifest.json` e 12 atlas PNG. Para reconstruir a partir dos GIFs comprovados de 5D.8K e 5D.8M, use `tools/prepare_original_visuals_5d8v.py` com Pillow e as opções `--states`, `--fx`, `--out rebuild/combat/original-visual`. Os GIFs derivam da distribuição original 0.02a; nenhuma cópia de SWF é comitada ao Git.

**Limite:** os quadros FFDec são amostras de sub-timelines, não a execução AVM2 da animação completa. O Bushwacker apresenta variação de quadros de ataque, mas as quatro amostras do Reaper Drone contêm somente uma pose renderizada por estado; a velocidade de ataque da demo, offsets de projeção, movimento de projéteis e sincronização ainda não foram validados como originais. O sprite interno visível do `p.laserMassiveDrone` é selecionado em vez do wrapper público transparente.

Validação: [workflow 5D.8V](https://github.com/Acccelll/Social_wars_test/actions/workflows/original-sprite-arena-5d8v.yml) executa o jogo próprio com 12 atlas, verifica dano, alternância de visual, efeitos, eliminação, 25 testes e screenshots de Chromium. Os artefatos expiram; após isso, os GIFs devem ser reexportados dos SWFs com os utilitários FFDec versionados em `tools/`.


## Lote 5D.8W — Cinco poses reais do Reaper Drone

A exportação dirigida da timeline raiz `DefineSprite 1654` recuperou **25 quadros raiz** do SWF original 1376, sem modificar os assets: 5 variações em cada estado `QUIETO`, `ANDAR` e `ATAQUE`, e apenas 1 visual diferente em `MUERTE` e `PICAR`. Os cinco quadros correspondentes de `QUIETO`, `ANDAR` e `ATAQUE` são **idênticos entre si** — são poses estáticas/direcionais, não três animações temporais distintas.

Na arena `/arena`, o botão **Reaper: direção 1/5** permite alternar manualmente as poses reais, mantendo combate, HP, disparos e fallback vetorial do motor próprio. O mapeamento 1–5 para ângulos de mundo ainda não foi recuperado; por isso a IA **não** força uma direção inventada.

[Relatório técnico 5D.8W](../../docs/LOTE_5D_8W.md) · [workflow original e browser](https://github.com/Acccelll/Social_wars_test/actions/workflows/reaper-root-frames-5d8w.yml). Os PNGs são gerados como artefato opcional, fora do Git; pacote de continuidade já inclui os 25 quadros e arquivos executáveis.


## Lote 5D.8X — Orientação automática e posição de tiro

O [lote 5D.8X](../../docs/LOTE_5D_8X.md) recuperou a regra autêntica do ActionScript: **oito direções lógicas**, cinco poses por estado e espelhamento horizontal para as direções 6–8. O Reaper Drone passa a encarar automaticamente o alvo na arena, usando a direção lógica `LEFT=7` e **pose 3 espelhada** quando o Bushwacker está à esquerda. Os botões **Reaper: manual** e **Reaper: direção automática** permitem testar o resultado. A arena mantém seu próprio motor TypeScript sem Flash.

Além disso, o scanner `tools/projectile_markers_5d8x.py` encontrou **26 eventos `projectilePoint*`** no SWF do Bushwacker, inclusive cinco marcadores das poses de ataque, e **nenhum marcador nomeado** no SWF do Reaper Drone. O fallback original é `(x, y-bmd.height*0.6)`. O runtime usa uma **aproximação** desse fallback para o Reaper com a altura gráfica **161 px da demo**, não comprovadamente a altura nativa do Flash. A posição real dos cinco marcadores do Bush depende de matrizes dos sprites pais e ainda não foi resolvida.

A versão 5D.8X foi aprovada no [CI com **35/35 testes**](https://github.com/Acccelll/Social_wars_test/actions/runs/39462605558), dois jobs de verificação e Chromium real com 13 imagens e zero erros.

**Próximo 5D.8Y:** calcular os pivôs/markers do Bushwacker a partir da hierarquia de matrizes dos sprites SWF e validar o alinhamento de FX antes de automatizar caminho isométrico.


## Lote 5D.8Y — Inspetor original dos cinco pontos de disparo do Bushwacker

Extraímos os **cinco caminhos de matriz únicos** `DefineSprite1092 → (643/675/716/752/786) → projectilePoint`. `src/bushMuzzle.ts` fornece offsets **locais da timeline original**, sem assumir posição de mundo ou zoom. O novo **http://127.0.0.1:5179/muzzle** mostra os cinco pontos, os oito sentidos e o espelhamento; a arena `/arena` contém um link para ele. As coordenadas só podem ser aplicadas a um tiro com a origem e escala do root sprite medidas; essa calibração é a próxima etapa. [Relatório 5D.8Y](../../docs/LOTE_5D_8Y.md) · [CI 40/40 testes](https://github.com/Acccelll/Social_wars_test/actions/runs/39472749217).
