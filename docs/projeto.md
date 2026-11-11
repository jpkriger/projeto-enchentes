# Projeto: Enchentes em Porto Alegre (CPAD / INCT SiMAI)

Documento de trabalho com a ideia, as decisões, os dados e as análises. Atualizado em 10/11/2026. A origem de cada arquivo está em [`dados/README.md`](../dados/README.md).

## 1. A ideia

O dashboard tem duas telas, como pede o enunciado.

A **Tela 1** responde à pergunta "se o rio chegar a X metros, quais bairros e quantas pessoas são afetados?". Ela usa somente o JSON do INCT, depois de limpo, e tem o slider de nível de 3,0 a 10,0 m, os indicadores, a porcentagem de prédios por bairro, a curva com o recorde de 5,35 m, o ranking e o aviso de limitações.

A **Tela 2** mapeia **para onde vai a verba da reconstrução**. O elemento central é um slider de nível do Guaíba: conforme a água avança, segundo a mancha simulada pelo INCT, o mapa mostra as obras que ficam na área alcançada e o **investimento exposto**, ou seja, o valor previsto para essas obras. Não é custo de dano: é quanto da verba da reconstrução está indo para lugares que a água alcança. A tela mostra também o tipo, o valor previsto e a situação de cada obra. Ela também compara o que a Prefeitura estima precisar com o que foi solicitado e recebido. Os dados do TCE-RS entram apenas para ligar obras específicas aos seus contratos e ao valor pago. A ligação com a Tela 1 é feita pelo mesmo nível do rio e pela mesma simulação. O slider da Tela 2 vai de 3,0 a 5,4 m, a faixa que a enchente de 2024 alcançou: acima disso não há evento real para comparar, e o resultado praticamente não muda.

**O que os dados já mostram.** O sistema de proteção concentra cerca de 83% do investimento previsto nas obras (R$ 620,6 mi de R$ 751,7 mi). Para a reconstrução, foram registrados R$ 8,4 mi recebidos de R$ 196,6 mi solicitados.

**O cuidado principal.** Os valores por obra são previsões, e 38% deles se repetem, o que indica rateio ou valor-padrão (ver a [auditoria](../dados/processados/auditoria_base_reconstrucao.md)). Por isso o mapa mostra o direcionamento do recurso, ou seja, onde e em quê, e não o custo exato. Somas por bairro ou por área só podem aparecer como ordem de grandeza e com o rótulo "previsto".

**Por que é extensionista.** O INCT recebe a lista de inconsistências do arquivo da simulação. A população recebe uma visão clara de para onde está indo o recurso da reconstrução e de quais dados públicos ainda têm lacunas.

## 2. Termos usados neste projeto

- **Cota:** altura de um ponto do terreno. A cota de 5,35 m é a área do município abaixo dessa altura.
- **Investimento previsto:** valor que a Prefeitura prevê para uma obra. Não é o valor pago.
- **Investimento exposto:** soma do investimento previsto das obras que ficam na área alcançada pela água em um nível do rio. Não é custo de dano.
- **Necessidade estimada:** custo que a Prefeitura estima para recompor perdas, como as moradias inabitáveis.
- **Solicitado e recebido:** valores que a Prefeitura registra como pedidos e recebidos para emergência e reconstrução.
- **Empenho:** reserva formal de dinheiro público para uma despesa. Depois vêm a liquidação e o pagamento.
- **P08:** produto do Copernicus com a marcação, feita por intérpretes humanos, de prédios e instalações atingidos.

## 3. Decisões já tomadas

O foco é **Porto Alegre**, porque os dados do INCT são só da cidade.

A Tela 2 trata da **verba da reconstrução**. As análises de validação da mancha, de falhas do sistema de proteção, de saúde e de fila do SUS foram retiradas, e os dados correspondentes foram apagados.

A validação da mancha saiu porque não existe uma fonte da verdade para a extensão da enchente, e a comparação viraria uma discussão de metodologia entre trabalhos de outras equipes. Dos dados de validação, ficaram apenas os pontos P08 do Copernicus, como camada de locais atingidos.

A busca por "desvio de dinheiro" virou **rastreabilidade do recurso**. Os dados mostram pontos de atenção, não provas, e o enunciado pede tom não sensacionalista.

Os valores por obra **não são usados como número preciso**, pelas razões descritas na auditoria.

A **fonte das obras e dos valores é a base de dados abertos da Prefeitura** (servidor ArcGIS do painel), com registros de 17/09/2026. O site do painel mostra alguns números diferentes, que não aparecem em nenhuma base publicada; o dashboard informa a fonte e a data, e o relatório registra as diferenças. Antes da versão final, a coleta deve ser repetida para ver se a base foi atualizada.

O **robots.txt é respeitado** em toda a coleta. O TCE-RS proíbe o caminho `/api/`, e o Copernicus proíbe `/download/`.

## 4. Os dados e o quanto confiar neles

A **base geográfica** traz os 94 bairros e as cotas de inundação da Prefeitura, e é confiável. Os **pontos P08 do Copernicus** registram 42,6 mil prédios e instalações atingidos em Porto Alegre, mas cobrem só parte da cidade.

A **simulação do INCT** é o `data.json`. Depois da limpeza é confiável como simulação, mas continua sendo estimativa.

As **bases de reconstrução da Prefeitura** trazem 318 obras de equipamentos públicos e do sistema de proteção, das quais 274 têm localização, as etapas das obras de prevenção, 120 áreas de habitação e os valores solicitados e recebidos. Localização e tipo são confiáveis, mas os valores são previsões e a situação das obras falta em muitos casos.

Os **empenhos e contratos do TCE-RS** são dados contábeis reais, mas não existe um marcador oficial que identifique toda a despesa da enchente. Um filtro por palavras erra para mais e para menos, por isso os totais dessa base não são usados: ela serve só para ligar uma obra específica ao seu contrato e ao valor pago.

## 5. O que os dados já mostram

### Para onde vai o recurso?

A Prefeitura estima em R$ 12,3 bilhões o prejuízo ao setor público, valor que também pediu ao governo federal por ofício. Esse valor inclui R$ 5,5 bi em habitação, R$ 4,7 bi em expansão da macrodrenagem e R$ 602,8 mi em perda de arrecadação. O painel registra R$ 379,4 mi solicitados e R$ 172,9 mi recebidos. Para emergência, foram R$ 164,4 mi recebidos de R$ 182,8 mi solicitados. Para reconstrução, R$ 8,4 mi de R$ 196,6 mi. Segundo o texto do painel, esses pedidos foram feitos à União por cadastros formais, como os da Defesa Civil e do Ministério da Saúde (R$ 381,9 mi no texto). Outra camada do painel, que o site chama de "recursos gastos", soma R$ 655,6 mi: R$ 398,7 mi em emergência e R$ 256,9 mi em reconstrução, sendo R$ 492,4 mi do Município, R$ 152,5 mi da União e R$ 10,7 mi do Estado. O texto do painel diz que esses valores incluem recursos destinados a projetos e obras contratadas, então podem não estar todos pagos.

O total pago com a enchente não é apresentado. A busca por um marcador oficial na base do TCE-RS só encontrou marcadores parciais: o projeto do Fundo Municipal de Reconstrução e Adaptação Climática, com R$ 12,5 mi pagos desde julho de 2025, e a subfunção Defesa Civil, que mistura outros eventos.

### Em que tipo de obra e onde?

O sistema de proteção soma R$ 620,6 mi previstos. Os equipamentos públicos somam R$ 131,1 mi, sendo as obras de esporte e lazer as mais numerosas (137). A habitação tem uma necessidade estimada de R$ 1,96 bi nas 120 áreas do DEMHAB.

Das 274 obras com localização, 265 ficam a até 50 m da área abaixo de 5,35 m, ou seja, onde a água chegou.

Quase todos os equipamentos públicos constam como concluídos. No sistema de proteção, das 124 obras, 31 constam como concluídas, 28 em andamento e 65 sem situação informada. A base não informa a data de cada situação.

### Pontos de atenção nos contratos

Esses casos indicam o que merece conferência manual e não são acusação. Três contratos ligados à enchente têm acréscimo acima do limite de 50% da Lei 14.981/2024: M C T Transportes (219,5%), SV Incorporadora (94%) e Velha Capital (90,8%). A M C T aparece com 7 contratos por dispensa para transporte de resíduos. Também há prováveis erros de registro, como o reajuste de 10.373% em um contrato de R$ 86 mil.

## 6. O que ainda pode ser feito

Ligar manualmente as 20 a 30 maiores obras aos contratos no LicitaCon Cidadão, para comparar o previsto com o contratado. Pedir à Prefeitura, via Lei de Acesso à Informação, a situação atual das obras e a relação entre obra, contrato e valor pago.

## 7. Proposta de telas

O esboço está em `relatorios/wireframe_telas.pdf`.

A **Tela 1** tem todos os requisitos fixos e usa só o JSON limpo.

A **Tela 2** tem filtros por tipo de obra, situação, fonte e bairro; o mapa das obras com a área abaixo de 5,35 m e os prédios atingidos; o investimento exposto por nível do rio; o caminho entre necessidade, solicitado e recebido; o investimento previsto por tipo; e a situação das obras. Ela mostra também, para obras ligadas a um contrato, o valor contratado e o pago segundo o TCE-RS. Ela usa bases obtidas por código (ArcGIS da Prefeitura e TCE-RS) e mostra a fonte de cada dado, com link e data de coleta.

## 8. Cuidados

O dashboard deve deixar claro que os números do INCT são estimativas, que os níveis acima de 5,35 m são cenários hipotéticos, e evitar cores e linguagem alarmistas.

Valores de investimento devem ser sempre rotulados como previstos ou estimados. Ponto de atenção não é acusação. Nomes de pessoas físicas não são publicados. Todo uso de IA precisa ser registrado, como exige o enunciado.

## 9. Próximos passos

Na **Fase 2** (09/11), falta publicar o repositório com a professora como colaboradora, fazer os commits e registrar no fórum do Moodle o trabalho realizado.

Na **Fase 3** (16/11), a entrega é o protótipo em Streamlit e `relatorios/dashboard.pdf`, que precisa trazer as observações sobre a ferramenta atual do INCT. Nessa fase também devem ser escritos o script do mapa das obras e a ligação entre obras e contratos.

A **versão final** é em 24/11 às 23h59, e a **apresentação**, de 10 minutos com demonstração ao vivo, em 25/11 ou 30/11.
