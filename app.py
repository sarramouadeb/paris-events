import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os
from dotenv import load_dotenv
import setup  # Import and run setup.py to ensure database creation

# Configuration du thème
st.set_page_config(page_title="Paris Events Explorer", layout="wide", page_icon="🎭")

# Charger les variables d'environnement
load_dotenv()
DB_PATH = os.getenv('DB_PATH', 'events.db')

# Styles CSS personnalisés
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        background-color: #1E90FF; 
        color: white; 
        border-radius: 5px; 
        padding: 8px 16px; 
    }
    .stSelectbox { 
        background-color: #ffffff; 
        border-radius: 5px; 
        border: 1px solid #ced4da; 
    }
    .stCheckbox { margin-top: 15px; }
    h1 { 
        color: #1E90FF; 
        font-size: 2.5em; 
        font-weight: bold; 
    }
    h2 { 
        color: #343a40; 
        font-size: 1.8em; 
        margin-top: 20px; 
    }
    .sidebar .sidebar-content { 
        background-color: #e9ecef; 
        padding: 10px; 
        border-radius: 5px; 
    }
    .event-table { 
        font-size: 15px; 
        border-collapse: collapse; 
    }
    .st-expander { 
        background-color: #ffffff; 
        border: 1px solid #dee2e6; 
        border-radius: 5px; 
    }
    hr { 
        border-top: 2px solid #dee2e6; 
        margin: 20px 0; 
    }
    </style>
""", unsafe_allow_html=True)

# Titre et introduction
st.title("🎭 Paris Events Explorer")
st.markdown("""
**Explorez les événements culturels de Paris** avec des visualisations interactives et un tableau détaillé.  
Utilisez la barre latérale pour filtrer par type de tarif ou d'accès, et découvrez les détails dans les sections ci-dessous.
""")

# Bouton de réinitialisation des filtres
if st.button("🗑️ Réinitialiser les Filtres"):
    st.session_state.clear()

# Connexion à la base de données
try:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM events", conn)
    conn.close()
except Exception as e:
    st.error(f"Erreur de base de données : {e}. Veuillez vérifier que les données sont disponibles.")
    st.stop()

# Nettoyage et préparation des données
df['arrondissement'] = df['address_zipcode'].str.extract(r'(\d{2})$').astype(float, errors='ignore')
df['date_start'] = pd.to_datetime(df['date_start'], errors='coerce')
df['category'] = df.apply(lambda row: row['tags'].split(',')[0] if isinstance(row['tags'], str) and row['tags'] and row['tags'] != 'Unknown' else (row['price_type'] if pd.notna(row['price_type']) else 'Other'), axis=1)

df_viz = df.dropna(subset=['date_start', 'latitude', 'longitude']).copy()
df_viz = df_viz[df_viz['arrondissement'].between(1, 20)]  # Filtrer pour Paris
st.write(f"**Événements disponibles : {len(df_viz)}**", unsafe_allow_html=True)

# Barre latérale pour les filtres
with st.sidebar:
    st.header("🎛️ Filtres")
    show_conditions = st.checkbox("Afficher uniquement les événements 'gratuit sous condition'", key="show_conditions")
    filters = st.multiselect(
        "Filtrer par Type de Tarif ou Type d'Accès",
        options=list(set(df_viz['price_type'].dropna().unique().tolist() + df_viz['access_type'].dropna().unique().tolist())),
        help="Sélectionnez plusieurs options pour filtrer les événements.",
        key="filters"
    )

# Filtrage des données
if show_conditions:
    df_filtered = df_viz[df_viz['price_type'] == 'gratuit sous condition']
    if df_filtered.empty:
        st.warning("Aucun événement 'gratuit sous condition' trouvé dans les données.")
    else:
        st.info("Les conditions sont généralement indiquées dans 'Détails du Tarif' ou 'Description'.")
elif filters:
    df_filtered = df_viz[df_viz['price_type'].isin(filters) | df_viz['access_type'].isin(filters)]
else:
    df_filtered = df_viz

# Section 1 : Aperçu des données
with st.container():
    st.header("📊 Aperçu des Événements")
    st.markdown("Visualisez la répartition des événements par arrondissement et leur localisation.")
    col1, col2 = st.columns([1, 1.5])
    
    # Viz 1 : Graphique en barres empilées
    with col1:
        if df_viz['arrondissement'].notna().sum() > 0 and df_viz['price_type'].notna().sum() > 0:
            bar_data = df_viz.groupby(['price_type', 'arrondissement']).size().reset_index(name='count')
            fig1 = px.bar(
                bar_data,
                x='arrondissement',
                y='count',
                color='price_type',
                title='Événements par Type de Tarif et Arrondissement',
                barmode='stack',
                labels={'arrondissement': 'Arrondissement', 'count': 'Nombre d\'Événements'},
                height=450,
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig1.update_layout(
                xaxis_title="Arrondissement",
                yaxis_title="Nombre d'Événements",
                legend_title="Type de Tarif",
                font=dict(size=14)
            )
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.error("Données insuffisantes pour type de tarif ou arrondissement.")

    # Viz 2 : Carte avec couleurs améliorées
    with col2:
        if len(df_viz) > 0 and df_viz['access_type'].notna().sum() > 0:
            map_data = df_viz.groupby(['latitude', 'longitude', 'access_type', 'title']).size().reset_index(name='count')
            fig2 = px.scatter_mapbox(
                map_data,
                lat='latitude',
                lon='longitude',
                color='access_type',
                size='count',
                size_max=25,
                zoom=11,
                mapbox_style="open-street-map",
                title='Localisation des Événements par Type d\'Accès',
                hover_data={'access_type': True, 'title': True, 'count': True},
                height=450,
                color_discrete_sequence=px.colors.qualitative.Vivid
            )
            fig2.update_layout(
                mapbox_center={"lat": 48.8566, "lon": 2.3522},
                legend=dict(title="Type d'Accès", font=dict(size=14)),
                font=dict(size=14)
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.error("Aucune donnée géographique ou de type d'accès valide pour la carte.")

# Section 2 : Analyse détaillée
with st.container():
    st.header("📈 Analyse Détaillée")
    st.markdown("Explorez les tendances et la répartition des types d'accès.")
    st.markdown("<hr>", unsafe_allow_html=True)
    
    with st.expander("Voir la Répartition par Type d'Accès", expanded=False):
        if df_viz['access_type'].notna().sum() > 0:
            pie_data = df_viz['access_type'].value_counts().reset_index(name='count')
            fig3 = px.pie(
                pie_data,
                names='access_type',
                values='count',
                title='Répartition des Événements par Type d\'Accès',
                height=400,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig3.update_layout(font=dict(size=14))
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.error("Aucune donnée de type d'accès pour le graphique en camembert.")
    
    with st.expander("Voir les Tendances Mensuelles", expanded=False):
        df_viz['month'] = df_viz['date_start'].dt.to_period('M').astype(str)
        monthly = df_viz.groupby('month').size().reset_index(name='count')
        if not monthly.empty:
            fig4 = px.line(
                monthly,
                x='month',
                y='count',
                title='Tendances Mensuelles des Événements',
                markers=True,
                height=400,
                line_shape='spline',
                color_discrete_sequence=['#1E90FF']
            )
            fig4.update_layout(
                xaxis_title="Mois",
                yaxis_title="Nombre d'Événements",
                xaxis_tickangle=45,
                font=dict(size=14)
            )
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.error("Aucune donnée pour les tendances mensuelles.")

# Section 3 : Exploration des données
with st.container():
    st.header("🔍 Explorer les Événements")
    st.markdown("Filtrez et explorez les détails des événements, y compris les conditions d'accès dans 'Détails du Tarif' ou 'Description'.")
    st.markdown("<hr>", unsafe_allow_html=True)
    
    columns_to_display = ['title', 'date_start', 'price_type', 'access_type', 'arrondissement', 'address_name', 'description']
    if 'price_detail' in df_filtered.columns:
        columns_to_display.insert(-1, 'price_detail')
    
    st.dataframe(
        df_filtered[columns_to_display],
        use_container_width=True,
        height=450,
        column_config={
            "title": st.column_config.TextColumn("Titre", width="medium"),
            "date_start": st.column_config.DatetimeColumn("Date de Début", format="DD/MM/YYYY"),
            "price_type": st.column_config.TextColumn("Type de Tarif"),
            "access_type": st.column_config.TextColumn("Type d'Accès"),
            "arrondissement": st.column_config.NumberColumn("Arrondissement", format="%d"),
            "address_name": st.column_config.TextColumn("Lieu", width="medium"),
            "price_detail": st.column_config.TextColumn("Détails du Tarif", width="medium") if 'price_detail' in df_filtered.columns else None,
            "description": st.column_config.TextColumn("Description", width="large")
        }
    )

# Pied de page
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("**Paris Events Explorer** - Développé avec Streamlit | Données : [Que Faire à Paris ?](https://opendata.paris.fr/) | 19 octobre 2025")