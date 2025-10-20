import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def fetch_events_data(max_records=2000):
    base_url = "https://opendata.paris.fr/api/records/1.0/search/"
    params = {
        "dataset": "que-faire-a-paris-",
        "rows": 1000,
        "sort": "-date_start",
        "facet": ["category", "tags", "address_zipcode", "price_type", "access_type"]
    }
    all_events = []
    offset = 0
    try:
        while len(all_events) < max_records:
            params["start"] = offset
            response = requests.get(base_url, params=params)
            if response.status_code == 200:
                data = response.json()
                records = data.get('records', [])
                if not records:
                    break
                events = [record['fields'] for record in records]
                if events:
                    print("Sample event fields:", list(events[0].keys()))
                    print("Sample event tags:", events[0].get('tags', []))
                    print("Sample price_type:", events[0].get('price_type', 'N/A'))
                    print("Sample access_type:", events[0].get('access_type', 'N/A'))
                all_events.extend(events)
                offset += params["rows"]
                print(f"Fetched {len(events)} events (total: {len(all_events)})")
            else:
                raise Exception(f"API error: {response.status_code}")
        os.makedirs('data', exist_ok=True)
        with open('data/raw_events.json', 'w', encoding='utf-8') as f:
            json.dump(all_events[:max_records], f, ensure_ascii=False, indent=4)
        print(f"Saved {len(all_events[:max_records])} events.")
    except Exception as e:
        print(f"Error in fetch_data: {e}")

if __name__ == "__main__":
    fetch_events_data()



def fetch_data(max_records=2000):
    """Compatibility wrapper so callers can import fetch_data.fetch_data().

    Delegates to fetch_events_data.
    """
    return fetch_events_data(max_records)