import streamlit as st
import pandas as pd

st.title("📊 Mon Portefeuille en Direct")

# 1. On utilise la connexion native de Databricks Apps (pas besoin d'identifiants !)
conn = st.connection("databricks")

# 2. Au lieu de spark.table, on fait une vraie requête SQL sur ta vue
input_table = "workspace.default.portfolio_view"
df_portfolio = conn.query(f"SELECT * FROM {input_table}")

# 3. On affiche le résultat
st.write("Voici ton portefeuille en direct de Databricks :")
st.dataframe(df_portfolio)