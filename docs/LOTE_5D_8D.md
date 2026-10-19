# Lote 5D.8D — Diagnóstico do bloqueio da interface original

## Descoberta fundamentada em capturas reais

O lote 5D.8C colocou quatro unidades (IDs de item 1313, 1358 e 1376)
em uma vila temporária e carregou os três SWFs no Ruffle. No entanto,
as três sondagens visuais foram feitas quando a janela modal
**“RESCUE YOUR COMRADE!”** estava cobrindo o mapa, com o botão “OK”
na parte inferior. Portanto, **nenhuma dessas sondagens demonstrou
movimento, ataque, dano ou seleção efetiva das unidades**.

Essa descoberta veio da inspeção do próprio artefato
[5D.8C](https://github.com/Acccelll/Social_wars_test/actions/runs/39313160511/artifacts/12217206551),
comparando PNGs do cliente original.

## Experimentos no 5D.8D

### Tentativa na largura ampliada

[Workflow 39315571893](https://github.com/Acccelll/Social_wars_test/actions/runs/39315571893)
acionou o clique na posição global correspondente ao “OK”
(645,682; coordenadas locais ao `ruffle-embed`: 550,568).
O registro do observador mostrou o evento `pointer` com
essas coordenadas. A imagem do diálogo permaneceu idêntica antes
e depois na região da janela. **O teste foi corretamente reprovado**
porque não houve fechamento verificável.

### Tentativa na dimensão nativa

A página oficial define 1090 px de largura para a área do embed,
enquanto o SWF original tem 760×600. O segundo experimento
[39316113739](https://github.com/Acccelll/Social_wars_test/actions/runs/39316113739)
reduziu o player a 760 px e tentou novamente a posição relativa
(380,568). O diálogo permaneceu sem alteração e a checagem de
fechamento não passou. **O ajuste de escala, isoladamente, não resolveu.**

### Diagnóstico de eventos e foco

O gravador passou a capturar o destino DOM do clique, elementos do
Shadow DOM do Ruffle, eventos de ponteiro, estado de foco, screenshots
antes/depois e uma tentativa adicional com Enter. A checagem desse
experimento é de **observabilidade**, não de sucesso na conclusão
da missão. Se a janela permanecer aberta, o manifesto deve preservar
esse resultado sem declarar progresso no gameplay.

## Implicações

- SWFs das unidades requisitados comprovam **carregamento**, não animação.
- Abertura de uma janela modal impede interpretar os cliques no mapa.
- Alterações nos pixels ao fundo do diálogo podem ocorrer sem
  qualquer interação efetiva com as unidades.
- **Nenhum estado de animação foi associado a `DefineSprite character_id`.**
- O servidor e os arquivos de save do computador do usuário não são
  alterados: os testes usam uma vila descartável no GitHub Actions.

## Próximo trabalho

Diagnosticar o tratamento de eventos do botão OK no Ruffle/ActionScript
e testar um caminho verificável para dispensar as janelas de entrada.
Em paralelo, é possível comprovar comandos de unidade na cópia
descartável do servidor, mas essa evidência isolada **não confirma a
animação gráfica**.
