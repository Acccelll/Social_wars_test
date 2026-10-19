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

## Execução validada

GitHub Actions: [39306732074](https://github.com/Acccelll/Social_wars_test/actions/runs/39306732074)
— sucesso. O navegador iniciou `play.html`, injetou Ruffle sem
alterar o arquivo original, mostrou o elemento `ruffle-embed`
e carregou a referência principal `Basesec_1.5.4.swf` via SWLoader.

Metadados do SWLoader observados: AVM2/AS3, SWF 10, 760×600,
30 quadros/s, 1 quadro declarado. Esse cabeçalho é do SWLoader;
**não** é a contagem de quadros do jogo inteiro.

Foram observadas requisições de SWF para 2 dos 14 arquivos da galeria:
`assets/sprites/0022_tower_1_m.swf` e
`assets/sprites/0026_command_center_1_m.swf`.
Há três linhas correspondentes (torre IDs 85 e 52; comando ID 21)
na [matriz CSV](../data/visual/runtime_boot_presence_5d8.csv),
mas uma requisição à origem do SWF **não confirma** que esses sprites
específicos foram desenhados, animados ou associados a ações.

O teste capturou marcas **sintéticas** `other` de início/fim
e capturas PNG para demonstrar o observador em cima da página real.
A associação movimento/ataque/dano só será realizada após sequência
dirigida no jogo e comparação visual com as prévias catalogadas.

Arquivos da execução: [pacote de evidências do GitHub
Actions](https://github.com/Acccelll/Social_wars_test/actions/runs/39306732074/artifacts/12213468689).
Contém `report.json`, capturas e um log do servidor descartável.

### Próximo lote 5D.8B

1. Capturar uma sessão com unidade existente (por exemplo, seleção,
   deslocamento, parada, ataque, dano), preferencialmente na vila de teste.
2. Marcar início/fim no observador em cada ação e salvar as imagens.
3. Verificar se a unidade e o SWF correspondente são visíveis na
   sessão antes de atribuir um `character_id` a um evento.
4. Anexar evidência de quadro/instante; manter estados não demonstrados
   como `pending_in_game_validation`. Nenhuma substituição SWF no jogo original.
