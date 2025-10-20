import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os
from dotenv import load_dotenv
import setup  
import re

# Configuration du thème
st.set_page_config(
    page_title="Paris Events Explorer", 
    layout="wide", 
    page_icon="🎭",
    initial_sidebar_state="expanded"
)

# Charger les variables d'environnement
load_dotenv()
DB_PATH = os.getenv('DB_PATH', 'events.db')

# Styles CSS 
st.markdown("""
    <style>
    /* MAIN APP - FOND UNI POUR TOUTE LA PAGE */
    .stApp {
       
    }
    
    /* Supprimer les boîtes vides et espaces inutiles */
    .main-block {
       
    }
    
    /* HEADERS - TOUS BIEN VISIBLES */
    h1, h2, h3, h4, h5, h6 {
        color: #1E3A8A !important;
        font-weight: 700 !important;
        margin-bottom: 1rem !important;
    }
    
    /* Texte normal bien visible */
    .stMarkdown {
        color: #374151 !important;
    }
    
    /* Messages d'information bien visibles */
    .stInfo, .stSuccess, .stWarning {
        background-color: #F0F9FF !important;
        border: 1px solid #1E90FF !important;
        border-radius: 8px !important;
        color: #1E3A8A !important;
        padding: 1rem !important;
    }
    
    /* Card-like containers avec fond uni */
    .main-container {
        background-color: #ffffff !important;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
        border: 1px solid #E5E7EB;
    }
    
    /* Button styling */
    .stButton>button {
        background-color: #1E90FF !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        border: none !important;
        width: 100%;
    }
    
    /* Sidebar styling */
    .css-1d391kg, .css-1lcbmhc {
        background-color: #1E3A8A !important;
    }
    
    /* Titres dans la sidebar en blanc */
    .sidebar .sidebar-content h1, 
    .sidebar .sidebar-content h2, 
    .sidebar .sidebar-content h3 {
        color: white !important;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        color: #1E3A8A !important;
    }
    
    /* Tab styling - TOUS LES TITRES VISIBLES */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #F8FAFC;
        padding: 8px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #E8F4FD;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        color: #1E3A8A !important;
        border: 1px solid #BFDBFE;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1E90FF !important;
        color: white !important;
        border: 1px solid #1E90FF;
    }
    
    /* Expander styling - BIEN VISIBLE */
    .streamlit-expanderHeader {
        background-color: #F8FAFC !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        color: #1E3A8A !important;
        border: 2px solid #1E90FF !important;
        margin-bottom: 8px;
        font-size: 1.1rem !important;
    }
    
    .streamlit-expanderContent {
        background-color: white;
        border-radius: 0 0 8px 8px;
        padding: 1rem;
        border: 1px solid #E5E7EB;
        border-top: none;
    }
    
    /* PLOTLY CHARTS - FOND BLANC */
    .js-plotly-plot .plotly, 
    .plotly, 
    .js-plotly-plot .svg-container {
        background-color: white !important;
    }
    
    .js-plotly-plot .bg {
        fill: white !important;
    }
    
    /* Widget labels bien visibles */
    .stSelectbox label, .stMultiselect label, .stCheckbox label, .stSlider label {
        color: #1E3A8A !important;
        font-weight: 600 !important;
    }
    
    /* Cacher les éléments vides */
    .empty-box {
        display: none !important;
    }
    
    /* Assurer que tout le texte est visible */
    .stText, .stMarkdown p, .stMarkdown div {
        color: #374151 !important;
    }
    </style>
""", unsafe_allow_html=True)

THEME_COLOR = '#1E90FF'

try:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM events", conn)
    conn.close()
except Exception as e:
    st.error(f"Erreur de base de données : {e}. Veuillez vérifier que les données sont disponibles.")
    st.stop()

# Nettoyage et préparation des données
df['arrondissement'] = df['address_zipcode'].str.extract(r'(\d{2})$').astype(float, errors='ignore')
df['date_start'] = pd.to_datetime(df['date_start'], errors='coerce', utc=True)
df['category'] = df.apply(lambda row: row['tags'].split(',')[0] if isinstance(row['tags'], str) and row['tags'] and row['tags'] != 'Unknown' else (row['price_type'] if pd.notna(row['price_type']) else 'Other'), axis=1)

df_viz = df.dropna(subset=['date_start', 'latitude', 'longitude']).copy()
df_viz = df_viz[df_viz['arrondissement'].between(1, 20)]  # Filtrer pour Paris

# catégories
CATEGORY_KEYWORDS = {
    'Culturel': ['exposition', 'concert', 'théâtre', 'theatre', 'musée', 'musee', 'spectacle', 'festival', 'cinema', 'projection', 'opéra', 'opera', 'danse', 'vernissage', 'lecture', 'expo', 'art'],
    'Sportif': ['match', 'tournoi', 'course', 'marathon', 'compétition', 'competition', 'sport', 'randonnée', 'randonnee', 'yoga', 'football', 'basket', 'tennis', 'gym'],
    'Famille': ['atelier', 'famille', 'enfant', 'jeunesse', 'kids', 'conte', 'animation', 'atelier enfant'],
}

def infer_category_from_description(text: str):
    if not isinstance(text, str) or not text.strip():
        return 'Autre', []
    t = text.lower()
    best_cat = 'Autre'
    best_matches = []
    best_count = 0
    for cat, keywords in CATEGORY_KEYWORDS.items():
        matches = [kw for kw in keywords if kw in t]
        if len(matches) > best_count:
            best_count = len(matches)
            best_matches = matches
            best_cat = cat
    return best_cat, best_matches

df_viz[['inferred_category', 'keywords_found']] = df_viz['description'].fillna('').apply(lambda s: pd.Series(infer_category_from_description(s)))

# SIDEBAR 
with st.sidebar:
    st.markdown("<h1 style='color: white; text-align: center;'>🎛️ Filtres</h1>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Événements totaux", len(df_viz), help="Nombre total d'événements dans la base de données")
    with col2:
        st.metric("Catégories", df_viz['inferred_category'].nunique(), help="Nombre de catégories différentes")
    
    st.markdown("---")
    
    # Filters
    st.markdown("**Filtres principaux**")
    show_conditions = st.checkbox("🎫 Gratuit sous condition uniquement", key="show_conditions")
    
    filters = st.multiselect(
        "💰 Type de Tarif/Accès",
        options=list(set(df_viz['price_type'].dropna().unique().tolist() + df_viz['access_type'].dropna().unique().tolist())),
        help="Sélectionnez plusieurs options pour filtrer les événements.",
        key="filters"
    )
    
    st.markdown("---")
    st.markdown("**Filtres avancés**")
    
    all_cats = sorted(df_viz['inferred_category'].fillna('Autre').unique().tolist())
    sel_cats = st.multiselect(
        "📂 Catégories à afficher", 
        options=all_cats, 
        default=all_cats, 
        key='sel_cats',
        help="Choisissez les catégories à inclure dans l'analyse"
    )
    
    map_style = st.selectbox(
        '🗺️ Style de carte', 
        options=['open-street-map', 'carto-positron', 'stamen-terrain'], 
        index=0, 
        key='map_style',
        help="Choisissez le style de fond de carte"
    )

# MAIN CONTENT

# Header
st.title("🎭 Paris Events Explorer")
st.markdown("""
**Explorez les événements culturels de Paris** avec des visualisations interactives et un tableau détaillé.  
Utilisez la barre latérale pour filtrer par type de tarif ou d'accès, et découvrez les détails dans les sections ci-dessous.
""")

# Reset button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🗑️ Réinitialiser tous les filtres", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# Filtrage des données
if show_conditions:
    df_filtered = df_viz[df_viz['price_type'] == 'gratuit sous condition']
    if df_filtered.empty:
        st.warning("Aucun événement 'gratuit sous condition' trouvé dans les données.")
    else:
        st.success(f"🎫 **{len(df_filtered)} événements gratuits sous condition trouvés**")
elif filters:
    df_filtered = df_viz[df_viz['price_type'].isin(filters) | df_viz['access_type'].isin(filters)]
    if df_filtered.empty:
        st.warning("Aucun événement ne correspond aux filtres sélectionnés.")
    else:
        st.success(f"✅ **{len(df_filtered)} événements correspondent aux filtres**")
else:
    df_filtered = df_viz
    st.info(f"📊 **Affichage de tous les {len(df_filtered)} événements disponibles**")

# Metrics Row
st.markdown("<div class='main-container'>", unsafe_allow_html=True)
st.header("📊 Vue d'ensemble des événements")

metric_cols = st.columns(4)
with metric_cols[0]:
    st.metric("Événements filtrés", len(df_filtered), help="Nombre d'événements après application des filtres")
with metric_cols[1]:
    min_date = df_filtered['date_start'].min().strftime('%d/%m/%Y') if not df_filtered.empty else 'N/A'
    st.metric("Date de début", min_date, help="Date du premier événement")
with metric_cols[2]:
    st.metric("Arrondissements", df_filtered['arrondissement'].nunique() if not df_filtered.empty else 0, help="Nombre d'arrondissements concernés")
with metric_cols[3]:
    st.metric("Types d'accès", df_filtered['access_type'].nunique() if not df_filtered.empty else 0, help="Diversité des types d'accès")
st.markdown("</div>", unsafe_allow_html=True)

# styliser les graphiques Plotly
def style_plotly_white(fig):
    """Applique un fond blanc et des couleurs visibles aux graphiques Plotly"""
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#1E3A8A', size=12),
        xaxis=dict(gridcolor='#E5E7EB', linecolor='#E5E7EB'),
        yaxis=dict(gridcolor='#E5E7EB', linecolor='#E5E7EB'),
        legend=dict(
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='#E5E7EB',
            borderwidth=1
        )
    )
    return fig

# Visualisations principales
st.markdown("<div class='main-container'>", unsafe_allow_html=True)
st.header("📍 Carte et répartition géographique")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📈 Événements par arrondissement")
    if df_viz['arrondissement'].notna().sum() > 0 and df_viz['price_type'].notna().sum() > 0:
        bar_data = df_viz.groupby(['price_type', 'arrondissement']).size().reset_index(name='count')
        fig1 = px.bar(
            bar_data,
            x='arrondissement',
            y='count',
            color='price_type',
            title='',
            barmode='stack',
            labels={'arrondissement': 'Arrondissement', 'count': "Nombre d'événements"},
            height=400,
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig1 = style_plotly_white(fig1)
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.error("Données insuffisantes pour générer le graphique")

with col2:
    st.subheader("🗺️ Carte des événements")
    if len(df_filtered) > 0 and df_filtered['access_type'].notna().sum() > 0:
        scatter_map_fn = getattr(px, 'scatter_map', getattr(px, 'scatter_mapbox', None))
        if scatter_map_fn:
            fig2 = scatter_map_fn(
                df_filtered,
                lat='latitude',
                lon='longitude',
                color='access_type',
                hover_data={'title': True, 'address_name': True, 'price_type': True},
                title='',
                height=400,
                zoom=11,
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            if hasattr(fig2, 'update_layout'):
                fig2.update_layout(
                    mapbox_style=st.session_state.get('map_style', 'open-street-map'),
                    mapbox_center={"lat": 48.8566, "lon": 2.3522},
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    showlegend=True,
                    legend=dict(
                        title="Type d'accès",
                        bgcolor='rgba(255,255,255,0.9)',
                        bordercolor='#E5E7EB',
                        borderwidth=1
                    )
                )
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Aucune donnée à afficher sur la carte avec les filtres actuels")
st.markdown("</div>", unsafe_allow_html=True)

#Analyse par catégorie
st.markdown("<div class='main-container'>", unsafe_allow_html=True)
st.header("🔍 Analyse détaillée par catégorie")

categories = [c for c in df_viz['inferred_category'].fillna('Autre').unique().tolist() if c in (st.session_state.get('sel_cats') or [])]

if not categories:
    st.warning("⚠️ **Aucune catégorie sélectionnée. Veuillez en sélectionner dans la barre latérale.**")
else:
    tabs = st.tabs([f"📌 {cat}" for cat in categories])
    
    for tab, cat in zip(tabs, categories):
        with tab:
            cat_df = df_viz[df_viz['inferred_category'] == cat].copy()
            
            if cat_df.empty:
                st.info(f"ℹ️ **Aucun événement trouvé pour la catégorie {cat}.**")
                continue
            
            # Metrics
            st.subheader(f"📊 Statistiques pour la catégorie {cat}")
            cat_cols = st.columns(4)
            with cat_cols[0]:
                st.metric(f"Total {cat}", len(cat_df))
            with cat_cols[1]:
                gratuit_count = len(cat_df[cat_df['price_type'] == 'gratuit'])
                st.metric("Événements gratuits", gratuit_count)
            with cat_cols[2]:
                payant_count = len(cat_df[cat_df['price_type'] == 'payant'])
                st.metric("Événements payants", payant_count)
            with cat_cols[3]:
                st.metric("Arrondissements", cat_df['arrondissement'].nunique())
            
            # Map
            st.subheader(f"📍 Localisation et calendrier - {cat}")
            col_map, col_tl = st.columns([1, 1])
            
            with col_map:
                st.markdown("**🗺️ Carte géographique**")
                scatter_fn = getattr(px, 'scatter_map', getattr(px, 'scatter_mapbox', None))
                if scatter_fn:
                    fig_map = scatter_fn(
                        cat_df,
                        lat='latitude',
                        lon='longitude',
                        color='price_type',
                        hover_name='title',
                        hover_data={'address_name': True, 'date_start': True},
                        height=400
                    )
                    if hasattr(fig_map, 'update_layout'):
                        fig_map.update_layout(
                            mapbox_style='open-street-map',
                            mapbox_center={"lat": 48.8566, "lon": 2.3522},
                            plot_bgcolor='white',
                            paper_bgcolor='white',
                            legend=dict(
                                bgcolor='rgba(255,255,255,0.9)',
                                bordercolor='#E5E7EB',
                                borderwidth=1
                            )
                        )
                    st.plotly_chart(fig_map, use_container_width=True)
            
            with col_tl:
                st.markdown("**📅 Calendrier des événements**")
                timeline_df = cat_df.sort_values('date_start')
                if not timeline_df.empty:
                    fig_tl = px.scatter(
                        timeline_df,
                        x='date_start',
                        y='title',
                        color='price_type',
                        hover_data={'address_name': True, 'date_start': True},
                        height=400
                    )
                    fig_tl = style_plotly_white(fig_tl)
                    fig_tl.update_layout(
                        xaxis_title="Date de l'événement",
                        yaxis_title="Nom de l'événement",
                        showlegend=True
                    )
                    st.plotly_chart(fig_tl, use_container_width=True)
            
            # show upcoming events
            with st.expander(f"📋 **Liste complète des événements {cat} ({len(cat_df)})**", expanded=False):
                st.markdown(f"**📝 Liste des événements {cat} :**")
                tmp = cat_df.copy()
                tmp['date_start'] = pd.to_datetime(tmp['date_start'], errors='coerce', utc=True)
                now = pd.Timestamp.now(tz='UTC')
                upcoming = tmp[tmp['date_start'] >= now].sort_values('date_start')
                if not upcoming.empty:
                    st.markdown(f"**Événements à venir ({len(upcoming)}) :**")
                    to_show = upcoming
                else:
                    st.markdown("**Aucun événement à venir — 10 événements les plus récents :**")
                    to_show = tmp.sort_values('date_start', ascending=False).head(10)

                for idx, row in to_show.iterrows():
                    left, right = st.columns([3, 1])
                    with left:
                        st.write(f"**{row.get('title', 'Sans titre')}**")
                        st.write(f"📍 {row.get('address_name', 'Adresse non précisée')}")
                        if pd.notna(row.get('description')):
                            # Remove HTML tags
                            desc = str(row.get('description'))
                            # strip common HTML tags
                            clean = re.sub(r'<[^>]+>', ' ', desc)
                            # unescape HTML entities if any (basic replacements)
                            clean = clean.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
                            # collapse whitespace
                            clean = re.sub(r'\s+', ' ', clean).strip()
                            excerpt = (clean[:300] + '...') if len(clean) > 300 else clean
                            st.caption(excerpt)
                    with right:
                        ds = row['date_start']
                        st.write(f"📅 {ds.strftime('%d/%m/%Y') if pd.notna(ds) else 'Date non précisée'}")
                        st.write(f"💰 {row.get('price_type', 'Non spécifié')}")
                    st.markdown("---")
st.markdown("</div>", unsafe_allow_html=True)

#Statistiques détaillées
st.markdown("<div class='main-container'>", unsafe_allow_html=True)
st.header("📈 Statistiques et analyses avancées")

col1, col2 = st.columns(2)

with col1:
    with st.expander("📊 **Répartition par type d'accès**", expanded=True):
        st.markdown("**Répartition des événements par type d'accès :**")
        if df_viz['access_type'].notna().sum() > 0:
            pie_data = df_viz['access_type'].value_counts().reset_index()
            fig_pie = px.pie(
                pie_data,
                names='access_type',
                values='count',
                height=350,
                title='',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_pie = style_plotly_white(fig_pie)
            fig_pie.update_layout(showlegend=True)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("ℹ️ Aucune donnée de type d'accès disponible")

with col2:
    with st.expander("📈 **Tendances mensuelles des événements**", expanded=True):
        st.markdown("**Évolution du nombre d'événements par mois :**")
        df_viz['month'] = df_viz['date_start'].dt.strftime('%Y-%m')
        monthly = df_viz.groupby('month').size().reset_index(name='count')
        if not monthly.empty:
            fig_line = px.line(
                monthly,
                x='month',
                y='count',
                markers=True,
                height=350,
                title='',
                line_shape='spline'
            )
            fig_line = style_plotly_white(fig_line)
            fig_line.update_layout(
                xaxis_title="Mois",
                yaxis_title="Nombre d'événements"
            )
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("ℹ️ Aucune donnée temporelle disponible")
st.markdown("</div>", unsafe_allow_html=True)

