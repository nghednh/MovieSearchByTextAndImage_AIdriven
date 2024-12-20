import pandas as pd
import sqlite3




# def preprocess_overview(overview):
#     parts = overview.split("/", 1) 
#     title = parts[0].strip()  
#     description = parts[1].strip() if len(parts) > 1 else ""  
#     weighted_title = (title + " ") * 10  
#     return weighted_title + description  


def csv_to_sqlite(csv_file, db_file, table_name, index_column):
    # Load the CSV file into a Pandas DataFrame
    df = pd.read_csv(csv_file)
    
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Save the DataFrame to a table in the database
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    print(f"Data from '{csv_file}' has been loaded into the table '{table_name}' in the database '{db_file}'.")

    # Create an index on the specified column
    cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{index_column} ON {table_name} ({index_column});")
    print(f"Index on column '{index_column}' has been created.")
    
    # Commit changes and close the connection
    conn.commit()
    conn.close()

# Example usage
# csv_file = "subtitle.csv"
# db_file = "subtitle.db"
# table_name = "subtitle"
# index_column = "imdb_id"  # Column to index for faster searches

# csv_to_sqlite(csv_file, db_file, table_name, index_column)

csv_file = "overview.csv"
db_file = "overview.db"
table_name = "overview"
index_column = "imdb_id"  # Column to index for faster searches
csv_to_sqlite(csv_file, db_file, table_name, index_column)