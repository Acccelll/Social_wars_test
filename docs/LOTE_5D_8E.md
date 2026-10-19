# Lote 5D.8E — Movimento persistido e pesquisa do modal

**Concluído como prova de movimentação no servidor; animação Ruffle pendente.**

## Resultado do teste original

A execução [39318650244](https://github.com/Acccelll/Social_wars_test/actions/runs/39318650244) terminou com sucesso em 19/10/2026, com 6 testes Python aprovados.

O script tools/original_move_probe_5d8e.py criou uma vila temporária pelo servidor Flask original, selecionou o Splinter Mech (item ID 1313, índice 41) e enviou um comando real MOVE via POST para o endpoint original /dynamic/menvswomen/srvsexwars/command.php.

| Prova | Valor |
|---|---|
| Item de mapa | 41 |
| Unidade | Splinter Mech — ID de item 1313 |
| Coordenadas antes | (52,45) |
| Coordenadas depois | **(53,46)** |
| Objetos existentes | 44 |
| Objetos alterados | **1** |
| Campos da unidade além das coordenadas | sem alteração |
| Save persistido no disco | **sim** |
| Animação visual do cliente | **não comprovada** |
| ID interno de Sprite | **não identificado** |

O teste confere SHA-256 antes/depois e verifica que somente o item escolhido foi alterado. O código recusa qualquer servidor fora de loopback e exige a pasta de saves descartável vazia; nenhum save do usuário foi tocado.

[Prova JSON de movimentação](../data/visual/original_move_proof_5d8e.json) · [Workflow executado](https://github.com/Acccelll/Social_wars_test/actions/runs/39318650244)

## Investigação da janela “Rescue Your Comrade!”

O scanner de bytes originais encontrou no cliente Basesec_1.5.4.swf **2 ocorrências da frase “Rescue Your Comrade”** e **48 de “tutorial”**; encontrou 0 para ambos no SWLoader.swf.

Há indícios de símbolos/classes de interesse na aplicação principal: PopupTutorialMC, TutorialMain, tutorialMode e closeWindow. Esses nomes foram detectados nos bytes do SWF, mas **não foi decompilado o fluxo de controle que realmente processa o botão OK**. A causa da janela permanecer aberta ainda não está resolvida.

[Resultados de busca de strings](../data/visual/original_intro_text_5d8e.json) · [Logs temporários](https://github.com/Acccelll/Social_wars_test/actions/runs/39318650244/artifacts/12219730265)

## Limites e próximo lote

O comando original comprova a alteração persistida na vila, não que o Flash tenha exibido um deslocamento. O servidor original apenas confere a estrutura do prefixo do campo data, sem autenticá-lo criptograficamente; o teste é restrito ao servidor local isolado.

**Lote 5D.8F:** analisar especificamente a lógica de PopupTutorialMC/TutorialMain em ActionScript e verificar o comportamento do botão OK. Depois, só atribuir os estados de animação a sprites quando houver evidência visual confirmada.
