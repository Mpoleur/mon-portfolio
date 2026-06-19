import os
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

st.title("📊 Mon Portefeuille en Direct")

@st.cache_resource
def get_dataframe():
    # 1. On récupère les variables cachées de l'Étape 2
    host = os.environ.get("DB_HOST")
    path = os.environ.get("DB_PATH")
    token = os.environ.get("DB_TOKEN")
    
    # 2. On crée une URL de connexion universelle (SQLAlchemy)
    # Cette syntaxe force l'utilisation du Token (PAT) et ignore l'OAuth de Databricks
    connection_url = f"databricks://token:{token}@{host}?http_path={path}"
    
    # 3. On se connecte et on lit la table
    engine = create_engine(connection_url)
    query = "SELECT * FROM workspace.default.portfolio_view"
    
    return pd.read_sql(query, engine)

try:
    # Récupération et affichage direct
    df_portfolio = get_dataframe()
    st.write("Voici ton portefeuille en direct de Databricks :")
    st.dataframe(df_portfolio)

except Exception as e:
    st.error(f"Erreur de connexion à la base de données : {e}")