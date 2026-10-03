import os
import streamlit as st
import pandas as pd
import yfinance as yf
from databricks import sql
from databricks.sdk.core import Config, oauth_service_principal

#############################
# Get data frame from csv
#############################

@st.cache_data
#Get dataframe method (combination of the 2 below might be improved by fuzing them)
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

#get connection to databricks method
def get_connection():
    host = os.environ.get("DATABRICKS_HOST")
    client_id = os.environ.get("DATABRICKS_CLIENT_ID")
    client_secret = os.environ.get("DATABRICKS_CLIENT_SECRET")
    
    config = Config(
        host=f"https://{host}",
        client_id=client_id,
        client_secret=client_secret,
    )
    return sql.connect(
        server_hostname=host,
        http_path="/sql/1.0/warehouses/984a09b701253a55",
        credentials_provider=lambda: oauth_service_principal(config),
    )

#SQL execution method
def sql_exe(query, fetch=False):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            if fetch:
                return cursor.fetchall_arrow().to_pandas()
    except Exception as e:
        if "Invalid SessionHandle" in str(e) or "closed" in str(e):
            st.cache_resource.clear()
            connection = get_connection()
            with connection.cursor() as cursor:
                cursor.execute(query)
                if fetch:
                    return cursor.fetchall_arrow().to_pandas()
        else:
            raise

#############################
# Page config
#############################

st.set_page_config(
    page_title="Portfolio X",
    page_icon="📊",
    layout="wide",
)
#############################
# Title section
#############################

st.title("📊 My amazing portfolio")
select_trx = "select * from workspace.default.portfolio_transaction"
df_portfolio = sql_exe(select_trx, fetch=True)
st.dataframe(df_portfolio)


#############################
# Add transaction expander
#############################

with st.expander("New transaction", expanded=False):
    select_trx = "select * from workspace.default.portfolio_transaction"
    df_portfolio = sql_exe(select_trx, fetch=True)
    # Widgets conditionnels EN DEHORS du form
    in_orig_currency = st.segmented_control("Devise", options=["EUR","USD","NOK","CAD"], selection_mode="single", default="EUR")
    
    in_change = None
    in_price_currency = None
    in_price_eur = 0.0

    if in_orig_currency != "EUR":
        in_change = st.number_input("Taux de change", min_value=0.000001)

    # Le form sans widget conditionnel
    with st.form("new_transaction", enter_to_submit=False, clear_on_submit=True):
        in_ticker = st.selectbox("Ticker", options=(df_portfolio["ticker"].unique()), accept_new_options=True)
        in_date = st.date_input("Date", format="YYYY/MM/DD")
        in_year = in_date.year
        in_transtype = st.segmented_control("Type", options=["Buy","Sell","Dividend","Option"], selection_mode="single", default="Buy")
        in_number = st.number_input("Shares", min_value=1, step=1)
        in_price = st.number_input("Prix unitaire", min_value=0.01)
        in_total = st.number_input("Total", min_value=0.01)

        submitted = st.form_submit_button("Add", icon=":material/add:")

    # Logique après submit, en dehors du form
    if submitted:
        if in_orig_currency == "EUR":
            in_price_eur = in_price
        else:
            in_price_currency = in_price
            if in_change and in_change > 0:
                in_price_eur = in_price / in_change

        in_total_cost = (in_price_eur * in_number) - in_total
        in_id = "D"

        in_query = f"""
            INSERT INTO workspace.default.portfolio_transaction
            (Transaction_ID,
            Transaction_Date,
            Transaction_Year,
            Title,
            Transaction_type,
            Shares,
            Price_EUR,
            Change,
            Price_Currency,
            Original_Currency,
            Transaction_cost,
            Total_Transaction)
            VALUES (
                {in_id},
                {in_date},
                {in_year},
                {in_ticker},
                {in_transtype},
                {in_number},
                {in_price_eur},
                {in_change if in_change is not None else 'NULL'},
                {f"'{in_price_currency}'" if in_price_currency is not None else 'NULL'},
                {in_orig_currency},
                {in_total_cost},
                {in_total}
            )
        """
        submitted = st.form_submit_button("Add",icon=":material/add:")

    if submitted:
        st.write(in_query)

