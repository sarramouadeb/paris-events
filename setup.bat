python -m venv venv
call venv\Scripts\activate
pip install requests pandas streamlit plotly python-dotenv
python fetch_data.py
python load_to_db.py
python analyze.py
streamlit run app.py