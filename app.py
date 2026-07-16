import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

st.set_page_config(
    page_title="DNA do Mercado — Explorador de PCA & K-Means",
    page_icon="📈",
    layout="wide",
)

SECTOR_MAP = {
    "AAPL": "Tecnologia", "MSFT": "Tecnologia", "GOOGL": "Tecnologia", "NVDA": "Tecnologia",
    "META": "Tecnologia", "ORCL": "Tecnologia", "CRM": "Tecnologia", "ADBE": "Tecnologia",
    "AMD": "Tecnologia", "INTC": "Tecnologia",
    "JPM": "Financeiro", "BAC": "Financeiro", "GS": "Financeiro", "MS": "Financeiro",
    "WFC": "Financeiro", "AXP": "Financeiro", "C": "Financeiro",
    "JNJ": "Saúde", "PFE": "Saúde", "UNH": "Saúde", "MRK": "Saúde",
    "ABBV": "Saúde", "LLY": "Saúde",
    "XOM": "Energia", "CVX": "Energia", "COP": "Energia", "SLB": "Energia",
    "KO": "Consumo", "PEP": "Consumo", "WMT": "Consumo", "PG": "Consumo",
    "MCD": "Consumo", "NKE": "Consumo",
    "BA": "Industrial", "CAT": "Industrial", "GE": "Industrial", "HON": "Industrial",
    "TSLA": "Automotivo", "F": "Automotivo",
    "VZ": "Telecom", "T": "Telecom",
}
TICKERS = sorted(SECTOR_MAP.keys())

SECTOR_COLORS = {
    "Tecnologia": "#6C8EBF", "Financeiro": "#82B366", "Saúde": "#D6B656",
    "Energia": "#B85450", "Consumo": "#9673A6", "Industrial": "#D79B00",
    "Automotivo": "#4A6B8A", "Telecom": "#767676",
}


@st.cache_data(ttl=3600, show_spinner="Baixando um ano de dados de mercado...")
def fetch_price_data(tickers):
    raw = yf.download(tickers, period="1y", auto_adjust=False, progress=False)["Adj Close"]
    return raw


def build_returns(prices: pd.DataFrame):
    clean_prices = prices.dropna(axis=1, how="any")
    dropped = sorted(set(prices.columns) - set(clean_prices.columns))
    returns = clean_prices.pct_change().dropna(how="any")
    return returns, dropped


st.title("📈 DNA do Mercado: Encontrando Padrões Ocultos nas Ações")
st.markdown(
    """
Todos os dias, o preço de cada ação sobe e desce um pouco. Escondida nesse ruído existe
uma estrutura oculta: algumas empresas tendem a se mover *juntas*, enquanto outras se
movem de forma *independente*. Este painel usa duas ferramentas clássicas de aprendizado
de máquina para revelar essa estrutura:

- **PCA (Análise de Componentes Principais)** — comprime centenas de variações diárias
  de preço em um punhado de "movimentos de mercado" mais importantes, filtrando o ruído.
- **K-Means (Agrupamento por K-Médias)** — agrupa ações que se comportam de forma
  matematicamente parecida, mesmo que sejam de setores completamente diferentes.
"""
)

with st.spinner("Buscando dados..."):
    raw_prices = fetch_price_data(TICKERS)
    returns, dropped_tickers = build_returns(raw_prices)

if dropped_tickers:
    st.warning(f"⚠️ Removidas por histórico incompleto: {', '.join(dropped_tickers)}")

company_returns = returns.T
scaler = StandardScaler()
scaled_returns = scaler.fit_transform(company_returns)

n_companies, n_days = scaled_returns.shape
max_components = max(2, min(10, n_companies - 1, n_days))

st.sidebar.header("⚙️ Controles")
n_components = st.sidebar.slider(
    "Número de Componentes Principais",
    min_value=2, max_value=max_components, value=min(5, max_components),
    help="Quantos 'sinais de mercado comprimidos' manter do PCA.",
)
k_clusters = st.sidebar.slider(
    "Número de Grupos do K-Means (k)",
    min_value=2, max_value=10, value=4,
    help="Em quantos grupos as ações serão divididas.",
)
available_tickers = sorted(company_returns.index)
selected_ticker = st.sidebar.selectbox(
    "🔍 Destacar uma ação",
    options=available_tickers,
    index=available_tickers.index("AAPL") if "AAPL" in available_tickers else 0,
    help="Digite para buscar. Essa ação será destacada nos gráficos abaixo.",
)

st.sidebar.markdown("---")
st.sidebar.caption(f"Universo: {n_companies} ações · {n_days} dias de negociação de retornos")

pca = PCA(n_components=max_components, random_state=42)
pca_scores_full = pca.fit_transform(scaled_returns)
explained_variance = pca.explained_variance_ratio_
cumulative_variance = np.cumsum(explained_variance)

cluster_features = pca_scores_full[:, :n_components]
kmeans = KMeans(n_clusters=k_clusters, random_state=42, n_init=10)
cluster_labels = kmeans.fit_predict(cluster_features)

component_cols = [f"PC{i+1}" for i in range(n_components)]
results_df = pd.DataFrame(
    pca_scores_full[:, :n_components], columns=component_cols, index=company_returns.index
)
results_df.insert(0, "Ticker", company_returns.index)
results_df.insert(1, "Setor", [SECTOR_MAP.get(t, "Outro") for t in company_returns.index])
results_df["Grupo"] = cluster_labels.astype(str)
results_df = results_df.reset_index(drop=True)

st.markdown("---")

# ---------------------------------------------------------------------------
# Seção A — Matemática do PCA & Gráfico de Variância
# ---------------------------------------------------------------------------
st.header("🔬 Seção A — Comprimindo o Ruído (PCA)")
st.markdown(
    """
Cada ação tem cerca de 250 dias de variações de preço — dimensões demais para olhar
diretamente. O PCA encontra novos "supersinais" (chamados de **componentes principais**)
que resumem os maiores padrões compartilhados entre todas as ações. O **gráfico de
variância** abaixo mostra o quanto do movimento geral do mercado cada componente explica
— os primeiros componentes normalmente capturam a maior parte da ação, e o restante é
principalmente ruído.
"""
)

scree_df = pd.DataFrame(
    {
        "Componente": [f"PC{i+1}" for i in range(len(explained_variance))],
        "Variância Explicada": explained_variance,
    }
)
scree_fig = px.bar(
    scree_df,
    x="Componente",
    y="Variância Explicada",
    template="plotly_white",
    text_auto=".1%",
)
scree_fig.update_traces(marker_color="#6C8EBF")
scree_fig.update_layout(
    yaxis_tickformat=".0%",
    height=380,
    margin=dict(t=20, b=20),
)

col_a1, col_a2 = st.columns([3, 1])
with col_a1:
    st.plotly_chart(scree_fig, use_container_width=True)
with col_a2:
    selected_cumulative = cumulative_variance[n_components - 1]
    st.metric(
        f"Variância Acumulada ({n_components} CPs)",
        f"{selected_cumulative:.1%}",
    )
    st.markdown(
        f"""
> Os primeiros **{n_components}** componentes capturam cerca de **{selected_cumulative:.0%}**
> de toda a "energia" do movimento de mercado entre as {n_companies} ações. Tudo além
> disso é, em sua maioria, ruído do dia a dia.
"""
    )

st.markdown("---")

# ---------------------------------------------------------------------------
# Seção B — Agrupamento K-Means & Projeção 2D
# ---------------------------------------------------------------------------
st.header("🧭 Seção B — Agrupando Ações Parecidas (K-Means)")
st.markdown(
    """
Agora que o PCA reduziu cada ação aos seus sinais mais essenciais, o **K-Means** analisa
**todos os {n} componentes selecionados** e organiza as ações em grupos (**clusters**) de
empresas que se movem de forma matematicamente parecida — independentemente do setor em
que realmente atuam. Como só dá pra desenhar 2 eixos por vez, escolha abaixo quais
componentes visualizar; os clusters foram calculados usando todos os {n}, então o gráfico
2D é sempre uma "sombra" parcial da separação real.
""".format(n=n_components)
)

with st.expander("📐 Ajuda para escolher k (silhouette score)"):
    st.markdown(
        """
O **silhouette score** mede o quão bem separados e coesos estão os clusters (vai de -1 a
1; quanto maior, melhor). Ele é calculado aqui usando os mesmos {n} componentes que
alimentam o K-Means acima — use-o como uma bússola para saber se o k escolhido na barra
lateral é uma escolha razoável ou se um vizinho seria melhor.
""".format(n=n_components)
    )
    k_range = list(range(2, 11))
    silhouette_scores = []
    for k in k_range:
        labels_k = KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(cluster_features)
        silhouette_scores.append(silhouette_score(cluster_features, labels_k))

    silhouette_df = pd.DataFrame({"k": k_range, "Silhouette": silhouette_scores})
    silhouette_fig = px.line(
        silhouette_df, x="k", y="Silhouette", markers=True, template="plotly_white"
    )
    silhouette_fig.add_vline(x=k_clusters, line_dash="dash", line_color="#E63946")
    silhouette_fig.update_layout(height=280, margin=dict(t=20, b=20))
    st.plotly_chart(silhouette_fig, use_container_width=True)
    best_k = k_range[int(np.argmax(silhouette_scores))]
    st.caption(
        f"A linha vermelha tracejada marca o k atual ({k_clusters}). O melhor score no "
        f"intervalo testado é em **k={best_k}**."
    )

axis_col1, axis_col2 = st.columns(2)
with axis_col1:
    x_axis = st.selectbox("Eixo X", options=component_cols, index=0)
with axis_col2:
    y_options = [c for c in component_cols if c != x_axis] or component_cols
    y_axis = st.selectbox("Eixo Y", options=y_options, index=0)

x_idx = int(x_axis[2:]) - 1
y_idx = int(y_axis[2:]) - 1
shown_variance = explained_variance[x_idx] + explained_variance[y_idx]
used_variance = cumulative_variance[n_components - 1]

scatter_fig = px.scatter(
    results_df,
    x=x_axis,
    y=y_axis,
    color="Grupo",
    hover_name="Ticker",
    hover_data={"Setor": True, "Grupo": True, x_axis: ":.2f", y_axis: ":.2f"},
    template="plotly_white",
    color_discrete_sequence=px.colors.qualitative.Set2,
)
scatter_fig.update_traces(marker=dict(size=14, opacity=0.85, line=dict(width=0)))

highlight_row = results_df[results_df["Ticker"] == selected_ticker]
if not highlight_row.empty:
    scatter_fig.add_trace(
        go.Scatter(
            x=highlight_row[x_axis],
            y=highlight_row[y_axis],
            mode="markers+text",
            text=highlight_row["Ticker"],
            textposition="top center",
            marker=dict(
                size=26,
                color="rgba(0,0,0,0)",
                line=dict(width=3, color="#E63946"),
                symbol="circle",
            ),
            name=f"Selecionada: {selected_ticker}",
            hoverinfo="skip",
            showlegend=False,
        )
    )

scatter_fig.update_layout(
    height=520,
    legend_title_text="Grupo",
    xaxis_title=f"{x_axis} ({explained_variance[x_idx]:.1%} da variância)",
    yaxis_title=f"{y_axis} ({explained_variance[y_idx]:.1%} da variância)",
    margin=dict(t=20, b=20),
)
st.plotly_chart(scatter_fig, use_container_width=True)
st.caption(
    f"🔴 O ponto com contorno vermelho é **{selected_ticker}** — a ação que você selecionou na barra lateral."
)
st.info(
    f"Os eixos exibidos ({x_axis} + {y_axis}) mostram **{shown_variance:.1%}** da variância "
    f"de mercado. O K-Means, porém, usou **{n_components} componentes**, capturando "
    f"**{used_variance:.1%}** ao todo — parte da separação dos grupos pode estar acontecendo "
    f"em eixos que este gráfico não exibe."
)

st.markdown("---")

# ---------------------------------------------------------------------------
# Seção C — Análise de Grupos & "Ações Gêmeas"
# ---------------------------------------------------------------------------
st.header("👯 Seção C — Composição dos Grupos & Ações Gêmeas")
st.markdown(
    """
Abaixo está o detalhamento completo de quais ações ficaram em cada grupo, seguido de uma
busca pelas empresas que se comportam de forma mais parecida com a ação escolhida na
barra lateral — suas **"ações gêmeas"**.
"""
)

col_c1, col_c2 = st.columns([1.3, 1])

with col_c1:
    st.subheader("Composição dos Grupos")
    for cluster_id in sorted(results_df["Grupo"].unique(), key=int):
        members = results_df[results_df["Grupo"] == cluster_id].sort_values("Ticker")
        with st.expander(f"Grupo {cluster_id} — {len(members)} ações", expanded=True):
            st.dataframe(
                members[["Ticker", "Setor"]].reset_index(drop=True),
                use_container_width=True,
                hide_index=True,
            )

with col_c2:
    st.subheader(f"🧬 Ações parecidas com {selected_ticker}")
    if highlight_row.empty:
        st.info("Selecione uma ação na barra lateral.")
    else:
        selected_cluster = highlight_row["Grupo"].iloc[0]
        twins = results_df[
            (results_df["Grupo"] == selected_cluster)
            & (results_df["Ticker"] != selected_ticker)
        ].sort_values("Ticker")

        st.markdown(f"**{selected_ticker}** está no **Grupo {selected_cluster}**.")
        if twins.empty:
            st.write(f"Nenhuma outra ação compartilha o grupo de {selected_ticker} — ela se move de forma única!")
        else:
            st.markdown(f"**Ações matematicamente parecidas com {selected_ticker}:**")
            for _, row in twins.iterrows():
                st.markdown(f"- **{row['Ticker']}** ({row['Setor']})")

st.markdown("---")
st.caption(
    "Feito com Streamlit, yfinance, scikit-learn & Plotly · Demonstração educacional — "
    "não é recomendação de investimento. 📊"
)
