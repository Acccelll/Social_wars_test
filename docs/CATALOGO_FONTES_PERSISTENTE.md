# Catálogo persistente das fontes de arte

A indexação metadata-only em GitHub Actions salva no repositório:

- `data/visual/swf_catalog.csv`: todos os **1.118 SWFs**
  com caminho completo, pasta de origem, rótulo e tamanho.
- `data/visual/catalog_summary.json`: quantidades por pasta.
- `data/visual/building_candidates.csv`: arquivo de **candidatos
  a construções**, com nomes detectados por expressão regular
  (não implica classificação visual confirmada).

Workflow de atualização:
[Publish Visual SWF Catalog Metadata](../.github/workflows/publish-visual-catalog.yml).

A publicação inclui **somente caminhos, nomes, tamanhos e rótulos** da
distribuição pública 0.02a. Imagens, animações, executáveis, SWFs e
salvamentos continuam fora do histórico Git.

O catálogo permite selecionar SWFs de construções com nomes
verificados antes de iniciar lotes de exportação, sem gastar
recursos repetindo amostras de mechas já processadas.
