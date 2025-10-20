
 Paris Events Explorer

Overview
Paris Events Explorer is an interactive web application built with Streamlit to visualize and analyze cultural events in Paris using data from the Que Faire à Paris? API. The app stores data in a SQLite database and offers:

Interactive Visualizations: Bar, map, pie, and line charts.
Filtering: By price_type (e.g., "gratuit sous condition") and access_type.
Map: Uses vivid colors (px.colors.qualitative.Vivid) for clear access_type visualization.
Detailed Analysis: Pie and line charts in collapsible expanders.
Event Details: Shows price_detail and description for event conditions.
User-Friendly UI: Includes a reset button to clear filters.

The app is deployed on Streamlit Community Cloud for free access.
Dependencies
The project requires the following Python packages:



Package
Version



streamlit
1.38.0


pandas
2.2.2


plotly
5.22.0


requests
2.32.3


python-dotenv
1.0.1



Note: Python's built-in sqlite3 module is used (no installation needed).

Local Setup
To run the project locally on a Windows machine, follow these steps:

Clone the Repository:
git clone https://github.com/sarramouadeb/paris-events.git
cd paris-events


Create and Activate a Virtual Environment:
python -m venv venv
call venv\Scripts\activate


Install Dependencies:
pip install requests==2.32.3 pandas==2.2.2 streamlit==1.38.0 plotly==5.22.0 python-dotenv==1.0.1


Fetch Data:
python fetch_data.py


Creates data/raw_events.json with event data from the Paris Open Data API.


Load Data to SQLite:
python load_to_db.py


Generates events.db from the JSON data.


Analyze Data:
python analyze.py


Performs additional data processing (if required).


Run the Streamlit App:
streamlit run app.py


Open http://localhost:8501 in your browser.


Configure Environment:

Ensure .env exists with DB_PATH=events.db:
copy .env.example .env





Deployment
The app is deployed on Streamlit Community Cloud (free tier):


Repository: https://github.com/sarramouadeb/paris-events
Environment Variable: DB_PATH=events.db (set in Streamlit Cloud settings)


Deploy Your Own Instance

Push the repository to GitHub (public repo required for free tier).
Sign in to share.streamlit.io with GitHub.
Click "New app", select sarramouadeb/paris-events, set:
Branch: main
Main file: app.py


In "Advanced settings", add: DB_PATH=events.db.
Click "Deploy" to get a public URL.

Notes

UI Features:
Expanders for pie and line charts.
Vivid map colors for clear access_type visualization.
Reset button to clear filters.
Displays price_detail and description for "gratuit sous condition" events.


Data Source: Que Faire à Paris? API, stored in events.db.
Environment: Uses a virtual environment (no Docker).
Date: 19 October 2025

Troubleshooting

API Rate Limits:
If fetch_data.py fails, add a delay in the API loop:
import time
# Inside fetch_data.py loop
time.sleep(1)


Re-run and push changes.



Database Issues:
Verify events.db:
sqlite3 events.db "SELECT count(*) FROM events;"




Deployment Errors:
Check Streamlit Cloud logs (app > "Manage app" > "Logs").
Ensure requirements.txt matches the dependency versions above.



For issues, open a ticket on GitHub Issues.