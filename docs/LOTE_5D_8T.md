# Social Wars — lote 5D.8T: primeiro núcleo independente de combate TypeScript

**Concluído.** Este lote inicia efetivamente a **reconstrução das mecânicas** sem Ruffle/Flash. O módulo é novo, isolado da distribuição original e testado por GitHub Actions.

## Entregas executáveis

| Arquivo | Papel |
|---|---|
| [`rebuild/combat/src/model.ts`](../rebuild/combat/src/model.ts) | Dano, crítico, vida, nearDeath, barra, partículas e evento de morte |
| [`rebuild/combat/src/healthBar.ts`](../rebuild/combat/src/healthBar.ts) | Segmentos de 4px, cor, escala e visibilidade da barra |
| [`rebuild/combat/src/rng.ts`](../rebuild/combat/src/rng.ts) | RNG determinístico injetável para teste |
| [`rebuild/combat/test/combat.test.mjs`](../rebuild/combat/test/combat.test.mjs) | 16 testes automatizados Node |
| [`rebuild/combat/demo/index.html`](../rebuild/combat/demo/index.html) | Demo interativa independente dos SWFs |
| [`rebuild/combat/serve.mjs`](../rebuild/combat/serve.mjs) | Servidor HTTP local restrito a 127.0.0.1 |
| [`.github/workflows/independent-combat-5d8t.yml`](../.github/workflows/independent-combat-5d8t.yml) | CI: TypeScript, testes e smoke HTTP |

### Como executar

```bash
cd rebuild/combat
npm install
npm test
npm run demo
```

Abra **http://127.0.0.1:5179**. Não há serviço externo, estado de conta ou jogo Flash necessário.

### Validação real

- [GitHub Actions #39425028520](https://github.com/Acccelll/Social_wars_test/actions/runs/39425028520) — **success**.
- TypeScript `5.8.3` compilado com `strict`, `noUncheckedIndexedAccess` e `noEmitOnError`.
- **16 testes passaram**, **zero falhas**.
- Smoke de `serve.mjs`: HTML, código da demo e módulo compilado servidos com **HTTP 200**.
- [Artefato do compilado e da demo](https://github.com/Acccelll/Social_wars_test/actions/runs/39425028520/artifacts/12265073518).

## Fidelidade e limites

As rotinas do jogo **0.02a** foram comparadas diretamente com `core.isoengine.IsoFightingElement` e `battle.HealthBar`, exportadas no [lote 5D.8S](LOTE_5D_8S.md), hash original `e4ce0218920a30fceee85ba750df3eedffa3f90e977bd117655704e297e0dc77`.

O núcleo reproduz apenas o **escopo implementado e testado**:

- Sorteia primeiro a chance de crítico de **10%** e depois a variância `Math.random()*8-4`; crítico usa `abs(variância)` e multiplica por **1,5**.
- Aplica defesa, `Math.round`, mínimo **1 de dano**; inclui coerção inteira da base do escudo.
- Atualiza HP, limiar de quase-morte a **10%**, proteção contra morrer e invencibilidade, morte e eventos discriminados.
- Agrupa números de dano pendentes, com intervalo nominal de **15 frames**, em vez de presumir um número visual por disparo.
- Calcula barras com **4/8/12/16/20** divisões conforme vida máxima, cor interpolada original `#800000 → #ff0000 → #ffff00 → #00ff00 → #008000`, e visibilidade apenas quando danificado e vivo.

**Não implementado ainda:** IA, escolha de alvo, ataques automáticos, caminho de movimento, FX e projéteis, sincronização de frames, modificadores complexos `best_against`/XP/cerco/tutorial, persistência/recompensa. A demo é uma interface demonstrativa com atributos inventados e explicitamente rotulados, **não uma reprodução das estatísticas exatas dos personagens**.

Não afirmamos equivalência matemática completa com todo o `recibirAtaque`: ele contém ramificações específicas de unidade, missão, cerco e modificadores que serão tratadas nos próximos lotes. O RNG xorshift32 do protótipo serve somente para testes determinísticos e não é o `Math.random` exato do Flash.

## Próximo lote — 5D.8U

Recuperar do catálogo original os **parâmetros exatos** do Bushwacker 1358 e Reaper Drone 1376 (HP/defesa/ataque/alcance/cadência), e ligar o núcleo novo a uma tela 2D com dano/vida visualmente atualizados. Manter original no Ruffle somente como **referência**, não como motor da implementação independente.
