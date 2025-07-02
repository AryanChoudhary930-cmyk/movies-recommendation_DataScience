import streamlit as st
import pickle
import pandas as pd
import requests
import os
import re

# ✅ OMDb API key
OMDB_API_KEY = "24e9c668"

# ✅ Hugging Face URL for similarity matrix
SIMILARITY_URL = "https://huggingface.co/datasets/aryanchoudhary01/movies-recommendation-data/resolve/main/similarity.pkl"
SIMILARITY_FILE = "similarity.pkl"

# ✅ Download similarity.pkl if missing
def download_similarity():
    with requests.get(SIMILARITY_URL, stream=True) as r:
        r.raise_for_status()
        with open(SIMILARITY_FILE, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

if not os.path.exists(SIMILARITY_FILE):
    with st.spinner("Downloading similarity matrix..."):
        download_similarity()

# ✅ Clean movie title for API search
def clean_title(title):
    return re.sub(r'[^a-zA-Z0-9 ]', '', title).strip()

# ✅ Fetch movie poster from OMDb API
def fetch_poster(movie_title):
    cleaned_title = clean_title(movie_title)
    url = f"http://www.omdbapi.com/?t={cleaned_title}&apikey={OMDB_API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        if data.get("Poster") and data["Poster"] != "N/A":
            return data["Poster"]
    except:
        pass
    return "https://via.placeholder.com/200x300?text=No+Image"

# ✅ Recommend similar movies
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movie_list:
        title = movies.iloc[i[0]].title
        poster = fetch_poster(title)
        recommended_movies.append(title)
        recommended_posters.append(poster)

    return recommended_movies, recommended_posters

# ✅ Load movies_dict.pkl
try:
    with open("movies_dict.pkl", "rb") as f:
        movies_dict = pickle.load(f)
    movies = pd.DataFrame(movies_dict)
except FileNotFoundError:
    st.error("❌ Error: 'movies_dict.pkl' not found. Please upload it.")
    st.stop()

# ✅ Load similarity.pkl
with open(SIMILARITY_FILE, "rb") as f:
    similarity = pickle.load(f)

# ✅ Streamlit UI
st.set_page_config(page_title="Movie Recommender", layout="wide")
st.title("🎬 Movie Recommender System")

selected_movie_name = st.selectbox(
    "Select a movie to get recommendations:",
    movies['title'].values
)

if st.button("Recommend"):
    with st.spinner("Fetching recommendations..."):
        names, posters = recommend(selected_movie_name)

    st.markdown("### 🎥 Top 5 Recommended Movies")
    st.write("")  # spacing

    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.image(posters[i], use_container_width=True)
            st.caption(names[i])
