import os
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

st.title("📊 Mon Portefeuille en Directm")

@st.cache_resource
def get_dataframe():
    # Adresses exactes tirées de ton écran de variables
    host = "dbc-dfa4bdfc-bac2.cloud.databricks.com"
    path = "/sql/1.0/warehouses/984a09b701253a55"
    
    # On utilise la variable système native générée automatiquement par Databricks
    # Pas besoin de créer de variable 'DB_TOKEN', l'app possède déjà celle-ci !
    token = os.environ.get("DATABRICKS_CLIENT_TOKEN")
    
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