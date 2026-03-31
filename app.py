import streamlit as st
import pandas as pd
import plotly.express as px

# ----------- PAGE CONFIG -----------
st.set_page_config(page_title="Netflix Dashboard", layout="wide")

# ----------- CUSTOM CSS (FULL RED THEME) -----------
st.markdown("""
    <style>
    .stApp {
        background-color: #FFFFFF;
    }

    /* Sidebar RED */
    section[data-testid="stSidebar"] {
        background-color: #E50914;
        color: white;
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
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

    /* Subheaders */
    h2 {
        color: #E50914 !important;
    }

    h3 {
        color: #E50914 !important;
    }

    /* General text fix */
    p, span, label {
        color: #141414 !important;
    }

    </style>
""", unsafe_allow_html=True)

# ----------- LOAD DATA -----------
df = pd.read_csv("netflix_titles.csv")

# ----------- TITLE -----------
st.markdown("<h1 style='color:#E50914;'>🎬 Netflix Dashboard</h1>", unsafe_allow_html=True)
st.markdown("Analyze Netflix content trends, genres, and global distribution")

# ----------- CLEAN GENRE -----------
df['genre'] = df['genre'].apply(lambda x: [i.strip().lower() for i in x.split(',')])

# ----------- FILTERS -----------
st.sidebar.title("🎛️ Filters")

all_genres = sorted(set(g for sublist in df['genre'] for g in sublist))

year = st.sidebar.multiselect("Select Year", sorted(df['release_year'].unique()))
genre = st.sidebar.multiselect("Select Genre", all_genres)
country = st.sidebar.multiselect("Select Country", df['country'].dropna().unique())
ctype = st.sidebar.multiselect("Content Type", df['type'].unique())

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
                  title="Content Type Distribution",
                  color_discrete_sequence=["#E50914", "#FF4D4D"])
    st.plotly_chart(fig1, use_container_width=True)

with colB:
    fig4 = px.histogram(filtered_df, x='rating',
                        title="Rating Distribution",
                        color_discrete_sequence=["#E50914"])
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ----------- GENRE TREND -----------
st.subheader("🎭 Top Genres per Year")

genre_year = df_exploded.groupby(['release_year', 'genre']) \
                        .size().reset_index(name='count')

top_genres = df_exploded['genre'].value_counts().head(10).index
genre_year = genre_year[genre_year['genre'].isin(top_genres)]

fig2 = px.bar(genre_year, x='release_year', y='count', color='genre',
              title="Top Genres per Year",
              color_discrete_sequence=px.colors.sequential.Reds)

st.plotly_chart(fig2, use_container_width=True)

# ----------- COUNTRY -----------
st.subheader("🌍 Top Countries Producing Content")

country_count = filtered_df['country'].value_counts().reset_index()
country_count.columns = ['country', 'count']

fig3 = px.bar(country_count.head(10), x='country', y='count',
              title="Top Countries",
              color_discrete_sequence=["#E50914"])

st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ----------- GROWTH -----------
st.subheader("📈 Content Growth Over Years")

growth = filtered_df.groupby('release_year').size().reset_index(name='count')

fig_growth = px.line(growth, x='release_year', y='count',
                     markers=True,
                     title="Netflix Content Growth",
                     color_discrete_sequence=["#E50914"])

st.plotly_chart(fig_growth, use_container_width=True)

# ----------- DURATION -----------
def classify_duration(x):
    if 'min' in str(x):
        val = int(x.split()[0])
        return "Short" if val < 60 else "Medium" if val < 120 else "Long"
    elif 'Season' in str(x):
        val = int(x.split()[0])
        return "Mini Series" if val <= 2 else "Long Series"
    return "Unknown"

filtered_df['duration_category'] = filtered_df['duration'].apply(classify_duration)

fig_len = px.pie(filtered_df, names='duration_category',
                 title="Content Length",
                 color_discrete_sequence=px.colors.sequential.Reds)

st.plotly_chart(fig_len, use_container_width=True)

# ----------- ORIGINAL VS LICENSED -----------
st.subheader("🎬 Original vs Licensed")

df_exploded['date_added'] = pd.to_datetime(df_exploded['date_added'], errors='coerce')
df_exploded['year_added'] = df_exploded['date_added'].dt.year

df_exploded['is_original'] = (
    (abs(df_exploded['year_added'] - df_exploded['release_year']) <= 1) |
    (df_exploded['release_year'] >= 2016)
)

original_dist = df_exploded['is_original'].value_counts().reset_index()
original_dist.columns = ['is_original', 'count']

fig_orig = px.pie(original_dist, names='is_original', values='count',
                  color_discrete_sequence=["#E50914", "#FF9999"])

st.plotly_chart(fig_orig, use_container_width=True)

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

# ----------- GLOBAL DISTRIBUTION MAP -----------
st.markdown("<h2 style='color:#E50914;'>🌍 Global Content Distribution</h2>", unsafe_allow_html=True)

# Count content per country
country_map = filtered_df['country'].value_counts().reset_index()
country_map.columns = ['country', 'count']

# Create world map
fig_map = px.choropleth(
    country_map,
    locations='country',
    locationmode='country names',
    color='count',
    title="Content Distribution Across the World",
    color_continuous_scale="Reds"
)

st.plotly_chart(fig_map, use_container_width=True)