import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import random

# Load CSV files
df_search = pd.read_csv('overview.csv')
df_subtitle = pd.read_csv('subtitle.csv')

def preprocess_overview(overview):
    parts = overview.split("/", 1)
    title = parts[0].strip()
    description = parts[1].strip() if len(parts) > 1 else ""
    weighted_title = (title + " ") * 10
    return weighted_title + description

df_search['weighted_overview'] = df_search['overview'].apply(preprocess_overview)

# Combine the text data from both DataFrames for fitting the vectorizer
combined_corpus = pd.concat([df_search['weighted_overview'], df_subtitle['text']])

# Create a single TF-IDF vectorizer and fit it on the combined corpus
vectorizer = TfidfVectorizer(stop_words='english')
vectorizer.fit(combined_corpus)

# Create the TF-IDF matrix for the search DataFrame
tfidf_matrix = vectorizer.transform(df_search['weighted_overview'])

# Create the TF-IDF matrix for the subtitle DataFrame
tfidf_matrix_subtitle = vectorizer.transform(df_subtitle['text'])


# Connect to the database
conn = sqlite3.connect('movies_meta.db')
cursor = conn.cursor()

def query_db_by_id(imdb_id):
    cursor.execute("SELECT * FROM my_table WHERE imdb_id = ?", (imdb_id,))
    return cursor.fetchone()

def get_movie_details_by_ids(top_ids):
    movie_details = []
    for movie_id in top_ids:
        cursor.execute("SELECT imdb_id, title FROM my_table WHERE imdb_id = ?", (movie_id,))
        result = cursor.fetchone()
        if result:
            movie_details.append(result)  # Append only ID and name
    return movie_details

def search(query, top_k=5):
    query_tfidf = vectorizer.transform([query])
    similarities = cosine_similarity(query_tfidf, tfidf_matrix)
    similar_indices = similarities.argsort()[0][::-1]
    top_ids = df_search.iloc[similar_indices[:top_k]]['imdb_id'].tolist()
    return top_ids

def search_subtitle(query, top_k=5):
    query_tfidf = vectorizer.transform([query])
    similarities = cosine_similarity(query_tfidf, tfidf_matrix_subtitle)
    similar_indices = similarities.argsort()[0][::-1]
    top_ids = df_subtitle.iloc[similar_indices[:top_k]]['imdb_id'].tolist()  # Fixed to use df_subtitle
    return top_ids

def boolean_search(query, top_k=5):
    terms = re.split(r'\s+(AND|OR|NOT)\s+', query)
    current_result = set(range(len(df_search)))  # Start with all document indices

    for i in range(0, len(terms), 2):
        term = terms[i]
        operator = terms[i - 1] if i > 0 else "AND"

        term_tfidf = vectorizer.transform([term])
        similarities = cosine_similarity(term_tfidf, tfidf_matrix).flatten()
        matching_indices = set(similarities.argsort()[::-1][:top_k])

        if operator == "AND":
            current_result &= matching_indices
        elif operator == "OR":
            current_result |= matching_indices
        elif operator == "NOT":
            current_result -= matching_indices

    # Retrieve top results
    final_indices = sorted(current_result, key=lambda idx: -similarities[idx])
    top_ids = df_search.iloc[final_indices[:top_k]]['imdb_id'].tolist()
    return top_ids


def calculate_score(top_ids, expected_ids):
    score = 0
    for idx, imdb_id in enumerate(top_ids):
        if imdb_id in expected_ids:
            if idx == 0:
                score += 100
            elif idx == 1:
                score += 80
            elif idx == 2:
                score += 60
            elif idx == 3:
                score += 40
            elif idx == 4:
                score += 20
    return score

def remove_random_chars(query, words_to_remove=5):
    words = query.split()
    num_words = len(words)
    for i in range(0, num_words, words_to_remove):
        word = words[i]
        if len(word) > 1:
            random_index = random.randint(0, len(word) - 1)
            word = word[:random_index] + word[random_index + 1:]
            words[i] = word
    modified_query = ' '.join(words)
    return modified_query
def run_tests1(num_tests=1000):
    total_score = 0
    for _ in range(num_tests):
        rand_index = random.randint(0, len(df_search) - 1)
        query_overview = df_search.iloc[rand_index]['overview']
        expected_imdb_id = df_search.iloc[rand_index]['imdb_id']
        modified_query = remove_random_chars(query_overview)
        top_ids = search(modified_query, top_k=5)
        score = calculate_score(top_ids, [expected_imdb_id])
        total_score += score
    average_score = total_score / num_tests
    accuracy = average_score / 100
    return accuracy
def run_tests2(num_tests=1000):
    """
    Run tests by selecting random queries from the subtitle DataFrame and calculating the search results' score.
    """
    if df_subtitle.empty:
        print("Subtitle DataFrame is empty. Exiting tests.")
        return 0

    total_score = 0
    for _ in range(num_tests):
        # Randomly select an index to pick a query from df_subtitle
        rand_index = random.randint(0, len(df_subtitle) - 1)  # Fixed to use df_subtitle length
        query_overview = df_subtitle.iloc[rand_index]['text']
        expected_imdb_id = df_subtitle.iloc[rand_index]['imdb_id']
        modified_query = remove_random_chars(query_overview)
        # Perform the search using the overview query
        top_ids = search_subtitle(modified_query, top_k=5)

        # Calculate the score for this test
        score = calculate_score(top_ids, [expected_imdb_id])
        total_score += score

    # Calculate the average score
    average_score = total_score / num_tests
    accuracy = average_score / 100  # To convert it into percentage
    return accuracy


def main():
    print("Running test for 'search' function...")
    accuracy = run_tests1(num_tests=100)
    print(f"Search function accuracy: {accuracy * 100}%")

    print("Running test for 'search_subtitle' function...")
    accuracy_subtitle = run_tests2(num_tests=100)
    print(f"Search subtitle function accuracy: {accuracy_subtitle * 100}%")

    print("Running test for 'boolean_search' function...")
    accuracy_boolean = run_tests1(num_tests=100)
    print(f"Boolean search function accuracy: {accuracy_boolean * 100}%")


if __name__ == "__main__":
    main()
