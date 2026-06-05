import streamlit as st
import pickle
import pandas as pd
import requests

# ─────────────────────────────────────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CineMatch · AI Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# Inject ALL CSS + Animations
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&display=swap');

/* ─── BASE ─── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #050508;
    color: #f0f0f5;
    overflow-x: hidden;
}

/* ─── Hide Streamlit chrome ─── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 0 2rem 5rem !important;
    max-width: 1400px !important;
}

/* ─── Animated aurora background ─── */
.aurora-bg {
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    z-index: -1;
    overflow: hidden;
    pointer-events: none;
}
.aurora-blob {
    position: absolute;
    border-radius: 50%;
    filter: blur(100px);
    opacity: 0.18;
    animation: auroraFloat 12s ease-in-out infinite alternate;
}
.aurora-blob:nth-child(1) {
    width: 700px; height: 700px;
    background: radial-gradient(circle, #7c3aed, #4f46e5);
    top: -20%; left: -15%;
    animation-duration: 14s;
}
.aurora-blob:nth-child(2) {
    width: 600px; height: 600px;
    background: radial-gradient(circle, #db2777, #9333ea);
    top: 10%; right: -10%;
    animation-duration: 10s;
    animation-delay: -4s;
}
.aurora-blob:nth-child(3) {
    width: 500px; height: 500px;
    background: radial-gradient(circle, #0ea5e9, #6366f1);
    bottom: -10%; left: 30%;
    animation-duration: 16s;
    animation-delay: -8s;
}
@keyframes auroraFloat {
    0%   { transform: translate(0, 0) scale(1); }
    50%  { transform: translate(30px, -40px) scale(1.1); }
    100% { transform: translate(-20px, 30px) scale(0.95); }
}

/* ─── Floating particles ─── */
.particles {
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    z-index: -1;
    pointer-events: none;
}
.particle {
    position: absolute;
    border-radius: 50%;
    background: rgba(255,255,255,0.6);
    animation: particleDrift linear infinite;
}
@keyframes particleDrift {
    0%   { opacity: 0; transform: translateY(100vh) rotate(0deg); }
    10%  { opacity: 1; }
    90%  { opacity: 1; }
    100% { opacity: 0; transform: translateY(-10vh) rotate(720deg); }
}

/* ─── HERO SECTION ─── */
.hero {
    text-align: center;
    padding: 4rem 1rem 3rem;
    animation: heroFadeIn 0.8s ease-out;
}
@keyframes heroFadeIn {
    from { opacity: 0; transform: translateY(-30px); }
    to   { opacity: 1; transform: translateY(0); }
}

.hero-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(124, 58, 237, 0.15);
    border: 1px solid rgba(139, 92, 246, 0.4);
    color: #a78bfa;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    padding: 0.4rem 1.1rem;
    border-radius: 100px;
    margin-bottom: 1.8rem;
    backdrop-filter: blur(10px);
}

.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(3rem, 7vw, 5.5rem);
    font-weight: 700;
    line-height: 1.05;
    letter-spacing: -0.02em;
    margin-bottom: 1.2rem;
}
.hero-title .line1 { color: #f0f0f5; }
.hero-title .line2 {
    background: linear-gradient(135deg, #a78bfa 0%, #ec4899 50%, #f97316 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    position: relative;
}
.hero-title .line2::after {
    content: '';
    position: absolute;
    bottom: -6px; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(135deg, #a78bfa, #ec4899, #f97316);
    border-radius: 2px;
    opacity: 0.5;
}

.hero-sub {
    color: #6b7280;
    font-size: 1.05rem;
    font-weight: 400;
    max-width: 520px;
    margin: 1.5rem auto 0;
    line-height: 1.75;
}

/* ─── STAT PILLS ─── */
.stat-bar {
    display: flex;
    justify-content: center;
    gap: 1rem;
    flex-wrap: wrap;
    margin: 2.5rem 0 3rem;
    animation: heroFadeIn 1s ease-out 0.2s both;
}
.stat-pill {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    backdrop-filter: blur(12px);
    border-radius: 100px;
    padding: 0.45rem 1.2rem;
    font-size: 0.82rem;
    color: #9ca3af;
    font-weight: 500;
}
.stat-pill span { color: #e5e7eb; font-weight: 700; }

/* ─── SEARCH CARD ─── */
.search-wrapper {
    animation: heroFadeIn 1s ease-out 0.3s both;
}

.stSelectbox > label {
    color: #9ca3af !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    margin-bottom: 0.4rem !important;
}
.stSelectbox > div > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 14px !important;
    color: #f0f0f5 !important;
    font-size: 0.98rem !important;
    font-weight: 500 !important;
    backdrop-filter: blur(20px) !important;
    transition: all 0.25s ease !important;
    padding: 0.2rem 0 !important;
}
.stSelectbox > div > div:focus-within {
    border-color: rgba(167, 139, 250, 0.7) !important;
    box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.15), 0 0 30px rgba(124, 58, 237, 0.1) !important;
}

/* ─── BUTTON ─── */
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #7c3aed 0%, #a855f7 50%, #ec4899 100%) !important;
    color: #fff !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: 0.04em !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.9rem 2rem !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 30px rgba(124, 58, 237, 0.35) !important;
    position: relative !important;
    overflow: hidden !important;
    margin-top: 0.6rem !important;
}
.stButton > button::before {
    content: '';
    position: absolute;
    top: 0; left: -100%; width: 100%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
    transition: left 0.5s ease;
}
.stButton > button:hover::before { left: 100%; }
.stButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 12px 40px rgba(124, 58, 237, 0.5) !important;
}
.stButton > button:active {
    transform: translateY(-1px) !important;
}

/* ─── SECTION LABEL ─── */
.section-label {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    color: #4b5563;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    margin: 3.5rem 0 2rem;
}
.section-label::before,
.section-label::after {
    content: '';
    flex: 1;
    max-width: 120px;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1));
}
.section-label::after {
    background: linear-gradient(90deg, rgba(255,255,255,0.1), transparent);
}

/* ─── MOVIE CARDS ─── */
.movie-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 1.2rem;
    animation: cardsReveal 0.6s ease-out;
}
@keyframes cardsReveal {
    from { opacity: 0; transform: translateY(40px); }
    to   { opacity: 1; transform: translateY(0); }
}

.movie-card {
    position: relative;
    border-radius: 18px;
    overflow: hidden;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(10px);
    transition: transform 0.4s cubic-bezier(0.34,1.56,0.64,1), box-shadow 0.4s ease, border-color 0.3s ease;
    cursor: pointer;
    group: true;
}
.movie-card:hover {
    transform: translateY(-12px) scale(1.03);
    box-shadow: 0 30px 70px rgba(0,0,0,0.6), 0 0 0 1px rgba(167,139,250,0.4), 0 0 60px rgba(124,58,237,0.15);
    border-color: rgba(167,139,250,0.5);
}

.movie-card-nth-1 { animation: cardSlideIn 0.5s ease-out 0.1s both; }
.movie-card-nth-2 { animation: cardSlideIn 0.5s ease-out 0.2s both; }
.movie-card-nth-3 { animation: cardSlideIn 0.5s ease-out 0.3s both; }
.movie-card-nth-4 { animation: cardSlideIn 0.5s ease-out 0.4s both; }
.movie-card-nth-5 { animation: cardSlideIn 0.5s ease-out 0.5s both; }
@keyframes cardSlideIn {
    from { opacity: 0; transform: translateY(50px) scale(0.95); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
}

.card-poster-wrap {
    position: relative;
    aspect-ratio: 2/3;
    overflow: hidden;
}
.card-poster {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    transition: transform 0.5s ease;
}
.movie-card:hover .card-poster {
    transform: scale(1.08);
}

/* Gradient overlay on poster */
.card-poster-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(
        to bottom,
        rgba(0,0,0,0) 40%,
        rgba(5,5,8,0.95) 100%
    );
    transition: opacity 0.3s ease;
}

/* Rank badge */
.card-rank {
    position: absolute;
    top: 10px; left: 10px;
    font-size: 0.65rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    padding: 0.28rem 0.7rem;
    border-radius: 100px;
    backdrop-filter: blur(12px);
    border: 1px solid;
    text-transform: uppercase;
}
.rank-1 { background: rgba(234,179,8,0.2); border-color: rgba(234,179,8,0.5); color: #fbbf24; }
.rank-2 { background: rgba(156,163,175,0.2); border-color: rgba(156,163,175,0.4); color: #d1d5db; }
.rank-3 { background: rgba(180,83,9,0.2); border-color: rgba(180,83,9,0.4); color: #f97316; }
.rank-4 { background: rgba(99,102,241,0.2); border-color: rgba(99,102,241,0.4); color: #818cf8; }
.rank-5 { background: rgba(236,72,153,0.2); border-color: rgba(236,72,153,0.4); color: #f472b6; }

/* Play button hover */
.card-play {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%) scale(0.7);
    width: 52px; height: 52px;
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(12px);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem;
    opacity: 0;
    transition: all 0.3s ease;
    border: 2px solid rgba(255,255,255,0.3);
}
.movie-card:hover .card-play {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1);
}

.card-body {
    padding: 1rem;
}
.card-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.88rem;
    font-weight: 600;
    color: #f0f0f5;
    line-height: 1.4;
    margin-bottom: 0.4rem;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
.card-meta {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.72rem;
    color: #6b7280;
    font-weight: 500;
}
.card-meta .dot { color: #374151; }
.card-rating {
    display: inline-flex;
    align-items: center;
    gap: 3px;
    color: #fbbf24;
    font-weight: 700;
    font-size: 0.76rem;
}

/* ─── SHIMMER PLACEHOLDER ─── */
.shimmer-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 18px;
    overflow: hidden;
}
.shimmer-poster {
    aspect-ratio: 2/3;
    background: linear-gradient(90deg, #111116 25%, #1a1a22 50%, #111116 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
}
@keyframes shimmer {
    0%   { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

/* ─── FOOTER ─── */
.footer {
    text-align: center;
    padding: 4rem 1rem 2rem;
    color: #374151;
    font-size: 0.78rem;
    line-height: 2.2;
}
.footer a { color: #4b5563; text-decoration: none; transition: color 0.2s; }
.footer a:hover { color: #a78bfa; }

/* ─── Spinner override ─── */
.stSpinner > div { border-top-color: #7c3aed !important; }
</style>

<!-- Aurora background -->
<div class="aurora-bg">
    <div class="aurora-blob"></div>
    <div class="aurora-blob"></div>
    <div class="aurora-blob"></div>
</div>

<!-- Floating particles -->
<div class="particles">
    <div class="particle" style="width:3px;height:3px;left:15%;animation-duration:18s;animation-delay:0s;"></div>
    <div class="particle" style="width:2px;height:2px;left:32%;animation-duration:22s;animation-delay:-4s;"></div>
    <div class="particle" style="width:4px;height:4px;left:55%;animation-duration:16s;animation-delay:-8s;"></div>
    <div class="particle" style="width:2px;height:2px;left:72%;animation-duration:20s;animation-delay:-2s;"></div>
    <div class="particle" style="width:3px;height:3px;left:88%;animation-duration:24s;animation-delay:-12s;"></div>
    <div class="particle" style="width:2px;height:2px;left:45%;animation-duration:19s;animation-delay:-6s;"></div>
    <div class="particle" style="width:1px;height:1px;left:65%;animation-duration:25s;animation-delay:-15s;"></div>
    <div class="particle" style="width:3px;height:3px;left:8%;animation-duration:21s;animation-delay:-10s;"></div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Data Loading — cached + load CSV for posters & metadata
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data():
    # Load the similarity model
    movies_df = pd.DataFrame(pickle.load(open('movies.pkl', 'rb')))
    similarities = pickle.load(open('similarity.pkl', 'rb'))

    # Load full CSV for poster links, ratings, genre, year
    csv_df = pd.read_csv('movies.csv')
    csv_df = csv_df[['Series_Title', 'Poster_Link', 'IMDB_Rating', 'Genre', 'Released_Year']].copy()

    # Upgrade Amazon thumbnail URL → full size (replace small size params)
    def upgrade_poster(url):
        if isinstance(url, str) and 'amazon' in url:
            # Replace the thumbnail size with a larger image
            import re
            url = re.sub(r'_V1_.*?\.jpg', '_V1_SX500.jpg', url)
        return url

    csv_df['Poster_Link'] = csv_df['Poster_Link'].apply(upgrade_poster)
    return movies_df, similarities, csv_df


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
PLACEHOLDER = "https://placehold.co/500x750/111116/a78bfa?text=🎬"

def get_movie_info(title: str, csv_df: pd.DataFrame) -> dict:
    """Get poster, rating, genre and year from the CSV by title."""
    row = csv_df[csv_df['Series_Title'] == title]
    if row.empty:
        return {"poster": PLACEHOLDER, "rating": "N/A", "genre": "", "year": ""}
    r = row.iloc[0]
    return {
        "poster": r['Poster_Link'] if pd.notna(r['Poster_Link']) else PLACEHOLDER,
        "rating": str(r['IMDB_Rating']) if pd.notna(r['IMDB_Rating']) else "N/A",
        "genre": str(r['Genre']).split(',')[0].strip() if pd.notna(r['Genre']) else "",
        "year": str(int(r['Released_Year'])) if pd.notna(r['Released_Year']) and str(r['Released_Year']).isdigit() else str(r['Released_Year']),
    }


def recommend(movie: str, movies_df: pd.DataFrame, similarities) -> list[str]:
    """Return top-5 recommended movie titles."""
    matches = movies_df[movies_df['Series_Title'] == movie]
    if matches.empty:
        return []
    idx = matches.index[0]
    scores = sorted(enumerate(similarities[idx]), reverse=True, key=lambda x: x[1])[1:6]
    return [movies_df.iloc[i]['Series_Title'] for i, _ in scores]


# ─────────────────────────────────────────────────────────────────────────────
# Load Data
# ─────────────────────────────────────────────────────────────────────────────
try:
    movies, similarities, csv_df = load_data()
except FileNotFoundError as e:
    st.error(f"❌ Missing files: {e}")
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# HERO SECTION
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-tag">✦ AI-Powered · 1000 Films</div>
    <div class="hero-title">
        <div class="line1">Find Your Next</div>
        <div class="line2">Obsession</div>
    </div>
    <p class="hero-sub">
        Tell us one movie you love. Our AI engine analyses
        thousands of patterns to surface your perfect next watch.
    </p>
</div>

<div class="stat-bar">
    <div class="stat-pill">🎬 <span>1,000</span> curated films</div>
    <div class="stat-pill">⚡ <span>Instant</span> recommendations</div>
    <div class="stat-pill">🧠 <span>AI</span> similarity engine</div>
    <div class="stat-pill">🌍 <span>Global</span> cinema</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SEARCH CONTROLS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="search-wrapper">', unsafe_allow_html=True)
_, col_center, _ = st.columns([1, 2.2, 1])
with col_center:
    selected_movie = st.selectbox(
        "Search for a movie",
        options=movies['Series_Title'].values,
        label_visibility="collapsed",
        placeholder="🔍  Search for a movie…",
    )
    recommend_btn = st.button("✨  Discover Similar Movies", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# RESULTS
# ─────────────────────────────────────────────────────────────────────────────
rank_labels  = ["🥇 Top Pick", "🥈 #2", "🥉 #3", "✦ #4", "✦ #5"]
rank_classes = ["rank-1", "rank-2", "rank-3", "rank-4", "rank-5"]

if recommend_btn:
    with st.spinner(""):
        rec_titles = recommend(selected_movie, movies, similarities)

    if not rec_titles:
        st.error("Movie not found. Please try another title.")
    else:
        # Fetch info for all 5 recommended movies
        rec_info = [get_movie_info(t, csv_df) for t in rec_titles]

        # Also show the selected movie info at top
        sel_info = get_movie_info(selected_movie, csv_df)

        # "Because you liked" bar
        st.markdown(f"""
        <div class="section-label">Because you liked &nbsp;<strong style="color:#e5e7eb">{selected_movie}</strong></div>
        """, unsafe_allow_html=True)

        # Build the 5 cards as a single HTML block for smooth animations
        cards_html = '<div class="movie-grid">'
        for i, (title, info) in enumerate(zip(rec_titles, rec_info)):
            short_genre = info['genre'][:14] + ('…' if len(info['genre']) > 14 else '')
            cards_html += f"""
            <div class="movie-card movie-card-nth-{i+1}">
                <div class="card-poster-wrap">
                    <img class="card-poster"
                         src="{info['poster']}"
                         alt="{title}"
                         loading="lazy"
                         onerror="this.src='{PLACEHOLDER}'" />
                    <div class="card-poster-overlay"></div>
                    <div class="card-rank {rank_classes[i]}">{rank_labels[i]}</div>
                    <div class="card-play">▶</div>
                </div>
                <div class="card-body">
                    <div class="card-title">{title}</div>
                    <div class="card-meta">
                        <span class="card-rating">★ {info['rating']}</span>
                        <span class="dot">·</span>
                        <span>{info['year']}</span>
                        {'<span class="dot">·</span><span>' + short_genre + '</span>' if short_genre else ''}
                    </div>
                </div>
            </div>
            """
        cards_html += '</div>'
        st.markdown(cards_html, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    Crafted with ♥ using <a href="https://streamlit.io" target="_blank">Streamlit</a>
    &nbsp;·&nbsp;
    Data from <a href="https://www.imdb.com" target="_blank">IMDb Top 1000</a>
    &nbsp;·&nbsp;
    Posters via <a href="https://www.amazon.com" target="_blank">Amazon</a>
    <br/>
    <span style="color:#1f2937;font-size:0.68rem;">
        © 2025 CineMatch · AI Movie Recommendation Engine
    </span>
</div>
""", unsafe_allow_html=True)
