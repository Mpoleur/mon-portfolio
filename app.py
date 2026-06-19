import os
import streamlit as st
import pandas as pd
from databricks import sql

st.title("📊 Mon Portefeuille en Direct")

@st.cache_resource
def get_databricks_connection():
    # On force l'authentification par Token (PAT) pour éviter l'erreur OAuth 400
    return sql.connect(
        server_hostname="dbc-bfa6bdfc-bac2.cloud.databricks.com", 
        http_path="/sql/1.0/warehouses/dcae3895e63dfcf2",
        auth_type="pat", 
        access_token=os.environ.get("MON_TOKEN_SECRET") # Récupéré de l'Étape A
    )

try:
    input_table = "workspace.default.portfolio_view"
    
    connection = get_databricks_connection()
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {input_table}")
        result = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
    
    df_portfolio = pd.DataFrame(result, columns=column_names)
    
    st.write("Voici ton portefeuille en direct de Databricks :")
    st.dataframe(df_portfolio)

except Exception as e:
    st.error(f"Erreur lors de la récupération des données : {e}")