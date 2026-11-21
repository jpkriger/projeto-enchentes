"""Tela 1: se o rio chegar a X metros, quais bairros e quantas pessoas são afetados?

Usa somente o JSON do INCT depois de limpo (o mapa usa também a malha oficial de bairros, só para desenhar).
"""
import plotly.graph_objects as go
import streamlit as st

import dados
import estado
from estilo import (AGUA, CONFIG_PLOTLY, NEUTRO, NEUTRO_CLARO, NIVEL_RECORDE_SIMULADO, RAMPA_AZUL, RECORDE_2024,
                    TINTA_SECUNDARIA, cartao, fonte, layout_grafico, nivel, niveis, numero, secao, titulo)

FONTE_INCT = ('simulação do <a href="http://vhlab.com.br/INCT/floods/" target="_blank">INCT SiMAI</a> '
              '(arquivo data.json fornecido pela disciplina, coletado em 27/10/2026), depois da limpeza descrita no relatório')


def estado_do_nivel(valor):
    if valor > RECORDE_2024:
        return '<span class="estado hipotetico">Acima do recorde de 2024: cenário hipotético, que nunca ocorreu</span>'
    if valor == NIVEL_RECORDE_SIMULADO:
        return '<span class="estado">Nível simulado mais próximo do recorde de maio de 2024 (5,35 m)</span>'
    return '<span class="estado">Abaixo do recorde de maio de 2024 (5,35 m)</span>'


def mapa(no_nivel):
    malha = dados.malha_bairros()
    atingidos = no_nivel.set_index("bairro_malha")
    nomes, valores, textos = [], [], []
    for feicao in malha["features"]:
        nome = feicao["properties"]["bairro"]
        linha = atingidos.loc[nome]
        nomes.append(nome)
        valores.append(linha["percentage"])
        textos.append(f"<b>{linha['bairro']}</b><br>{numero(linha['percentage'], 1)}% dos prédios afetados"
                      f"<br>{numero(linha['affected_buildings'])} de {numero(linha['total_buildings'])} prédios"
                      f"<br>{numero(linha['affected_population'])} pessoas (estimativa)")
    escala = [[0, "#f2f1ee"], [0.0001, RAMPA_AZUL[0]]]
    for i, cor in enumerate(RAMPA_AZUL[1:], start=1):
        escala.append([i / (len(RAMPA_AZUL) - 1), cor])
    fig = go.Figure(go.Choroplethmap(
        geojson=malha, featureidkey="properties.bairro", locations=nomes, z=valores, zmin=0, zmax=100,
        colorscale=escala, marker_line_color="white", marker_line_width=.8, text=textos, hoverinfo="text",
        colorbar=dict(title=dict(text="% dos<br>prédios", font=dict(size=12)), thickness=10, len=.6, ticksuffix="%",
                      x=.99, xanchor="right", bgcolor="rgba(255,255,255,.85)"),
    ))
    fig.update_layout(map=dict(style="carto-positron", center=dict(lat=-30.09, lon=-51.18), zoom=9.6))
    return layout_grafico(fig, altura=520)


def barras_por_bairro(no_nivel):
    atingidos = no_nivel[no_nivel["affected_buildings"] > 0].sort_values("percentage")
    fig = go.Figure(go.Bar(
        x=atingidos["percentage"], y=atingidos["bairro"], orientation="h", marker_color=AGUA,
        marker_line_width=0, customdata=atingidos[["affected_buildings", "total_buildings"]],
        hovertemplate="<b>%{y}</b><br>%{x:.1f}% dos prédios<br>%{customdata[0]:,.0f} de %{customdata[1]:,.0f}<extra></extra>",
    ))
    fig.update_xaxes(range=[0, 104], tickvals=[0, 25, 50, 75, 100], ticktext=["0%", "25%", "50%", "75%", "100%"], side="top")
    fig = layout_grafico(fig, altura=max(260, 20 * len(atingidos) + 40))
    fig.update_layout(bargap=.25)
    return fig, len(atingidos)


def curva_populacao(limpo, valor):
    total = limpo.groupby("nivel_m")["affected_population"].sum().reset_index()
    atual = total[total["nivel_m"] == valor]["affected_population"].iloc[0]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=total["nivel_m"], y=total["affected_population"], mode="lines", line=dict(color=AGUA, width=2.5),
                             hovertemplate="Rio a %{x:.1f} m<br>%{y:,.0f} pessoas<extra></extra>", name="Pessoas afetadas"))
    fig.add_vline(x=RECORDE_2024, line_dash="dash", line_color=NEUTRO, line_width=1.2)
    fig.add_annotation(x=RECORDE_2024, y=1, yref="paper", text="recorde de 2024: 5,35 m", showarrow=False,
                       xanchor="left", xshift=6, font=dict(size=12, color=TINTA_SECUNDARIA))
    fig.add_trace(go.Scatter(x=[valor], y=[atual], mode="markers", marker=dict(size=13, color=AGUA, line=dict(color="white", width=2)),
                             hovertemplate="Nível escolhido: %{x:.1f} m<br>%{y:,.0f} pessoas<extra></extra>", showlegend=False))
    fig.update_xaxes(title_text="Nível do Guaíba (m)", dtick=1)
    fig.update_yaxes(title_text="Pessoas afetadas", rangemode="tozero", tickformat=",.0f")
    fig = layout_grafico(fig, altura=390)
    fig.update_layout(showlegend=False)
    return fig


def ranking(no_nivel):
    topo = no_nivel[no_nivel["affected_population"] > 0].nlargest(10, "affected_population")
    pessoas = []
    for valor in topo["affected_population"]:
        pessoas.append(numero(valor))
    tabela = {"#": list(range(1, len(topo) + 1)), "Bairro": list(topo["bairro"]), "Pessoas afetadas": pessoas,
              "% dos prédios": list(topo["percentage"])}
    return tabela


def mostrar():
    limpo = dados.inct_limpo()
    titulo("Se o Guaíba chegar a X metros, quem é afetado?",
           "Simulação do INCT SiMAI para Porto Alegre: escolha o nível do rio e veja bairros, prédios e pessoas afetados.")
    st.markdown('<div class="aviso"><b>Estes números são estimativas de uma simulação</b>, não previsões nem contagens oficiais. '
                'A população afetada supõe pessoas distribuídas igualmente entre todos os prédios do bairro.</div>',
                unsafe_allow_html=True)

    st.session_state["nivel_t1"] = estado.nivel_atual()   # parte do nível usado por último em qualquer tela
    coluna_slider, coluna_botao = st.columns([5, 1.3], vertical_alignment="bottom")
    with coluna_slider:
        valor = st.select_slider("Nível do Guaíba", options=niveis(3.0, 10.0), format_func=nivel, key="nivel_t1",
                          on_change=estado.guardar_nivel, args=("nivel_t1",),
                          help="De 3,0 a 10,0 m, em passos de 0,1 m. Todos os elementos da tela mudam juntos.")
    with coluna_botao:
        st.button("Ir para o recorde de 2024", on_click=estado.ir_para, args=(NIVEL_RECORDE_SIMULADO, "nivel_t1"),
                  width="stretch", help="O JSON tem passos de 0,1 m: 5,3 m é o nível simulado mais próximo de 5,35 m.")
    valor = round(valor, 1)
    st.markdown(estado_do_nivel(valor), unsafe_allow_html=True)

    no_nivel = limpo[limpo["nivel_m"] == valor]
    pessoas = no_nivel["affected_population"].sum()
    populacao = no_nivel["population"].sum()
    predios = no_nivel["affected_buildings"].sum()
    total_predios = no_nivel["total_buildings"].sum()
    bairros = int((no_nivel["affected_buildings"] > 0).sum())

    c1, c2, c3 = st.columns([1.4, 1, 1])
    with c1:
        cartao("Pessoas afetadas (estimativa)", numero(pessoas), f"{numero(pessoas / populacao * 100, 1)}% da população da cidade",
               destaque=True)
    with c2:
        cartao("Prédios afetados", numero(predios), f"{numero(predios / total_predios * 100, 1)}% dos prédios da cidade")
    with c3:
        cartao("Bairros atingidos", f"{bairros} de 94", "com pelo menos um prédio afetado")

    st.write("")
    esquerda, direita = st.columns([1.45, 1])
    with esquerda:
        secao("Onde a água chega", f"Porcentagem de prédios afetados em cada bairro, com o rio a {nivel(valor)}. "
              "Bairros em cinza não são atingidos.")
        st.plotly_chart(mapa(no_nivel), width="stretch", config=CONFIG_PLOTLY)
    with direita:
        figura, quantidade = barras_por_bairro(no_nivel)
        secao("Porcentagem de prédios afetados por bairro", f"{quantidade} bairros atingidos, do mais ao menos afetado.")
        if quantidade:
            with st.container(height=520, border=False):
                st.plotly_chart(figura, width="stretch", config=CONFIG_PLOTLY)

    esquerda, direita = st.columns([1.45, 1])
    with esquerda:
        secao("População afetada na cidade, nível a nível", "O ponto mostra o nível escolhido; a linha tracejada, o recorde de 2024.")
        st.plotly_chart(curva_populacao(limpo, valor), width="stretch", config=CONFIG_PLOTLY)
    with direita:
        secao("Bairros com mais pessoas afetadas", f"Os 10 primeiros com o rio a {nivel(valor)}.")
        st.dataframe(ranking(no_nivel), hide_index=True, width="stretch", height=388,
                     column_config={"#": st.column_config.NumberColumn(width="small"),
                                    "Pessoas afetadas": st.column_config.TextColumn(),
                                    "% dos prédios": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%.0f%%")})

    fonte(FONTE_INCT + '. Malha de bairros: <a href="https://gis-smamus.portoalegre.rs.gov.br/server/rest/services/'
          'A02_SOLO_CRIADO/bairros/FeatureServer/0" target="_blank">Prefeitura de Porto Alegre</a>, coletada em 27/10/2026.')
    with st.expander("Limitações dos dados"):
        st.markdown(
            "- A simulação considera a altura da água; não sabemos se inclui diques, comportas e casas de bombas.\n"
            "- A população afetada é a população do bairro multiplicada pela porcentagem de prédios afetados, "
            "supondo pessoas distribuídas igualmente entre todos os prédios, inclusive os não residenciais.\n"
            "- Acima de 5,35 m os valores são cenários que nunca ocorreram.\n"
            "- O arquivo original tinha inconsistências (porcentagem arredondada para cima e contagens que caíam com o rio "
            "subindo), corrigidas na limpeza. Os detalhes estão no relatório e na página *Sobre os dados*.")
