# Lote 5D.8H — Identidade visual das unidades e ordens nativas isoladas

**Resultado: concluído.** O jogo SWF original rodou em Chromium/Ruffle contra o
servidor Flask original, com **três vilas independentes e descartáveis**. O
cliente, e não o script de teste, originou as ordens de movimento.

**CI:** https://github.com/Acccelll/Social_wars_test/actions/runs/39347814190
**Provas (vídeo/WebM, PNGs, relatório por cenário, fixtures):**
https://github.com/Acccelll/Social_wars_test/actions/runs/39347814190/artifacts/12232061894

## Ambiente e isolamento

- Original: distribuição Social Wars 0.02a; `assets/flash/Basesec_1.5.4.swf`, **sem modificações**.
- Repositório usado para executar o teste: `Acccelll/Social_wars_test`.
- Motor: Chromium + Ruffle, com Flask original em `127.0.0.1:5055`.
- Três cenários criados por `tools/seed_original_unit_5d8h.py` a partir de
  **uma cópia preservada** de `villages/initial.json`.
- Cada cenário conserva os 40 objetos iniciais e acrescenta **apenas uma**
  unidade de jogador, no tile inicial `(55,45)`, índice `41`. O cenário
  anterior, com vários mechas simultaneamente, deixa de induzir seleção ambígua.
- Entre cenários, o servidor é desligado, o save descartável é removido e uma
  nova vila é criada. O jogo não utiliza saves pessoais.
- `tests/original/client_move_5d8h.mjs` apenas clica no Flash e observa
  as requisições reais do navegador para `command.php`, sem enviar POSTs `move`.

## Resultado verificado

| Cenário (nome na UI original) | ID do item | Índice da unidade | Pares de cliques | Comandos `move` nativos | Coordenadas inicial → final | Ordem/save |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| **BUSHWACKER** | 1358 | 41 | 2 | 2 | `(55,45)` → `(54,35)` | ✅ |
| **REAPER DRONE** | 1376 | 41 | 6 | 1 | `(55,45)` → `(58,40)` | ✅ |
| **SPLINTER MECH** | 1313 | 41 | 5 | 2 | `(55,45)` → `(55,39)` | ✅ |

A execução terminou **success**; zero erros de página capturados nos três
cenários. O ID do objeto de mapa é **41** para todos porque **não se tratam da
mesma vila**: cada cenário cria sua própria vila isolada a partir do original.

### Observações por unidade

- **Bushwacker:** o log contém dois `move`: destino intermediário `(55,43)`
  e destino final persistido `(54,35)`.
- **Reaper Drone:** `move` para `(58,40)`.
- **Splinter Mech:** duas ordens `move` para `(54,40)` e `(55,39)`
  registradas na mesma requisição; o save terminou em `(55,39)`.

Além da correspondência entre ID do item, requisição original e save, a
**inspeção visual manual dos quadros `final.png`** mostrou três modelos
distintos e o nome do painel inferior da UI de acordo com o fixture de cada
cenário: `BUSHWACKER`, `REAPER DRONE`, `SPLINTER MECH`.
Assim, a inconsistência visual de seleção do lote 5D.8G foi sanada **no contexto
dos cenários individuais**.

## Limites da prova

- O nome da **UI**, o **item de gameplay** e o **índice de mapa** estão
  correlacionados com os resultados acima.
- **Não foi determinado o ID `DefineSprite` interno**, nem o SWF responsável
  pelos frames visuais de cada animação.
- A gravação e os PNGs permitem inspecionar a movimentação em Ruffle, mas
  o teste automatizado **não identifica sozinho** a sequência de frames AVM2
  ou um estado de movimento. Os campos automáticos
  `animation_visual_confirmed=false`, `sprite_define_id_confirmed=null`
  permanecem conservadores.
- A simples presença de duas ordens em uma requisição **não** prova que todas
  as etapas intermediárias foram exibidas como animação.

## Arquivos criados

- `tools/seed_original_unit_5d8h.py`
- `tests/original/client_move_5d8h.mjs`
- `.github/workflows/isolated-original-unit-5d8h.yml`
- `data/visual/isolated_original_units_5d8h.json` (síntese estável)
- `docs/LOTE_5D_8H.md` (este documento)

No artefato CI estão `dist/5d8h/{bushwacker,reaper,splinter}/`, com o
vídeo `session.webm`, capturas `probe-*`, `final.png` e `report.json`.

## Próxima etapa proposta — 5D.8I

Isolar combate em vila descartável: selecionar unidade original, clicar em alvo
inimigo real, inspecionar requisições **attack/damage** produzidas pelo SWF,
salvar resultados e conferir mudanças de HP/estado sem forçar POST manual.
Depois prosseguir para mapear os estados/IDs das animações.
