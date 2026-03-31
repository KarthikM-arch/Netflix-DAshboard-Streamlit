import streamlit as st
import pandas as pd
import plotly.express as px

st.markdown("""
    <style>
    /* App background */
    .stApp {
        background-color: #FFFFFF;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #141414;
        color: white;
    }

    /* Sidebar text */
    .css-1d391kg, .css-1v0mbdj {
        color: white;
    }

    /* Buttons */
    .stButton>button {
        background-color: #E50914;
        color: white;
        border-radius: 8px;
    }

    /* Metrics */
    [data-testid="metric-container"] {
        background-color: #F8F8F8;
        padding: 10px;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ----------- PAGE CONFIG -----------
st.set_page_config(page_title="Netflix Dashboard", layout="wide")

# Load dataset
df = pd.read_csv("netflix_titles.csv")

st.title("🎬 Netflix Content Strategy Dashboard")
st.markdown("Analyze Netflix content trends, genres, and global distribution")

# ----------- CLEAN GENRE COLUMN -----------
df['genre'] = df['genre'].apply(lambda x: [i.strip().lower() for i in x.split(',')])

# ----------- FILTER OPTIONS -----------
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

# ----------- EXPLODE AFTER FILTERING -----------
df_exploded = filtered_df.explode('genre')

# ----------- KPI CARDS -----------
st.markdown("### 📊 Key Insights")

col1, col2, col3 = st.columns(3)

total_titles = len(filtered_df)
total_movies = len(filtered_df[filtered_df['type'] == 'movie'])
total_shows = len(filtered_df[filtered_df['type'] == 'tv show'])
total_countries = filtered_df['country'].nunique()

col1.metric("Total Titles", total_titles)
col2.metric("Movies", total_movies)
col3.metric("TV Shows", total_shows)

st.markdown(f"🌍 **Countries Covered:** {total_countries}")

st.markdown("---")

# ----------- CONTENT TYPE + RATING -----------
colA, colB = st.columns(2)

with colA:
    fig1 = px.pie(filtered_df, names='type', title="Content Type Distribution")
    st.plotly_chart(fig1, use_container_width=True)

with colB:
    fig4 = px.histogram(filtered_df, x='rating', title="Rating Distribution")
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ----------- TOP GENRES PER YEAR -----------
st.subheader("🎭 Top Genres per Year")

genre_year = df_exploded.groupby(['release_year', 'genre']) \
                        .size().reset_index(name='count')

top_genres = df_exploded['genre'].value_counts().head(10).index
genre_year = genre_year[genre_year['genre'].isin(top_genres)]

fig2 = px.bar(genre_year, x='release_year', y='count', color='genre',
              title="Top Genres per Year")

st.plotly_chart(fig2, use_container_width=True)

# ----------- COUNTRY DISTRIBUTION -----------
st.subheader("🌍 Top Countries Producing Content")

country_count = filtered_df['country'].value_counts().reset_index()
country_count.columns = ['country', 'count']

fig3 = px.bar(country_count.head(10), x='country', y='count',
              title="Top Countries")

st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ----------- GROWTH TREND -----------
st.subheader("📈 Content Growth Over Years")

growth = filtered_df.groupby('release_year').size().reset_index(name='count')

fig_growth = px.line(growth, x='release_year', y='count',
                     markers=True, title="Netflix Content Growth")

st.plotly_chart(fig_growth, use_container_width=True)


# ----------- CONTENT LENGTH CATEGORY -----------

def classify_duration(x):
    if 'min' in str(x):
        val = int(x.split()[0])
        if val < 60:
            return "Short Movie"
        elif val < 120:
            return "Medium Movie"
        else:
            return "Long Movie"
    elif 'Season' in str(x):
        val = int(x.split()[0])
        if val <= 2:
            return "Mini Series"
        else:
            return "Long Series"
    return "Unknown"

filtered_df['duration_category'] = filtered_df['duration'].apply(classify_duration)

fig_len = px.pie(filtered_df, names='duration_category',
                 title="Content Length Distribution")

st.plotly_chart(fig_len, use_container_width=True)

# ----------- TOP COUNTRY PER YEAR -----------

country_year = filtered_df.groupby(['release_year', 'country']) \
                          .size().reset_index(name='count')

top_country = country_year.sort_values(['release_year','count'], ascending=[True, False]) \
                          .groupby('release_year').first().reset_index()

fig_country_year = px.bar(top_country, x='release_year', y='count',
                          color='country',
                          title="Top Content Producing Country per Year")

st.plotly_chart(fig_country_year, use_container_width=True)


# ----------- ORIGINAL VS LICENSED -----------
st.subheader("🎬 Original vs Licensed Content")

df_exploded['date_added'] = pd.to_datetime(df_exploded['date_added'], errors='coerce')
df_exploded['year_added'] = df_exploded['date_added'].dt.year

df_exploded['is_original'] = (
    (abs(df_exploded['year_added'] - df_exploded['release_year']) <= 1) |
    (df_exploded['release_year'] >= 2016)
)

original_dist = df_exploded['is_original'].value_counts().reset_index()
original_dist.columns = ['is_original', 'count']

original_dist['is_original'] = original_dist['is_original'].map({
    True: 'Original',
    False: 'Licensed'
})

fig_orig = px.pie(original_dist, names='is_original', values='count',
                  title="Original vs Licensed")

st.plotly_chart(fig_orig, use_container_width=True)


st.subheader("🎬 Top 10 Movies")

top_movies = filtered_df[filtered_df['type'] == 'movie'] \
                .sort_values(by='release_year', ascending=False) \
                [['title', 'release_year', 'country']] \
                .head(10)

st.dataframe(top_movies, use_container_width=True)

st.subheader("📺 Top 10 TV Shows")

top_shows = filtered_df[filtered_df['type'] == 'tv show'] \
                .sort_values(by='release_year', ascending=False) \
                [['title', 'release_year', 'country']] \
                .head(10)

st.dataframe(top_shows, use_container_width=True)