"""Tela 2: conforme a água avança, quanto da verba da reconstrução está na área alcançada?

Investimento exposto = valor previsto das obras de reconstrução que ficam na área alcançada pela água (mancha do INCT).
Não é custo de dano.
"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import dados
import estado
from estilo import (AGUA_CLARA, CONFIG_PLOTLY, CORES_CATEGORIA, NEUTRO, NIVEL_RECORDE_SIMULADO, RECORDE_2024, TINTA,
                    TINTA_SECUNDARIA, cartao, escopo, fonte, layout_grafico, nivel, niveis, numero, reais, secao, titulo)

NIVEL_MAXIMO = 5.4
CATEGORIAS = ["Sistema de proteção", "Equipamentos públicos"]
ARCGIS = "https://gis-smamus.portoalegre.rs.gov.br/server/rest/services/HUB"
COR_FORA = "#c9c8c3"      # obras fora da área alcançada (contexto)
COR_P08 = "#9a9994"       # prédios atingidos em 2024 (contexto)


def legenda_categorias(mostrar_p08):
    partes = []
    for nome, cor in CORES_CATEGORIA.items():
        partes.append(f'<span class="legenda-cor" style="background:{cor}"></span>{nome}')
    partes.append(f'<span class="legenda-cor" style="background:{COR_FORA}"></span>fora da área alcançada')
    if mostrar_p08:
        partes.append(f'<span class="legenda-cor" style="background:{COR_P08};width:6px;height:6px"></span>prédio atingido em 2024')
    st.markdown(f'<div class="subsecao">{"".join(partes)}</div>', unsafe_allow_html=True)


def mapa(obras, valor, mostrar_p08):
    fig = go.Figure()
    if mostrar_p08:
        p08 = dados.predios_atingidos_2024()
        fig.add_trace(go.Scattermap(lat=p08["lat"], lon=p08["lon"], mode="markers", marker=dict(size=3, color=COR_P08, opacity=.35),
                                    hoverinfo="skip", name="Prédios atingidos em 2024 (Copernicus)"))

    fora = obras[obras["alcancada"] == False]
    fig.add_trace(go.Scattermap(lat=fora["lat"], lon=fora["lon"], mode="markers", marker=dict(size=7, color=COR_FORA),
                                text=fora["dica"], hoverinfo="text", name="Fora da área alcançada"))
    for categoria in CATEGORIAS:
        grupo = obras[(obras["alcancada"] == True) & (obras["categoria"] == categoria)]
        tamanho = 8 + (grupo["valor_previsto"].fillna(0) / 1e6) ** 0.5 * 2.2
        fig.add_trace(go.Scattermap(lat=grupo["lat"], lon=grupo["lon"], mode="markers",
                                    marker=dict(size=tamanho, color=CORES_CATEGORIA[categoria], opacity=.92),
                                    text=grupo["dica"], hoverinfo="text", name=categoria))

    camadas = [dict(source=dados.mancha(valor), type="fill", color=AGUA_CLARA, opacity=.45, below="traces")]
    camadas.append(dict(source=dados.malha_bairros(), type="line", color="#b8b7b2", line=dict(width=.6), below="traces"))
    fig.update_layout(map=dict(style="carto-positron", center=dict(lat=-30.07, lon=-51.18), zoom=9.9, layers=camadas))
    fig = layout_grafico(fig, altura=560)
    fig.update_layout(showlegend=False)
    return fig


def curva(obras_filtradas, valor):
    pontos = niveis(3.0, NIVEL_MAXIMO)
    fig = go.Figure()
    for categoria in CATEGORIAS:
        grupo = obras_filtradas[obras_filtradas["categoria"] == categoria]
        totais = []
        for n in pontos:
            totais.append(grupo.loc[grupo["nivel_alcance"] <= n, "valor_previsto"].sum() / 1e6)
        fig.add_trace(go.Scatter(x=pontos, y=totais, mode="lines", stackgroup="um", name=categoria,
                                 line=dict(color=CORES_CATEGORIA[categoria], width=1.5),
                                 hovertemplate=f"{categoria}<br>Rio a %{{x:.1f}} m: R$ %{{y:,.1f}} mi<extra></extra>"))
    fig.add_vline(x=valor, line_color=TINTA, line_width=1.5)
    fig.add_annotation(x=valor, y=.04, yref="paper", text=f"nível escolhido: {nivel(valor)}", showarrow=False,
                       xanchor="right", xshift=-6, font=dict(size=12, color=TINTA), bgcolor="rgba(255,255,255,.85)")
    fig.add_vline(x=RECORDE_2024, line_dash="dash", line_color=NEUTRO, line_width=1.2)
    fig.update_xaxes(title_text="Nível do Guaíba (m)", range=[3.0, 5.4], dtick=.5)
    fig.update_yaxes(title_text="R$ milhões (previsto)", rangemode="tozero")
    fig = layout_grafico(fig, altura=330)
    fig.update_layout(legend=dict(traceorder="normal"))
    return fig


def solicitado_recebido(financeiro):
    grupos = ["Emergência", "Reconstrução"]
    pedidos = financeiro["solicitado_recebido"]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=grupos, y=[pedidos[g]["Solicitado"] / 1e6 for g in grupos], name="Solicitado à União",
                         marker_color="#d6d5d0", hovertemplate="%{x}: R$ %{y:,.1f} mi solicitados<extra></extra>"))
    fig.add_trace(go.Bar(x=grupos, y=[pedidos[g]["Recebido"] / 1e6 for g in grupos], name="Recebido",
                         marker_color=TINTA_SECUNDARIA, hovertemplate="%{x}: R$ %{y:,.1f} mi recebidos<extra></extra>",
                         text=[reais(pedidos[g]["Recebido"]) for g in grupos], textposition="outside", textfont=dict(color=TINTA)))
    fig.update_yaxes(title_text="R$ milhões")
    fig = layout_grafico(fig, altura=300)
    fig.update_layout(barmode="group", bargap=.35, bargroupgap=.08)
    return fig


def necessidade(financeiro):
    itens = sorted(financeiro["necessidade_estimada"].items(), key=lambda item: item[1])
    nomes = []
    valores = []
    for nome, valor in itens:
        nomes.append(nome)
        valores.append(valor / 1e9)
    fig = go.Figure(go.Bar(x=valores, y=nomes, orientation="h", marker_color="#a9a8a3",
                           hovertemplate="%{y}: R$ %{x:,.2f} bi<extra></extra>"))
    fig.update_xaxes(title_text="R$ bilhões")
    return layout_grafico(fig, altura=300)


@st.cache_data(show_spinner=False)
def preparar_obras(obras, valor):
    obras = obras.copy()
    obras["alcancada"] = obras["nivel_alcance"].notna() & (obras["nivel_alcance"] <= valor)
    dicas = []
    for _, obra in obras.iterrows():
        if pd.isna(obra["valor_previsto"]):
            valor_texto = "sem valor informado"
        else:
            valor_texto = reais(obra["valor_previsto"]) + " previstos"
        if pd.isna(obra["nivel_alcance"]):
            alcance = "não alcançada até 5,4 m"
        else:
            alcance = f"alcançada a partir de {nivel(obra['nivel_alcance'])}"
        dicas.append(f"<b>{obra['obra'].title()}</b><br>{obra['tipo']} · {obra['bairro'].title()}<br>{valor_texto}"
                     f"<br>Situação: {obra['situacao'].lower()}<br>{alcance}")
    obras["dica"] = dicas
    return obras


def mostrar():
    titulo("Tela 2 · Investimento exposto",
           "A mesma simulação do INCT da Tela 1, cruzada com as obras que a Prefeitura monitora desde a enchente de 2024.")
    escopo(["Se o rio subir, quais obras da reconstrução ficam na área alcançada pela água, e quanto está previsto nelas?"],
           ["As 318 obras de reconstrução monitoradas pela Prefeitura após a enchente de 2024 (274 com localização)",
            "194 de equipamentos públicos (193 com localização): 137 de esporte e lazer, 20 de assistência social, 18 de saúde, 14 de educação e 5 de cultura",
            "124 do sistema de proteção contra cheias: diques, casas de bombas, comportas (só 81 com localização)",
            "Valor previsto e situação de cada obra, informados pela Prefeitura"],
           ["Todas as obras da cidade: só as da reconstrução",
            "Habitação, cujo valor é uma necessidade estimada, e não o valor de uma obra",
            "Transformação urbana e ações de adaptação climática, sem localização ou valor por obra",
            "Valores pagos: o valor de cada obra é previsto"])
    st.markdown('<div class="aviso"><b>Investimento exposto</b> é a soma do valor <b>previsto</b> das obras que ficam na área '
                'alcançada pela água. <b>Não é custo de dano</b>: mostra quanto da verba da reconstrução está em lugares que alagam. Diques, casas de bombas e comportas ficam '
                'na beira da água por função, então é esperado que sejam alcançados já nos níveis baixos e que dominem a soma; '
                'para ver os serviços à população, filtre <b>Equipamentos públicos</b>.</div>',
                unsafe_allow_html=True)

    nivel_compartilhado = estado.nivel_atual()
    st.session_state["nivel_t2"] = min(nivel_compartilhado, NIVEL_MAXIMO)
    coluna_slider, coluna_botao = st.columns([5, 1.3], vertical_alignment="bottom")
    with coluna_slider:
        valor = st.select_slider("Nível do Guaíba", options=niveis(3.0, NIVEL_MAXIMO), format_func=nivel, key="nivel_t2",
                          on_change=estado.guardar_nivel, args=("nivel_t2",),
                          help="De 3,0 a 5,4 m: as manchas do INCT foram coletadas só até 5,4 m, logo acima do recorde de 2024.")
    with coluna_botao:
        st.button("Ir para o recorde de 2024", on_click=estado.ir_para, args=(NIVEL_RECORDE_SIMULADO, "nivel_t2"),
                  width="stretch", key="recorde_t2")
    valor = round(valor, 1)
    if nivel_compartilhado > NIVEL_MAXIMO:
        st.info(f"A Tela 1 está em {nivel(nivel_compartilhado)}. Aqui o máximo é {nivel(NIVEL_MAXIMO)}: as manchas do INCT "
                "foram coletadas só até esse nível, logo acima do recorde de 2024, e a tela mostra 5,4 m.")

    filtro1, filtro2, filtro3 = st.columns([1.3, 1.6, 1])
    with filtro1:
        categorias = st.multiselect("Grupo de obra", CATEGORIAS, default=CATEGORIAS)
    todas = dados.obras()
    situacoes = sorted(todas["situacao"].unique())
    with filtro2:
        escolhidas = st.multiselect("Situação da obra de reconstrução", situacoes, default=situacoes)
    with filtro3:
        st.write("")
        mostrar_p08 = st.toggle("Prédios atingidos em 2024", help="Pontos do Copernicus EMSN194 (P08): prédios marcados como atingidos na enchente real.")

    obras = preparar_obras(todas, valor)
    obras = obras[obras["categoria"].isin(categorias) & obras["situacao"].isin(escolhidas)]
    alcancadas = obras[obras["alcancada"]]
    equipamentos = alcancadas[alcancadas["categoria"] == "Equipamentos públicos"]

    c1, c2, c3 = st.columns([1.4, 1, 1])
    with c1:
        cartao("Investimento exposto (valor previsto)", reais(alcancadas["valor_previsto"].sum()),
               f"com o rio a {nivel(valor)}, de {reais(obras['valor_previsto'].sum())} previstos nas obras selecionadas", destaque=True)
    with c2:
        cartao("Obras na área alcançada", f"{len(alcancadas)} de {len(obras)}", "obras de reconstrução com localização, conforme os filtros")
    with c3:
        cartao("Equipamentos públicos alcançados", numero(len(equipamentos)),
               f"{reais(equipamentos['valor_previsto'].sum())} previstos em esporte e lazer, assistência, saúde, educação e cultura")

    st.write("")
    esquerda, direita = st.columns([1.45, 1])
    with esquerda:
        secao("Onde estão as obras alcançadas?", f"Área azul: mancha simulada pelo INCT com o rio a {nivel(valor)}. Tamanho do ponto: valor previsto.")
        legenda_categorias(mostrar_p08)
        st.plotly_chart(mapa(obras, valor, mostrar_p08), width="stretch", config=CONFIG_PLOTLY)
    with direita:
        secao("Como cresce o investimento exposto conforme o rio sobe?", "Soma do valor previsto das obras alcançadas em cada nível.")
        st.plotly_chart(curva(obras, valor), width="stretch", config=CONFIG_PLOTLY)
        secao("Quais são as obras alcançadas?", "Ordenadas pelo valor previsto. Clique no cabeçalho para reordenar.")
        ordenadas = alcancadas.sort_values("valor_previsto", ascending=False)
        valores = []
        for valor_obra in ordenadas["valor_previsto"]:
            if pd.isna(valor_obra):
                valores.append("sem valor")
            else:
                valores.append(reais(valor_obra))
        tabela = {"Obra": list(ordenadas["obra"].str.title()), "Valor previsto": valores,
                  "Tipo": list(ordenadas["tipo"]), "Bairro": list(ordenadas["bairro"].str.title())}
        st.dataframe(tabela, hide_index=True, width="stretch", height=220,
                     column_config={"Obra": st.column_config.TextColumn(width="medium")})
    fonte(f'<a href="https://prefeitura.poa.br/monitoramento-reconstrucao" target="_blank">painel Monitoramento da Reconstrução</a>, '
          f'dados abertos da Prefeitura de Porto Alegre (<a href="{ARCGIS}/base_reconstrucao/FeatureServer" target="_blank">ArcGIS</a>), '
          'registros de 17/09/2026, coletados em 27/10/2026; manchas da API do <a href="http://vhlab.com.br/INCT/floods/" '
          'target="_blank">INCT SiMAI</a>, coletadas em 10/11/2026; prédios atingidos: <a href="https://riskandrecovery.emergency.copernicus.eu/EMSN194/" '
          'target="_blank">© European Union, Copernicus Emergency Management Service</a>, coletados em 04/11/2026. '
          '44 obras sem coordenada (43 delas do sistema de proteção) não aparecem.')

    st.divider()
    financeiro = dados.financeiro()
    secao("E quanto dinheiro a cidade estima precisar, pediu e recebeu?", "Totais da cidade no painel financeiro da Prefeitura, para toda a recuperação, não só para as obras do mapa. Não dependem do nível do rio.")
    a, b, c = st.columns(3)
    pedidos = financeiro["solicitado_recebido"]["Total Recebido"]
    aplicados = sum(financeiro["recursos_aplicados_por_origem"].values())
    total_necessidade = sum(financeiro["necessidade_estimada"].values())
    reconstrucao = financeiro["solicitado_recebido"]["Reconstrução"]
    parcela = reconstrucao["Recebido"] / reconstrucao["Solicitado"] * 100
    data_registros = financeiro["data_dos_registros"]
    with a:
        cartao("Necessidade estimada", reais(total_necessidade),
               "estimativa da Prefeitura para a recuperação, inclui perda de arrecadação")
    with b:
        cartao("Recebido da União", reais(pedidos["Recebido"]), f"de {reais(pedidos['Solicitado'])} solicitados por cadastros formais")
    with c:
        origem = financeiro["recursos_aplicados_por_origem"]
        cartao("Recursos aplicados", reais(aplicados),
               f"{reais(origem['Município'])} do Município, {reais(origem['União'])} da União, {reais(origem['Estado'])} do Estado")
    esquerda, direita = st.columns(2)
    with esquerda:
        secao("Quanto foi pedido à União e quanto chegou?", f"Para a reconstrução chegaram {numero(parcela, 1)}% do solicitado.")
        st.plotly_chart(solicitado_recebido(financeiro), width="stretch", config=CONFIG_PLOTLY)
    with direita:
        secao("Para onde iria o dinheiro estimado?", f"Habitação e macrodrenagem somam a maior parte dos {reais(total_necessidade)}.")
        st.plotly_chart(necessidade(financeiro), width="stretch", config=CONFIG_PLOTLY)
    fonte(f'<a href="{ARCGIS}/hub_base_financeiro/FeatureServer" target="_blank">painel financeiro da Prefeitura de Porto Alegre</a>, '
          f'registros de {data_registros}, coletados em 27/10/2026. Segundo o painel, os recursos aplicados incluem projetos e obras '
          'contratadas e podem não estar todos pagos.')
