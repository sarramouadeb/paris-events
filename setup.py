import os
from fetch_data import fetch_data
from load_to_db import load_data_to_db

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

# Run data pipeline only if events.db doesn't exist
if not os.path.exists('events.db'):
    print("Fetching data...")
    fetch_data()
    print("Loading data to SQLite...")
    load_data_to_db()