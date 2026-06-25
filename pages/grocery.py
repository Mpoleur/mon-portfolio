import os
import streamlit as st
from dataclasses import dataclass, field
import uuid
import pandas as pd
import random 
from databricks import sql
from databricks.sdk.core import Config, oauth_service_principal

# routine pour chercher une table avec connection à la db

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


#############################
#Variables
image_PX = "https://shoplineimg.com/5cc3db30527c4b0001a30cf0/5f8bc65696b102003bd6bf54/3860x.webp"
image_Costco = "https://upload.wikimedia.org/wikipedia/commons/5/59/Costco_Wholesale_logo_2010-10-26.svg"

#############################




# get data from sql
selectlist = "select * from workspace.default.grocery_list"
df_list = sql_exe(selectlist, fetch = True)
stores = df_list["store"].unique()
df_input = sql_exe("select distinct item from workspace.default.grocery_freq_buy", fetch = True)
# st.dataframe(df_list)

#############################
# Expander list PXmart
#############################

with st.expander("PXmart",expanded=True):
    store = "PXmart"
    with st.container(horizontal_alignment="center"):
        st.image(image_PX, width=100)
        st.title(
            "Liste PXmart",
            width="content",
            anchor=False,
        )

    with st.form(key="form_PXmart", border=False,enter_to_submit=False,clear_on_submit=True):
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
                    col_check, col_text, col_spacer, col_delete = st.columns([1, 4, 4, 1],vertical_alignment="center")
                    item=row["item"]
                    check_og=row["crossed"]
                    story=row["store"]
                    quantity = row["quantity"]
                    with col_check:
                        st.checkbox(
                            label="",
                            value=check_og,
                            width="content",
                            key=f"checkbox_{item}_{story}",
                            on_change=check_todo,
                            args=(item,story,check_og)
                        )
                    with col_text:
                        if check_og == False:
                            st.write(f"   {quantity} x {item}")
                        else:
                            st.write(f"<s>   {quantity} x {item}<s>", unsafe_allow_html=True)
                    with col_spacer:
                        st.empty()
                    with col_delete:
                        st.button(
                            ":material/delete:",
                            type="tertiary",
                            on_click=remove_todo,
                            args=(item,story),
                            key=f"delbutton_{item}_{story}",
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
# Expander list Costco
#############################

with st.expander("Costco",expanded=False):
    store = "Costco"
    with st.container(horizontal_alignment="center"):
        st.image(image_Costco, width=100)
        st.title(
            "Liste Costco",
            width="content",
            anchor=False,
        )

    with st.form(key="form_costco", border=False,enter_to_submit=False,clear_on_submit=True):
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
                    col_check, col_text, col_spacer, col_delete = st.columns([1, 4, 4, 1],vertical_alignment="center")
                    item=row["item"]
                    check_og=row["crossed"]
                    story=row["store"]
                    quantity = row["quantity"]
                    with col_check:
                        st.checkbox(
                            label="",
                            value=check_og,
                            width="content",
                            key=f"checkbox_{item}_{story}",
                            on_change=check_todo,
                            args=(item,story,check_og)
                        )
                    with col_text:
                        if check_og == False:
                            st.write(f"   {quantity} x {item}")
                        else:
                            st.write(f"<s>   {quantity} x {item}<s>", unsafe_allow_html=True)
                    with col_spacer:
                        st.empty()
                    with col_delete:
                        st.button(
                            ":material/delete:",
                            type="tertiary",
                            on_click=remove_todo,
                            args=(item,story),
                            key=f"delbutton_{item}_{story}",
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