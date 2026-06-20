import os
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

st.title("📊 Mon Portefeuille en Direct")

@st.cache_resource
def get_dataframe():
    # On récupère les variables exactes visibles sur ton écran (image_dba768.png)
    host = os.environ.get("DATABRICKS_HOST")
    
    # Construction automatique du HTTP Path avec l'ID du Workspace de ton écran
    workspace_id = os.environ.get("DATABRICKS_WORKSPACE_ID")
    path = f"/sql/1.0/warehouses/{workspace_id}" 
    
    # Le token secret que tu as mis dans l'onglet Settings de ton App
    token = os.environ.get("DATABRICKS_CLIENT_TOKEN")
    
    # Connexion propre via SQLAlchemy
    connection_url = f"databricks://token:{token}@{host}?http_path={path}"
    engine = create_engine(connection_url)
    
    query = text("SELECT * FROM workspace.default.portfolio_view")
    with engine.connect() as conn:
        result = conn.execute(query)
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df

try:
    df_portfolio = get_dataframe()
    st.write("Voici ton portefeuille en direct de Databricks :")
    st.dataframe(df_portfolio)

except Exception as e:
    st.error(f"Erreur de connexion à la base de données : {e}")