import streamlit as st
import pandas as pd
import plotly.express as px

# ----------- PAGE CONFIG -----------
st.set_page_config(page_title="Netflix Dashboard", layout="wide")

# ----------- CUSTOM CSS -----------
st.markdown("""
<style>
.stApp {
    background-color: #FFFFFF;
}

/* HIDE SIDEBAR */
section[data-testid="stSidebar"] {
    display: none !important;
}

/* Buttons */
.stButton>button {
    background-color: #E50914;
    color: white;
    border-radius: 8px;
}

/* Metrics */
[data-testid="metric-container"] {
    background-color: #FFF0F0;
    border-left: 5px solid #E50914;
    padding: 10px;
    border-radius: 10px;
}

/* Headers */
h1, h2, h3 {
    color: #E50914 !important;
}

/* Filter labels */
label {
    color: #E50914 !important;
    font-weight: bold;
}

/* Filter boxes */
div[data-baseweb="select"] {
    background-color: #FFF0F0;
    border-radius: 8px;
}
[data-testid="metric-container"] {
    color: #000000 !important;
}

[data-testid="stMetricValue"] {
    color: #E50914 !important;   /* Netflix red numbers */
    font-size: 28px !important;
    font-weight: bold;
}

[data-testid="stMetricLabel"] {
    color: #141414 !important;
}
</style>
""", unsafe_allow_html=True)

# ----------- LOAD DATA -----------
df = pd.read_csv("netflix_titles.csv")

# ----------- TITLE -----------
st.markdown("<h1>🎬 Netflix Dashboard</h1>", unsafe_allow_html=True)

# ----------- CLEAN GENRE -----------
df['genre'] = df['genre'].apply(lambda x: [i.strip().lower() for i in x.split(',')])

# ----------- TOP FILTER BAR -----------
st.markdown("### 🎛️ Filters")

col1, col2, col3, col4 = st.columns(4)

all_genres = sorted(set(g for sublist in df['genre'] for g in sublist))

with col1:
    year = st.multiselect("Year", sorted(df['release_year'].unique()))

with col2:
    genre = st.multiselect("Genre", all_genres)

with col3:
    country = st.multiselect("Country", df['country'].dropna().unique())

with col4:
    ctype = st.multiselect("Type", df['type'].unique())

# ----------- APPLY FILTERS -----------
filtered_df = df.copy()

if year:
    filtered_df = filtered_df[filtered_df['release_year'].isin(year)]

if genre:
    filtered_df = filtered_df[
        filtered_df['genre'].apply(lambda x: any(g in x for g in genre))
    ]

if country:
    filtered_df = filtered_df[filtered_df['country'].isin(country)]

if ctype:
    filtered_df = filtered_df[filtered_df['type'].isin(ctype)]

df_exploded = filtered_df.explode('genre')

# ----------- KPI -----------
st.markdown("### 📊 Key Insights")

col1, col2, col3 = st.columns(3)

col1.metric("Total Titles", len(filtered_df))
col2.metric("Movies", len(filtered_df[filtered_df['type'] == 'movie']))
col3.metric("TV Shows", len(filtered_df[filtered_df['type'] == 'tv show']))

st.markdown("---")

# ----------- PIE + HIST -----------
colA, colB = st.columns(2)

with colA:
    fig1 = px.pie(filtered_df, names='type',
                  color_discrete_sequence=["#E50914", "#FF4D4D"])
    st.plotly_chart(fig1, use_container_width=True)

with colB:
    fig4 = px.histogram(filtered_df, x='rating',
                        color_discrete_sequence=["#E50914"])
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ----------- GENRE TREND -----------
st.subheader("🎭 Top Genres per Year")

genre_year = df_exploded.groupby(['release_year', 'genre']) \
                        .size().reset_index(name='count')

fig2 = px.bar(genre_year, x='release_year', y='count', color='genre',
              color_discrete_sequence=px.colors.sequential.Reds)

st.plotly_chart(fig2, use_container_width=True)

# ----------- COUNTRY -----------
st.subheader("🌍 Top Countries Producing Content")

country_count = filtered_df['country'].value_counts().reset_index()
country_count.columns = ['country', 'count']

fig3 = px.bar(country_count.head(10), x='country', y='count',
              color_discrete_sequence=["#E50914"])

st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ----------- GROWTH -----------
st.subheader("📈 Content Growth Over Years")

growth = filtered_df.groupby('release_year').size().reset_index(name='count')

fig_growth = px.line(growth, x='release_year', y='count',
                     markers=True,
                     color_discrete_sequence=["#E50914"])

st.plotly_chart(fig_growth, use_container_width=True)

# ----------- GLOBAL MAP -----------
st.markdown("<h2>🌍 Global Content Distribution</h2>", unsafe_allow_html=True)

country_map = filtered_df['country'].value_counts().reset_index()
country_map.columns = ['country', 'count']

fig_map = px.choropleth(
    country_map,
    locations='country',
    locationmode='country names',
    color='count',
    color_continuous_scale="Reds"
)

st.plotly_chart(fig_map, use_container_width=True)

# ----------- TOP 10 -----------
st.subheader("🎬 Top 10 Movies")

top_movies = filtered_df[filtered_df['type'] == 'movie'] \
    .sort_values(by='release_year', ascending=False) \
    [['title', 'release_year', 'country']].head(10)

st.dataframe(top_movies, use_container_width=True)

st.subheader("📺 Top 10 TV Shows")

top_shows = filtered_df[filtered_df['type'] == 'tv show'] \
    .sort_values(by='release_year', ascending=False) \
    [['title', 'release_year', 'country']].head(10)

st.dataframe(top_shows, use_container_width=True)