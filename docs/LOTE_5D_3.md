# Lote 5D.3 — Extração de unidades e catálogo

## Amostras reais já exportadas

- **1.899 imagens externas**: 143 PNG e 1.756 JPG, 95.899.970 bytes.
  Execução [39278619312](https://github.com/Acccelll/Social_wars_test/actions/runs/39278619312),
  artefato [social-wars-1899-external-images](https://github.com/Acccelll/Social_wars_test/actions/runs/39278619312/artifacts/12199220872).
- **SWF principal, exportação visual ampliada**: FFDec retornou
  `swf_exported=1`, `exported_files=7493`, **0 erros**, saída com PNGs,
  vetores SVG e sprites/botões renderizados. Execução
  [39278874264](https://github.com/Acccelll/Social_wars_test/actions/runs/39278874264),
  artefato [social-wars-visual-export-sample](https://github.com/Acccelll/Social_wars_test/actions/runs/39278874264/artifacts/12200075411).
- A exportação do SWF principal não prova que TODOS os quadros e
  transições foram preservados no formato original. Ainda há timelines.

## Nova exportação em lote

O workflow `visual-units-batch.yml` usa cinco arquivos SWF **presentes
no inventário de origem**, todos relativos a `assets/sprites/`:

- `1212_tetrapod_mech.swf`
- `1313_splinterMech.swf`
- `1358_bushwacker.swf`
- `1376_reaperDrone.swf`
- `1408_urbanBuster.swf`

Esses nomes são identificadores do pacote; o significado dos rótulos
ainda precisa ser confrontado com o jogo e com as animações.

O workflow exporta imagens, SVGs, sprites e botões, com um arquivo
`export_results.csv` para auditar cada fonte. O mesmo script também
aceita uma lista de nomes no Windows:

```powershell
py -3 tools/visual_extract.py --archive "social-warriors_0.02a.zip" --ffdec "tools/ffdec.jar" --out "dist/visual-units" --names "1212_tetrapod_mech.swf,1313_splinterMech.swf" --types visual
```

O catálogo global de fontes `swf_catalog.csv` e `catalog_summary.json`
relaciona nomes de arquivos, diretórios, identificadores numéricos,
rótulos derivados de arquivo e tamanhos, sem acrescentar os binários
originais ao repositório.

As saídas são artefatos temporários do GitHub Actions, **não
arquivos da branch main**. Não alteram nem os binários do servidor
nem os salvamentos do usuário.

### Limites

- `sprite:png` não equivale ao formato de animação nativo.
- Nomes/categorias derivados da árvore do ZIP não são classificação
  visual confirmada.
- Exportação integral dos 1.118 SWFs não foi concluída.
