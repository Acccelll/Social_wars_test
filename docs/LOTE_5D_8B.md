# Lote 5D.8B — Registro em vídeo e variações visuais do jogo original

**Status:** captura técnica validada em 19/10/2026, mas o mapeamento funcional de animações ainda está pendente.

## Execução verificada

O [GitHub Actions 39310113510](https://github.com/Acccelll/Social_wars_test/actions/runs/39310113510)
terminou com **success**. Utilizou o servidor Flask original de Social
Warriors 0.02a, recursos SWF originais, Chromium/Playwright e Ruffle.
Criou uma vila descartável no runner, sem abrir arquivos de saves do usuário.

O navegador abriu `play.html`, carregou `SWLoader.swf` e
`Basesec_1.5.4.swf` e executou um clique na região do
`ruffle-embed` (760 × 600). Para esse ensaio, o observador marcou
o evento com a categoria **other**: não foi identificado um
deslocamento nem um ataque específico.

Foram validados:

- `session.webm`: vídeo do cliente original (2.521.901 bytes);
- imagens PNG no início e no fim do intervalo marcado;
- `report.json`: eventos de ponteiro, tempos e caminhos HTTP sem query;
- `action_evidence_5d8b.json`: comparação das imagens recortadas ao Flash;
- uma janela de observação com **mudança visual detectada**;
- **zero ações de gameplay e zero IDs internos de sprite confirmados**.

Também foram aprovados os testes sintéticos do observador,
do correlacionador de SWFs e do comparador de capturas.

[Baixar o pacote de evidências](https://github.com/Acccelll/Social_wars_test/actions/runs/39310113510/artifacts/12215307646)
(GitHub Actions, cerca de 5,7 MB compactados, expiração prevista em
02/11/2026).

## Para capturar uma ação real no Windows

Com o servidor original `social-warriors.exe` aberto em
`127.0.0.1:5055`, na raiz do repositório:

```powershell
npm install --prefix tests/ruffle
npx --prefix tests/ruffle playwright install chromium
node tests/original/record.mjs --duration 180 --out dist/original-observation
py -m pip install pillow
py tools/analyze_runtime_5d8b.py --report dist/original-observation/report.json --out dist/original-observation
```

O script abre uma janela Chromium com o Social Wars e o observador no
canto superior direito. Entre no jogo, selecione uma unidade, escolha
`Movimento` no painel, marque **Iniciar**, execute a ação no mapa e
marque **Finalizar**. Repita para outras ações enquanto durar a sessão.
São gerados vídeo e PNGs para revisar visualmente.

**Atenção aos salvamentos:** o gravador não edita SWFs nem saves, mas
as próprias ações no jogo podem salvar normalmente. Faça backup
ou use uma vila descartável.

## Limites e próxima etapa

Mudanças de pixels são observações de imagem, não comprovação de que
uma ação aconteceu. Mesmo a requisição de um SWF não prova que
determinado `character_id` foi utilizado. Não preencher
`animation_review_5d7_queue.csv` com estados definitivos
sem evidências de jogo e correspondência visual verificadas.

**Lote 5D.8C:** capturar uma sequência real com a unidade identificada,
deslocamento, combate e danos; confrontar capturas/frames do vídeo
com o GIF do sprite SWF e só então confirmar identidades.
