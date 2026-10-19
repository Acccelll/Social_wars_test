# Lote 5D.8A — Captura do cliente original

Foi criada uma instrumentação **externa** para executar a distribuição 0.02a original com Chromium e Ruffle, sem editar SWFs nem o servidor.

## Ambiente e limitações

O GitHub Actions baixa o release oficial e inicia o servidor Flask original em pasta descartável, criando uma vila de teste. Os salvamentos do usuário não são lidos. A instrumentação intercepta somente a resposta HTML de play.html para inserir o Ruffle e um painel de observação.

O relatório registra URLs por caminho (sem query, sem payloads nem tokens), presença do player e screenshots. O painel permite ao usuário marcar início/fim de espera, movimento, ataque, dano, destruição e construção, além de cliques relativos à área do Flash.

**Isso não descobre automaticamente o character_id do MovieClip.** As ações são rótulos fornecidos pelo operador e ainda precisam ser correlacionadas visualmente com os sprites inventariados. A execução em CI verifica o carregamento; não afirma ter realizado ou validado combate.

## Windows — sessão de jogo com marcações

1. Inicie o executável oficial social-warriors.exe normalmente em 127.0.0.1:5055.
2. Faça backup dos salvamentos, ou use uma vila separada: comandos no jogo original podem alterar saves normalmente.
3. Na pasta deste repositório, instale Node 20+, rode npm install na pasta tests/ruffle e npx playwright install chromium.
4. Execute: node tests/original/record.mjs --duration 180 --out dist/original-observation
5. No novo Chromium, faça login e marque cada ação no painel superior direito antes e depois de executá-la.

Os arquivos report.json e PNGs ficam em dist/original-observation, ignorados pelo Git. Não grave URLs com query, cookies ou respostas da API no relatório.

## Aceite

Verificar primeiro a execução do workflow Original Social Wars Ruffle Boot 5D.8. Uma prova de bootstrap demonstra que o servidor, SWF loader e browser foram usados, não que animações de ataque sejam identificáveis.

Próxima etapa: revisar vídeos/screenshots com a fila de IDs da pasta data/visual e preencher apenas relações sustentadas por evidências diretas.
