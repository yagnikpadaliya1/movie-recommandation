import streamlit as st
import pickle
import pandas as pd
import re

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CineMatch · AI Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "genre_filter" not in st.session_state:
    st.session_state.genre_filter = "All"

IS_DARK = st.session_state.dark_mode

# ─────────────────────────────────────────────────────────────────────────────
# THEME TOKENS
# ─────────────────────────────────────────────────────────────────────────────
if IS_DARK:
    BG          = "#08080f"
    BG_CARD     = "rgba(255,255,255,0.04)"
    BG_NAV      = "rgba(8,8,15,0.97)"
    BG_INPUT    = "rgba(255,255,255,0.06)"
    TEXT        = "#f0f0f5"
    TEXT_MUTED  = "#6b7280"
    TEXT_FAINT  = "#374151"
    BORDER      = "rgba(255,255,255,0.09)"
    BLOB1       = "rgba(147,51,234,0.18)"
    BLOB2       = "rgba(236,72,153,0.12)"
    GRID_COLOR  = "rgba(255,255,255,0.025)"
    SHADOW      = "rgba(0,0,0,0.6)"
    PLACEHOLDER = "https://placehold.co/500x750/0d0d1a/9333ea?text=No+Poster"
else:
    BG          = "#f5f5ff"
    BG_CARD     = "rgba(0,0,0,0.04)"
    BG_NAV      = "rgba(245,245,255,0.97)"
    BG_INPUT    = "rgba(0,0,0,0.05)"
    TEXT        = "#0a0a18"
    TEXT_MUTED  = "#6b7280"
    TEXT_FAINT  = "#d1d5db"
    BORDER      = "rgba(0,0,0,0.09)"
    BLOB1       = "rgba(147,51,234,0.08)"
    BLOB2       = "rgba(236,72,153,0.06)"
    GRID_COLOR  = "rgba(0,0,0,0.03)"
    SHADOW      = "rgba(0,0,0,0.15)"
    PLACEHOLDER = "https://placehold.co/500x750/ebebff/9333ea?text=No+Poster"

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS — injected once
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@500;600;700;800&display=swap');

/* ── Reset ── */
*, *::before, *::after {{ box-sizing: border-box; }}
html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}

/* ── App Shell ── */
.stApp {{
    background-color: {BG};
    color: {TEXT};
    min-height: 100vh;
}}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{
    padding: 0 0 4rem !important;
    max-width: 100% !important;
}}

/* ── Aurora blobs ── */
.aurora {{
    position: fixed; top: 0; left: 0;
    width: 100%; height: 100%;
    pointer-events: none; z-index: 0; overflow: hidden;
}}
.blob {{
    position: absolute; border-radius: 50%;
    filter: blur(120px); opacity: 1;
    animation: blobFloat ease-in-out infinite alternate;
}}
.blob-1 {{
    width: 650px; height: 650px;
    background: {BLOB1};
    top: -15%; left: -10%;
    animation-duration: 13s;
}}
.blob-2 {{
    width: 550px; height: 550px;
    background: {BLOB2};
    bottom: -10%; right: -8%;
    animation-duration: 17s; animation-delay: -5s;
}}
@keyframes blobFloat {{
    from {{ transform: translate(0,0) scale(1); }}
    to   {{ transform: translate(25px,-30px) scale(1.07); }}
}}

/* ── Grid texture ── */
.grid-texture {{
    position: fixed; top: 0; left: 0;
    width: 100%; height: 100%;
    pointer-events: none; z-index: 0;
    background-image:
        linear-gradient({GRID_COLOR} 1px, transparent 1px),
        linear-gradient(90deg, {GRID_COLOR} 1px, transparent 1px);
    background-size: 48px 48px;
}}

/* ── Content wrapper ── */
.content {{ position: relative; z-index: 1; }}

/* ── NAV BAR ── */
.app-nav {{
    background: {BG_NAV};
    border-bottom: 1px solid {BORDER};
    backdrop-filter: blur(20px);
    padding: 0 2.5rem;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky; top: 0; z-index: 100;
    margin-bottom: 0;
}}
.nav-logo {{
    display: flex; align-items: center; gap: 10px;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.2rem; font-weight: 700;
    color: {TEXT};
}}
.nav-logo .ai-pill {{
    background: linear-gradient(135deg, #9333ea, #ec4899);
    color: #fff;
    font-size: 0.6rem; font-weight: 700;
    letter-spacing: 0.1em;
    padding: 0.18rem 0.55rem;
    border-radius: 100px;
    vertical-align: middle;
}}
.nav-right {{ display: flex; align-items: center; gap: 1rem; }}

/* ── HERO ── */
.hero-section {{
    text-align: center;
    padding: 4rem 2rem 2.5rem;
    max-width: 800px; margin: 0 auto;
    animation: fadeUp 0.7s ease-out both;
}}
@keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(28px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
.hero-eyebrow {{
    display: inline-flex; align-items: center; gap: 8px;
    border-left: 3px solid #9333ea;
    padding: 0.3rem 1rem;
    color: #a855f7;
    font-size: 0.72rem; font-weight: 700;
    letter-spacing: 0.2em; text-transform: uppercase;
    margin-bottom: 1.5rem;
    background: rgba(147,51,234,0.08);
    border-radius: 0 6px 6px 0;
}}
.hero-h1 {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(2.8rem, 6vw, 5rem);
    font-weight: 800; line-height: 1.08;
    letter-spacing: -0.02em;
    margin-bottom: 0.3rem;
    color: {TEXT};
}}
.hero-h1-gradient {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(2.8rem, 6vw, 5rem);
    font-weight: 800; line-height: 1.08;
    letter-spacing: -0.02em;
    margin-bottom: 1.2rem;
    background: linear-gradient(135deg, #9333ea 0%, #ec4899 60%, #f97316 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    filter: drop-shadow(0 0 30px rgba(147,51,234,0.35));
}}
.hero-sub {{
    font-size: 1.05rem; color: {TEXT_MUTED};
    line-height: 1.75; max-width: 520px; margin: 0 auto 2.2rem;
}}

/* ── STAT PILLS ── */
.stat-row {{
    display: flex; justify-content: center; gap: 0.75rem;
    flex-wrap: wrap; margin-bottom: 2.5rem;
    animation: fadeUp 0.8s ease-out 0.15s both;
}}
.stat-pill {{
    background: {BG_INPUT};
    border: 1px solid {BORDER};
    backdrop-filter: blur(12px);
    border-radius: 100px;
    padding: 0.42rem 1.1rem;
    font-size: 0.82rem; font-weight: 500;
    color: {TEXT_MUTED};
}}
.stat-pill b {{ color: {TEXT}; }}

/* ── NAV & GENRE toggle button overrides ── */
div[data-testid="stHorizontalBlock"] {{ gap: 0.5rem !important; }}

/* ── Radio genre pills ── */
div[data-testid="stRadio"] > div {{
    display: flex !important; flex-wrap: wrap !important;
    gap: 0.5rem !important; justify-content: center !important;
}}
div[data-testid="stRadio"] label {{
    background: {BG_INPUT} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 100px !important;
    padding: 0.38rem 1.1rem !important;
    font-size: 0.82rem !important; font-weight: 500 !important;
    color: {TEXT_MUTED} !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    white-space: nowrap !important;
}}
div[data-testid="stRadio"] label:hover {{
    border-color: rgba(147,51,234,0.5) !important;
    color: #a855f7 !important;
    background: rgba(147,51,234,0.08) !important;
}}
div[data-testid="stRadio"] label[data-baseweb="radio"] span:first-child {{
    display: none !important;
}}
div[data-testid="stRadio"] [aria-checked="true"] label,
div[data-testid="stRadio"] label:has(input:checked) {{
    background: linear-gradient(135deg,#9333ea,#ec4899) !important;
    border-color: transparent !important;
    color: #fff !important;
    box-shadow: 0 4px 16px rgba(147,51,234,0.35) !important;
}}

/* ── Selectbox ── */
.stSelectbox > label {{
    display: none !important;
}}
.stSelectbox > div > div {{
    background: {BG_INPUT} !important;
    border: 1px solid rgba(147,51,234,0.35) !important;
    border-radius: 14px !important;
    color: {TEXT} !important;
    font-size: 1rem !important; font-weight: 500 !important;
    backdrop-filter: blur(16px) !important;
    transition: all 0.25s ease !important;
    padding: 0.15rem 0 !important;
}}
.stSelectbox > div > div:hover {{
    border-color: rgba(147,51,234,0.6) !important;
}}
.stSelectbox > div > div:focus-within {{
    border-color: #9333ea !important;
    box-shadow: 0 0 0 3px rgba(147,51,234,0.18), 0 0 30px rgba(147,51,234,0.12) !important;
}}

/* ── Recommend button ── */
.stButton > button {{
    width: 100% !important;
    background: linear-gradient(135deg, #9333ea 0%, #7c3aed 40%, #ec4899 100%) !important;
    color: #fff !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important; font-size: 1rem !important;
    letter-spacing: 0.03em !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.85rem 2rem !important;
    cursor: pointer !important;
    transition: all 0.3s cubic-bezier(0.34,1.56,0.64,1) !important;
    box-shadow: 0 4px 24px rgba(147,51,234,0.4) !important;
    margin-top: 0.6rem !important;
    position: relative !important; overflow: hidden !important;
}}
.stButton > button:hover {{
    transform: translateY(-3px) !important;
    box-shadow: 0 10px 40px rgba(147,51,234,0.55) !important;
}}
.stButton > button:active {{
    transform: translateY(-1px) !important;
}}

/* ── Theme toggle button override ── */
button[kind="secondary"] {{
    background: {BG_INPUT} !important;
    border: 1px solid {BORDER} !important;
    color: {TEXT_MUTED} !important;
    border-radius: 100px !important;
    font-size: 0.82rem !important;
    padding: 0.35rem 1rem !important;
}}

/* ── Section divider ── */
.section-divider {{
    display: flex; align-items: center; gap: 1rem;
    margin: 3rem 2rem 2rem;
    animation: fadeUp 0.6s ease-out 0.1s both;
}}
.divider-line {{
    flex: 1; height: 1px;
    background: linear-gradient(90deg, transparent, {BORDER});
}}
.divider-line.right {{
    background: linear-gradient(90deg, {BORDER}, transparent);
}}
.divider-text {{
    font-size: 0.72rem; font-weight: 700;
    letter-spacing: 0.18em; text-transform: uppercase;
    color: {TEXT_MUTED}; white-space: nowrap;
}}
.divider-text b {{ color: {TEXT}; font-weight: 700; }}

/* ── MOVIE CARD ── */
.movie-card {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 16px;
    overflow: hidden;
    cursor: pointer;
    transition: transform 0.35s cubic-bezier(0.34,1.56,0.64,1),
                box-shadow 0.35s ease,
                border-color 0.3s ease;
    position: relative;
    height: 100%;
}}
.movie-card:hover {{
    transform: translateY(-10px) scale(1.02);
    box-shadow: 0 24px 64px {SHADOW},
                0 0 0 1px rgba(147,51,234,0.5),
                0 0 50px rgba(147,51,234,0.18);
    border-color: rgba(147,51,234,0.5);
}}

/* Poster wrapper - fixed aspect ratio */
.card-poster-wrap {{
    position: relative;
    width: 100%;
    aspect-ratio: 2 / 3;
    overflow: hidden;
    background: {BG_CARD};
}}
.card-poster {{
    width: 100%; height: 100%;
    object-fit: cover; display: block;
    transition: transform 0.5s ease;
}}
.movie-card:hover .card-poster {{
    transform: scale(1.06);
}}

/* gradient fade at bottom of poster */
.card-poster-overlay {{
    position: absolute; inset: 0;
    background: linear-gradient(
        to bottom,
        rgba(0,0,0,0) 45%,
        rgba(8,8,15,0.85) 80%,
        rgba(8,8,15,1) 100%
    );
    pointer-events: none;
}}

/* rank badge */
.rank-badge {{
    position: absolute; top: 10px; left: 10px;
    font-size: 0.65rem; font-weight: 800;
    letter-spacing: 0.06em; text-transform: uppercase;
    padding: 0.25rem 0.65rem;
    border-radius: 100px; backdrop-filter: blur(10px);
    border: 1px solid; z-index: 2;
}}
.rk-1 {{ background:rgba(168,85,247,0.25); border-color:rgba(168,85,247,0.6); color:#c084fc;
          box-shadow:0 0 14px rgba(168,85,247,0.4); }}
.rk-2 {{ background:rgba(156,163,175,0.2); border-color:rgba(156,163,175,0.45); color:#d1d5db; }}
.rk-3 {{ background:rgba(245,158,11,0.2); border-color:rgba(245,158,11,0.45); color:#fbbf24; }}
.rk-4 {{ background:rgba(6,182,212,0.2);  border-color:rgba(6,182,212,0.45);  color:#22d3ee; }}
.rk-5 {{ background:rgba(236,72,153,0.2); border-color:rgba(236,72,153,0.45); color:#f472b6; }}

/* card body text */
.card-body {{
    padding: 0.9rem 0.95rem 1.1rem;
}}
.card-title {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.88rem; font-weight: 700;
    color: {TEXT}; line-height: 1.4;
    margin: 0 0 0.45rem;
    display: -webkit-box;
    -webkit-line-clamp: 2; -webkit-box-orient: vertical;
    overflow: hidden;
}}
.card-meta {{
    display: flex; align-items: center;
    gap: 5px; flex-wrap: wrap;
    font-size: 0.72rem; color: {TEXT_MUTED}; font-weight: 500;
}}
.meta-rating {{ color: #fbbf24; font-weight: 700; }}
.meta-dot {{ color: {TEXT_FAINT}; }}
.meta-genre {{
    background: rgba(6,182,212,0.12);
    color: #22d3ee; border: 1px solid rgba(6,182,212,0.3);
    border-radius: 100px; padding: 0.12rem 0.5rem;
    font-size: 0.65rem; font-weight: 600;
}}

/* ── Card stagger animation ── */
.card-anim {{ animation: cardIn 0.5s ease-out both; }}
.d0 {{ animation-delay: 0.05s; }}
.d1 {{ animation-delay: 0.15s; }}
.d2 {{ animation-delay: 0.25s; }}
.d3 {{ animation-delay: 0.35s; }}
.d4 {{ animation-delay: 0.45s; }}
@keyframes cardIn {{
    from {{ opacity: 0; transform: translateY(40px) scale(0.96); }}
    to   {{ opacity: 1; transform: translateY(0) scale(1); }}
}}

/* ── No results ── */
.no-results {{
    text-align: center; padding: 3rem 1rem;
    color: {TEXT_MUTED}; font-size: 0.95rem;
}}

/* ── Footer ── */
.app-footer {{
    text-align: center; padding: 3.5rem 1rem 2rem;
    font-size: 0.78rem; color: {TEXT_FAINT};
    border-top: 1px solid {BORDER}; margin-top: 3rem;
    position: relative; z-index: 1;
}}
.app-footer a {{ color: {TEXT_MUTED}; text-decoration: none; transition: color 0.2s; }}
.app-footer a:hover {{ color: #a855f7; }}

/* ── Spinner ── */
.stSpinner > div {{ border-top-color: #9333ea !important; }}

/* ── Search row spacing ── */
.search-area {{ padding: 0 2rem; animation: fadeUp 0.8s ease-out 0.2s both; }}
</style>

<!-- aurora + grid (always present) -->
<div class="aurora">
    <div class="blob blob-1"></div>
    <div class="blob blob-2"></div>
</div>
<div class="grid-texture"></div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data():
    movies_df   = pd.DataFrame(pickle.load(open('movies.pkl', 'rb')))
    similarities = pickle.load(open('similarity.pkl', 'rb'))
    csv_df = pd.read_csv('movies.csv')

    def upgrade_url(url):
        if isinstance(url, str) and 'media-amazon.com' in url:
            return re.sub(r'_V1_[^@.]+', '_V1_SX500', url)
        return url

    csv_df['Poster_Link'] = csv_df['Poster_Link'].apply(upgrade_url)
    return movies_df, similarities, csv_df


@st.cache_data(show_spinner=False)
def get_info(title, _csv_df):
    row = _csv_df[_csv_df['Series_Title'] == title]
    if row.empty:
        return {"poster": PLACEHOLDER, "rating": "N/A", "genre": "", "year": ""}
    r = row.iloc[0]
    year_raw = str(r.get('Released_Year', ''))
    year = year_raw[:4] if len(year_raw) >= 4 else year_raw
    genre_raw = str(r.get('Genre', '')) if pd.notna(r.get('Genre')) else ''
    genre = genre_raw.split(',')[0].strip()[:14]
    poster = r.get('Poster_Link', '')
    if not isinstance(poster, str) or poster.strip() == '':
        poster = PLACEHOLDER
    return {
        "poster": poster,
        "rating": str(r.get('IMDB_Rating', 'N/A')),
        "genre": genre,
        "year": year,
    }


def recommend(movie, movies_df, sims):
    m = movies_df[movies_df['Series_Title'] == movie]
    if m.empty:
        return []
    idx = m.index[0]
    top = sorted(enumerate(sims[idx]), reverse=True, key=lambda x: x[1])[1:11]
    return [movies_df.iloc[i]['Series_Title'] for i, _ in top]


try:
    movies, similarities, csv_df = load_data()
except FileNotFoundError as e:
    st.error(f"❌ Missing model file: {e}")
    st.stop()

GENRES = ['All', 'Action', 'Drama', 'Sci-Fi', 'Comedy', 'Thriller', 'Animation', 'Horror', 'Crime', 'Romance']
RANK_LABELS  = ['#1 Top Pick', '#2', '#3', '#4', '#5']
RANK_CLASSES = ['rk-1', 'rk-2', 'rk-3', 'rk-4', 'rk-5']


# ─────────────────────────────────────────────────────────────────────────────
# NAV BAR
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-nav" style="position:relative;z-index:10;">
    <div class="nav-logo">
        🎬&nbsp;CineMatch&nbsp;<span class="ai-pill">AI</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Theme toggle via actual Streamlit button
nav_l, nav_r = st.columns([6, 1])
with nav_r:
    toggle_label = "☀️ Light" if IS_DARK else "🌙 Dark"
    if st.button(toggle_label, key="theme_toggle"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="content">
<div class="hero-section">
    <div class="hero-eyebrow">✦ &nbsp;AI-Powered &nbsp;·&nbsp; 1000 Films</div>
    <div class="hero-h1">Discover Your</div>
    <div class="hero-h1-gradient">Perfect Film</div>
    <p class="hero-sub">
        Tell us one movie you love. Our AI engine finds your
        perfect next watch in seconds — no sign-up needed.
    </p>
    <div class="stat-row">
        <div class="stat-pill">🎬 <b>1,000</b> Curated Films</div>
        <div class="stat-pill">⚡ <b>Instant</b> AI Match</div>
        <div class="stat-pill">⭐ <b>IMDb</b> Ratings</div>
        <div class="stat-pill">🌍 <b>Global</b> Cinema</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# GENRE FILTER
# ─────────────────────────────────────────────────────────────────────────────
_, g_col, _ = st.columns([1, 4, 1])
with g_col:
    selected_genre = st.radio(
        "Genre Filter",
        options=GENRES,
        horizontal=True,
        label_visibility="collapsed",
        key="genre_radio",
    )

# ─────────────────────────────────────────────────────────────────────────────
# SEARCH + BUTTON
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="search-area">', unsafe_allow_html=True)
_, s_col, _ = st.columns([1, 2.4, 1])
with s_col:
    selected_movie = st.selectbox(
        "Movie",
        options=movies['Series_Title'].values,
        placeholder="🔍  Search for a movie…",
        label_visibility="collapsed",
    )
    recommend_btn = st.button("✨  Get Recommendations", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# RESULTS
# ─────────────────────────────────────────────────────────────────────────────
if recommend_btn:
    with st.spinner("Finding your perfect matches…"):
        all_recs = recommend(selected_movie, movies, similarities)

    # Apply genre filter (keep first 5 matching)
    if selected_genre == 'All':
        filtered = all_recs[:5]
    else:
        filtered = []
        for t in all_recs:
            info = get_info(t, csv_df)
            if selected_genre.lower() in info['genre'].lower():
                filtered.append(t)
            if len(filtered) == 5:
                break
        # If not enough genre matches, pad with unfiltered
        if len(filtered) < 5:
            extras = [t for t in all_recs if t not in filtered]
            filtered = (filtered + extras)[:5]

    if not filtered:
        st.markdown(f'<div class="no-results">No recommendations found for <b>{selected_movie}</b>.</div>', unsafe_allow_html=True)
    else:
        # Section divider
        safe_title = selected_movie.replace('<', '&lt;').replace('>', '&gt;')
        st.markdown(f"""
        <div class="section-divider">
            <div class="divider-line"></div>
            <div class="divider-text">BECAUSE YOU LIKED &nbsp;·&nbsp; <b>{safe_title}</b></div>
            <div class="divider-line right"></div>
        </div>
        """, unsafe_allow_html=True)

        # 5 columns — one card each
        card_cols = st.columns(5, gap="small")

        for i, (col, title) in enumerate(zip(card_cols, filtered)):
            info = get_info(title, csv_df)

            # Build safe pieces outside f-string
            safe_movie_title = title.replace('<', '&lt;').replace('>', '&gt;')
            poster_url       = info['poster']
            rating_txt       = info['rating']
            year_txt         = info['year']
            genre_txt        = info['genre']
            rank_label       = RANK_LABELS[i]
            rank_cls         = RANK_CLASSES[i]
            delay_cls        = f"d{i}"

            # Genre pill HTML — built before f-string
            if genre_txt:
                genre_part = f'<span class="meta-dot">·</span><span class="meta-genre">{genre_txt}</span>'
            else:
                genre_part = ''

            with col:
                st.markdown(f"""
<div class="movie-card card-anim {delay_cls}">
  <div class="card-poster-wrap">
    <img class="card-poster"
         src="{poster_url}"
         alt="{safe_movie_title}"
         loading="lazy"
         onerror="this.onerror=null;this.src=&quot;https://placehold.co/500x750/0d0d1a/9333ea?text=No+Poster&quot;" />
    <div class="card-poster-overlay"></div>
    <div class="rank-badge {rank_cls}">{rank_label}</div>
  </div>
  <div class="card-body">
    <p class="card-title">{safe_movie_title}</p>
    <div class="card-meta">
      <span class="meta-rating">★ {rating_txt}</span>
      <span class="meta-dot">·</span>
      <span>{year_txt}</span>
      {genre_part}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
</div>  <!-- /content -->
<div class="app-footer">
    Built with ♥ using
    <a href="https://streamlit.io" target="_blank">Streamlit</a>
    &nbsp;·&nbsp;
    Data from <a href="https://www.imdb.com" target="_blank">IMDb Top 1000</a>
    &nbsp;·&nbsp;
    Posters via Amazon CDN
    <br/>
    <span style="font-size:0.68rem;opacity:0.5;">© 2025 CineMatch · AI Movie Recommendation Engine</span>
</div>
""", unsafe_allow_html=True)
