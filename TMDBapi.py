import requests

# Replace with your TMDb API key
API_KEY = '50767d9d58baff413d3f12803125ce4d'
BASE_URL = 'https://api.themoviedb.org/3'

# Function to search movie by name and get its poster
def get_movie_poster_by_name(movie_name):
    # Search for the movie by name
    search_url = f"{BASE_URL}/search/movie?api_key={API_KEY}&query={movie_name}&language=en-US"
    search_response = requests.get(search_url)
    search_data = search_response.json()

    if search_response.status_code == 200 and search_data['results']:
        # Get the first movie from the search results
        movie = search_data['results'][0]
        movie_id = movie['id']

        # Get movie details to fetch the poster
        movie_url = f"{BASE_URL}/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        movie_response = requests.get(movie_url)
        movie_data = movie_response.json()

        if movie_response.status_code == 200:
            # Get poster path from the movie data
            poster_path = movie_data.get('poster_path')
            if poster_path:
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                return poster_url
            else:
                print("Poster not found.")
                return None
        else:
            print(f"Error fetching movie details: {movie_data.get('status_message')}")
            return None
    else:
        print(f"Error searching for movie: {search_data.get('status_message')}")
        return None

# Example: Get the poster for a movie by name
movie_name = "Fight Club"  # Replace with the name of the movie you want
poster_url = get_movie_poster_by_name(movie_name)

if poster_url:
    print(f"Poster URL: {poster_url}")
