import pandas as pd

# Load the full file
full_df = pd.read_csv("movies_meta.csv")  

# Select only specific columns
selected_columns = ["imdb_id", "title", "overview"]  
minimized_df = full_df[selected_columns]




minimized_df['overview'] = minimized_df['overview'].fillna('').str.strip()


minimized_df['overview'] = minimized_df['title'] + "/ " + minimized_df['overview']

minimized_df = minimized_df.drop(columns=['title'])

print(minimized_df.head(5))
minimized_df.to_csv("overview.csv")
