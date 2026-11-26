# Projeto: Enchentes em Porto Alegre (CPAD / INCT SiMAI)

Documento de trabalho com a ideia, as decisões e os dados do projeto. Atualizado em 24/11/2026. A origem de cada arquivo está em [`dados/README.md`](../dados/README.md).

## 1. A ideia

O dashboard tem duas telas, como pede o enunciado, e uma página de ajuda ("Sobre os dados").

A **Tela 1** responde à pergunta "se o Guaíba chegar a X metros, quais bairros e quantas pessoas são afetados?". Ela usa somente o JSON do INCT depois de limpo e tem o slider de nível de 3,0 a 10,0 m, os indicadores de pessoas, prédios e bairros, o mapa e as barras com a porcentagem de prédios por bairro, a curva da população afetada com o recorde de 5,35 m, o ranking e o aviso de limitações.

A **Tela 2** responde à pergunta "se o rio subir, quais obras da reconstrução ficam na área alcançada pela água, e quanto está previsto nelas?". Conforme o nível escolhido, a mancha simulada pelo INCT mostra quais das 318 obras de reconstrução monitoradas pela Prefeitura ficam dentro dela, ou a até 50 m. A soma do valor previsto dessas obras é o **investimento exposto**. Não é custo de dano: é quanto da verba da reconstrução está em lugares que a água alcança. A tela traz filtros por grupo de obra e por situação, a camada opcional dos prédios atingidos em 2024 (Copernicus), a curva do investimento exposto por nível e a tabela das obras alcançadas. No fim, um bloco curto compara as obras do mapa com a necessidade estimada pela Prefeitura e mostra quanto da União chegou para a reconstrução.

As duas telas são ligadas pelo **mesmo nível do rio**, que passa de uma para a outra, e pela mesma simulação. O slider da Tela 2 vai de 3,0 a 5,4 m, porque as manchas do INCT foram coletadas só até esse nível, logo acima do recorde de 2024.

**Por que é extensionista.** A população recebe uma visão clara de quem a simulação indica como afetado e de quanto da verba da reconstrução está em áreas que alagam, com as fontes e as lacunas dos dados públicos explicadas.

## 2. Termos usados neste projeto

- **Cota:** altura de um ponto do terreno.
- **Mancha:** área que a simulação do INCT indica como alagada em um nível do rio.
- **Investimento previsto:** valor que a Prefeitura prevê para uma obra. Não é o valor pago.
- **Investimento exposto:** soma do investimento previsto das obras que ficam na área alcançada pela água em um nível do rio. Não é custo de dano.
- **Necessidade estimada:** custo que a Prefeitura estima para a recuperação da cidade, incluindo habitação, macrodrenagem e perda de arrecadação.
- **Solicitado e recebido:** valores que a Prefeitura registra como pedidos à União e recebidos, para emergência e reconstrução.
- **P08:** produto do Copernicus com a marcação, feita por intérpretes humanos, de prédios e instalações atingidos em 2024.

## 3. Decisões tomadas

O foco é **Porto Alegre**, porque os dados do INCT são só da cidade.

A Tela 2 trata da **verba da reconstrução exposta à água**. As análises de validação da mancha, de falhas do sistema de proteção, de saúde e de fila do SUS foram retiradas, e os dados correspondentes foram apagados. A validação da mancha saiu porque não existe uma fonte da verdade para a extensão da enchente. Dos dados de validação, ficaram apenas os pontos P08 do Copernicus, como camada de contexto.

A **fonte das obras e dos valores é a base de dados abertos da Prefeitura** (servidor ArcGIS do painel Monitoramento da Reconstrução), com registros de 17/09/2026. O site do painel mostra alguns números diferentes, que não aparecem em nenhuma base publicada; o dashboard usa os dados abertos e informa a fonte e a data.

Os valores por obra **não são usados como número preciso**: são previsões, e muitos se repetem, o que indica rateio de um mesmo contrato entre projetos (ver a [auditoria](../dados/processados/auditoria_base_reconstrucao.md)). Os dados do TCE-RS serviram só para tentar ligar obras do sistema de proteção aos seus contratos, nunca para totais.

A habitação fica fora do mapa da Tela 2, porque o seu valor é uma necessidade estimada de reposição e não o valor de uma obra. Transformação urbana e adaptação climática também ficam fora, porque não têm localização nem valor por obra.

O **robots.txt é respeitado** em toda a coleta. O TCE-RS proíbe o caminho `/api/`, e o Copernicus proíbe `/download/`, que por isso é baixado à mão.

## 4. Os dados e o quanto confiar neles

A **malha de bairros** da Prefeitura é a base geográfica oficial e é confiável.

A **simulação do INCT** é o `data.json`, que depois da limpeza é coerente como simulação, mas continua sendo estimativa. As manchas por nível vêm da mesma API usada pelo site do INCT, coletadas em 10/11/2026, e são coerentes com o `data.json`: a 3,0 m, os bairros com mais de 1% da área dentro da mancha são os mesmos 24 que ele dá como atingidos (outros 4 só encostam na mancha), e a 5,3 m a área coberta em cada bairro acompanha a porcentagem de prédios atingidos (correlação de 0,97). O site foi atualizado depois e hoje serve outra versão da simulação, com totais maiores (a 5,3 m, 63.180 prédios no site e 53.989 no arquivo); o dashboard mantém as manchas de 10/11 para que as duas telas usem a mesma versão.

As **bases de reconstrução da Prefeitura** trazem 318 obras: 194 de equipamentos públicos e 124 obras do DMAE, que a Prefeitura agrupa como Sistema de Prevenção. Esse grupo não é só proteção contra cheias: 41 são equipamentos de proteção (casas de bombas, comportas, diques e o Muro da Mauá), 26 são de esgoto, 5 de captação de água, 3 de redes pluviais e 49 são prédios do DMAE. Delas, 274 têm localização; das 44 sem localização, 43 são do DMAE, quase todas prédios. Localização e tipo são confiáveis, mas os valores são previsões e a situação falta em muitas obras do sistema de proteção.

Os **pontos P08 do Copernicus** registram 42,6 mil prédios e instalações atingidos em Porto Alegre, mas cobrem só parte da cidade.

## 5. O que os dados mostram

Com o rio a 5,3 m, o nível simulado mais próximo do recorde de 2024, a simulação estima cerca de 136 mil pessoas afetadas em 36 bairros, e 255 das 274 obras com localização ficam na área alcançada, somando R$ 712,5 mi previstos.

As obras do DMAE dominam o investimento exposto desde os níveis baixos, porque diques, casas de bombas e comportas ficam na beira da água por função (a 5,3 m, 98% do valor exposto do DMAE é de equipamentos de proteção). O valor depende de poucas obras: só três diques somam R$ 368,7 mi previstos, 60% do investimento exposto a 3,0 m e 52% a 5,3 m, e deles só R$ 12,5 mi estão contratados. Com o valor da camada 4 nas obras do DMAE, o investimento exposto a 5,3 m seria R$ 485,9 mi; com o valor contratado, R$ 156,7 mi (`scripts/valores_alternativos.py`). Já a 3,0 m, 129 obras estão na área alcançada. As obras são cruzadas com a mancha inteira do INCT, sem recorte pelo limite do município: a mancha não cobre o lago Guaíba (cobre rios e canais menores), e o limite simplificado dos bairros cortaria faixas de orla onde ficam obras, como o Calçadão de Ipanema. Para ver o risco aos serviços à população, a leitura principal é a dos equipamentos públicos.

A Prefeitura estima em R$ 12,3 bi a necessidade para a recuperação, a maior parte em habitação (R$ 5,5 bi) e expansão da macrodrenagem (R$ 4,7 bi). O painel registra R$ 379,4 mi solicitados à União e R$ 172,9 mi recebidos; para a reconstrução, chegaram R$ 8,4 mi de R$ 196,6 mi (4,3%). O painel também registra R$ 655,6 mi como recursos aplicados, mas o dashboard não usa esse número: na parte de reconstrução, a maioria desses valores repete o valor previsto das obras, então não comprova dinheiro gasto. As 274 obras do mapa somam R$ 740,3 mi previstos: cerca de 6% da necessidade estimada e perto de metade dos R$ 1,5 bi estimados para reconstruir equipamentos, diques, água, esgoto e drenagem. O resto da necessidade é habitação, macrodrenagem nova e perda de arrecadação, que não são obras com local no mapa; como as categorias não coincidem uma a uma, os percentuais são ordem de grandeza.

## 6. Cuidados

O dashboard deixa claro que os números do INCT são estimativas de uma simulação, que os níveis acima de 5,35 m são cenários hipotéticos, e evita cores e linguagem alarmistas. Valores de investimento são sempre rotulados como previstos ou estimados. Nomes de pessoas físicas não são publicados, e os arquivos do TCE-RS com dados pessoais não são versionados. Todo uso de IA é registrado nos relatórios, como exige o enunciado.

## 7. Entregas

- **Fase 1:** `relatorios/base_dados.pdf`.
- **Fase 2:** scripts de coleta e limpeza, JSON limpo, `relatorios/limpeza_dados.pdf`, `notebooks/eda.ipynb` e `relatorios/wireframe_telas.pdf`.
- **Fase 3 e versão final (24/11, 23h59):** o dashboard em `app/`, publicado por link público, e `relatorios/dashboard.pdf`.
- **Apresentação:** 10 minutos com demonstração ao vivo, em 25/11 ou 30/11; slides em `relatorios/pitch_apresentacao.pdf`.
