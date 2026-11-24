"""Página de ajuda: o que o dashboard mostra, como usar, de onde vêm os dados e quais são as limitações."""
import streamlit as st

from estilo import titulo


def mostrar():
    titulo("Sobre os dados", "O que o dashboard mostra, de onde vêm os números e o que eles não dizem.")
    st.markdown("""
### Que perguntas o dashboard responde
- **Tela 1:** se o Guaíba chegar a X metros, quais bairros e quantas pessoas são afetados, segundo a simulação do INCT?
- **Tela 2:** com o rio a esse nível, quais obras da reconstrução ficam na área alcançada pela água, e quanto está previsto
  nelas? E quanto dinheiro a cidade estima precisar, pediu à União e recebeu?

### Que obras aparecem na Tela 2
Só as **318 obras de reconstrução** que a Prefeitura monitora desde a enchente de 2024, não todas as obras da cidade:
- **194 de equipamentos públicos:** 137 de esporte e lazer, 20 de assistência social, 18 de saúde, 14 de educação e 5 de cultura;
- **124 do sistema de proteção contra cheias:** diques, casas de bombas e comportas.

274 têm coordenada e aparecem no mapa. Das 44 sem coordenada, 43 são do sistema de proteção: só 81 das 124 obras de
proteção estão no mapa.

A situação (concluída, em andamento ou sem informação) é a da obra de reconstrução, como a Prefeitura informa. Habitação,
transformação urbana e ações de adaptação climática também estão no painel da Prefeitura, mas ficam fora do mapa: na
habitação, o valor é uma necessidade estimada de reposição, e não o valor de uma obra; nas outras duas, não há localização ou
valor por obra.

### Como usar
- **Tela 1:** escolha o nível do Guaíba no slider (3,0 a 10,0 m). Indicadores, mapa, barras, curva e ranking mudam juntos.
  O botão *Ir para o recorde de 2024* leva a 5,3 m, o nível simulado mais próximo dos 5,35 m de maio de 2024.
- **Tela 2:** o mesmo nível vale aqui, limitado a 5,4 m. Use os filtros de grupo e situação da obra e passe o mouse
  sobre os pontos do mapa para ver cada obra.

### Fontes
- **Simulação do INCT SiMAI:** arquivo `data.json` fornecido pela disciplina (coletado em 27/10/2026) e manchas
  simuladas por nível, da API do [site do INCT](http://vhlab.com.br/INCT/floods/) (coletadas em 10/11/2026). As manchas
  coletadas são coerentes com o `data.json`: a 3,0 m, cobrem os mesmos 24 bairros que ele dá como atingidos. O site foi
  atualizado depois e hoje mostra uma versão diferente da simulação; o dashboard mantém a de 10/11, a mesma da Tela 1.
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
  nível. A mancha é usada inteira, como o INCT a fornece. Ela não cobre o lago Guaíba, mas cobre rios e canais e termina num
  retângulo, que é o limite da área simulada. Ela não é recortada pelo limite do município porque o limite simplificado dos
  bairros cortaria faixas de orla onde ficam obras: com a mancha inteira, entra o Calçadão de Ipanema, e nenhuma outra obra muda. O valor somado é o investimento previsto pela Prefeitura para cada obra. Diques, casas de bombas e comportas ficam
  na beira da água por função, por isso já são alcançados nos níveis baixos e respondem pela maior parte da soma.

### Limitações
- Os números da simulação são estimativas, não previsões nem contagens oficiais. A população afetada supõe pessoas
  distribuídas igualmente entre todos os prédios do bairro.
- Comparada com os prédios que o Copernicus marcou como atingidos em 2024, a mancha de 5,3 m contém 80% deles (89% contando até 50 m da borda). Os demais ficam, em geral, a 100–250 m da borda, sobretudo no Sarandi, no Centro Histórico e no Santa Rosa de Lima: a mancha simulada é um pouco menor que a área atingida em 2024. As causas não foram investigadas.
- Acima de 5,35 m, os níveis são cenários que nunca ocorreram. Na Tela 2, as manchas do INCT foram coletadas só até 5,4 m.
- Os valores das obras são **previstos**, não pagos, e muitos são rateios: o mesmo contrato dividido entre vários projetos.
  Servem como ordem de grandeza, não como custo exato de cada obra.
- A Prefeitura publica o valor das obras do sistema de proteção em duas camadas que não concordam: a camada 3, por obra,
  soma R\\$ 620,6 mi, e a camada 4, por etapa, R\\$ 420,2 mi; os três maiores diques têm de R\\$ 101 a 152 mi cada na
  primeira e R\\$ 20 mi cada na segunda. O dashboard usa a camada 3, a única que traz os dois grupos de obra com o mesmo
  campo. Com a camada 4, o investimento exposto a 5,3 m seria de cerca de R\\$ 390 mi, e não R\\$ 712 mi.
- Cada obra é um ponto no mapa; um dique de vários quilômetros aparece como um único lugar. 44 obras não têm coordenada e
  ficam de fora, 43 delas do sistema de proteção.
- Os números exibidos no site do painel da Prefeitura às vezes diferem dos dados abertos que ele publica; este dashboard usa
  os dados abertos.

### Autoria
Projeto Extensionista da disciplina Coleta, Preparação e Análise de Dados (PUCRS). Autor: João Pedro da Silva Kriger.
O código e os dados tratados estão no repositório do projeto.
""")
