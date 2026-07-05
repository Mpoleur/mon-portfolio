import streamlit as st
import base64
from st_clickable_images import clickable_images


def image_to_base64(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return "data:image/png;base64," + base64.b64encode(data).decode()


#set up de la page streamlit
st.set_page_config(
    # Title and icon for the browser's tab bar:
    page_title="Toolbar",
    page_icon="🛠️",
    layout="wide",
)

st.title("🛠️My toolbar")
st.write("Choisis l'app que tu veux ouvrir :")
#url des images
image_url = image_to_base64("img/Inventory.png")
image_comp = image_to_base64("img/Comparator.png")
image_dice = image_to_base64("img/Dice.png")
image_flash = image_to_base64("img/Flashcard.png")
image_grocery = image_to_base64("img/Grocery.png")
image_portfolio = image_to_base64("img/portfolio.png")

images = [
    image_portfolio,
    image_grocery,
    image_comp,
    image_dice,
    image_flash,
    image_url
]

pages = [
    "pages/portfolio.py",
    "pages/grocery.py",
    "pages/comparator.py",
    "pages/dices.py",
    "pages/flashcard.py",
    "pages/comparator.py"
]

clicked = clickable_images(
    images,
    img_style={"margin": "0px", "width": "10%"},
    key="toolbar_images"
)

if clicked is not None and clicked >= 0:
    st.switch_page(pages[clicked])