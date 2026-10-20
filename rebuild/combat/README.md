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

Abra [http://127.0.0.1:5179](http://127.0.0.1:5179) no navegador. O servidor é limitado a loopback e serve apenas os arquivos da demo e o JavaScript compilado. Para apenas gerar os módulos `dist/*.js` e declarações `.d.ts`, use `npm run build`.

## Conteúdo

- `src/model.ts`: `calculateDamage()`, `receiveAttack()`, `createCombatant()`, `advanceFrames()`, `finishDamageParticle()`, eventos de dano, HP, nearDeath e morte.
- `src/healthBar.ts`: `healthBarDivisions()`, `originalHealthColor()`, `healthBarView()`: propriedades e geometria da barra original, sem reutilizar os arquivos gráficos SWF.
- `src/rng.ts`: `seededRng()` e `sequenceRng()` para testes reproduzíveis. O original usa `Math.random()`; o algoritmo **xorshift32 aqui é próprio do protótipo**.
- `test/combat.test.mjs`: **16 testes automáticos** com Node Test Runner; TypeScript estrito verificado em compilação.
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

Próximo lote 5D.8U: importar parâmetros reais das unidades 1358/1376 e integrar o módulo ao primeiro runtime 2D com atualização de HP em tela, **sem** afirmar que há equivalência geral com a aplicação Flash.
