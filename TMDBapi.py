import requests
from pymongo import MongoClient
import time

# Initialize MongoDB connection (replace with your MongoDB Atlas URI)
client = MongoClient(
    'mongodb+srv://nghednh:123@cluster0.llhn1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['movie_database']
movie_collection = db['movies']

# TMDb API Key
TMDB_API_KEY = '50767d9d58baff413d3f12803125ce4d'


# Function to fetch movie data from TMDb API by movie ID
def fetch_movie_data_by_id(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


# Function to store movie data into MongoDB
def store_movie_data(movie_data):
    try:
        movie_collection.update_one(
            {'tmdb_id': movie_data['tmdb_id']},
            {'$set': movie_data},
            upsert=True
        )
    except Exception as e:
        print(f"Error storing movie ID {movie_data['tmdb_id']} into MongoDB: {e}")


# Function to fetch and store movies until 10 valid movies are found
def fetch_and_store_movies_in_batches(start_id, valid_movie_count_target=10, batch_size=50):
    valid_movie_count = 0  # Counter for valid movies
    movie_id = start_id  # Start from the given ID

    while valid_movie_count < valid_movie_count_target:
        print(f"Fetching data for movie ID: {movie_id}")
        movie_data = fetch_movie_data_by_id(movie_id)

        if movie_data:
            # Print the raw data to debug title, overview, images, and original_title
            print(f"Raw data for movie ID {movie_id}:")
            print(f"Title: {movie_data.get('title')}")
            print(f"Overview: {movie_data.get('overview')}")
            print(f"Images: {movie_data.get('images')}")
            print(f"Original Title: {movie_data.get('original_title')}")

            # Check if the required fields are present before processing the movie
            if 'title' in movie_data and 'overview' in movie_data and 'images' in movie_data and 'original_title' in movie_data:
                print(f"Storing data for movie: {movie_data['title']}")

                # Prepare a set of data to store (only store the required fields)
                movie_set_data = {
                    'tmdb_id': movie_data['id'],
                    'title': movie_data['title'],
                    'overview': movie_data['overview'],
                    'subtitle': movie_data['original_title'],  # Use the original_title as subtitle (English)
                    'images': {}  # Add images data here
                }

                # Add additional images (stills) if available
                if 'stills' in movie_data['images']:
                    movie_set_data['images']['additional_images'] = [
                        f"https://image.tmdb.org/t/p/w500{image['file_path']}" for image in movie_data['images']['stills']
                    ]

                # Store the movie data in MongoDB
                store_movie_data(movie_set_data)

                # Print the stored data
                print(movie_set_data)

                # Increment valid movie count
                valid_movie_count += 1

        else:
            print(f"No data found for movie ID: {movie_id}")

        # Increase the movie ID to fetch the next one
        movie_id += 1

        # Add a small delay to avoid hitting the TMDb API rate limits
        time.sleep(0.2)  # Sleep for 200ms to avoid rate limiting

        # Optional: batch storage logic, to process data in batches
        if movie_id % batch_size == 0:
            print(f"Processed {valid_movie_count} valid movies...")

    print(f"Finished fetching and storing {valid_movie_count_target} valid movies.")


# Example usage: Fetch and store 10 valid movies starting from ID 1
fetch_and_store_movies_in_batches(1, valid_movie_count_target=10)

# Print the first 10 documents in the 'movies' collection
for movie in movie_collection.find().limit(10):
    print(movie)
