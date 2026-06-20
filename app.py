import os
import streamlit as st
import pandas as pd
from databricks import sql

st.title("📊 Mon Portefeuille en Direct")

@st.cache_resource
def get_dataframe():
    host = os.environ.get("DATABRICKS_HOST")
    http_path = "/sql/1.0/warehouses/984a09b701253a55"
    client_id = os.environ.get("DATABRICKS_CLIENT_ID")
    client_secret = os.environ.get("DATABRICKS_CLIENT_SECRET")

    with sql.connect(
        server_hostname=host,
        http_path=http_path,
        auth_type="oauth-m2m",
        oauth_client_id=client_id,
        oauth_client_secret=client_secret,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM workspace.default.portfolio_view")
            df = cursor.fetchall_arrow().to_pandas()
    return df

try:
    df_portfolio = get_dataframe()
    st.write("Voici ton portefeuille en direct de Databricks :")
    st.dataframe(df_portfolio)

except Exception as e:
    st.error(f"Erreur de connexion à la base de données : {e}")