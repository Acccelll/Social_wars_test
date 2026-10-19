# Lote 5D.8F — Botão OK e janela da missão desbloqueada no Ruffle

**Resultado: concluído.** O cliente original permaneceu intacto e a tela
“RESCUE YOUR COMRADE!” foi dispensada no Chromium/Ruffle.

## 1. Decompilação dirigida do SWF original

A distribuição Social Warriors 0.02a foi analisada com JPEXS FFDec 26.3.0,
sem editar o arquivo. O workflow de índice de ActionScript
[39320622043](https://github.com/Acccelll/Social_wars_test/actions/runs/39320622043)
recuperou **11 classes** de controle de UI/tutoriais.

Distinções verificadas:

- **PopupTutorialMC**: classe visual ligada ao SWF, declara componentes
  como \`butNext\` e campos de texto; o construtor não registra
  eventos do botão.
- **popups.PopupTutorial**: registra evento MOUSE_DOWN em
  \`butNext.hitZone\`; controla condições de etapas de tutorial.
- **core.TutorialMain**: contém \`nextStep()\`, \`endTutorial()\` e
  sequências orientadas de passos.
- **popups.PopupMissionInfo**: registra \`MouseEvent.MOUSE_UP\`
  em \`btnOk\`, chamando \`closeWindow()\` e disparando
  \`Event.CLOSE\`.
- **managers.PopupManager**: recebe \`Event.CLOSE\`, remove
  a janela ativa e desbloqueia sua fila.

A classe \`PopupMissionInfo\` corresponde fortemente ao layout do modal
de missão apresentado na captura, mas **não foi instrumentada a
identidade do MovieClip no runtime**. O índice de classes e métodos
está em [data/visual/tutorial_as3_index_5d8f.json](../data/visual/tutorial_as3_index_5d8f.json).
Os arquivos decompilados completos ficam em artefatos temporários do
GitHub Actions, não no repositório.

## 2. Causa observada do clique anterior não funcionar

A gravação no Ruffle mostrou uma camada de aviso própria do emulador,
informando que a aceleração de hardware estava desativada. A camada
aparecia **por cima da janela e do botão da missão** quando o cursor
entrava no player.

O ensaio separou os eventos de ponteiro, a 760×600:

| Captura | Resultado |
|---|---|
| Antes de interagir | Modal “Rescue Your Comrade!” aberto |
| Mover mouse sobre OK | Ruffle exibe aviso de aceleração de hardware |
| Primeiro clique, soltar botão | Aviso desaparece; modal segue aberto |
| Segundo clique independente no OK | **Modal desaparece; HUD, terreno e mechas visíveis** |

A comparação automática encontrou **0%** de alteração na área do
diálogo após o primeiro clique e **89,8668%** de alteração após o
segundo. Também verifiquei visualmente a captura final: o mapa
ficou acessível. Essa observação é evidência de desbloqueio do
cliente **sem patch de SWF ou alteração da lógica AS3**.

O workflow [39321595058](https://github.com/Acccelll/Social_wars_test/actions/runs/39321595058)
concluiu com \`success\`. O [pacote de evidências](https://github.com/Acccelll/Social_wars_test/actions/runs/39321595058/artifacts/12220326999)
contém \`event-before.png\`, \`event-hover.png\`, \`event-down.png\`,
\`event-up.png\`, \`event-second-up.png\` e \`session.webm\`.

## 3. Limites e próximos passos

O resultado elimina o bloqueio de interface encontrado no Lote 5D.8D
na sessão de teste. **Não** demonstra que uma unidade recebeu uma
ordem de movimento ou que um sprite executou animação de ataque.

**Próximo micro-lote 5D.8G:** configurar o teste para liberar o aviso
do Ruffle antes de operar o mapa, selecionar uma das unidades da
vila descartável, dirigir um deslocamento pela interface e verificar
requisição \`move\` oriunda do cliente, posição persistida e sequência
visual. Comparar a animação com o ID do SWF somente quando houver
evidência suficiente. Preservar o arquivo original e os saves do usuário.
