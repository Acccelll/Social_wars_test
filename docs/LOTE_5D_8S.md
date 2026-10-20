# Social Wars — Lote 5D.8S: vida, dano e eliminação como eventos distintos

**Concluído:** o lote confirmou no SWF original a cadeia completa de vida/dano, recuperou a classe real da barra de vida e regravou os confrontos leste/norte com capturas mais densas. O novo ensaio **também eliminou o Reaper Drone no cenário leste**, que na rodada anterior tinha permanecido vivo durante a janela monitorada.

## 1. Fonte e integridade

- SWF original `assets/flash/Basesec_1.5.4.swf` — SHA-256 `e4ce0218920a30fceee85ba750df3eedffa3f90e977bd117655704e297e0dc77`, verificado antes da extração.
- FFDec **26.3.0**, ActionScript e P-code extraídos apenas em artefato temporário.
- Chromium com Ruffle e Flask original em loopback, saves clonados/descar­táveis; **sem clique nas unidades ou POSTs sintéticos de ataque**.
- [Workflow 39416511124](https://github.com/Acccelll/Social_wars_test/actions/runs/39416511124): **três jobs aprovados** (código de vida, cenário leste e cenário norte).

Artefatos: [AS3/P-code e índice de métodos](https://github.com/Acccelll/Social_wars_test/actions/runs/39416511124/artifacts/12261472743) · [combate leste](https://github.com/Acccelll/Social_wars_test/actions/runs/39416511124/artifacts/12260849039) · [combate norte](https://github.com/Acccelll/Social_wars_test/actions/runs/39416511124/artifacts/12261318278).

## 2. Implementação real recuperada do cliente

O lote exportou as sete classes originais:
`battle.HealthBar`, `battle.projectiles.AbstractProjectile`,
`core.Config`, `core.Particle`, `core.isoengine.IsoFightingElement`,
`core.isoengine.IsoUnit`, `core.isoengine.delegates.units.ProjectileDelegate`.

### O ciclo de ataque

1. `IsoFightingElement.shootProjectile()` cria projétil no `ProjectileManager`. Para os disparos configurados, um `landed.addOnce` pode chamar `doProjectileDamage`.
2. `doProjectileDamage()` verifica existência/vida do alvo, as posições de impacto e o `blastRadius`, antes de chamar `recibirAtaque()`.
3. `recibirAtaque()` aplica modificadores de combate, usa `calculateDamage()` e reduz `iHealth` da unidade.
4. `calculateDamage()` introduz variação aleatória de **8** (aproximadamente ±4), chance base de crítico **10%** e multiplicador crítico **1,5**; desconta defesa e retorna no mínimo **1** de dano, antes de restrições/efeitos adicionais.
5. `recibirAtaque()` pode acumular vários danos em `_damageToDisplay` e exibi-los por `_showDamageParticle()`. A partícula visual não é obrigatoriamente **um disparo = um número**: há bloqueio temporário por `frameParticleAttack` e `_canDisplayDamageParticle`.
6. `updateVida()` chama `barraVida.set(iHealth)`. Se a unidade recebeu dano, continua viva e `displayBarraVida` está ligado, a barra é exibida.
7. Quando `iHealth` chega a zero, `die()` gerencia a morte. Dependendo do ramo original, isso envolve remoção, experiência e recompensas.

Além disso, a passagem de HP pela faixa de **10%** pode disparar `nearDeath`. Em alvos imortais (`canDie`/configuração de depuração), o HP pode ser limitado a 1. Não há motivo para presumir que todo dano observado gere imediatamente um comando HTTP `kill`.

### `battle.HealthBar` original

É uma barra desenhada vetorialmente em Flash, com segmentos:

| Vida máxima | Divisões |
|---|---:|
| Até 200 | 4 |
| 201–400 | 8 |
| 401–600 | 12 |
| 601–800 | 16 |
| Acima de 800 | 20 |

- Cada divisão tem **4 px** de largura e a barra tem **4 px** de altura.
- O preenchimento é `currentValue/maxValue`, limitado ao intervalo **0–100%**.
- A paleta interpolada (da pior para a melhor condição) é:
  `#800000 → #FF0000 → #FFFF00 → #00FF00 → #008000`.
- O fundo vazio é cinza e as bordas/divisões são pretas.
- O método `setScale` compensa o zoom com `scaleX=scaleY=1/zoom`.
- A existência de uma barra visível/colorida no screenshot **não dá acesso direto ao valor de HP** da instância.

## 3. Experimento: duas execuções independentes

| Cenário | Posições iniciais | Comandos nativos persistidos | Resultado |
|---|---|---|---|
| `east_midshift` | Bushwacker (45,43), Reaper (60,43) | **`kill(42)`** aos 48,983 s | Reaper removido do save; nenhum `move` persistido |
| `north_original` | Bushwacker (55,45), Reaper (55,30) | **`move(41,55,40)` + `kill(42)`** aos 42,174 s | Movimento e remoção persistidos |

**Os tempos são relativos ao início do navegador**, não à primeira agressão; o sistema já executa combate enquanto descarta diálogos ou inicializa o mapa. Os snapshots possuem latência de captura variável sob o Ruffle.

### No leste: disparos, números de dano e barra decrescente

A sequência de imagens do `east_midshift` mostra o Bushwacker disparando, números de dano sobre ambas as unidades e a barra do Reaper Drone migrando de **amarelo para vermelho** antes do desaparecimento do drone. O ataque visual foi confirmado em várias capturas. Em alguns instantes o dano exibido no Bushwacker foi agrupado.

Neste ensaio, o cliente enviou `kill(42)` aos **48.983 ms**. A primeira amostragem de save que encontrou o inimigo ausente foi aos **50.476 ms**. Os screenshots rotulados `damage-00` até `damage-08` abrangem os momentos anteriores e posteriores; isso não permite recuperar os HP exatos por frame.

### No norte: movimento e morte confirmados no save

Foi emitido `move` para a posição **(55,40)** e, depois, `kill(42)` aos **42.174 ms**. Como o ataque ocorreu durante os diálogos, boa parte das novas capturas periódicas veio **depois** da morte. Portanto a rodada serve como referência de movimento/morte, mas não de cronologia minuciosa de cada hit.

## 4. Correção importante ao lote 5D.8R

No 5D.8R, `east_midshift` mostrou troca de tiros e números de dano, mas **não houve `kill` durante a janela observada**. Em 5D.8S, com uma nova sessão e captura mais prolongada, **o mesmo fixture terminou com `kill` persistido**.

Logo, o combate nessa situação **não é garantidamente não letal**, e a ausência de `kill` em uma rodada não estabelece um raio de detecção, capacidade de dano ou situação permanente. O jogo inclui variação aleatória, eventos de inicialização e estados de vida não persistidos a cada hit.

## 5. O que não foi demonstrado

- Leitura direta dos valores internos `iHealth` e `maxLife` em runtime;
- medição numérica precisa de cada hit por frame; a partícula pode agrupar danos;
- associação exata do pixel de projétil à timeline do arquivo `assets/fx/`;
- um cliente independente recompilado com o mesmo combate.

## 6. Arquivos de repositório e próxima etapa

- `tools/original_combat_health_5d8s.py` — extração auditável de HealthBar, dano e morte com verificação de SHA;
- `tests/original/client_visual_damage_5d8s.mjs` — snapshots temporizados, eventos, vídeo e inspeção do save;
- `.github/workflows/visual-damage-5d8s.yml` — dois confrontos isolados e exportação dirigida de ActionScript;
- `data/visual/combat_damage_lifecycle_5d8s.json` — regras, evidências e incertezas;
- `docs/LOTE_5D_8S.md` — este relatório.

**Próximo 5D.8T:** usar as regras documentadas para iniciar um modelo próprio de combate **deterministicamente testável em TypeScript**, inclusive dano, críticos, eventos, barra de vida e morte, mantendo a instrumentação do Flash como padrão de comparação. Uma reconstrução independente ainda não foi comprovada como equivalente.
