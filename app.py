import streamlit as st
import pickle
import pandas as pd
import requests
import re

# ✅ Updated OMDb API key
OMDB_API_KEY = "24e9c668"

# ✅ Clean movie titles to improve matching on OMDb
def clean_title(title):
    title = re.sub(r'[^a-zA-Z0-9 ]', '', title)  # remove special characters
    return title.strip()

# ✅ Fetch poster from OMDb using cleaned movie title
def fetch_poster(movie_title):
    cleaned_title = clean_title(movie_title)
    url = f"http://www.omdbapi.com/?t={cleaned_title}&apikey={OMDB_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if 'Poster' in data and data['Poster'] != "N/A":
        return data['Poster']
    else:
        return "https://via.placeholder.com/200x300?text=No+Image"

# ✅ Recommend similar movies
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []

    for i in movies_list:
        title = movies.iloc[i[0]].title
        try:
            poster = fetch_poster(title)
        except Exception as e:
            st.error(f"Error fetching poster for '{title}': {e}")
            poster = "https://via.placeholder.com/200x300?text=Image+Not+Found"

        recommended_movies.append(title)
        recommended_movies_posters.append(poster)

    return recommended_movies, recommended_movies_posters

# ✅ Load data
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# ✅ Streamlit UI
st.title('🎬 Movie Recommender System')

selected_movie_name = st.selectbox(
    'Select a movie to get recommendations:',
    movies['title'].values
)

if st.button('Recommend'):
    st.write("Fetching recommendations...")
    names, posters = recommend(selected_movie_name)
    st.write("Recommendations received!")

    # Display recommendations in 5 columns
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.text(names[0])
        st.image(posters[0])
    with col2:
        st.text(names[1])
        st.image(posters[1])
    with col3:
        st.text(names[2])
        st.image(posters[2])
    with col4:
        st.text(names[3])
        st.image(posters[3])
    with col5:
        st.text(names[4])
        st.image(posters[4])
