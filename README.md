Paris Events Explorer
Overview
The Paris Events Explorer is an interactive web application built with Streamlit to analyze and visualize cultural events in Paris. It fetches data from the Que Faire à Paris ? API, stores it in a SQLite database, and provides visualizations (bar, map, pie, line charts) and a filterable table. Key features include:

Filtering events by price_type (e.g., "gratuit sous condition") and access_type.
Interactive map with vivid colors (px.colors.qualitative.Vivid) for clear access_type visualization. 
Expanders for detailed analysis (pie and line charts).
Display of price_detail and description for event conditions.
Reset button to clear filters.

The app is deployed on Streamlit Community Cloud for easy access.
Dependencies
The project requires the following Python packages with specific versions for compatibility:



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


Python's built-in sqlite3 module is also used (no installation needed).
Setup Instructions
Follow these steps to run the project locally on a Windows machine:

Clone the Repository:
git clone https://github.com/sarramouadeb/paris-events.git
cd paris-events


Create and Activate a Virtual Environment:
python -m venv venv
call venv\Scripts\activate


Install Dependencies:
pip install requests==2.32.3 pandas==2.2.2 streamlit==1.38.0 plotly==5.22.0 python-dotenv==1.0.1


Fetch Data from the Paris Open Data API:
python fetch_data.py

This creates data/raw_events.json with event data.

Load Data into SQLite Database:
python load_to_db.py

This generates events.db from the JSON data.

Analyze Data:
python analyze.py

This performs additional data processing (if required).

Run the Streamlit App:
streamlit run app.py

Open http://localhost:8501 in your browser to view the app.


Note: Ensure .env is configured with DB_PATH=events.db. Copy .env.example to .env if needed:
copy .env.example .env

Deployment
The app is deployed on Streamlit Community Cloud for free:

Repository: https://github.com/sarramouadeb/paris-events

Environment variable DB_PATH=events.db is set in Streamlit Cloud settings.

To deploy your own instance:

Push the repository to GitHub (public repo required for free tier).
Sign in to share.streamlit.io with GitHub.
Create a new app, select sarramouadeb/paris-events, set branch to main, and app.py as the main file.
Add environment variable DB_PATH=events.db in advanced settings.
Deploy and access the public URL.

Notes

The app uses a modern UI with expanders for pie and line charts, a reset button, and vivid map colors for clarity.
Conditions for "gratuit sous condition" events are shown in price_detail and description columns.
Data is sourced from Que Faire à Paris ? and processed into a SQLite database (events.db).
Date: 19 October 2025

Troubleshooting

API Rate Limits: If fetch_data.py fails, add time.sleep(1) in the API loop and re-run.
Database Errors: Verify events.db is generated:sqlite3 events.db "SELECT count(*) FROM events;"

