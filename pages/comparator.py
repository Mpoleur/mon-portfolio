import os
import streamlit as st
import pandas as pd
from databricks import sql
from databricks.sdk.core import Config, oauth_service_principal

# routine pour chercher une table avec connection à la db
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

#function highlight row
def highlight_min_row(row):
    is_min = row["unit_price"] == df_select["unit_price"].min()
    return ['background-color: green' if is_min else '' for _ in row]

#set up de la page streamlit
st.set_page_config(
    # Title and icon for the browser's tab bar:
    page_title="Price comparator",
    page_icon="🛒",
)

st.title("🛒 Comparateur de prix - Taïwan édition")


# call comparator_inpu view
select1 = "select * from workspace.default.comparator_input"
df_input = get_dataframe(select1)

# display and compute dataframe based on input
df_compute = df_input.copy()
df_compute.loc[df_compute["metrics"] == "u", "unit_price"] = round(df_compute["price"]/df_compute["quantity"],2)
df_compute.loc[df_compute["metrics"] == "g", "unit_price"] = round(df_compute["price"]/df_compute["quantity"]*100,2)
df_compute.loc[df_compute["metrics"] == "Kg", "unit_price"] = round(df_compute["price"]/df_compute["quantity"]/10,2)
df_compute.loc[df_compute["metrics"] == "l", "unit_price"] = round(df_compute["price"]/df_compute["quantity"]/10,2)
df_compute.loc[df_compute["metrics"] == "u", "measure"] = "/ unit"
df_compute.loc[df_compute["metrics"] == "g", "measure"] = "/ 100g"
df_compute.loc[df_compute["metrics"] == "Kg", "measure"] = "/ 100g"
df_compute.loc[df_compute["metrics"] == "l", "measure"] = "/ liter"

# creation and selection of df_display
df_display = df_compute[["item","store","unit_price","measure"]].copy()

# select one item
dropdown = st.selectbox(
    "Details on one ticker?",
    (df_display["item"].unique()),
)
df_select = df_display[df_display["item"]==dropdown]

#display intput selected by dropdown
st.dataframe(df_select.style.apply(highlight_min_row, axis=1))



with st.expander("Add data"):
    with st.form("Add new price",enter_to_submit=False,clear_on_submit=True):
        item = st.text_input("Product name: ")
        store = st.text_input("Store: ")
        price = round(st.number_input("Price: ", min_value=0.01, step=0.01),2)
        quantity = round(st.number_input("Quantity: ", min_value=0.00, step=1.00),2)
        metrics = st.selectbox("Metrics: ",["Kg","g","u","l"])
        submitted = st.form_submit_button("➕Add data")

        if submitted:
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
                    cursor.execute(
                            "INSERT INTO workspace.default.comparator_input (item, store, price, quantity, metrics) VALUES (%(item)s, %(store)s, %(price)s, %(quantity)s, %(metrics)s)",
                            {"item": item, "store": store, "price": price, "quantity": quantity, "metrics": metrics}
                        )
                st.success(f"Prix de {price}  ajouté pour {item} chez {store} !")
                st.cache_data.clear()
                st.badge("Success", icon=":material/check:", color="green")
                st.cache_data.clear()
                st.rerun()

with st.expander("See data"):
    st.dataframe(df_input)
