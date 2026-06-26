import os
import streamlit as st
from dataclasses import dataclass, field
import uuid
import pandas as pd
import random 
from databricks import sql
from databricks.sdk.core import Config, oauth_service_principal
from st_clickable_images import clickable_images

# force non responsive action
st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        overflow-x: hidden !important;
        max-width: 100vw !important;
    }
    [data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
    }
    [data-testid="column"] {
        min-width: 0 !important;
        flex: 1 1 0 !important;
    }
</style>
""", unsafe_allow_html=True)

#set up de la page streamlit
st.set_page_config(
    # Title and icon for the browser's tab bar:
    page_title="Liste de courses",
    page_icon=":memo:",
)


@dataclass
class Todo:
    text: str
    is_done = False
    uid: uuid.UUID = field(default_factory=uuid.uuid4)


#if "todos" not in state:
#    state.todos = [
#        Todo(text="Buy milk"),
#        Todo(text="Wash dishes"),
#        Todo(text="Write a novel"),
#    ]

@st.cache_resource
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

def sql_exe(query, fetch=False):
    connection = get_connection()
    with connection.cursor() as cursor:
        cursor.execute(query)
        if fetch:
            return cursor.fetchall_arrow().to_pandas()

def remove_todo(item, store):
    query=f'Delete from workspace.default.grocery_list where store = "{store}" and item = "{item}"'
    sql_exe(query)
    st.cache_data.clear()

def add_todo(store,item,quantity):
    query=f'insert into workspace.default.grocery_list(store, item, quantity,crossed) values ("{store}","{item}",{quantity},False)'
    sql_exe(query)
    st.cache_data.clear()

def check_todo(item, store, val):
    if val == True:
        query=f'update workspace.default.grocery_list set crossed = False where store = "{store}" and item = "{item}"'
        sql_exe(query)
        st.cache_data.clear()
    else:
        query=f'update workspace.default.grocery_list set crossed = True where store = "{store}" and item = "{item}"'
        sql_exe(query)
        st.cache_data.clear()

def delete_all_checked(store):
    query=f'Delete from workspace.default.grocery_list where store = "{store}"'
    sql_exe(query)
    st.cache_data.clear()

def remove_freq(item):
    query=f'Delete from workspace.default.grocery_freq_buy where item = "{item}"'
    sql_exe(query)
    st.cache_data.clear()

def add_freq_buy(item):
    query=f'insert into workspace.default.grocery_freq_buy(item) values ("{item}")'
    sql_exe(query)
    st.cache_data.clear()

def create_list(mag):
    with st.expander(mag,expanded=True):
        store = mag
        with st.container(horizontal_alignment="center"):
            if mag == "Costco":
                img_url = image_Costco
            elif mag == "Coupang":
                img_url = image_coupang
            elif mag == "Ikea":
                img_url = image_ikea
            elif mag == "PXmart":
                img_url = image_PX
            else:
                img_url = image_other
            st.image(img_url, width=100)
            st.title(
                f"Liste {mag}",
                width="content",
                anchor=False,
            )

        with st.form(key=f"form_{mag}", border=False,enter_to_submit=False,clear_on_submit=True):
            with st.container(
                horizontal=True,
                vertical_alignment="bottom",
            ):
                item=st.selectbox(
                    "Article: ", 
                    options = sorted(df_input["item"].unique()), 
                    accept_new_options = True, 
                    label_visibility="collapsed", 
                    placeholder="Nouvel article",
                )

                quantity=st.number_input(
                    "Quantity",
                    label_visibility="collapsed",
                    placeholder="Quantité",
                    min_value=1, step=1
                )
                submit=st.form_submit_button(
                    "Add",
                    icon=":material/add:",
                )
            if submit:
                if item not in (df_list[df_list["store"]==store]["item"].unique()):
                    add_todo(store,item,quantity)
                    st.rerun()
                else:
                    st.warning("Cet article est déjà dans la liste", icon="⚠️")

        if store in stores:
            with st.container(gap=None, border=True):
                df_store = df_list[df_list["store"]==store]
                for i,row in df_store.iterrows():
                    with st.container(horizontal=True, vertical_alignment="center"):
#                        col_check, col_text, col_delete = st.columns([1, 6, 1],vertical_alignment="center")
                        item=row["item"]
                        check_og=row["crossed"]
                        story=row["store"]
                        quantity = row["quantity"]
                        col_check, col_rest = st.columns([1, 11], vertical_alignment="center")
                        with col_check:
                            st.checkbox(
                                label="",
                                value=check_og,
                                key=f"checkbox_{item}_{story}_{num}",
                                on_change=check_todo,
                                args=(item, story)
                            )
                        with col_rest:
                            sous_col_text, sous_col_delete = st.columns([10, 2], vertical_alignment="center")
                            with sous_col_text:
                                st.markdown(
                                    f"<div style='overflow:hidden; text-overflow:ellipsis; white-space:nowrap;'>{quantity} x {item}</div>",
                                    unsafe_allow_html=True
                                )
                            with sous_col_delete:
                                st.button(
                                    ":material/delete:",
                                    type="tertiary",
                                    on_click=remove_todo,
                                    args=(item, story),
                                    key=f"delbutton_{item}_{story}_{num}",
                                )

            with st.container(horizontal=True, horizontal_alignment="center"):
                story=df_list[df_list["store"]==store]["store"].unique()
                st.button(
                    ":small[Effacer la liste]",
                    icon=":material/delete_forever:",
                    type="tertiary",
                    on_click=delete_all_checked,
                    args=(story),
                    key=f"delbutton_{story}"
                )
        else:
            st.info("Pas d'article pour le moment :material/family_link:")    

#############################
#Variables
image_PX = "https://shoplineimg.com/5cc3db30527c4b0001a30cf0/5f8bc65696b102003bd6bf54/3860x.webp"
image_Costco = "https://upload.wikimedia.org/wikipedia/commons/5/59/Costco_Wholesale_logo_2010-10-26.svg"
image_coupang = "https://www.aboutcoupang.com/wp-content/themes/aboutcp/assets/images/logo.svg"
image_ikea =  "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Ikea_logo.svg/960px-Ikea_logo.svg.png"
image_other = "https://us.123rf.com/450wm/grigoriyzhukov/grigoriyzhukov2503/grigoriyzhukov250300207/243689390-red-shopping-basket-filled-with-groceries-and-fresh-food-items-vector-illustration.jpg"
mags = ["PXmart","Costco", "Coupang","Ikea", "Autre"]
#############################



# get data from sql
selectlist = "select * from workspace.default.grocery_list"
df_list = sql_exe(selectlist, fetch = True)
stores = df_list["store"].unique()
df_input = sql_exe("select distinct item from workspace.default.grocery_freq_buy", fetch = True)
# st.dataframe(df_list)

#############################
# Check if a list exist, if yes display them
#############################
for store in stores:
    create_list(store)

with st.expander("Créer une nouvelle list", expanded = False):
    with st.container(horizontal = False, border=True):
        clicked_PXmart = -1
        clicked_Costco = -1
        clicked_coupang = -1
        clicked_ikea = -1
        clicked_other = -1
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            if "PXmart" not in stores:
                clicked_PXmart = clickable_images([image_PX],img_style={"margin": "5px", "width": "50px"})
        with col2:
            if "Costco" not in stores:
                clicked_Costco = clickable_images([image_Costco],img_style={"margin": "5px", "width": "50px"})
        with col3:
            if "Coupang" not in stores:
                clicked_coupang = clickable_images([image_coupang],img_style={"margin": "5px", "width": "50px"})
        with col4:
            if "Ikea" not in stores:
                clicked_ikea = clickable_images([image_ikea],img_style={"margin": "5px", "width": "50px"})
        with col5:
            clicked_other = clickable_images([image_other],img_style={"margin": "5px", "width": "50px"})

        if clicked_PXmart == 0:
            create_list("PXmart")
        if clicked_Costco == 0:
            create_list("Costco")
        if clicked_coupang == 0:
            create_list("Coupang")
        if clicked_ikea == 0:
            create_list("Ikea")
        if clicked_other == 0:
            create_list("other")

#############################
# Manage Freq buy
#############################

with st.expander("Gestion des achats fréquants"):
    with st.form(key="add_freq_buy", border=False,enter_to_submit=False,clear_on_submit=True):
        with st.container(
            horizontal=True,
            vertical_alignment="bottom",
        ):
            item=st.text_input(
                "Nouvel article: ", 
                placeholder="Nouvel article",
            )

            submit=st.form_submit_button(
                "Add",
                icon=":material/add:",
            )
        if submit:
            if item not in (df_input["item"].unique()):
                add_freq_buy(item)
                st.rerun()
            else:
                st.warning("Cet article est déjà dans la liste", icon="⚠️")

    for i,row in df_input.iterrows():
        with st.container(horizontal=True, vertical_alignment="center"):
            col_text, col_delete = st.columns([9, 1],vertical_alignment="center")
            item=row["item"]
            with col_text:
                st.write(f"{item}")
            with col_delete:
                st.button(
                    ":material/delete:",
                    type="tertiary",
                    on_click=remove_freq,
                    args=(item,),
                    key=f"delfreqbutton_{item}",
                )