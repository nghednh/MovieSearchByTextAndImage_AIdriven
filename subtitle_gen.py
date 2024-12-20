import pandas as pd

df = pd.read_csv("text.csv")

selected_column = ["imdb_id", "text"]  

minimize_df = df[selected_column]
minimize_df['text'] = minimize_df['text'].fillna('').str.strip()

merged_df = minimize_df.groupby('imdb_id', as_index=False).agg({'text': ' '.join})
merged_df.to_csv("subtitle.csv", index=False)

print(merged_df.head())
