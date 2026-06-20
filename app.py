import os
import streamlit as st
import pandas as pd
from databricks import sql
from databricks.sdk.core import Config, oauth_service_principal

# routine pour chercher une table avec connection à la db
@st.cache_resource
def get_dataframe(selection):
    host = os.environ.get("DATABRICKS_HOST")
    http_path = "/sql/1.0/warehouses/984a09b701253a55"
    client_id = os.environ.get("DATABRICKS_CLIENT_ID")
    client_secret = os.environ.get("DATABRICKS_CLIENT_SECRET")

    config = Config(
        host=f"https://{host}",
        client_id=client_id,
        client_secret=client_secret,
    )

    with sql.connect(
        server_hostname=host,
        http_path=http_path,
        credentials_provider=lambda: oauth_service_principal(config),
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(selection)
            df = cursor.fetchall_arrow().to_pandas()
    return df

#set up de la page streamlit
st.set_page_config(
    # Title and icon for the browser's tab bar:
    page_title="Portfolio",
    page_icon="📊",
    # Make the content take up the width of the page:
    layout="wide",
)
st.title("📊 Mon Portefeuille en Direct")

# call portfolio view
select1 = "select * from workspace.default.portfolio_view"
df_portfolio = get_dataframe(select1)
st.write("Voici ton portefeuille en direct de Databricks :")
st.dataframe(df_portfolio)

# call input

select2 = "select * from workspace.default.portfolio"
df_raw = get_dataframe(select2)
st.write("Voici tes raw data :")
st.dataframe(df_raw)