# Social Wars — Lote 5D.8M: identificação dos projéteis e impactos originais

**Resultado: análise estática e extração dos quatro FX concluídas; identificação dos efeitos em runtime ainda pendente.**

Não foram editados arquivos SWF nem saves do usuário. O lote parte
do combate real já confirmado no [5D.8J](LOTE_5D_8J.md) e das animações
direcionais recuperadas em [5D.8L](LOTE_5D_8L.md).

## 1. Fonte: código ActionScript original

O SWF principal `Basesec_1.5.4.swf` teve SHA-256
`e4ce0218920a30fceee85ba750df3eedffa3f90e977bd117655704e297e0dc77`
confirmado pela análise no GitHub Actions. A decompilação dirigida
recuperou **23 classes originais**, incluindo `ProjectileDefinition`,
`ProjectileManager`, `DelegatesManager`,
`BushwackerDelegate`, `ReaperDelegate` e `ProjectileDelegate`.
O relatório indexou **77 métodos relevantes**.

[Execução da decompilação (CI 39360234686)](https://github.com/Acccelll/Social_wars_test/actions/runs/39360234686).
[Artefato AS3 e P-code](https://github.com/Acccelll/Social_wars_test/actions/runs/39360234686/artifacts/12237330282).

### Como o cliente original carrega um projétil

O caminho estático comprovado no código original é:

1. `DelegatesManager.registerDelegate(...)` define os projéteis da unidade.
2. O delegate invoca `ProjectileManager.addMachinegun` ou
   `IsoFightingElement.shootProjectile`.
3. `ProjectileManager.loadAsset` solicita
   `Base.Main.apfx + "fx/" + effectName + ".swf"`.
4. O `ProjectileManager.addProjectile` instancia o projétil;
   `addBlast` pode criar o impacto quando ele chega.
5. `IsoFightingElement.doProjectileDamage` verifica o alvo e
   pode chamar `recibirAtaque`. Os estados e o resultado final
   dependem do sistema de combate do cliente.

A passagem pelo código não substitui telemetria de um determinado
frame de jogo. É o **vínculo de definição** dos efeitos, não
uma prova de qual GIF/frame aparece em cada instante.

## 2. Correspondência exata das unidades do experimento

| Unidade | ID gameplay | Delegate efetivo | Projétil de ataque normal | Impacto definido |
|---|---:|---|---|---|
| **Bushwacker** | **1358** | `BushwackerDelegate` | `p.bulletAirBig` | `b.bazookaSmall` |
| **Reaper Drone** | **1376** | `ProjectileDelegate` | `p.laserMassiveDrone` | `b.laserBlue` |

Para o Bushwacker, `DelegatesManager` registra
`MACHINEGUN_BIG.clone` com `P_BULLET_AIR_BIG`, velocidade 120,
escala do projétil 4 e `BLAST_BAZOOKA_SMALL`.
O `BushwackerDelegate.onAttack` usa `addMachinegun`.

Para o Reaper Drone, `DelegatesManager` registra
`ProjectileDelegate` com `BeamDefinition(P_LASER_MASSIVE_DRONE,
7,0,20,0.5,false,Beam).blast(BLAST_LASER_BLUE)`.
A classe `ProjectileDelegate.onDelayedAttack` chama
`self.shootProjectile(projectileDefinition)`.

**Distinção essencial:** `ReaperDelegate` pertence ao **Reaper
(item 1375)**, não ao **Reaper Drone (item 1376)**. Atribuir ao
drone o projétil de `ReaperDelegate` seria incorreto.

Os quatro identificadores `p.` e `b.` foram recuperados de
`ProjectileDefinition`. Eles são nomes de classes de efeito,
**não IDs `DefineSprite` globais**.

## 3. SWFs físicos encontrados e extraídos

O segundo workflow buscou os caminhos exatos em
`assets/fx/` na distribuição 0.02a, verificou a integridade,
leu as timelines e exportou recursos via FFDec 26.3.0.

| SWF em `assets/fx/` | Bytes | FPS | ID `SymbolClass` local | Sprites internos | Recursos gráficos exportados |
|---|---:|---:|---:|---:|---:|
| `p.bulletAirBig.swf` | 1.860 | 24 | 4 | 2 | 4 |
| `b.bazookaSmall.swf` | 12.931 | 24 | 16 | 2 | 16 |
| `p.laserMassiveDrone.swf` | 1.121 | 24 | 5 | 3 | 5 |
| `b.laserBlue.swf` | 1.590 | 24 | 7 | 2 | 7 |

Os quatro hashes SHA-256 individuais estão registrados em
[`data/visual/projectile_fx_mapping_5d8m.json`](../data/visual/projectile_fx_mapping_5d8m.json).
Esses FX usam **24 FPS**, diferentes dos **30 FPS** dos SWFs
de corpo das unidades no lote anterior.

[CI 39360481633 — sucesso](https://github.com/Acccelll/Social_wars_test/actions/runs/39360481633).
[Artefato de exportação de FX](https://github.com/Acccelll/Social_wars_test/actions/runs/39360481633/artifacts/12236729193).

### Inspeção visual

A exportação mostrou:
- `p.bulletAirBig`: projétil amarelo estreito.
- `b.bazookaSmall`: explosão amarela com partículas e fumaça.
- `p.laserMassiveDrone`: feixe claro visível no
  `DefineSprite 3`; a prévia GIF do símbolo público
  `DefineSprite 5` ficou transparente. Portanto, a
  prévia do símbolo 3 é **uma composição interna**, não
  reprodução direta do símbolo público.
- `b.laserBlue`: efeito de impacto circular azul.

Os resultados visuais são **prévias extraídas do SWF**,
sem comprovação de sincronização temporal com o vídeo Ruffle.

## 4. O que foi efetivamente comprovado

**Sim:**
- configuração de ataque normal das duas unidades no
  ActionScript original, com suas classes de delegate corretas;
- existência dos quatro arquivos FX na versão 0.02a;
- hashes, classe simbólica interna, dimensões/timelines e
  extração de formas/sprites;
- separação entre projétil e efeito de impacto.

**Ainda não:**
- se cada arquivo foi carregado pela rede durante exatamente
  o ataque registrado no 5D.8J (a inicialização pode
  pré-carregar FX sem dispará-los);
- a correspondência de pixels e frames do impacto no vídeo
  Ruffle com uma timeline específica;
- implementação da mesma mecânica num cliente próprio
  recompilado ou totalmente reconstruído.

## 5. Arquivos adicionados ao repositório

- `tools/projectile_flow_as3_5d8m.py`
- `.github/workflows/projectile-flow-5d8m.yml`
- `tools/original_fx_assets_5d8m.py`
- `.github/workflows/original-fx-assets-5d8m.yml`
- `data/visual/projectile_fx_mapping_5d8m.json`
- `docs/LOTE_5D_8M.md`

Os SWFs e gráficos exportados **não foram adicionados ao Git**;
permanecem apenas nos artefatos de execução e no pacote
compacto de continuidade.

## Próximo microlote 5D.8N

Instrumentar no Chromium/Ruffle as solicitações
`assets/fx/` durante o combate em cenário descartável;
separar preloads de recursos de eventos de ataque;
verificar visualmente os momentos de disparo e impacto
em uma gravação temporizada, sem alterar o SWF.
