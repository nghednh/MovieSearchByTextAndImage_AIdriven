import spacy
import requests
from pymongo import MongoClient
from elasticsearch import Elasticsearch

# Initialize spaCy NLP model
nlp = spacy.load("en_core_web_sm")

# Initialize MongoDB connection (use your MongoDB Atlas URI)
client = MongoClient('mongodb+srv://nghednh:bJxOFDklmxwEDxey@cluster0.llhn1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['movie_database']
movie_collection = db['movies']

# Initialize Elasticsearch
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

# TMDb API Key
TMDB_API_KEY = '50767d9d58baff413d3f12803125ce4d'


# Function to fetch movie data from TMDb API
def fetch_movie_data(query):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['results']
    return []


# Function to index movie data into Elasticsearch
def index_movie_data(movie_data):
    for movie in movie_data:
        movie_doc = {
            'title': movie['title'],
            'release_date': movie['release_date'],
            'overview': movie['overview'],
            'tmdb_id': movie['id']
        }
        es.index(index='movies', id=movie['id'], document=movie_doc)


# Function to store movie data into MongoDB
def store_movie_data(movie_data):
    for movie in movie_data:
        movie_collection.update_one(
            {'tmdb_id': movie['id']},
            {'$set': movie},
            upsert=True
        )


# Function to process and analyze user query using spaCy
def analyze_query(query):
    doc = nlp(query)
    # Extract key phrases and entities from the query to refine the search
    entities = [ent.text for ent in doc.ents]
    return entities


# Function to search movies based on overviews in Elasticsearch
def search_movies_by_overview(query):
    # Search in Elasticsearch index for movies based on the query's overview
    res = es.search(index="movies", body={
        "query": {
            "match": {
                "overview": query  # Search for the description part of the query
            }
        }
    })
    return res['hits']['hits']


# Main function to handle search for movie by description/overview
def movie_search_by_description(query):
    # Analyze the query using spaCy to extract entities or key details
    entities = analyze_query(query)
    print(f"Query analysis: {entities}")

    # If the query contains key terms/phrases, perform search in Elasticsearch
    if entities:
        es_results = search_movies_by_overview(' '.join(entities))
        if es_results:
            print("Found results in Elasticsearch based on description:")
            for res in es_results:
                print(
                    f"Title: {res['_source']['title']}, Release Date: {res['_source']['release_date']}, Overview: {res['_source']['overview']}")
        else:
            print("No results found in Elasticsearch, querying TMDb API...")
            # If no results are found in Elasticsearch, query the TMDb API
            tmdb_results = fetch_movie_data(query)
            if tmdb_results:
                print("Found results in TMDb API:")
                for movie in tmdb_results:
                    print(
                        f"Title: {movie['title']}, Release Date: {movie['release_date']}, Overview: {movie['overview']}")

                # Index the TMDb results into Elasticsearch and store in MongoDB for future queries
                index_movie_data(tmdb_results)
                store_movie_data(tmdb_results)
            else:
                print("No results found from TMDb API.")


# Example usage: searching for a movie by its description
query = "A man who can enter people's dreams and steal their secrets"
movie_search_by_description(query)
