import streamlit as st
import pickle
import pandas as pd
import requests

# ─────────────────────────────────────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CineMatch — Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# Custom CSS — Dark Cinematic Theme
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=Playfair+Display:wght@700&display=swap');

/* ── Reset & Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: radial-gradient(ellipse at top, #0d1117 0%, #080b10 60%, #020408 100%);
    color: #e8eaed;
    min-height: 100vh;
}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 4rem; max-width: 1400px; }

/* ── Hero Section ── */
.hero-wrapper {
    text-align: center;
    padding: 3.5rem 1rem 2.5rem;
    position: relative;
}

.hero-badge {
    display: inline-block;
    background: rgba(245, 197, 24, 0.12);
    border: 1px solid rgba(245, 197, 24, 0.35);
    color: #F5C518;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    padding: 0.35rem 1.1rem;
    border-radius: 100px;
    margin-bottom: 1.4rem;
}

.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(2.6rem, 6vw, 4.5rem);
    font-weight: 700;
    background: linear-gradient(135deg, #ffffff 0%, #F5C518 55%, #ff8c42 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.15;
    margin-bottom: 1rem;
}

.hero-sub {
    color: #8b949e;
    font-size: 1.05rem;
    font-weight: 300;
    max-width: 540px;
    margin: 0 auto 2.5rem;
    line-height: 1.7;
}

/* ── Divider ── */
.gold-divider {
    width: 80px;
    height: 3px;
    background: linear-gradient(90deg, transparent, #F5C518, transparent);
    margin: 0 auto 2.5rem;
    border-radius: 2px;
}

/* ── Select Box ── */
.stSelectbox > label {
    color: #F5C518 !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
}

.stSelectbox > div > div {
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(245, 197, 24, 0.3) !important;
    border-radius: 12px !important;
    color: #e8eaed !important;
    font-size: 1rem !important;
    padding: 0.1rem 0 !important;
    transition: border-color 0.25s ease !important;
}

.stSelectbox > div > div:hover,
.stSelectbox > div > div:focus-within {
    border-color: #F5C518 !important;
    box-shadow: 0 0 0 3px rgba(245, 197, 24, 0.12) !important;
}

/* ── Recommend Button ── */
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #F5C518 0%, #e6b000 100%) !important;
    color: #0d1117 !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: 0.05em !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.85rem 2rem !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 24px rgba(245, 197, 24, 0.25) !important;
    margin-top: 0.5rem;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 36px rgba(245, 197, 24, 0.45) !important;
    background: linear-gradient(135deg, #ffe44d 0%, #F5C518 100%) !important;
}

.stButton > button:active {
    transform: translateY(0px) !important;
}

/* ── Section Label ── */
.results-label {
    color: #8b949e;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    text-align: center;
    margin: 3rem 0 1.5rem;
}

/* ── Movie Cards ── */
.movie-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    overflow: hidden;
    transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
    cursor: pointer;
    position: relative;
}

.movie-card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(245, 197, 24, 0.4);
    border-color: rgba(245, 197, 24, 0.4);
}

.movie-card img {
    width: 100%;
    border-radius: 12px 12px 0 0;
    display: block;
    aspect-ratio: 2/3;
    object-fit: cover;
}

.movie-card-body {
    padding: 0.85rem 0.9rem 1rem;
}

.movie-title {
    font-weight: 600;
    font-size: 0.88rem;
    color: #e8eaed;
    line-height: 1.4;
    margin: 0;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.movie-rank {
    display: inline-block;
    background: rgba(245, 197, 24, 0.15);
    color: #F5C518;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    padding: 0.22rem 0.6rem;
    border-radius: 100px;
    margin-bottom: 0.5rem;
    border: 1px solid rgba(245, 197, 24, 0.25);
}

/* ── Footer ── */
.footer {
    text-align: center;
    padding: 3rem 1rem 1rem;
    color: #444d56;
    font-size: 0.78rem;
    line-height: 2;
}
.footer a { color: #6e7681; text-decoration: none; }
.footer a:hover { color: #F5C518; }

/* ── Error / Warning box ── */
.stAlert { border-radius: 12px !important; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: #F5C518 !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Data Loading — Cached for performance (Bug Fix #4)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    movies_df = pd.DataFrame(pickle.load(open('movies.pkl', 'rb')))
    similarities = pickle.load(open('similarity.pkl', 'rb'))
    return movies_df, similarities


# ─────────────────────────────────────────────────────────────────────────────
# Poster Fetcher — With error handling (Bug Fix #1 & #2)
# ─────────────────────────────────────────────────────────────────────────────
TMDB_API_KEY = "8265bd1679663a7ea12ac168da84d2e8"
PLACEHOLDER_POSTER = "https://placehold.co/500x750/1a1f2e/F5C518?text=No+Poster"

@st.cache_data(show_spinner=False)
def fetch_poster(movie_title: str) -> str:
    """Fetch movie poster from TMDB API with graceful fallback."""
    try:
        url = (
            f"https://api.themoviedb.org/3/search/movie"
            f"?api_key={TMDB_API_KEY}&query={requests.utils.quote(str(movie_title))}"
        )
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get('results'):
            poster_path = data['results'][0].get('poster_path')
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"
    except Exception:
        pass  # Silently fall through to placeholder

    return PLACEHOLDER_POSTER


# ─────────────────────────────────────────────────────────────────────────────
# Recommendation Engine — With index guard (Bug Fix #3)
# ─────────────────────────────────────────────────────────────────────────────
def recommend(movie: str, movies_df: pd.DataFrame, similarities) -> tuple[list, list]:
    """Return top-5 recommended movie titles and poster URLs."""
    matches = movies_df[movies_df['Series_Title'] == movie]
    if matches.empty:                          # Bug Fix #3: guard against empty match
        st.error("Movie not found in database. Please try another title.")
        return [], []

    movie_index = matches.index[0]
    distance = similarities[movie_index]
    top5 = sorted(enumerate(distance), reverse=True, key=lambda x: x[1])[1:6]

    titles, posters = [], []
    for idx, _ in top5:
        title = movies_df.iloc[idx]['Series_Title']
        titles.append(title)
        posters.append(fetch_poster(title))

    return titles, posters


# ─────────────────────────────────────────────────────────────────────────────
# Load Data
# ─────────────────────────────────────────────────────────────────────────────
try:
    movies, similarities = load_data()
except FileNotFoundError as e:
    st.error(f"❌ Could not load model files: {e}. Make sure `movies.pkl` and `similarity.pkl` are present.")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# Hero Header
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrapper">
    <div class="hero-badge">🎬 AI-Powered</div>
    <h1 class="hero-title">Discover Your Next<br>Favourite Film</h1>
    <p class="hero-sub">
        Select a movie you love and our recommendation engine will find
        5 films crafted just for your taste.
    </p>
    <div class="gold-divider"></div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Search & Recommend Controls
# ─────────────────────────────────────────────────────────────────────────────
col_left, col_center, col_right = st.columns([1, 2, 1])
with col_center:
    selected_movie = st.selectbox(
        "Choose a Movie",
        options=movies['Series_Title'].values,
        placeholder="Search for a movie…",
        label_visibility="visible",
    )
    recommend_btn = st.button("✨  Find Recommendations", use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# Results
# ─────────────────────────────────────────────────────────────────────────────
if recommend_btn:
    with st.spinner("🎬 Finding perfect matches for you…"):
        rec_titles, rec_posters = recommend(selected_movie, movies, similarities)

    if rec_titles:
        st.markdown('<div class="results-label">✦ Recommended For You ✦</div>', unsafe_allow_html=True)

        cols = st.columns(5, gap="medium")
        for i, (col, title, poster) in enumerate(zip(cols, rec_titles, rec_posters)):
            with col:
                rank_labels = ["Top Pick", "#2", "#3", "#4", "#5"]
                st.markdown(f"""
                <div class="movie-card">
                    <img src="{poster}" alt="{title}" loading="lazy"
                         onerror="this.src='{PLACEHOLDER_POSTER}'"/>
                    <div class="movie-card-body">
                        <div class="movie-rank">{rank_labels[i]}</div>
                        <p class="movie-title">{title}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    Built with ❤️ using <a href="https://streamlit.io" target="_blank">Streamlit</a>
    &nbsp;·&nbsp;
    Movie data & posters via <a href="https://www.themoviedb.org" target="_blank">TMDB</a>
    &nbsp;·&nbsp;
    IMDb Top 1000 Dataset
</div>
""", unsafe_allow_html=True)
