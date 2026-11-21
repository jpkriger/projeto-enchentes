# Auditoria da base de reconstrução da Prefeitura

Auditoria feita em 28/10/2026 sobre os dados coletados em 27/10/2026 do painel [Monitoramento da Reconstrução](https://prefeitura.poa.br/monitoramento-reconstrucao) (servidor ArcGIS `gis-smamus.portoalegre.rs.gov.br`, serviço `HUB/base_reconstrucao`).

Arquivos auditados:
- `originais/3_investimento_reconstrucao/base_reconstrucao_3_infraestrutura.json`: camada 3, 318 registros
- `originais/3_investimento_reconstrucao/base_reconstrucao_2_infraestrutura_centroid.json`: camada 2, 313 registros
- `originais/3_investimento_reconstrucao/base_reconstrucao_4_prevencao.json`: camada 4, 114 projetos e 570 etapas
- `originais/3_investimento_reconstrucao/hub_habitacao_1_demhab.*`: 120 áreas do DEMHAB
- Contratos e aditivos do TCE-RS (`originais/4_rastreabilidade_recurso/tce_rs/`), usados como comparação

---

## 1. Estrutura: consistente

| Verificação | Resultado |
|---|---|
| Identificadores repetidos na camada 3 | 0 |
| Nomes de obra repetidos na camada 3 | 0 |
| Obras da camada 3 também presentes na camada 2 | 274 de 318 |
| Mesmo valor para o mesmo id entre as camadas 3 e 2 | 274 de 274 |
| Projetos de proteção da camada 3 presentes na camada 4 | 114 de 114 |
| Obras cujas coordenadas caem no bairro informado | 267 de 274 (as 7 restantes estão na orla ou na divisa entre bairros) |

**Conclusão:** a base é internamente bem ligada. Localização, tipo e bairro são confiáveis.

---

## 2. Valores: previsões, com rateio e valor-padrão

- **Natureza do valor:** `valor_invest` e `val_investimento` são investimento **previsto ou necessário**, não pago. A soma da infraestrutura (R$ 752 mi) se aproxima, com diferença de 4%, da linha "Reconstrução de equipamentos públicos e infraestrutura: R$ 784,5 mi", que o próprio painel apresenta como demanda.
- **Valores repetidos (rateio ou valor-padrão):** **112 de 293 registros com valor (38%)** têm o mesmo valor repetido 3 ou mais vezes. Somam R$ 186 mi dos R$ 752 mi. Exemplos:
  - 12 casas de bombas com R$ 12.148.528,84 cada;
  - 21 estações de bombeamento de esgoto com R$ 65.866,17 cada;
  - 27 praças com R$ 40.000,00 cada;
  - 39 registros com R$ 256.091,99, incluindo unidades administrativas do DMAE ("ADM. DT/GTAG", "C-BENS");
  - 3 unidades de saúde das ilhas com R$ 5.326.268,00 cada.
- **Conflito entre camadas (proteção):** para o mesmo projeto, o valor da camada 3 difere do da camada 4 em **109 de 114 casos**. Ex.: a Comporta 11 vale R$ 2.771.833,33 na camada 3 e R$ 142.857,14 na camada 4. Os totais também divergem: R$ 620 mi × R$ 420 mi.
- **Investimento por casa de bombas:** quase uniforme: R$ 3,4 mi em cada uma das 20 casas na camada 4 e, na camada 3, R$ 12,15 mi em 12 casas. Não serve para comparar uma casa de bombas com outra.
- **Habitação (DEMHAB):** `investim_03` é custo **estimado** de reposição. Só 34 de 120 áreas seguem exatamente "domicílios totalmente inabitáveis × R$ 170 mil"; nas demais a regra varia, e 18 áreas não têm valor.

---

## 3. Status: incompleto e conflitante

| Tipo | Registros | Com status | Sem status | Fonte do recurso |
|---|---|---|---|---|
| Equipamentos públicos (camada 3) | 194 | 158 (151 concluídas, 7 em andamento) | 36 (20 de esporte e lazer, 11 de assistência social, 4 de saúde, 1 de cultura) | todos preenchidos |
| Sistema de proteção (camada 3) | 124 | 59 (31 concluídas, 28 em andamento) | 65 | **nenhum preenchido** |
| Sistema de proteção (camada 4, etapa "obra") | 114 | 62 | 52 | — |
| Habitação (DEMHAB) | 120 | **sem campo de status** | — | — |

**Conflito de status entre camadas (proteção):** 12 projetos aparecem como "concluída" na camada 3, mas com a etapa "obra" em andamento (6), contratada (2) ou sem registro (4) na camada 4. Hipótese: a camada 3 se refere ao reparo emergencial ("apoio"), e a camada 4 à obra definitiva. A base não deixa isso explícito.

**Datas:**
- `data_atualizacao` é **idêntica para os 318 registros** (17/09/2026). É a data da exportação, não da atualização de cada obra.
- 169 registros não têm data de conclusão.
- A camada 4 não tem nenhuma data de atualização.

---

## 4. Comparação com contratos do TCE-RS

Busca automática pelo nome da obra no objeto dos contratos de 2024–2026 (Prefeitura e DMAE): **38 de 191** obras com valor foram encontradas, e várias dessas são falsos positivos (contratos de serviço com nome parecido). Casos verificados:

| Obra | Valor na base | Contratos encontrados | Avaliação |
|---|---|---|---|
| Ginásio Tesourinha | R$ 5,05 mi | 94258/2025: R$ 3,82 mi + R$ 1,07 mi de aditivo; 89606/2024 emergencial: R$ 0,38 mi + R$ 0,03 mi | ≈ R$ 5,3 mi. **Compatível.** |
| CF Diretor Pestana | R$ 0,36 mi | 89183/2024: R$ 0,23 mi; 89184/2024: R$ 0,16 mi | ≈ R$ 0,39 mi. **Compatível.** |
| EMEI Miguel Granato + EMEF Pres. João Goulart | R$ 0,44 mi + R$ 1,73 mi = R$ 2,17 mi | 91040/2024 (SV Incorporadora, dispensa): R$ 2,07 mi + **R$ 1,95 mi de aditivos** | ≈ R$ 4,0 mi. **A base registra o valor inicial e ignora os aditivos.** |
| Praça Fábio André Koff | R$ 0,44 mi | 88901/2024: R$ 0,40 mi; 95526/2025: R$ 0,20 mi | ≈ R$ 0,60 mi. Diverge. |
| US Ilha da Pintada | R$ 5,33 mi | 92548/2024: reforma de R$ 0,11 mi | **Valor-padrão sem contrato correspondente encontrado.** |
| US Fradique Vizeu | R$ 0,89 mi | 92325/2024 e 92458/2024: R$ 0,15 mi no total | Parcial. |
| EMEB Liberato Salzano | R$ 7,95 mi | nenhum contrato público (obra paga por doação privada) | Esperado. |

**Conclusão:** o valor da base às vezes é compatível com o contrato, às vezes é o valor inicial sem aditivos, e às vezes é valor-padrão sem contrato correspondente. **Ligar obra a contrato com confiança exige conferência manual** no LicitaCon Cidadão.

---

## 5. Grau de confiança dos cruzamentos do projeto

| Cruzamento | Confiança | Motivo |
|---|---|---|
| Localização e tipo das obras | alta | coordenadas e bairros conferem |
| Previsto × solicitado × recebido (total da cidade) | média-alta | números do próprio painel financeiro |
| Pago por fonte de recurso (TCE-RS) | **baixa** | não há marcador oficial da enchente; o filtro por texto erra para mais e para menos, por isso não é usado como total |
| Status das obras | baixa-média | metade sem status; conflito entre camadas |
| Valor por obra, por bairro ou por área de drenagem | **baixa** | previsões, rateios e valor-padrão; ignora aditivos |

---

## 6. Recomendações

1. **No dashboard, não apresentar o valor por obra como preciso.** Mostrar o tipo, o local, a fonte e o status, com o valor rotulado "previsto". Não somar por bairro nem calcular custo por área.
2. **Para totais, usar o painel financeiro da Prefeitura** (necessidade, solicitado e recebido). O TCE-RS serve para conferir obras específicas, não para totais.
3. **Para precisão por obra:** ligar manualmente as 20 a 30 maiores obras ao contrato no LicitaCon Cidadão, ou pedir a tabela obra → contrato → valor pago via Lei de Acesso à Informação (Prefeitura e DMAE).
4. **Registrar as inconsistências acima no relatório de limpeza:** valores rateados, conflito de valor e de status entre camadas, aditivos fora da base, ausência de data de atualização por obra e status ausente na habitação.
