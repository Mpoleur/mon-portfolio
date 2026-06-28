import streamlit as st
from st_clickable_images import clickable_images

#set up de la page streamlit
st.set_page_config(
    # Title and icon for the browser's tab bar:
    page_title="Toolbar",
    page_icon="🛠️",
    layout="wide",
)

st.title("🛠️My toolbar")
st.write("Choisis l'app que tu veux ouvrir :")
image_url = "https://media.forgecdn.net/avatars/thumbnails/1031/807/256/256/638554680736765570.png"


col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.subheader("📊 Portfolio Tracker")
        st.write("Suivi de mes investissements")
        if st.button("Ouvrir Portfolio"):
            st.switch_page("pages/portfolio.py")

with col2:
    with st.container(border=True):
        st.subheader("📋 Grocery list")
        st.write("Liste de course")
        if st.button("Ouvrir la liste de course"):
            st.switch_page("pages/grocery.py")

with col3:
    with st.container(border=True):
        st.subheader("🛒 Price comparator")
        st.write("Price comparator in Taiwan")
        if st.button("Ouvrir comparateur"):
            st.switch_page("pages/comparator.py")


with st.container(horizontal=True, border=False, gap=None):
    click1 = clickable_images([image_url],img_style={"margin": "Opx", "width": "10%"},key="o")
    if click1 == 0:
        st.switch_page("pages/comparator.py")
    click2 = clickable_images([image_url],img_style={"margin": "Opx", "width": "10%"},key="i")
    if click2 == 0:
        st.switch_page("pages/comparator.py")
    click3 = clickable_images([image_url],img_style={"margin": "Opx", "width": "10%"},key="u")
    if click3 == 0:
        st.switch_page("pages/comparator.py")
    click4 = clickable_images([image_url],img_style={"margin": "Opx", "width": "10%"},key="y")
    if click4 == 0:
        st.switch_page("pages/comparator.py")
    click5 = clickable_images([image_url],img_style={"margin": "Opx", "width": "10%"},key="t")
    if click5 == 0:
        st.switch_page("pages/comparator.py")
    click6 = clickable_images([image_url],img_style={"margin": "Opx", "width": "10%"},key="r")
    if click6 == 0:
        st.switch_page("pages/comparator.py")
    click7 = clickable_images([image_url],img_style={"margin": "Opx", "width": "10%"},key="e")
    if click7 == 0:
        st.switch_page("pages/comparator.py")
    click8 = clickable_images([image_url],img_style={"margin": "Opx", "width": "10%"},key="z")
    if click8 == 0:
        st.switch_page("pages/comparator.py")
    click9 = clickable_images([image_url],img_style={"margin": "Opx", "width": "10%"},key="a")
    if click9 == 0:
        st.switch_page("pages/comparator.py")