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

#############################
# Page config
#############################

st.set_page_config(
    page_title="Portfolio",
    page_icon="📊",
    layout="wide",
)
#############################
# Title section
#############################

st.title("📊 Mon Portefeuille en Direct")

#############################
# Portfolio Dataframe with pills filtering
#############################

select1 = "select * from workspace.default.portfolio_view"
df_portfolio = get_dataframe(select1)

with st.expander("Portofolio summary",expanded=False):
    st.write("Voici ton portefeuille en direct de Databricks :")
    status = df_portfolio["status"].unique()
    # Pills filtering
    selected_status = st.pills(
        "Sélection de status: ", status, default="Open", selection_mode="multi"
    )

    df_filtered_port=df_portfolio[df_portfolio["status"].isin(selected_status)]
    # Display dataframe
    st.dataframe(df_filtered_port)

# call input
select2 = "select * from workspace.default.portfolio"
df_raw = get_dataframe(select2)

# slection de la date via des bulles
YEARS = df_raw["transaction_year"].unique()
selected_years = st.pills(
    "Years to compare", YEARS, default=YEARS.max(), selection_mode="multi"
)
df_filtered_raw = df_raw[df_raw["transaction_year"].isin(selected_years)]

st.write("Voici tes raw data :")
buy = df_filtered_raw[df_filtered_raw["transaction_type"]=="Buy"]["total"].sum().round(2)
dividend = df_filtered_raw[df_filtered_raw["transaction_type"]=="Dividend"]["total"].sum().round(2)
option = df_filtered_raw[df_filtered_raw["transaction_type"]=="Option"]["total"].sum().round(2)
sell = df_filtered_raw[df_filtered_raw["transaction_type"]=="Sell"]["total"].sum().round(2)

# affichage en tableau
row1 = st.columns(2,gap="xsmall")
with row1[0]:
    st.write("Option : ", option, "€")
with row1[1]:
    st.write("Dividend : ", dividend, "€")

row2 = st.columns(2, gap="xsmall")
with row2[0]:
    st.write("Buy : ", buy, "€")
with row2[1]:
    st.write("Sell : ", sell, "€")

# dropdown specific

dropdown = st.selectbox(
    "Details on one ticker?",
    (df_portfolio[df_portfolio["status"]=="Open"]["ticker"].unique()),
)


# On interroge Yahoo Finance pour ce ticker
stat_ticker = yf.Ticker(dropdown)
# get info from yahoo for selected ticker
current_price = stat_ticker.info.get('currentPrice')
ycurrency = stat_ticker.info.get('currency')
yname = stat_ticker.info.get('shortName')

#Daily market price USD
yUSD = stat_ticker = yf.Ticker("USDEUR=X")
eUSD = yUSD.info.get('regularMarketPrice')

#Daily market price NOK
yNOK = stat_ticker = yf.Ticker("NOKEUR=X")
eNOK = yNOK.info.get('regularMarketPrice')

#conversion USD, NOK to EUR
if ycurrency == "USD":
    ecurrent_price = round(current_price * eUSD,2)
    st.write("You selected:", dropdown ," - ", yname , " its current price is : " ,round(current_price * eUSD,2), ' in EUR - ',current_price, " in ", ycurrency)
elif ycurrency == "NOK":
    ecurrent_price = round(current_price * eUSD,2)
    st.write("You selected:", dropdown ," - ", yname , " its current price is : " ,round(current_price * eNOK,2), ' in EUR - ',current_price, " in ", ycurrency)
elif ycurrency == "EUR":
    ecurrent_price = current_price
    st.write("You selected:", dropdown ," - ", yname , " its current price is : " ,current_price, " in ", ycurrency)
else:
    current_price = 0
    ecurrent_price = 0

# compute spcific variable

doption = df_portfolio[df_portfolio["ticker"]==dropdown]["option"].sum().round(2)
ddividend = df_portfolio[df_portfolio["ticker"]==dropdown]["dividend"].sum().round(2)
dsell = df_portfolio[df_portfolio["ticker"]==dropdown]["sell"].sum().round(2)
dbuy = df_portfolio[df_portfolio["ticker"]==dropdown]["buy"].sum().round(2)
dremaining = df_portfolio[df_portfolio["ticker"]==dropdown]["remaining"].sum().round(2)
drealized = df_portfolio[df_portfolio["ticker"]==dropdown]["realized"].sum().round(2)
dbreakpoint = df_portfolio[df_portfolio["ticker"]==dropdown]["break_price"].sum().round(2)


# affichage en tableau
row3 = st.columns(3,gap="xsmall")
with row3[0]:
    st.write("Option : ", doption, "€")
with row3[1]:
    st.write("Dividend : ", ddividend, "€")
with row3[2]:
    st.write("Remaining : ", dremaining)

row4 = st.columns(3,gap="xsmall")
with row4[0]:
    st.write("Realized : ", drealized, "€")
with row4[1]:
    st.write("Bougth : ", dbuy, "€")
with row4[2]:
    st.write("Sold : ", dsell, "€")

row5 = st.columns(3, gap = "xsmall")
with row5[0]:
    st.write("Unrealized : ", round(dremaining * ecurrent_price,2) ," €")
with row5[1]:
    st.write("Break price : ", dbreakpoint, " €")
with row5[2]:
    if ycurrency == "USD":
        st.write("Break price in ",ycurrency, round(dbreakpoint/eUSD,2))
    elif ycurrency =="NOK":
        st.write("Break price in ",ycurrency, round(dbreakpoint/eNOK,2))
    else:
        pass

#############################
# Add Data section
#############################

with st.expander("New transaction", expanded=False):
    
    # Widgets conditionnels EN DEHORS du form
    in_orig_currency = st.segmented_control("Devise", options=["EUR","USD","NOK","CAD"], selection_mode="single", default="EUR")
    
    in_change = None
    in_price_currency = None
    in_price_eur = 0.0

    if in_orig_currency != "EUR":
        in_change = st.number_input("Taux de change", min_value=0.000001)

    # Le form sans widget conditionnel
    with st.form("new_transaction", enter_to_submit=False, clear_on_submit=True):
        in_ticker = st.selectbox("Ticker", options=(df_portfolio[df_portfolio["status"]=="Open"]["ticker"].unique()), accept_new_options=True)
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
            INSERT INTO workspace.default.portfolio_view 
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

