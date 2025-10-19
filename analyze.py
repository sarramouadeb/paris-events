import sqlite3
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv('DB_PATH', 'events.db')

def analyze_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM events", conn)
        conn.close()
    except Exception as e:
        print(f"Error reading database: {e}")
        return
    
    print(f"Initial rows: {len(df)}")
    if df.empty:
        print("Error: DataFrame is empty. Check database or fetch step.")
        return
    
    print("Columns in DataFrame:", df.columns.tolist())
    print(f"Rows with valid address_zipcode: {df['address_zipcode'].notna().sum()}")
    print(f"Sample address_zipcode: {df['address_zipcode'].head().tolist()}")
    print(f"Rows with valid tags: {df['tags'].notna().sum()}")
    print(f"Sample tags: {df['tags'].head().tolist()}")
    print(f"Rows with valid price_type: {df['price_type'].notna().sum()}")
    print(f"Sample price_type: {df['price_type'].head().tolist()}")
    print(f"Rows with valid access_type: {df['access_type'].notna().sum()}")
    print(f"Sample access_type: {df['access_type'].head().tolist()}")
    
    df['arrondissement'] = df['address_zipcode'].str.extract(r'(\d{2})$').astype(float, errors='ignore')
    df['date_start'] = pd.to_datetime(df['date_start'], errors='coerce')
    df['category'] = df.apply(lambda row: row['tags'].split(',')[0] if isinstance(row['tags'], str) and row['tags'] and row['tags'] != 'Unknown' else (row['price_type'] if pd.notna(row['price_type']) else 'Other'), axis=1)
    
    df_clean = df.dropna(subset=['date_start']).copy()
    print(f"Rows after cleaning: {len(df_clean)}")
    if df_clean.empty:
        print("Error: No rows after cleaning. Check date_start.")
        return
    
    if df_viz['arrondissement'].notna().sum() > 0:
        corr_df = pd.pivot_table(df_clean, index='category', columns='arrondissement', aggfunc='size', fill_value=0)
        print("Event count by category and arrondissement:\n", corr_df)
    else:
        print("Warning: No valid arrondissements, skipping correlation.")
    
    df_clean['month'] = df_clean['date_start'].dt.to_period('M').astype(str)
    monthly = df_clean.groupby('month').size().reset_index(name='count')
    print("Monthly event count:\n", monthly)
    
    if monthly.empty:
        print("Error: Monthly DataFrame is empty. Check date_start values.")
    else:
        print(f"Monthly rows: {len(monthly)}")
    
    os.makedirs('data', exist_ok=True)
    df_clean.to_csv('data/analyzed_events.csv', index=False)
    monthly.to_json('data/monthly.json', orient='records', lines=False)
    print("Analysis exported to data/analyzed_events.csv and data/monthly.json")

if __name__ == "__main__":
    analyze_data()