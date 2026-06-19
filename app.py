import os
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

st.title("📊 Mon Portefeuille en Direct")

@st.cache_resource
def get_dataframe():
    host = os.environ.get("DB_HOST")
    path = os.environ.get("DB_PATH")
    token = os.environ.get("DB_TOKEN")
    
    connection_url = f"databricks://token:{token}@{host}?http_path={path}"
    engine = create_engine(connection_url)
    
    # Avec SQLAlchemy, pandas lit directement sans cursor ni fetchall !
    query = "SELECT * FROM workspace.default.portfolio_view"
    return pd.read_sql(query, engine)

try:
    df_portfolio = get_dataframe()
    st.write("Voici ton portefeuille en direct de Databricks :")
    st.dataframe(df_portfolio)

except Exception as e:
    st.error(f"Erreur de connexion à la base de données : {e}")