# Lote 5D.8G — Movimento pelo cliente original (Ruffle)

**Resultado: a ordem nativa de movimento foi comprovada; identificação visual do sprite ainda pendente.**
**Data:** 2026-10-19. **Original SWF não alterado.**
**Execução CI:** https://github.com/Acccelll/Social_wars_test/actions/runs/39329666474
**Artefato:** https://github.com/Acccelll/Social_wars_test/actions/runs/39329666474/artifacts/12224430675

## O que foi realizado

1. Executado o servidor Flask original AcidCaos em `127.0.0.1:5055`, com vila descartável e quatro unidades instaladas pelo fixture 5D.8C.
2. Carregado o `assets/flash/Basesec_1.5.4.swf` sem modificações em Chromium + Ruffle.
3. Enviados dois cliques independentes no botão OK (primeiro consome o aviso do Ruffle e o segundo fecha o modal Flash).
4. Instrumentado `tests/original/client_move_5d8g.mjs` para observar **apenas requisições do próprio navegador** a `/dynamic/menvswomen/srvsexwars/command.php`. O script não constrói nem envia `move` via HTTP.
5. Experimentados pares de cliques seleção→destino e analisado o save original isolado antes/depois. As capturas e o vídeo estão anexados à execução CI.

## Resultado de rede e persistência — confirmado

| Evidência | Resultado |
| --- | --- |
| Tentativas de cliques | 3 pares |
| Requisições a `command.php` observadas | 3 |
| Comandos nativos `move` | **1** |
| Origem da requisição `move` | **navegador, a partir da UI original** |
| Índice do objeto alterado | **42** |
| ID de item do jogo | **1358 (Bushwacker)** |
| Coordenadas salvas antes | **(55,45)** |
| Coordenadas salvas depois | **(52,41)** |
| Outros objetos de mapa alterados | **0** |
| Correspondência requisição ↔ mudança de save | **sim** |
| Erros no browser capturados | **0** |

A requisição `move` observada contém o índice **42** e o destino **(52,41)**, idênticos aos valores persistidos no save. Isso confirma a cadeia cliente original → comando HTTP → servidor original → save. O evento foi produzido por clique; **não** pelo probe sintético do lote 5D.8E.

## Vídeo, sprite e limites — não confundir

A gravação de 46,28 segundos (`session.webm`), as dez capturas PNG e o relatório JSON estão no artefato do workflow. A inspeção visual posterior de quadros da gravação identificou **deslocamento de uma unidade representada no mapa** após os cliques. A interface da captura exibe o painel **REAPER DRONE**, ao passo que o comando persistido altera o item **Bushwacker 1358**. Essas evidências não bastam para atribuir com segurança o movimento visual ao item 42 ou a um `DefineSprite` específico.

Portanto:
- **Confirmado:** pedido `move` emitido pelo cliente e persistido com índice 42; movimento visível de entidade na sessão capturada.
- **Ainda não confirmado:** identidade exata da entidade animada em relação ao índice 42; vínculo da animação com o `DefineSprite` interno; conjunto de frames do estado `walk/move`.
- Os booleanos conservadores do relatório automático **`animation_visual_confirmed:false`** e **`sprite_define_id_confirmed:null`** permanecem corretos para correlação de animação por ID, até uma verificação direcionada.

O relatório foi minimizado: nomes de ações, índice, destino e hashes de save apenas. Nenhum cookie, USERID, token, conteúdo completo de save ou POST bruto foi persistido no relatório.

## Continuação — 5D.8H

1. Determinar correspondência UI selecionada ↔ `map_index` real, distinguindo Bushwacker, Reaper Drone e Splinter Mech na vila densa.
2. Criar cenários separados (uma unidade por vila ou posições muito distantes), para seleção sem sobreposição ou ícones do tutorial.
3. Gravar sequências de frames de movimentação e associar aos SWFs/IDs apenas depois da confirmação por evidência temporal.
4. Depois, investigar uma ordem **attack/damage** pelo cliente original, ainda sem envio sintético.

Não alterar o cliente Flash/SWF, nem usar saves pessoais.
