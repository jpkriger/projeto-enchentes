# Dados

Esta pasta guarda as bases do projeto, organizadas por tema. Em `originais/` ficam os dados como vieram da fonte, e em `processados/` ficam os dados limpos e os resultados dos cruzamentos.

**Datas de coleta.** As bases da Prefeitura e do TCE-RS, e o `data.json`, foram obtidos em 27/10/2026. Os pontos do Copernicus são de 04/11/2026, e as manchas do INCT, de 10/11/2026. Em 09/11/2026 foi conferido que as camadas da Prefeitura têm o mesmo número de registros das fontes.

O servidor das camadas da Prefeitura é `https://gis-smamus.portoalegre.rs.gov.br/server/rest/services/`.

## Base geográfica (`comum/`)

`bairros.geojson` traz os limites dos 94 bairros (camada `A02_SOLO_CRIADO/bairros`), em versão simplificada. Dois nomes diferem do INCT, e a equivalência está na coluna `bairro_malha` do dado limpo.

`cotas_inunda_5_35_limite_muni.geojson` é a área do município abaixo da cota de 5,35 m. É usada só no notebook de análise exploratória (gráfico 8), e não no dashboard.

`copernicus_p08/` traz os pontos do produto P08 do [Copernicus EMSN194](https://riskandrecovery.emergency.copernicus.eu/EMSN194/): 119.626 prédios e instalações atingidos, marcados por intérpretes em imagens de 0,5 m, dos quais 42,6 mil em Porto Alegre. O download é manual, porque o robots.txt proíbe `/download/`. Citar "© European Union, Copernicus Emergency Management Service".

## 1. Simulação do INCT (Tela 1)

`1_simulacao_inct/data.json` é o arquivo fornecido pela disciplina, com prédios afetados por bairro de 3,0 a 10,0 m. O resultado limpo está em `processados/1_simulacao_inct/inct_longo_limpo.json` e `.csv`, e cada valor alterado está em `inct_alteracoes.csv`. O tratamento está explicado em `relatorios/limpeza_dados.pdf`.

`mancha_inct_api/` tem a mancha simulada de cada um dos 25 níveis de 3,0 a 5,4 m, a faixa usada na Tela 2, obtida da mesma API usada pelo [site do INCT](http://vhlab.com.br/INCT/floods/) (`POST http://vhlab.lad.pucrs.br:5002/api/map-data`, campo `flood`), coletada em 10/11/2026. Cada arquivo é a resposta da API guardada sem alteração; o desenho que a API serve já é simplificado. Essas manchas são coerentes com o `data.json`: a 3,0 m, os bairros com mais de 1% da área dentro da mancha são os mesmos 24 que ele dá como atingidos, e outros 4 só encostam na mancha. Por isso não devem ser baixadas de novo (`--forcar`), para não trocar a versão usada. Elas alimentam o slider da Tela 2. Como são preparadas para as contas e para o mapa está em `relatorios/limpeza_dados.pdf`.

## 2. Investimento na reconstrução (Tela 2)

A pergunta deste tema é: se o rio subir, quais obras da reconstrução ficam na área alcançada pela água, e quanto está previsto nelas?

`base_reconstrucao_2` e `_3` vêm do painel [Monitoramento da Reconstrução](https://prefeitura.poa.br/monitoramento-reconstrucao) e trazem as obras com bairro, valor previsto, fonte do recurso e situação. `base_reconstrucao_4_prevencao.json` traz as etapas das obras do DMAE (grupo "Sistema de Prevenção"), com contratos, empresas e a classificação entre equipamentos de proteção e demais equipamentos. `hub_habitacao_1_demhab.json` traz as áreas de habitação do DEMHAB com a necessidade estimada de reposição. `hub_base_financeiro_*` traz a necessidade estimada, os valores solicitados e recebidos da União e os recursos registrados como aplicados.

**Antes de usar os valores, leia `processados/auditoria_base_reconstrucao.md`.** Ela mostra por que os valores são previsões e por que somas por bairro só servem como ordem de grandeza. `obras_por_nivel.csv` (gerado por `scripts/obras_por_nivel.py`) traz, para cada nível, as obras dentro da mancha do INCT e o investimento previsto nelas. `valores_alternativos.csv` (gerado por `scripts/valores_alternativos.py`) refaz o investimento exposto com os outros campos de valor das obras do DMAE (camada 4 e valor contratado) e mostra o peso dos diques. `obras_contratos_rateio.csv` (gerado por `scripts/cruza_obras_contratos.py`) mostra os três contratos do TCE-RS cujo valor, dividido igualmente entre projetos, é o valor que o painel atribui a cada obra, o que confirma o rateio.

## 3. Contratos do TCE-RS

Os [dados abertos do TCE-RS](https://dados.tce.rs.gov.br) (licitações, contratos e empenhos de 2024 e 2025; código 54900 é a Prefeitura e 54907 o DMAE) serviram só para conferir o rateio dos valores das obras do DMAE, em `scripts/cruza_obras_contratos.py`, e **não aparecem no dashboard**. Não são usados para totais, porque não existe um marcador oficial que identifique toda a despesa da enchente. Ficam em `originais/4_rastreabilidade_recurso/tce_rs/` e **não são versionados**, porque contêm CPF e nome de credores pessoa física. Para obtê-los, rode `python scripts/coleta_bases.py --temas tce`.

## 4. Arquivos do dashboard

`processados/dashboard/` é gerado por `scripts/prepara_dashboard.py` e traz versões leves do que o app lê: as obras com o nível em que cada uma é alcançada (`obras.csv`), as manchas inteiras de cada nível, simplificadas para exibir, os pontos P08 de Porto Alegre e os números do painel financeiro.

## Licenças

Os dados da Prefeitura de Porto Alegre e do TCE-RS são publicados como dados abertos pelos próprios órgãos, sem licença explícita nas camadas e conjuntos consultados; o uso cita a fonte e a data. Os produtos do Copernicus EMS são de uso livre com a citação "© European Union, Copernicus Emergency Management Service". O `data.json` e as manchas do INCT SiMAI são usados para fins acadêmicos, citando o INCT como fonte.

## Coleta responsável

Os arquivos robots.txt foram verificados em 27/10/2026. O `dados.tce.rs.gov.br` proíbe `/api/` e pede 10 segundos entre acessos, por isso o script usa só URLs diretas de download, com essa pausa. O Copernicus proíbe `/download/`. O servidor da Prefeitura não tem robots.txt, mas o script faz pausas mesmo assim.

## Cuidados

Nomes de pessoas físicas não devem ser publicados, incluindo credores e servidores citados nos históricos do TCE-RS.
