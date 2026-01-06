import requests
import streamlit as st

API_BASE = "https://movie-rec-466x.onrender.com" or "http://127.0.0.1:8000"
TMDB_IMG = "https://image.tmdb.org/t/p/w500"

st.set_page_config(page_title="MatchMojo", page_icon="📽️", layout="wide")

st.markdown(
    """
<style>
.block-container { padding-top: 1rem; padding-bottom: 2rem; max-width: 1400px; }
.small-muted { color:#6b7280; font-size: 0.92rem; }
.card-container {
    background-color: #1e1e1e;
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 1rem;
}
.card-poster img {
    width: 100%;
    height: 225px;
    object-fit: cover;
    border-radius: 6px;
}
.card-title {
    text-align: center;
    color: white;
    font-size: 0.9rem;
    line-height: 1.15rem;
    margin-top: 0.4rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
</style>
""",
    unsafe_allow_html=True,
)

if "view" not in st.session_state:
    st.session_state.view = "home"
if "selected_tmdb_id" not in st.session_state:
    st.session_state.selected_tmdb_id = None

qp_view = st.query_params.get("view")
qp_id = st.query_params.get("id")
if qp_view in ("home", "details"):
    st.session_state.view = qp_view
if qp_id:
    try:
        st.session_state.selected_tmdb_id = int(qp_id)
        st.session_state.view = "details"
    except (TypeError, ValueError):
        pass


def goto_home():
    st.session_state.view = "home"
    st.query_params["view"] = "home"
    if "id" in st.query_params:
        del st.query_params["id"]
    st.rerun()


def goto_details(tmdb_id: int):
    st.session_state.view = "details"
    st.session_state.selected_tmdb_id = int(tmdb_id)
    st.query_params["view"] = "details"
    st.query_params["id"] = str(int(tmdb_id))
    st.rerun()


@st.cache_data(ttl=30)
def api_get_json(path: str, params: dict | None = None):
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=25)
        if r.status_code >= 400:
            return None, f"HTTP {r.status_code}: {r.text[:300]}"
        return r.json(), None
    except Exception as e:
        return None, f"Request failed: {e}"


def poster_grid(cards, cols=6, key_prefix="grid"):
    if not cards:
        st.info("No movies to show.")
        return

    idx = 0
    while idx < len(cards):
        colset = st.columns(cols)
        for c in range(cols):
            if idx >= len(cards):
                break
            m = cards[idx]
            idx += 1

            tmdb_id = m.get("tmdb_id")
            title = m.get("title", "Untitled")
            poster = m.get("poster_url")

            with colset[c]:
                if poster and isinstance(poster, str) and poster.strip():
                    st.markdown(
                        f'<img src="{poster}" style="width:100%; height:225px; object-fit:cover; border-radius:6px; margin-bottom:16px; margin-top:20px;" />',
                        unsafe_allow_html=True,
                    )
                else:
                    fallback_url = "https://www.themoviedb.org/assets/2/apple-touch-icon-cfba7699efe7a742de25c28e08c38525f19381d31087c69e89d6bcb8e3c0ddfa.png"
                    st.markdown(
                        f'<img src="{fallback_url}" style="width:100%; height:225px; object-fit:cover; border-radius:6px; opacity:0.3; margin-bottom:8px;" />',
                        unsafe_allow_html=True,
                    )

                if st.button("Open", key=f"{key_prefix}_{idx}_{tmdb_id}", use_container_width=True):
                    goto_details(tmdb_id)

                st.markdown(
                    f'<div style="text-align:center; color:white; font-size:0.9rem; line-height:1.15rem; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="{title}">{title}</div>',
                    unsafe_allow_html=True,
                )

def to_cards_from_tfidf_items(tfidf_items):
    cards = []
    for x in tfidf_items or []:
        tmdb = x.get("tmdb") or {}
        if tmdb.get("tmdb_id"):
            cards.append({
                "tmdb_id": tmdb["tmdb_id"],
                "title": tmdb.get("title") or x.get("title") or "Untitled",
                "poster_url": tmdb.get("poster_url"),
            })
    return cards


def parse_tmdb_search_to_cards(data, keyword: str, limit: int = 24):
    keyword_l = keyword.strip().lower()

    raw_items = []
    if isinstance(data, dict) and "results" in data:
        for m in data.get("results", []):
            title = (m.get("title") or "").strip()
            tmdb_id = m.get("id")
            poster_path = m.get("poster_path")
            if not title or not tmdb_id:
                continue
            poster_url = f"{TMDB_IMG}{poster_path}" if poster_path else None
            raw_items.append({
                "tmdb_id": int(tmdb_id),
                "title": title,
                "poster_url": poster_url,
                "release_date": m.get("release_date", ""),
            })
    elif isinstance(data, list):
        for m in data:
            tmdb_id = m.get("tmdb_id") or m.get("id")
            title = (m.get("title") or "").strip()
            poster_url = m.get("poster_url")
            if not title or not tmdb_id:
                continue
            raw_items.append({
                "tmdb_id": int(tmdb_id),
                "title": title,
                "poster_url": poster_url,
                "release_date": m.get("release_date", ""),
            })
    else:
        return [], []

    matched = [x for x in raw_items if keyword_l in x["title"].lower()]
    final_list = matched if matched else raw_items

    suggestions = []
    for x in final_list[:10]:
        year = (x.get("release_date") or "")[:4]
        label = f"{x['title']} ({year})" if year else x["title"]
        suggestions.append((label, x["tmdb_id"]))

    cards = [
        {"tmdb_id": x["tmdb_id"], "title": x["title"], "poster_url": x["poster_url"]}
        for x in final_list[:limit]
    ]
    return suggestions, cards


with st.sidebar:
    st.markdown("## MatchMojo")
    if st.button("Home"):
        goto_home()

    st.markdown("---")
    st.markdown("### Home Feed")
    home_category = st.selectbox(
        "Category",
        ["trending", "popular", "top_rated", "now_playing", "upcoming"],
        index=0,
    )

st.title("MatchMojo")
st.markdown(
    "<div class='small-muted'>Enter a movie title to search, view details, and receive personalized recommendations.</div>",
    unsafe_allow_html=True,
)
st.divider()

if st.session_state.view == "home":
    typed = st.text_input(
        "Search by movie title", placeholder="e.g., Inception, The Dark Knight..."
    )
    st.divider()

    if typed.strip():
        if len(typed.strip()) < 2:
            st.caption("Please enter at least 2 characters.")
        else:
            data, err = api_get_json("/tmdb/search", params={"query": typed.strip()})
            if err or data is None:
                st.error(f"Search failed: {err}")
            else:
                suggestions, cards = parse_tmdb_search_to_cards(data, typed.strip(), limit=24)

                if suggestions:
                    labels = ["Select a movie"] + [s[0] for s in suggestions]
                    selected = st.selectbox("Results", labels, index=0)
                    if selected != "Select a movie":
                        label_to_id = {s[0]: s[1] for s in suggestions}
                        goto_details(label_to_id[selected])
                else:
                    st.info("No matching suggestions found.")

                st.markdown("### Search Results")
                poster_grid(cards, cols=6, key_prefix="search_results")
        st.stop()

    st.markdown(f"### {home_category.replace('_', ' ').title()} Movies")
    home_cards, err = api_get_json("/home", params={"category": home_category, "limit": 24})
    if err or not home_cards:
        st.error(f"Failed to load home feed: {err or 'Unknown error'}")
        st.stop()
    poster_grid(home_cards, cols=6, key_prefix="home_feed")

elif st.session_state.view == "details":
    tmdb_id = st.session_state.selected_tmdb_id
    if not tmdb_id:
        st.warning("No movie selected.")
        if st.button("Back to Home"):
            goto_home()
        st.stop()

    top_col1, top_col2 = st.columns([3, 1])
    with top_col1:
        st.markdown("### Movie Details")
    with top_col2:
        if st.button("Back to Home"):
            goto_home()

    data, err = api_get_json(f"/movie/id/{tmdb_id}")
    if err or not data:
        st.error(f"Could not load movie details: {err or 'Unknown error'}")
        st.stop()

    left, right = st.columns([1, 2.4], gap="large")

    with left:
        poster_url = data.get("poster_url")
        if poster_url and isinstance(poster_url, str):
            st.image(poster_url, use_column_width=True)
        else:
            st.markdown(
                """
                <div style='height:300px; background:#1e1e1e; display:flex; align-items:center; 
                justify-content:center; color:#888; border-radius:6px;'>No Poster Available</div>
                """,
                unsafe_allow_html=True,
            )

    with right:
        st.markdown(f"## {data.get('title', '')}")
        release = data.get("release_date") or "Unknown"
        genres = ", ".join([g["name"] for g in data.get("genres", [])]) or "Unknown"
        st.markdown(f"<div class='small-muted'>Release Date: {release}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='small-muted'>Genres: {genres}</div>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("### Overview")
        st.write(data.get("overview") or "No overview available.")

    backdrop_url = data.get("backdrop_url")
    if backdrop_url and isinstance(backdrop_url, str):
        st.divider()
        st.markdown("### Backdrop Image")
        st.image(backdrop_url, use_column_width=True)

    st.divider()
    st.markdown("### Recommendations")

    title = (data.get("title") or "").strip()
    if title:
        bundle, err2 = api_get_json(
            "/movie/search",
            params={"query": title, "tfidf_top_n": 12, "genre_limit": 12},
        )

        if not err2 and bundle:
            st.markdown("#### Similar Movies (Content-Based)")
            tfidf_items = bundle.get("tfidf_recommendations")
            if tfidf_items:
                poster_grid(to_cards_from_tfidf_items(tfidf_items), cols=6, key_prefix="details_tfidf")
            else:
                st.info("No content-based recommendations.")

            st.markdown("#### More Like This (Genre-Based)")
            genre_items = bundle.get("genre_recommendations", [])
            if genre_items:
                poster_grid(genre_items, cols=6, key_prefix="details_genre")
            else:
                st.info("No genre-based recommendations.")
        else:
            st.info("Loading genre-based recommendations...")
            genre_only, err3 = api_get_json("/recommend/genre", params={"tmdb_id": tmdb_id, "limit": 18})
            if not err3 and genre_only:
                poster_grid(genre_only, cols=6, key_prefix="details_genre_fallback")
            else:
                st.warning("No recommendations are currently available.")
    else:
        st.warning("Unable to generate recommendations without a valid title.")