import streamlit as st
import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests

# Initialize session state for theme if not already set
if 'theme' not in st.session_state:
    st.session_state['theme'] = 'dark'  # Default to dark mode

# Load the search data
df_search = pd.read_csv('overview.csv')

# Initialize TF-IDF Vectorizer
vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(df_search['overview'])

# Connect to the database
conn = sqlite3.connect('movies_meta.db')
cursor = conn.cursor()

API_KEY = '50767d9d58baff413d3f12803125ce4d'
BASE_URL = 'https://api.themoviedb.org/3'


# Function to query the database by IMDb ID
def query_db_by_id(imdb_id):
    cursor.execute("SELECT * FROM my_table WHERE imdb_id = ?", (imdb_id,))
    return cursor.fetchone()


# Function to search for top K matching movies
def search(query, top_k=5):
    query_tfidf = vectorizer.transform([query])
    similarities = cosine_similarity(query_tfidf, tfidf_matrix)
    similar_indices = similarities.argsort()[0][::-1]
    top_ids = df_search.iloc[similar_indices[:top_k]]['imdb_id'].tolist()
    return top_ids


# Function to retrieve movie details by IDs
def get_movie_details(top_ids):
    movie_details = []
    for movie_id in top_ids:
        result = query_db_by_id(movie_id)
        if result:
            movie_details.append(result)
    return movie_details


# Function to get movie title from the database by IMDb ID
def get_movie_name_by_id(imdb_id):
    cursor.execute("SELECT title FROM my_table WHERE imdb_id = ?", (imdb_id,))
    result = cursor.fetchone()
    return result[0] if result else None


# Function to get detailed movie information from TMDB
def get_movie_info_by_name(movie_name):
    search_url = f"{BASE_URL}/search/movie?api_key={API_KEY}&query={movie_name}&language=en-US"
    search_response = requests.get(search_url)
    search_data = search_response.json()

    if search_response.status_code == 200 and search_data['results']:
        movie = search_data['results'][0]
        movie_id = movie['id']
        movie_url = f"{BASE_URL}/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        movie_response = requests.get(movie_url)
        movie_data = movie_response.json()

        if movie_response.status_code == 200:
            poster_path = movie_data.get('poster_path')
            release_date = movie_data.get('release_date', 'Not available')
            rating = movie_data.get('vote_average', 'Not available')
            genres = [genre['name'] for genre in movie_data.get('genres', [])]
            overview = movie_data.get('overview', 'No overview available')

            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
            return {
                'poster_url': poster_url,
                'release_date': release_date,
                'rating': rating,
                'genres': ', '.join(genres) if genres else 'Not available',
                'overview': overview
            }

    return None


st.title("Movie Search App")
st.write("Enter a query below and find the best matching movies!")

# Input field for the user's query
user_query = st.text_input("Enter your query:", "")

# Slider to choose the number of top results to display
top_k = st.slider("Number of results to display:", min_value=1, max_value=10, value=5)

# Search button
if st.button("Search"):
    if user_query.strip():
        top_ids = search(user_query, top_k=top_k)
        movie_details = get_movie_details(top_ids)
        movie_names = [get_movie_name_by_id(movie_id) for movie_id in top_ids]

        for name in movie_names:
            if name:
                movie_info = get_movie_info_by_name(name)
                if movie_info:
                    poster_url = movie_info['poster_url']
                    release_date = movie_info['release_date']
                    rating = movie_info['rating']
                    genres = movie_info['genres']
                    overview = movie_info['overview']

                    with st.container():
                        st.markdown("---")
                        col1, col2 = st.columns([1, 3])

                        with col1:
                            if poster_url:
                                st.image(poster_url, width=200)
                            else:
                                st.write("Poster not found")

                        with col2:
                            st.subheader(name)
                            st.write(f"**Release Date:** {release_date}")
                            st.write(f"**Rating:** {rating} 🌟")
                            st.write(f"**Genres:** {genres}")
                            st.write(f"**Overview:** {overview}")
                else:
                    st.write(f"- Could not retrieve information for '{name}' from TMDB.")
            else:
                st.write("- Movie not found in the database")
    else:
        st.write("Please enter a query.")
