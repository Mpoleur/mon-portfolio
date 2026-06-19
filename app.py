import streamlit as st
import pandas as pd
from databricks import sql
import os

st.title("📊 Mon Portefeuille en Direct")

# On se connecte en utilisant EXACTEMENT le nom de la Resource key de Databricks
conn = st.connection("sql-warehouse")

try:
    input_table = "workspace.default.portfolio_view"
    
    # On lance la requête
    df_portfolio = conn.query(f"SELECT * FROM {input_table}")

    st.write("Voici ton portefeuille en direct de Databricks :")
    st.dataframe(df_portfolio)

except Exception as e:
    st.error(f"Erreur lors de la récupération des données : {e}")