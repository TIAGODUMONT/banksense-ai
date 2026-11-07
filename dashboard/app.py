"""Dashboard executivo do BankSense AI (estilo Power BI, com storytelling).

Uso:
    streamlit run dashboard/app.py

Todos os dados são SINTÉTICOS.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from banksense.dados import premissas as P
from dados import carregar

st.set_page_config(page_title="BankSense AI", page_icon="🏦", layout="wide")

# ---------------------------------------------------------------------------
# Tema visual (inspirado no Power BI: fundo cinza claro, cartões brancos, azul como destaque)
# ---------------------------------------------------------------------------
AZUL = "#118DFF"
AZUL_ESCURO = "#12239E"
LARANJA = "#E66C37"
ROXO = "#6B007B"
CINZA = "#605E5C"
CORES_SENTIMENTO = {"Negativo": LARANJA, "Neutro": "#A0A0A0", "Positivo": AZUL}
PALETA = [AZUL, AZUL_ESCURO, LARANJA, ROXO, "#E044A7", "#744EC2", "#D9B300", "#D64550", "#197278"]

st.markdown(
    """
    <style>
      .stApp { background: #F3F2F1; }
      [data-testid="stSidebar"] { background: #FFFFFF; border-right: 1px solid #E1DFDD; }
      .block-container { padding-top: 1.2rem; padding-bottom: 2rem; }
      h1, h2, h3, p, span, div { font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif; }
      .kpi { background: #FFFFFF; border-radius: 6px; padding: 14px 18px; box-shadow: 0 1px 3px rgba(0,0,0,.12);
             border-top: 4px solid #118DFF; height: 100%; }
      .kpi .rotulo { color: #605E5C; font-size: .82rem; text-transform: uppercase; letter-spacing: .04em; }
      .kpi .valor { color: #252423; font-size: 1.9rem; font-weight: 600; line-height: 1.2; }
      .kpi .delta { font-size: .85rem; }
      .delta-ruim { color: #D64550; } .delta-bom { color: #197278; } .delta-neutro { color: #605E5C; }
      .capitulo { background: #FFFFFF; border-radius: 6px; padding: 18px 22px; box-shadow: 0 1px 3px rgba(0,0,0,.12);
                  margin: 6px 0 10px 0; border-left: 5px solid #12239E; }
      .capitulo .num { color: #118DFF; font-weight: 700; font-size: .85rem; text-transform: uppercase;
                       letter-spacing: .06em; }
      .capitulo h3 { margin: 2px 0 6px 0; color: #252423; }
      .capitulo p { color: #3B3A39; font-size: 1.02rem; margin: 0; }
      .aviso { background: #FFF4CE; border: 1px solid #F2D888; border-radius: 6px; padding: 8px 14px;
               color: #3B3A39; font-size: .9rem; }
      div[data-testid="stPlotlyChart"] { background: #FFFFFF; border-radius: 6px; padding: 6px;
                                         box-shadow: 0 1px 3px rgba(0,0,0,.12); }
    </style>
    """,
    unsafe_allow_html=True,
)


def estilizar(fig: go.Figure, titulo: str, altura: int = 340) -> go.Figure:
    fig.update_layout(
        title={"text": titulo, "font": {"size": 15, "color": "#252423"}, "x": 0.01},
        height=altura, margin={"l": 10, "r": 10, "t": 48, "b": 10},
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", font={"color": CINZA, "size": 12},
        legend={"orientation": "h", "y": -0.18, "title": None}, colorway=PALETA,
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#EDEBE9")
    return fig


def mostrar(fig: go.Figure) -> None:
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def fmt(n: float, casas: int = 0) -> str:
    return f"{n:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def pct(x: float, casas: int = 1) -> str:
    return f"{fmt(100 * x, casas)}%"


def cartao_kpi(coluna, rotulo: str, valor: str, delta: str = "", classe: str = "delta-neutro") -> None:
    coluna.markdown(
        f'<div class="kpi"><div class="rotulo">{rotulo}</div><div class="valor">{valor}</div>'
        f'<div class="delta {classe}">{delta}&nbsp;</div></div>',
        unsafe_allow_html=True,
    )


def capitulo(numero: int, titulo: str, texto: str) -> None:
    st.markdown(
        f'<div class="capitulo"><div class="num">Capítulo {numero}</div><h3>{titulo}</h3><p>{texto}</p></div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Dados e filtros (slicers)
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="Carregando dados...")
def dados_em_cache() -> tuple[pd.DataFrame, str]:
    return carregar()


base, origem = dados_em_cache()

with st.sidebar:
    st.markdown("### 🏦 BankSense AI")
    st.caption("Filtros: todos os visuais respondem a eles")
    data_min, data_max = base["data_mensagem"].min().date(), base["data_mensagem"].max().date()
    periodo = st.date_input("Período", (data_min, data_max), min_value=data_min, max_value=data_max,
                            format="DD/MM/YYYY")
    categorias = st.multiselect("Categoria", sorted(base["Categoria"].unique()))
    canais = st.multiselect("Canal", sorted(base["Canal"].unique()))
    regioes = st.multiselect("Região", sorted(base["Região"].dropna().unique()))
    segmentos = st.multiselect("Segmento", sorted(base["Segmento"].dropna().unique()))
    st.divider()
    st.caption(f"Fonte: {origem}")
    st.caption("⚠️ Dados 100% sintéticos, gerados para estudo.")

inicio, fim = (periodo if isinstance(periodo, tuple) and len(periodo) == 2 else (data_min, data_max))
inicio, fim = pd.Timestamp(inicio), pd.Timestamp(fim)


def aplicar_filtros(df: pd.DataFrame, de: pd.Timestamp, ate: pd.Timestamp) -> pd.DataFrame:
    m = df["data_mensagem"].between(de, ate)
    for coluna, escolhidos in (("Categoria", categorias), ("Canal", canais), ("Região", regioes),
                               ("Segmento", segmentos)):
        if escolhidos:
            m &= df[coluna].isin(escolhidos)
    return df[m]


df = aplicar_filtros(base, inicio, fim)
duracao = fim - inicio
anterior = aplicar_filtros(base, inicio - duracao - pd.Timedelta(days=1), inicio - pd.Timedelta(days=1))

if df.empty:
    st.warning("Nenhuma mensagem com esses filtros.")
    st.stop()

# ---------------------------------------------------------------------------
# Cabeçalho e KPIs
# ---------------------------------------------------------------------------
st.markdown("## Voz do Cliente · Banco digital fictício")
st.markdown(
    f'<div class="aviso">Período: <b>{inicio:%d/%m/%Y}</b> a <b>{fim:%d/%m/%Y}</b> · '
    f"{fmt(len(df))} mensagens · <b>Dados sintéticos:</b> nenhum número representa um banco real.</div>",
    unsafe_allow_html=True,
)
st.write("")


def indicadores(d: pd.DataFrame) -> dict[str, float]:
    resolvidas = d[d["situacao"] == "resolvida"]
    return {
        "volume": len(d),
        "neg": d["negativo"].mean() if len(d) else float("nan"),
        "nota": d["nota_satisfacao"].mean(),
        "tempo": resolvidas["tempo_resolucao_horas"].median(),
        "resol": (d["situacao"] == "resolvida").mean() if len(d) else float("nan"),
    }


atual, prev = indicadores(df), indicadores(anterior)


def variacao(chave: str, maior_e_ruim: bool, em_pontos: bool = False) -> tuple[str, str]:
    a, b = atual[chave], prev[chave]
    if pd.isna(b) or b == 0 or len(anterior) == 0:
        return "sem período anterior", "delta-neutro"
    if em_pontos:
        diff = (a - b) * 100
        texto = f"{'▲' if diff > 0 else '▼'} {fmt(abs(diff), 1)} p.p. vs período anterior"
    else:
        diff = a / b - 1
        texto = f"{'▲' if diff > 0 else '▼'} {pct(abs(diff))} vs período anterior"
    piorou = (diff > 0) == maior_e_ruim
    return texto, ("delta-ruim" if piorou else "delta-bom") if abs(diff) > 1e-9 else "delta-neutro"


k = st.columns(5)
cartao_kpi(k[0], "Mensagens", fmt(atual["volume"]), *variacao("volume", True))
cartao_kpi(k[1], "% negativas", pct(atual["neg"]), *variacao("neg", True, em_pontos=True))
cartao_kpi(k[2], "Nota média (1 a 5)", fmt(atual["nota"], 2), *variacao("nota", False))
cartao_kpi(k[3], "Tempo mediano de resolução", f"{fmt(atual['tempo'], 1)} h", *variacao("tempo", True))
cartao_kpi(k[4], "% resolvidas", pct(atual["resol"]), *variacao("resol", False, em_pontos=True))
st.write("")

aba_historia, aba_reclamacoes, aba_atendimento, aba_clientes, aba_modelo = st.tabs(
    ["📖 A História", "📉 Reclamações", "⏱️ Atendimento", "👥 Clientes", "🤖 Modelo"]
)

# ---------------------------------------------------------------------------
# Página 1: A História
# ---------------------------------------------------------------------------
with aba_historia:
    por_categoria = (df.groupby("Categoria")
                     .agg(total=("negativo", "size"), neg=("negativo", "mean"), nota=("nota_satisfacao", "mean"))
                     .sort_values("neg", ascending=False))
    pior_cat, melhor_cat = por_categoria.index[0], por_categoria.index[-1]
    reclamacoes_por_cat = (df[df["negativo"] == 1]["Categoria"].value_counts(normalize=True))
    top2 = reclamacoes_por_cat.head(2)

    if atual["neg"] >= 0.45:
        leitura = "Quase metade das conversas começa com um problema."
    elif atual["neg"] >= 0.30:
        leitura = "Cerca de um terço das conversas é uma reclamação."
    else:
        leitura = "A maioria das conversas não é reclamação."
    capitulo(
        1, "O cenário",
        f"No período, o banco recebeu <b>{fmt(len(df))} mensagens</b> de clientes. "
        f"<b>{pct(atual['neg'])}</b> delas são negativas, e a nota média de satisfação é "
        f"<b>{fmt(atual['nota'], 2)}</b> numa escala de 1 a 5. {leitura}",
    )
    c1, c2 = st.columns([1, 2])
    with c1:
        sent = df["Sentimento"].value_counts().reindex(["Negativo", "Neutro", "Positivo"]).reset_index()
        fig = px.pie(sent, names="Sentimento", values="count", hole=0.6, color="Sentimento",
                     color_discrete_map=CORES_SENTIMENTO)
        fig.update_traces(textinfo="percent", sort=False)
        mostrar(estilizar(fig, "Sentimento das mensagens"))
    with c2:
        semanal = (df.set_index("data_mensagem").groupby("Sentimento").resample("W")["id_mensagem"].count()
                   .reset_index(name="Mensagens"))
        fig = px.area(semanal, x="data_mensagem", y="Mensagens", color="Sentimento",
                      color_discrete_map=CORES_SENTIMENTO, category_orders={"Sentimento": ["Negativo", "Neutro",
                                                                                          "Positivo"]})
        fig.update_xaxes(title=None)
        mostrar(estilizar(fig, "Mensagens por semana"))

    if len(por_categoria) >= 3 and len(top2) == 2:
        texto_cap2 = (
            f"<b>{pior_cat}</b> é a categoria com mais insatisfação: "
            f"<b>{pct(por_categoria.loc[pior_cat, 'neg'])}</b> das mensagens são negativas. Em volume, "
            f"<b>{top2.index[0]}</b> e <b>{top2.index[1]}</b> concentram <b>{pct(top2.sum())}</b> de todas as "
            f"reclamações. No outro extremo, <b>{melhor_cat}</b> tem só "
            f"{pct(por_categoria.loc[melhor_cat, 'neg'])} de mensagens negativas."
        )
    else:
        nomes = " e ".join(f"<b>{c}</b> ({pct(v)} negativas)" for c, v in por_categoria["neg"].items())
        texto_cap2 = f"Com os filtros atuais, a análise cobre {nomes}. Limpe o filtro de categoria para comparar."
    capitulo(2, "Onde dói", texto_cap2)
    c1, c2 = st.columns(2)
    with c1:
        dados_bar = por_categoria.reset_index().sort_values("neg")
        fig = px.bar(dados_bar, x="neg", y="Categoria", orientation="h", text=dados_bar["neg"].map(pct),
                     color_discrete_sequence=[LARANJA])
        fig.update_xaxes(tickformat=".0%", title=None)
        fig.update_yaxes(title=None)
        mostrar(estilizar(fig, "% de mensagens negativas por categoria"))
    with c2:
        vol = df[df["negativo"] == 1]["Categoria"].value_counts().reset_index()
        fig = px.treemap(vol, path=["Categoria"], values="count", color_discrete_sequence=PALETA)
        fig.update_traces(texttemplate="%{label}<br>%{value:,}")
        mostrar(estilizar(fig, "Volume de reclamações por categoria"))

    diario = df.groupby("data_mensagem").agg(total=("negativo", "size"), neg=("negativo", "sum"))
    pico_dia = diario["neg"].idxmax()
    media_neg_dia = diario["neg"].mean()
    evento_no_periodo = inicio <= pd.Timestamp(P.EVENTO_INICIO) <= fim
    texto_evento = (
        f" O pior momento foi entre <b>{P.EVENTO_INICIO:%d/%m}</b> e <b>{P.EVENTO_FIM:%d/%m/%Y}</b>, quando uma "
        f"instabilidade no aplicativo (evento simulado) multiplicou as reclamações de app e Pix."
        if evento_no_periodo else ""
    )
    capitulo(
        3, "Quando piorou",
        f"Em média, chegam <b>{fmt(media_neg_dia, 0)} reclamações por dia</b>. O pico foi em "
        f"<b>{pico_dia:%d/%m/%Y}</b>, com <b>{fmt(diario.loc[pico_dia, 'neg'])}</b>, cerca de "
        f"{fmt(diario.loc[pico_dia, 'neg'] / media_neg_dia, 1)} vezes a média.{texto_evento}",
    )
    serie = diario["neg"].rename("Reclamações").reset_index()
    serie["Média móvel 7 dias"] = serie["Reclamações"].rolling(7, min_periods=1).mean()
    fig = go.Figure()
    fig.add_bar(x=serie["data_mensagem"], y=serie["Reclamações"], name="Reclamações por dia",
                marker_color="#C8C6C4")
    fig.add_scatter(x=serie["data_mensagem"], y=serie["Média móvel 7 dias"], name="Média móvel de 7 dias",
                    line={"color": LARANJA, "width": 3})
    if evento_no_periodo:
        fig.add_vrect(x0=P.EVENTO_INICIO, x1=P.EVENTO_FIM, fillcolor=LARANJA, opacity=0.12, line_width=0,
                      annotation_text="Instabilidade no app", annotation_position="top left")
    mostrar(estilizar(fig, "Reclamações por dia", altura=360))

    neg_canal = (df[df["Canal"] != "Não informado"].groupby("Canal")["negativo"].mean()
                 .sort_values(ascending=False))
    resolvidas = df[df["situacao"] == "resolvida"]
    tempo_sent = resolvidas.groupby("Sentimento")["tempo_resolucao_horas"].median()
    nota_por_tempo = resolvidas.assign(
        faixa=pd.qcut(resolvidas["tempo_resolucao_horas"], 4, labels=["Mais rápidos", "2º quartil",
                                                                    "3º quartil", "Mais lentos"])
    ).groupby("faixa", observed=True)["nota_satisfacao"].mean()
    capitulo(
        4, "Como o atendimento responde",
        f"Reclamações demoram mais: o tempo mediano de resolução de uma mensagem negativa é "
        f"<b>{fmt(tempo_sent.get('Negativo', float('nan')), 1)} h</b>, contra "
        f"{fmt(tempo_sent.get('Positivo', float('nan')), 1)} h das positivas. Os 25% atendimentos mais lentos têm "
        f"nota média <b>{fmt(nota_por_tempo.iloc[-1], 2)}</b>; os 25% mais rápidos, "
        f"<b>{fmt(nota_por_tempo.iloc[0], 2)}</b>. O canal com mais mensagens negativas é "
        f"<b>{neg_canal.index[0]}</b> ({pct(neg_canal.iloc[0])}).",
    )
    c1, c2 = st.columns(2)
    with c1:
        med = (resolvidas.groupby("Canal")["tempo_resolucao_horas"].median().sort_values().reset_index())
        fig = px.bar(med, x="tempo_resolucao_horas", y="Canal", orientation="h",
                     text=med["tempo_resolucao_horas"].map(lambda v: f"{fmt(v, 1)} h"),
                     color_discrete_sequence=[AZUL])
        fig.update_xaxes(title=None, type="log")
        fig.update_yaxes(title=None)
        mostrar(estilizar(fig, "Tempo mediano de resolução por canal (escala log)"))
    with c2:
        nt = nota_por_tempo.reset_index(name="Nota média")
        fig = px.bar(nt, x="faixa", y="Nota média", text=nt["Nota média"].map(lambda v: fmt(v, 2)),
                     color_discrete_sequence=[AZUL_ESCURO])
        fig.update_xaxes(title="Tempo de resolução (quartis)")
        fig.update_yaxes(range=[1, 5])
        mostrar(estilizar(fig, "Nota média conforme a demora"))

    st.markdown("#### O que fazer")
    r1, r2, r3 = st.columns(3)
    maiores = " e ".join(top2.index) if len(top2) else pior_cat
    acoes = (
        (r1, f"1. Atacar {pior_cat}", f"É a categoria com maior proporção de reclamações "
                                      f"({pct(por_categoria.loc[pior_cat, 'neg'])}). Revisar regras e comunicação."),
        (r2, f"2. Priorizar {maiores}",
         f"Somam {pct(top2.sum())} do volume de reclamações: qualquer melhora aqui move o indicador geral."),
        (r3, "3. Monitorar picos com o modelo", "Classificar cada mensagem na chegada e alertar quando a média "
                                                "móvel de reclamações sair do normal, como no evento do app."),
    )
    for coluna, titulo, texto in acoes:
        coluna.markdown(f'<div class="kpi" style="border-top-color:{AZUL_ESCURO}"><b>{titulo}</b>'
                        f'<p style="margin:6px 0 0 0;color:#3B3A39">{texto}</p></div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Página 2: Reclamações
# ---------------------------------------------------------------------------
with aba_reclamacoes:
    c1, c2 = st.columns(2)
    with c1:
        matriz = df.pivot_table(index="Categoria", columns="Canal", values="negativo", aggfunc="mean")
        fig = px.imshow(matriz, text_auto=".0%", color_continuous_scale=["#FFFFFF", LARANJA], aspect="auto")
        fig.update_coloraxes(showscale=False)
        mostrar(estilizar(fig, "% negativo: categoria x canal", altura=420))
    with c2:
        dias = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]
        semana = df[df["negativo"] == 1].assign(dia=lambda d: d["data_mensagem"].dt.dayofweek.map(dict(enumerate(dias))))
        sem = semana.pivot_table(index="Categoria", columns="dia", values="negativo", aggfunc="sum")[dias]
        fig = px.imshow(sem, text_auto=True, color_continuous_scale=["#FFFFFF", AZUL], aspect="auto")
        fig.update_coloraxes(showscale=False)
        mostrar(estilizar(fig, "Reclamações por dia da semana", altura=420))

    mensal = (df.set_index("data_mensagem").groupby("Categoria").resample("MS")["negativo"].mean()
              .reset_index(name="% negativo"))
    fig = px.line(mensal, x="data_mensagem", y="% negativo", color="Categoria", markers=True)
    fig.update_yaxes(tickformat=".0%")
    fig.update_xaxes(title=None)
    mostrar(estilizar(fig, "Evolução mensal do % negativo por categoria", altura=380))

    st.markdown("##### Reclamações mais recentes")
    recentes = (df[df["negativo"] == 1].sort_values("data_mensagem", ascending=False)
                [["data_mensagem", "Categoria", "Canal", "Região", "texto", "Situação"]].head(200))
    st.dataframe(recentes.rename(columns={"data_mensagem": "Data", "texto": "Mensagem"}), hide_index=True,
                 width="stretch", height=320,
                 column_config={"Data": st.column_config.DateColumn(format="DD/MM/YYYY")})

# ---------------------------------------------------------------------------
# Página 3: Atendimento
# ---------------------------------------------------------------------------
with aba_atendimento:
    resolvidas = df[(df["situacao"] == "resolvida") & df["tempo_resolucao_horas"].notna()]
    c1, c2 = st.columns(2)
    with c1:
        fig = px.box(resolvidas, x="Canal", y="tempo_resolucao_horas", color="Canal", points=False,
                     color_discrete_sequence=PALETA)
        fig.update_yaxes(type="log", title="horas (escala log)")
        fig.update_layout(showlegend=False)
        mostrar(estilizar(fig, "Distribuição do tempo de resolução por canal", altura=380))
    with c2:
        sit = df.groupby(["Canal", "Situação"]).size().reset_index(name="Mensagens")
        fig = px.bar(sit, x="Canal", y="Mensagens", color="Situação", barmode="stack",
                     color_discrete_sequence=[AZUL, "#C8C6C4", LARANJA, ROXO])
        mostrar(estilizar(fig, "Situação dos atendimentos por canal", altura=380))
    c1, c2 = st.columns(2)
    with c1:
        notas = df.dropna(subset=["nota_satisfacao"]).groupby(["Sentimento", "nota_satisfacao"]).size()
        notas = notas.reset_index(name="Mensagens")
        fig = px.bar(notas, x="nota_satisfacao", y="Mensagens", color="Sentimento", barmode="group",
                     color_discrete_map=CORES_SENTIMENTO)
        fig.update_xaxes(title="Nota", dtick=1)
        mostrar(estilizar(fig, "Distribuição das notas por sentimento"))
    with c2:
        num = df.assign(mes=(df["data_mensagem"] - df["data_mensagem"].min()).dt.days)[
            ["nota_satisfacao", "tempo_resolucao_horas", "negativo", "mes"]]
        corr = num.rename(columns={"nota_satisfacao": "Nota", "tempo_resolucao_horas": "Tempo",
                                   "negativo": "Negativo", "mes": "Data"}).corr(method="spearman")
        fig = px.imshow(corr, text_auto=".2f", zmin=-1, zmax=1,
                        color_continuous_scale=[LARANJA, "#FFFFFF", AZUL])
        mostrar(estilizar(fig, "Correlação de Spearman"))

# ---------------------------------------------------------------------------
# Página 4: Clientes
# ---------------------------------------------------------------------------
with aba_clientes:
    c1, c2 = st.columns(2)
    with c1:
        reg = df.groupby("Região").agg(Mensagens=("negativo", "size"), neg=("negativo", "mean")).reset_index()
        fig = px.bar(reg.sort_values("Mensagens"), x="Mensagens", y="Região", orientation="h",
                     color="neg", color_continuous_scale=["#FFFFFF", LARANJA],
                     labels={"neg": "% negativo"})
        mostrar(estilizar(fig, "Mensagens por região (cor = % negativo)"))
    with c2:
        seg = df.groupby(["Segmento", "Sentimento"]).size().reset_index(name="Mensagens")
        fig = px.bar(seg, x="Segmento", y="Mensagens", color="Sentimento", barmode="relative",
                     color_discrete_map=CORES_SENTIMENTO)
        mostrar(estilizar(fig, "Sentimento por segmento"))
    c1, c2 = st.columns(2)
    with c1:
        idade = df.groupby("Faixa etária")["nota_satisfacao"].mean().reset_index()
        fig = px.bar(idade, x="Faixa etária", y="nota_satisfacao", color_discrete_sequence=[AZUL_ESCURO],
                     text=idade["nota_satisfacao"].map(lambda v: fmt(v, 2)))
        fig.update_yaxes(range=[1, 5], title="Nota média")
        mostrar(estilizar(fig, "Nota média por faixa etária"))
    with c2:
        por_cliente = df.groupby("id_cliente").size()
        fig = px.histogram(por_cliente, nbins=30, color_discrete_sequence=[AZUL])
        fig.update_xaxes(title="Mensagens por cliente")
        fig.update_yaxes(title="Clientes")
        fig.update_layout(showlegend=False)
        mostrar(estilizar(fig, "Quantas mensagens cada cliente envia"))

# ---------------------------------------------------------------------------
# Página 5: Modelo (preenchida após a Etapa 4)
# ---------------------------------------------------------------------------
with aba_modelo:
    st.info("O classificador de sentimentos e a previsão de volume entram aqui depois do treinamento "
            "(Etapa 4): métricas reais, matriz de confusão, previsão futura e um campo para classificar "
            "uma mensagem nova.")
