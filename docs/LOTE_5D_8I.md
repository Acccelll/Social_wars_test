# Lote 5D.8I — Observação de combate no cliente original

**Resultado: diagnóstico concluído; ataque/dano NÃO comprovados.**
**Data:** 2026-10-19 (execuções UTC 2026-10-20).
**Original:** Social Wars 0.02a, `assets/flash/Basesec_1.5.4.swf`, sem alterações.

## Objetivo

Testar se o cliente original no Chromium/Ruffle gera ordens nativas de combate,
altera HP ou elimina uma unidade oponente, mantendo o servidor Flask original,
saves descartáveis e sem comandos sintéticos de ataque.

## Código original analisado

No `command.py` do projeto AcidCaos, a rotina principal recebe uma lista
`commands` e implementa `move` (alteração de coordenadas), `sell`, `kill`,
`kill_iid` e `batch_remove`. Existe `end_attack` para o resultado
agregado de combate, mas **não há um branch individual `attack`** naquela
rotina. O cálculo de dano pode ocorrer no próprio cliente antes da persistência.
Logo, ausência de `attack` nas requisições não descarta animação/combate
interno: é necessário observar tela, HP e eventual `kill/sell/end_attack`.

Referência externa: https://github.com/AcidCaos/socialwarriors/blob/main/command.py

## Cenários reproduzíveis

O fixture `tools/seed_original_combat_5d8i.py` conserva os 40 itens originais
de `villages/initial.json` e adiciona apenas:
- Jogador, índice **41**: **Bushwacker**, item **1358**, lado **1**, tile **(55,45)**.
- Oponente, índice **42**: **Reaper Drone**, item **1376**, lado **3**, com três posições
  testadas: `near_east=(59,44)`, `near_north=(55,40)`,
  `near_west=(51,43)`.

Cada caso inicia em uma vila descartável. Não se usa save pessoal, nem se
modifica o SWF. O registrador observa requests `/command.php`, nomes de
comandos, mudanças de objeto e prints/vídeo.

## Três execuções

| Tentativa | GitHub Actions | Probes | `move` nativo | `kill/sell/end_attack` | Dano persistido |
|---|---|---:|---:|---|---|
| Posição leste | [39349462830](https://github.com/Acccelll/Social_wars_test/actions/runs/39349462830) | 14 | 1 | Não observado | Não |
| Norte e oeste | [39349850417](https://github.com/Acccelll/Social_wars_test/actions/runs/39349850417) | 28 (14 + 14) | 0 | Não observado | Não |
| Coordenadas calibradas — norte | [39350441517](https://github.com/Acccelll/Social_wars_test/actions/runs/39350441517) | 10 | 0 | Não observado | Não |

As três execuções passaram na infraestrutura/testes **de observação**. Um
workflow verde **não confirma um ataque**. Os `batch_remove` vistos na
inicialização não foram classificados como mortes: aparecem no bootstrap e
não removeram o alvo experimental.

## Inspeção visual — achado importante

1. No cenário `near_east`, o Reaper Drone ficava parcialmente atrás do
   painel inferior; os probes exploratórios não davam certeza de atingir o alvo.
2. Em `near_north`, o alvo ficou claramente visível, mas a grade exploratória
   não selecionava consistentemente o atacante.
3. A versão de coordenadas calibradas selecionou claramente **BUSHWACKER**:
   screenshot `probe-01-selected.png` mostrou a ficha `6500/6500` e as
   quatro habilidades/armas do Bushwacker.
4. O clique seguinte sobre o Reaper Drone mostrou a borda de seleção e
   o painel **REAPER DRONE — 700/700**, `probe-01-after-1900ms.png`.
   O clique **trocou o alvo selecionado**, não disparou ataque observado.
5. O `report.json` final do teste calibrado confirmou
   `target_object_changed=false`, `target_removed_from_save=false`,
   nenhum `kill`, `sell` ou `end_attack`, sem erros de página.

Conclusão: **seleção funcional dos dois lados; ataque não reproduzido**.
Ainda não é possível afirmar se a causa é modo de batalha, ação de habilidade
necessária, tutorial ou regras do mapa/campanha. Essas são hipóteses.

## Arquivos versionados

- `tools/seed_original_combat_5d8i.py`
- `tests/original/native_combat_5d8i.mjs`
- `tests/original/native_combat_targeted_5d8i.mjs`
- `.github/workflows/native-original-combat-5d8i.yml`
- `data/visual/native_combat_observation_5d8i.json`
- `docs/LOTE_5D_8I.md`

### Provas externas preservadas

- [Leste — ZIP artefato](https://github.com/Acccelll/Social_wars_test/actions/runs/39349462830)
- [Norte e oeste — ZIP artefato](https://github.com/Acccelll/Social_wars_test/actions/runs/39349850417)
- [Norte, cliques direcionados — ZIP artefato](https://github.com/Acccelll/Social_wars_test/actions/runs/39350441517)

Nenhum POST de ataque/dano foi fabricado. O relatório não armazena cookies,
tokens, USERID ou o conteúdo de saves completos.

## Próximo microlote: 5D.8J

Estudar o cliente e a UI de batalha, diferenciar **seleção/inspeção** de
**ordem de ataque** e identificar se há habilidade a ativar ou transição
de modo de missão. Reproduzir o estado de combate no SWF **antes** de
atribuir animação, dano ou persistência. Evitar novos probes cegos de
coordenadas; começar pela máquina de estados/fluxo AVM2 e evidência visual.
