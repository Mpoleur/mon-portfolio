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
 

images = [
    image_url,
    image_url,
    image_url,
    image_url,
    image_url,
    image_url,
    image_url,
    image_url,
    image_url
]

pages = [
    "pages/portfolio.py",
    "pages/grocery.py",
    "pages/comparator.py",
    "pages/dices.py",
    "pages/grocery.py",
    "pages/comparator.py",
    "pages/portfolio.py",
    "pages/grocery.py",
    "pages/comparator.py"
]

clicked = clickable_images(
    images,
    img_style={"margin": "0px", "width": "10%"},
    key="toolbar_images"
)

if clicked is not None and clicked >= 0:
    st.switch_page(pages[clicked])