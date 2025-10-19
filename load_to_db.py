import json
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv('DB_PATH', 'events.db')

def create_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            date_start TEXT,
            date_end TEXT,
            address_name TEXT,
            address_street TEXT,
            address_zipcode TEXT,
            address_city TEXT,
            latitude REAL,
            longitude REAL,
            tags TEXT,
            category TEXT,
            price_type TEXT,
            access_type TEXT,
            price_detail TEXT
        )
    ''')
    conn.commit()

def load_data_to_db():
    try:
        if not os.path.exists('data/raw_events.json'):
            raise FileNotFoundError("raw_events.json not found. Run fetch_data.py first.")
        
        with open('data/raw_events.json', 'r', encoding='utf-8') as f:
            events = json.load(f)
        
        conn = sqlite3.connect(DB_PATH)
        create_table(conn)
        cursor = conn.cursor()
        
        for event in events:
            tags = event.get('tags', []) or event.get('program', []) or event.get('event_type', [])
            tags_str = ','.join([str(tag).strip() for tag in tags if tag]) if isinstance(tags, list) and tags else 'Unknown'
            geo = event.get('lat_lon', [None, None])
            lat = float(geo[0]) if geo[0] and 48.8 <= float(geo[0]) <= 48.9 else None
            lon = float(geo[1]) if geo[1] and 2.2 <= float(geo[1]) <= 2.4 else None
            cursor.execute('''
                INSERT OR REPLACE INTO events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.get('id', 'Unknown'),
                event.get('title', 'Unknown'),
                event.get('description', ''),
                event.get('date_start', None),
                event.get('date_end', None),
                event.get('address_name', ''),
                event.get('address_street', ''),
                event.get('address_zipcode', ''),
                event.get('address_city', ''),
                lat,
                lon,
                tags_str,
                event.get('category', 'Unknown'),
                event.get('price_type', 'Unknown'),
                event.get('access_type', 'Unknown'),
                event.get('price_detail', '')
            ))
        conn.commit()
        conn.close()
        print("Data loaded into SQLite.")
    except Exception as e:
        print(f"Error in load_to_db: {e}")

if __name__ == "__main__":
    load_data_to_db()