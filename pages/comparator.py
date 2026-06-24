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
    is_min = row["unit_price"] == df_display["unit_price"].min()
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
df_compute.loc[df_compute["metric"] == "u", "unit_price"] = round(df_compute["price"]/df_compute["quantity"],2)
df_compute.loc[df_compute["metric"] == "g", "unit_price"] = round(df_compute["price"]/df_compute["quantity"]*100,2)
df_compute.loc[df_compute["metric"] == "Kg", "unit_price"] = round(df_compute["price"]/df_compute["quantity"]/10,2)
df_compute.loc[df_compute["metric"] == "l", "unit_price"] = round(df_compute["price"]/df_compute["quantity"]/10,2)
df_compute.loc[df_compute["metric"] == "u", "measure"] = "/ unit"
df_compute.loc[df_compute["metric"] == "g", "measure"] = "/ 100g"
df_compute.loc[df_compute["metric"] == "Kg", "measure"] = "/ 100g"
df_compute.loc[df_compute["metric"] == "l", "measure"] = "/ liter"


# select one item
dropdown = st.selectbox(
    "Sélectionne un produit",
    (df_compute["item"].unique()),
)

df_display = df_compute[["item","store","unit_price","measure"]][df_compute["item"]==dropdown]

#display intput selected by dropdown
st.dataframe(df_display.style.apply(highlight_min_row, axis=1)
            .format({"unit_price": "{:.2f}"})
            )



with st.expander("Ajouter un article"):
    with st.form("Add new price",enter_to_submit=False,clear_on_submit=True):
        item = st.text_input("Nom de l'article: ")
        store = st.text_input("Magasin: ")
        price = round(st.number_input("Prix: ", min_value=0.01, step=0.01),2)
        quantity = round(st.number_input("Quantité: ", min_value=0.00, step=1.00),2)
        metric = st.selectbox("Métric: ",["Kg","g","u","l"])
        submitted = st.form_submit_button("➕Ajouter l'article")

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
                            "INSERT INTO workspace.default.comparator_input (item, store, price, quantity, metric) VALUES (%(item)s, %(store)s, %(price)s, %(quantity)s, %(metric)s)",
                            {"item": item, "store": store, "price": price, "quantity": quantity, "metric": metric}
                        )
                st.success(f"Prix de {price}  ajouté pour {item} chez {store} !")
                st.cache_data.clear()
                st.badge("Success", icon=":material/check:", color="green")
                st.cache_data.clear()
                st.rerun()

with st.expander("Voir la DB"):
    st.dataframe(df_input)
