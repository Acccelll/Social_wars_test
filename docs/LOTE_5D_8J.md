# Lote 5D.8J — Primeiro combate original confirmado no Chromium/Ruffle

**Estado: concluído, ataque e eliminação comprovados.**
**Cliente:** Social Wars 0.02a, `assets/flash/Basesec_1.5.4.swf`, SHA-256
`e4ce0218920a30fceee85ba750df3eedffa3f90e977bd117655704e297e0dc77`,
**não modificado**.

> **Nota de correção — lote 5D.8N:** o 5D.8J continua comprovando o
> combate visual e o `kill(42)` do cliente original. Porém,
> um teste posterior instrumentado detectou `kill` **antes do
> primeiro clique manual no inimigo**, e um controle independente
> eliminou o mesmo alvo com **zero cliques nas unidades**.
> Portanto, as interações do 5D.8J não demonstraram que o clique
> causou o ataque; o combate automático é suficiente no cenário
> investigado. Consulte [5D.8N](LOTE_5D_8N.md).


## Descoberta que resolveu 5D.8I

A decompilação do SWF original em FFDec 26.3.0 encontrou:

| Constante AVM2 (`core.Constants`) | Valor original |
| --- | ---: |
| `PLAYER_SELF` | 1 |
| `PLAYER_ENEMY` | **2** |
| `PLAYER_NEUTRAL` | **3** |

**Falha do fixture anterior:** no lote 5D.8I, o Reaper Drone havia
sido colocado como **3 (neutro)**. Não era um alvo da equipe inimiga.
Esses testes não demonstravam falha de combate; apenas seleção/inspeção de
uma unidade neutra. Os históricos anteriores foram preservados.

## Fluxo de ataque recuperado do ActionScript

- `core.isoengine.IsoInteractiveElement.clickItem`, em estado `STATE_INQUIRE`,
  ao clicar uma unidade **PLAYER_ENEMY** com pelo menos uma unidade própria
  selecionada no `Base.Main.hitArray`, chama
  `Base.Main.startMovements(tile, selectedUnits, PLAYER_SELF)`.
- `core.Base.startMovements` monta a formação de aproximação ao alvo e
  chama `IsoUnit.setMove` para cada unidade selecionada.
- `core.isoengine.IsoUnit.setMove` verifica o `PlayerID` do alvo;
  se diferente do próprio e do neutro, marca `bAttacking`,
  atribui `TargetElement` e procura rota pela malha A*.
- `IsoUnit.updateAttack` executa a verificação periódica de ataque;
  `IsoUnit.attackNormal` invoca `IsoFightingElement.recibirAtaque`.
- `IsoFightingElement.recibirAtaque` aplica modificadores, atualiza
  `iHealth`, exibe partículas de dano e pode invocar `die` ao chegar
  a zero.
- `battle.IAAttack` e `IsoUnit.IA_Attack` são os caminhos IA
  complementares, utilizados para aquisição e aproximação a alvos.
- O tutorial original, `core.TutorialMain`, possui
  `STEP_CLICK_ENEMY = 116`, `STEP_WAIT_BATTLE = 118` e cria
  soldados Orc inimigos com `spawnEnemies()` próximo dos tiles
  `(61,28)` e `(63,28)`.

**Fonte da análise:** decompilação direta do SWF original, não a
reconstrução experimental AS3. [Workflow de extração
39352875836](https://github.com/Acccelll/Social_wars_test/actions/runs/39352875836)
e [artefato contendo AS3 e P-code](https://github.com/Acccelll/Social_wars_test/actions/runs/39352875836/artifacts/12234560766).
O ID de item 1358/1376 não é o ID interno `DefineSprite`.

## Reexecução corrigida com inimigo real

- Fixture em `tools/seed_original_hostile_5d8j.py`, a partir de
  `villages/initial.json` original com seus 40 objetos.
- Bushwacker próprio: índice **41**, item **1358**, `PlayerID=1`, tile `(55,45)`.
- Reaper Drone adversário: índice **42**, item **1376**,
  `PlayerID=2`, tile `(55,40)`.
- O testador `tests/original/native_hostile_combat_5d8j.mjs` usa
  **cliques reais** no cliente SWF executado pelo Ruffle/Chromium;
  não envia POSTs `attack/kill` artificiais.
- Capturas mostram **Bushwacker selecionado**, projéteis/impactos
  na região do Reaper Drone, experiência e desaparecimento do alvo.
- Servidor original observou comando `kill`, com argumento
  `object_reference=42` e `reason='u'`; o objeto 42 foi **removido
  do save**. Houve `add_xp_unit` também originado pelo cliente.
- Foram necessários **2 pares de cliques**. Foram observadas
  **5 requisições** ao endpoint `command.php`. Erros de página: **0**.
- O relatório e vídeo no artefato fazem a correspondência entre
  o comando de eliminação e a persistência.

**Execução confirmatória:**
[GitHub Actions 39353157986](https://github.com/Acccelll/Social_wars_test/actions/runs/39353157986)
([arquivo de evidências original](https://github.com/Acccelll/Social_wars_test/actions/runs/39353157986/artifacts/12233034780)).

## Resultado e limites

**Comprovado:** seleção, ordem ofensiva de uma unidade própria contra
um verdadeiro inimigo, efeitos visuais de combate, `kill` emitido
pelo cliente e remoção persistida pelo servidor original.

**Não comprovado ainda:** o `DefineSprite` exato dos efeitos de
tiro/dano, identificação de cada frame/estado de ataque, equivalência
de P-code com AS3 recompilado, ou execução do combate em um cliente
reconstruído do zero. O SWF original executado no Ruffle ainda é a
referência funcional.

A ausência de `attack` como comando individual em `command.py`
é compatível com a mecânica comprovada: o golpe e o HP são calculados
no cliente e a eliminação pode ser sincronizada por `kill`.

## Arquivos versionados

- `tools/battle_state_as3_5d8j.py`
- `.github/workflows/battle-state-5d8j.yml`
- `tools/seed_original_hostile_5d8j.py`
- `tests/original/native_hostile_combat_5d8j.mjs`
- `.github/workflows/native-hostile-combat-5d8j.yml`
- `data/visual/original_combat_proof_5d8j.json`
- `docs/LOTE_5D_8J.md` (este arquivo)

## Próximo microlote — 5D.8K

Correlacionar **efeitos de disparo, impactos, dano e eliminação**
da gravação ao asset e aos estados de sprite de
`1358_bushwacker.swf` e `1376_reaperDrone.swf`, antes de propor
alterações de gameplay ou recompilar todo o cliente. Preservar
sempre originais e saves de usuário.
