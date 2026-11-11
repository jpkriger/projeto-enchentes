# Dados

Esta pasta guarda as bases do projeto, organizadas por tema. Em `originais/` ficam os dados como vieram da fonte, e em `processados/` ficam os dados limpos e os resultados dos cruzamentos.

**Datas de coleta.** As bases da Prefeitura e do TCE-RS, e o `data.json`, foram obtidos em 27/10/2026. Os pontos do Copernicus são de 04/11/2026, e as manchas do INCT, de 10/11/2026. Em 09/11/2026 foi conferido que as camadas da Prefeitura têm o mesmo número de registros das fontes.

O servidor das camadas da Prefeitura é `https://gis-smamus.portoalegre.rs.gov.br/server/rest/services/`.

## Base geográfica (`comum/`)

`bairros.geojson` traz os limites dos 94 bairros (camada `A02_SOLO_CRIADO/bairros`), em versão simplificada. Dois nomes diferem do INCT, e a equivalência está na coluna `bairro_malha` do dado limpo.

`cotas_inunda_5_35_limite_muni.geojson` é a área do município abaixo da cota de 5,35 m e é usada como área atingida nos mapas. `cota_inundacao_535.geojson` e `cotas_inundacao_300_400_535.geojson` trazem outras versões da cota.

`copernicus_p08/` traz os pontos do produto P08 do [Copernicus EMSN194](https://riskandrecovery.emergency.copernicus.eu/EMSN194/): 119.626 prédios e instalações atingidos, marcados por intérpretes em imagens de 0,5 m, dos quais 42,6 mil em Porto Alegre. O download é manual, porque o robots.txt proíbe `/download/`. Citar "© European Union, Copernicus Emergency Management Service".

## 1. Simulação do INCT (Tela 1)

`1_simulacao_inct/data.json` é o arquivo fornecido pela disciplina, com prédios afetados por bairro de 3,0 a 10,0 m. O resultado limpo está em `processados/1_simulacao_inct/inct_longo_limpo.json` e `.csv`, e cada valor alterado está em `inct_alteracoes.csv`. O tratamento está explicado em `relatorios/limpeza_dados.pdf`.

`mancha_inct_api/` tem a mancha simulada de cada um dos 25 níveis de 3,0 a 5,4 m, a faixa usada na Tela 2, obtida da mesma API usada pelo [site do INCT](http://vhlab.com.br/INCT/floods/) (`POST http://vhlab.lad.pucrs.br:5002/api/map-data`, campo `flood`), coletada em 10/11/2026. É uma versão simplificada para exibição. Ela alimenta o slider da Tela 2.

## 3. Investimento na reconstrução (Tela 2)

A pergunta deste tema é: para onde vai a verba da reconstrução, por tipo de obra e por local?

`base_reconstrucao_2` e `_3` vêm do painel [Monitoramento da Reconstrução](https://prefeitura.poa.br/monitoramento-reconstrucao) e trazem as obras com bairro, valor previsto, fonte do recurso e situação. `base_reconstrucao_4_prevencao.json` traz as etapas das obras do sistema de proteção, com contratos e empresas. `hub_habitacao_*` traz os domicílios inabitáveis e a necessidade de habitação estimada. `hub_base_financeiro_*` traz os valores solicitados e recebidos.

**Antes de usar os valores, leia `processados/auditoria_base_reconstrucao.md`.** Ela mostra por que os valores são previsões e por que somas por bairro só servem como ordem de grandeza. `processados/3_investimento_reconstrucao/mapa_poa.json` traz os 394 pontos do mapa: 274 obras com coordenada e 120 áreas de habitação. `obras_por_nivel.csv` (gerado por `scripts/obras_por_nivel.py`) traz, para cada nível, as obras dentro da mancha do INCT e o investimento previsto nelas. `obras_contratos_rateio.csv` (gerado por `scripts/cruza_obras_contratos.py`) mostra os contratos do TCE-RS cujo valor, dividido igualmente entre projetos, é o valor que o painel atribui a cada obra.

## 4. Rastreabilidade do recurso (Tela 2)

Esta base serve para ligar obras específicas aos seus contratos e ao valor pago. Ela **não é usada para totais**, porque não existe um marcador oficial que identifique toda a despesa da enchente.

`tce_rs/` traz os [dados abertos do TCE-RS](https://dados.tce.rs.gov.br): licitações, contratos e empenhos de 2024 e 2025. O código 54900 é a Prefeitura e o 54907 é o DMAE. **Esses arquivos não são versionados**, porque contêm CPF e nome de credores pessoa física. Para obtê-los, rode `python scripts/coleta_bases.py --temas tce`.

Em `processados/4_rastreabilidade_recurso/`, `empenhos_enchente.csv` e `pago_enchente_por_fonte.json` são um recorte exploratório feito por palavras no histórico, com erros para mais e para menos, e não devem ser usados como total da enchente. O histórico ainda contém dados pessoais e precisa ser mascarado antes da publicação. `contratos_credores_enchente.csv` tem contratos e aditivos de credores com despesas ligadas à enchente; o limite de acréscimo na calamidade é de 50% (Lei 14.981/2024).

## Coleta responsável

Os arquivos robots.txt foram verificados em 27/10/2026. O `dados.tce.rs.gov.br` proíbe `/api/` e pede 10 segundos entre acessos, por isso o script usa só URLs diretas de download. Na exploração inicial a `/api/` foi usada para busca, o que foi corrigido. O Copernicus proíbe `/download/`. O servidor da Prefeitura não tem robots.txt, mas o script faz pausas mesmo assim.

## Cuidados

Sinal de alerta não é prova de irregularidade: serve apenas para indicar o que merece conferência. Nomes de pessoas físicas não devem ser publicados, incluindo credores, servidores citados nos históricos e sócios.
