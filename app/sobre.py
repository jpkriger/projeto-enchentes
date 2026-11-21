"""Página de ajuda: o que o dashboard mostra, como usar, de onde vêm os dados e quais são as limitações."""
import streamlit as st

from estilo import titulo


def mostrar():
    titulo("Sobre os dados", "O que o dashboard mostra, de onde vêm os números e o que eles não dizem.")
    st.markdown("""
### Como usar
- **Tela 1:** escolha o nível do Guaíba no slider (3,0 a 10,0 m). Indicadores, mapa, barras, curva e ranking mudam juntos.
  O botão *Ir para o recorde de 2024* leva a 5,3 m, o nível simulado mais próximo dos 5,35 m de maio de 2024.
- **Tela 2:** o mesmo nível vale aqui, limitado a 5,4 m. Use os filtros de tipo e situação da obra e passe o mouse
  sobre os pontos do mapa para ver cada obra.

### Fontes
- **Simulação do INCT SiMAI:** arquivo `data.json` fornecido pela disciplina (coletado em 27/10/2026) e manchas
  simuladas por nível, da API do [site do INCT](http://vhlab.com.br/INCT/floods/) (coletadas em 10/11/2026).
- **Prefeitura de Porto Alegre:** malha de bairros, obras de reconstrução e painel financeiro do
  [Monitoramento da Reconstrução](https://prefeitura.poa.br/monitoramento-reconstrucao), pelos dados abertos do servidor
  ArcGIS. Registros de 17/09/2026, coletados em 27/10/2026.
- **Copernicus EMSN194:** prédios atingidos em 2024 (produto P08), © European Union, Copernicus Emergency Management Service
  ([link](https://riskandrecovery.emergency.copernicus.eu/EMSN194/)), coletados em 04/11/2026.

### Como os dados foram tratados
- **Simulação do INCT:** o arquivo original tinha a porcentagem arredondada sempre para cima, contagens de prédios que caíam
  com o rio subindo em 5 bairros e um bairro fora de ordem em 5,3 m. Os valores foram corrigidos por interpolação, primeiro
  valor plausível ou máximo acumulado, e a porcentagem e a população foram recalculadas. Detalhes em
  `relatorios/limpeza_dados.pdf`.
- **Investimento exposto:** uma obra é contada quando o seu ponto fica dentro da mancha do INCT, ou a até 50 m dela, naquele
  nível. O valor somado é o investimento previsto pela Prefeitura para cada obra.

### Limitações
- Os números da simulação são estimativas, não previsões nem contagens oficiais. A população afetada supõe pessoas
  distribuídas igualmente entre todos os prédios do bairro.
- Acima de 5,35 m, os níveis são cenários que nunca ocorreram.
- Os valores das obras são **previstos**, não pagos, e muitos são rateios: o mesmo contrato dividido entre vários projetos.
  Servem como ordem de grandeza, não como custo exato de cada obra.
- Cada obra é um ponto no mapa; um dique de vários quilômetros aparece como um único lugar. 44 obras não têm coordenada e
  ficam de fora.
- Os números exibidos no site do painel da Prefeitura às vezes diferem dos dados abertos que ele publica; este dashboard usa
  os dados abertos.

### Autoria
Projeto Extensionista da disciplina Coleta, Preparação e Análise de Dados (PUCRS). Autor: João Pedro da Silva Kriger.
O código e os dados tratados estão no repositório do projeto.
""")
