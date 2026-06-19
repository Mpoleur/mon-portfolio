import os
import streamlit as st
import pandas as pd
from databricks import sql

st.title("📊 Mon Portefeuille en Direct")

@st.cache_resource
def get_databricks_connection():
    # Databricks Apps injecte automatiquement ces variables grâce à ta ressource liée !
    return sql.connect(
        server_hostname="dbc-bfa6bdfc-bac2.cloud.databricks.com", 
        http_path="/sql/1.0/warehouses/dcae3895e63dfcf2",
        access_token=os.environ.get("dapi0036e9500bc2cbc1ff6ad590fc724d25") # <--- L'astuce est là !
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
