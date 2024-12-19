import pandas as pd

# # Load the full file
# full_df = pd.read_csv("joined_output.csv", dtype={'imdb_id': str})  # Ensure 'imdb_id' is string

# # Ensure the 'text' column is treated as a string
# full_df['text'] = full_df['text'].astype(str)

# # Select only specific columns
# selected_columns = ["imdb_id", "title","overview"]
# minimized_df = full_df[selected_columns]

# minimized_df['overview'] = minimized_df['title'].astype(str) + " " + minimized_df['overview'].astype(str)
# minimized_df = minimized_df.drop(columns=['title'])
# minimized_df.to_csv("overview.csv", index=False)
import sqlite3
import pandas as pd

# Load search.csv
df_search = pd.read_csv('overview.csv')

# Connect to the database
conn = sqlite3.connect('movies_meta.db')
cursor = conn.cursor()

# Optionally, let's define a function to query the database by id
def query_db_by_id(imdb_id):
    cursor.execute("SELECT * FROM my_table WHERE imdb_id = ?", (imdb_id,))
    return cursor.fetchone()

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Initialize TF-IDF Vectorizer
vectorizer = TfidfVectorizer(stop_words='english')

# Fit the vectorizer on the overviews in search.csv
tfidf_matrix = vectorizer.fit_transform(df_search['overview'])

def search(query):
    # Transform the user's query into a TF-IDF vector
    query_tfidf = vectorizer.transform([query])
    
    # Compute cosine similarities between the query and the document vectors
    similarities = cosine_similarity(query_tfidf, tfidf_matrix)
    
    # Get the indices of the most similar rows (documents)
    similar_indices = similarities.argsort()[0][::-1]  # Sorted in descending order
    
    # Get the ids of the top N results (for example, top 5)
    top_n = 5
    top_ids = df_search.iloc[similar_indices[:top_n]]['imdb_id'].tolist()
    
    return top_ids
def get_movie_details(top_ids):
    movie_details = []
    for movie_id in top_ids:
        result = query_db_by_id(movie_id)
        movie_details.append(result)
    
    return movie_details
# Example user query
user_query = "space adventure toys"

# Step 1: Get the top ids based on search
top_ids = search(user_query)

# Step 2: Retrieve movie details from the database using the ids
movie_details = get_movie_details(top_ids)

# Print the movie details
for detail in movie_details:
    print(detail)

