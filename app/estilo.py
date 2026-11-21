"""Cores, tipografia e componentes visuais compartilhados pelas telas.

Princípios aplicados em todo o app:
- Gestalt: proximidade (indicadores agrupados em cartões lado a lado), semelhança (a mesma cor sempre
  significa a mesma coisa), região comum (cada bloco em um cartão) e figura-fundo (a informação principal
  em destaque, o contexto em cinza).
- Nielsen: visibilidade do estado (o nível escolhido aparece sempre), correspondência com o mundo real
  (metros, reais e bairros, em português), controle do usuário (atalho para o recorde), consistência,
  prevenção de erros (slider limitado à faixa válida), reconhecimento em vez de memorização (legendas e
  dicas ao passar o mouse), design minimalista e ajuda (avisos curtos e página "Sobre os dados").
"""
import streamlit as st

# Paleta: as três primeiras cores da paleta categórica validada para daltonismo, mais tons neutros.
AGUA = "#2a78d6"            # informação principal: água e pessoas afetadas
AGUA_CLARA = "#86b6ef"      # área da mancha no mapa
PROTECAO = "#eb6834"        # sistema de proteção (diques, casas de bombas, comportas)
EQUIPAMENTOS = "#1baf7a"    # equipamentos públicos (escolas, saúde, praças...)
TINTA = "#0b0b0b"           # texto principal
TINTA_SECUNDARIA = "#52514e"
NEUTRO = "#8c8b86"          # contexto, referências, itens fora da seleção
NEUTRO_CLARO = "#e4e3df"
FUNDO_CARTAO = "#ffffff"
SUPERFICIE = "#fcfcfb"

RAMPA_AZUL = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#2a78d6", "#1c5cab", "#104281"]
CORES_CATEGORIA = {"Sistema de proteção": PROTECAO, "Equipamentos públicos": EQUIPAMENTOS}

RECORDE_2024 = 5.35
NIVEL_RECORDE_SIMULADO = 5.3   # o JSON tem passos de 0,1 m; 5,35 fica entre 5,3 e 5,4


def numero(valor, casas=0):
    """Formata número no padrão brasileiro: 1234567.8 vira 1.234.567,8."""
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def reais(valor):
    """R$ em milhões ou bilhões, com uma casa decimal."""
    if abs(valor) >= 1e9:
        return f"R$ {numero(valor / 1e9, 1)} bi"
    return f"R$ {numero(valor / 1e6, 1)} mi"


def nivel(valor):
    return f"{numero(valor, 1)} m"


def niveis(inicio, fim):
    """Lista de níveis em passos de 0,1 m, para os sliders."""
    quantidade = round((fim - inicio) * 10) + 1
    return [round(inicio + i / 10, 1) for i in range(quantidade)]


def aplicar_css():
    st.markdown(f"""
    <style>
      .block-container {{ padding-top: 2.2rem; max-width: 1280px; }}
      h1 {{ font-size: 1.9rem !important; font-weight: 700; color: {TINTA}; margin-bottom: .1rem; }}
      .pergunta {{ color: {TINTA_SECUNDARIA}; font-size: 1.05rem; margin-bottom: .8rem; }}
      .cartao {{ background: {FUNDO_CARTAO}; border: 1px solid {NEUTRO_CLARO}; border-radius: 12px;
                 padding: 14px 18px; height: 100%; }}
      .cartao .rotulo {{ color: {TINTA_SECUNDARIA}; font-size: .86rem; margin-bottom: 2px; }}
      .cartao .valor {{ color: {TINTA}; font-size: 1.75rem; font-weight: 700; line-height: 1.15; }}
      .cartao .detalhe {{ color: {TINTA_SECUNDARIA}; font-size: .82rem; margin-top: 4px; }}
      .cartao.destaque {{ border-left: 6px solid var(--cor-destaque, {AGUA}); }}
      .cartao.destaque .valor {{ font-size: 2.35rem; }}
      .estado {{ display: inline-block; padding: 5px 12px; border-radius: 999px; font-size: .9rem;
                 background: #eef4fc; color: {TINTA}; border: 1px solid #cde2fb; margin: 2px 0 10px 0; }}
      .estado.hipotetico {{ background: #f5f4f1; border-color: {NEUTRO_CLARO}; }}
      .aviso {{ background: #f7f6f3; border: 1px solid {NEUTRO_CLARO}; border-radius: 10px; padding: 10px 14px;
                color: {TINTA_SECUNDARIA}; font-size: .9rem; margin-bottom: .6rem; }}
      .aviso b {{ color: {TINTA}; }}
      .escopo {{ display: grid; grid-template-columns: 1.1fr 1.3fr 1fr; gap: 0; background: {FUNDO_CARTAO};
                  border: 1px solid {NEUTRO_CLARO}; border-radius: 12px; margin: .2rem 0 .9rem 0; }}
      .escopo > div {{ padding: 12px 16px; border-left: 1px solid {NEUTRO_CLARO}; font-size: .88rem; color: {TINTA_SECUNDARIA}; }}
      .escopo > div:first-child {{ border-left: none; }}
      .escopo .cab {{ font-size: .74rem; letter-spacing: .04em; text-transform: uppercase; color: {NEUTRO}; margin-bottom: 4px; font-weight: 600; }}
      .escopo .pergunta-principal {{ color: {TINTA}; font-size: 1rem; font-weight: 650; line-height: 1.3; }}
      .escopo ul {{ margin: 0; padding-left: 1.05rem; }} .escopo li {{ margin: 1px 0; }}
      @media (max-width: 900px) {{ .escopo {{ grid-template-columns: 1fr; }} .escopo > div {{ border-left: none; border-top: 1px solid {NEUTRO_CLARO}; }} }}
      .secao {{ font-size: 1.1rem; font-weight: 650; color: {TINTA}; margin: .4rem 0 .1rem 0; }}
      .subsecao {{ color: {TINTA_SECUNDARIA}; font-size: .86rem; margin-bottom: .3rem; }}
      .fonte {{ color: {NEUTRO}; font-size: .78rem; margin-top: -.2rem; }}
      .fonte a {{ color: {TINTA_SECUNDARIA}; }}
      .legenda-cor {{ display: inline-block; width: 11px; height: 11px; border-radius: 50%; margin: 0 5px -1px 10px; }}
    </style>""", unsafe_allow_html=True)


def cartao(rotulo, valor, detalhe="", destaque=False, cor=AGUA):
    """Cartão de indicador. O destacado é a informação principal da tela (figura); os outros são contexto."""
    classe = "cartao destaque" if destaque else "cartao"
    estilo = f'style="--cor-destaque:{cor}"' if destaque else ""
    st.markdown(f'<div class="{classe}" {estilo}><div class="rotulo">{rotulo}</div><div class="valor">{valor}</div>'
                f'<div class="detalhe">{detalhe}</div></div>', unsafe_allow_html=True)


def escopo(perguntas, cobre, nao_cobre):
    """Quadro no topo da tela: que pergunta ela responde, o que os dados cobrem e o que fica de fora."""
    itens_perguntas = "".join(f'<div class="pergunta-principal">{p}</div>' for p in perguntas)
    itens_cobre = "".join(f"<li>{item}</li>" for item in cobre)
    itens_nao = "".join(f"<li>{item}</li>" for item in nao_cobre)
    st.markdown(f'<div class="escopo"><div><div class="cab">Pergunta que esta tela responde</div>{itens_perguntas}</div>'
                f'<div><div class="cab">O que os dados cobrem</div><ul>{itens_cobre}</ul></div>'
                f'<div><div class="cab">O que fica de fora</div><ul>{itens_nao}</ul></div></div>', unsafe_allow_html=True)


def titulo(texto, pergunta):
    st.markdown(f"# {texto}")
    st.markdown(f'<div class="pergunta">{pergunta}</div>', unsafe_allow_html=True)


def secao(texto, subtitulo=""):
    st.markdown(f'<div class="secao">{texto}</div>', unsafe_allow_html=True)
    if subtitulo:
        st.markdown(f'<div class="subsecao">{subtitulo}</div>', unsafe_allow_html=True)


def fonte(texto):
    st.markdown(f'<div class="fonte">Fonte: {texto}</div>', unsafe_allow_html=True)


def layout_grafico(fig, altura=320):
    """Aparência comum dos gráficos: grade discreta, eixos recessivos, separador decimal brasileiro."""
    fig.update_layout(
        height=altura, margin=dict(l=8, r=8, t=8, b=8), separators=",.",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, 'Source Sans Pro', sans-serif", size=13, color=TINTA_SECUNDARIA),
        hoverlabel=dict(bgcolor="white", font_size=13, font_color=TINTA, bordercolor=NEUTRO_CLARO),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title_text=""),
    )
    fig.update_xaxes(showgrid=False, linecolor=NEUTRO_CLARO, tickcolor=NEUTRO_CLARO, zeroline=False)
    fig.update_yaxes(gridcolor="#efeeea", linecolor=NEUTRO_CLARO, zeroline=False)
    return fig


CONFIG_PLOTLY = {"displayModeBar": False, "locale": "pt-BR"}
