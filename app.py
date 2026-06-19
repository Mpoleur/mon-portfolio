import streamlit as st
import pandas as pd
from databricks import sql
import os

st.title("📊 Mon Portefeuille en Direct")

# 1. Connexion automatique grâce aux variables d'environnement de Databricks Apps
@st.cache_resource
def get_databricks_connection():
    return sql.connect(
        server_hostname=os.environ.get("DATABRICKS_SERVER_HOSTNAME"),
        http_path=os.environ.get("DATABRICKS_HTTP_PATH"),
        access_token=os.environ.get("DATABRICKS_CLIENT_TOKEN") # Token temporaire généré par l'app
    )

try:
    # 2. Exécution de la requête SQL
    input_table = "workspace.default.portfolio_view"
    
    connection = get_databricks_connection()
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {input_table}")
        result = cursor.fetchall()
        # Récupération des noms de colonnes
        column_names = [desc[0] for desc in cursor.description]
    
    # 3. Transformation en DataFrame Pandas et affichage
    df_portfolio = pd.DataFrame(result, columns=column_names)
    
    st.write("Voici ton portefeuille en direct de Databricks :")
    st.dataframe(df_portfolio)

except Exception as e:
    st.error(f"Erreur lors de la récupération des données : {e}")
