import streamlit as st
import pandas as pd
import random

#############################
# Functions
#############################


#############################
# Page set up
#############################

st.set_page_config(
    # Title and icon for the browser's tab bar:
    page_title="Flashcard",
    page_icon="🀄",
)

#############################
# Get data frame from csv
#############################

st.set_page_config(page_title="Flashcards Chinois", page_icon="🀄", layout="centered")

CSV_PATH = "voc.csv"

MODES = ["English", "Pinyin", "Hanzi"]
COL_FOR_MODE = {"English": "Anglais", "Pinyin": "Pinyin", "Hanzi": "Chinois"}


@st.cache_data
def load_vocab():
    return pd.read_csv(CSV_PATH)


df = load_vocab()

# --- Initialisation de l'état de session ---
if "order" not in st.session_state:
    order = list(range(len(df)))
    random.shuffle(order)
    st.session_state.order = order
    st.session_state.pos = 0
    st.session_state.revealed = False

if "mode" not in st.session_state:
    st.session_state.mode = "English"


def new_shuffle():
    order = list(range(len(df)))
    random.shuffle(order)
    st.session_state.order = order
    st.session_state.pos = 0
    st.session_state.revealed = False


# --- CSS pour styliser la carte et rendre le bouton "invisible" mais cliquable ---
st.markdown(
    """
    <style>
    .card {
        border: 2px solid #4472C4;
        border-radius: 18px;
        background-color: #f8f9fb;
        min-height: 260px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        padding: 30px 20px;
        margin-bottom: -290px;
        position: relative;
        z-index: 1;
    }
    .front-text { font-size: 40px; font-weight: 700; color: #1a1a1a; }
    .big-text   { font-size: 52px; font-weight: 700; color: #1a1a1a; }
    .small-text { font-size: 20px; color: #666666; margin-top: 12px; }
    div.stButton > button {
        height: 260px;
        width: 100%;
        opacity: 0;
        position: relative;
        z-index: 2;
        cursor: pointer;
        border: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🀄 Flashcards")

mode = st.selectbox("Mode d'affichage", MODES, index=MODES.index(st.session_state.mode))
if mode != st.session_state.mode:
    st.session_state.mode = mode
    st.session_state.revealed = False

st.caption(f"Carte {st.session_state.pos + 1} / {len(df)}")

current_idx = st.session_state.order[st.session_state.pos]
word = df.iloc[current_idx]

front_col = COL_FOR_MODE[st.session_state.mode]
other_cols = [c for c in ["Anglais", "Pinyin", "Chinois"] if c != front_col]
# ordre d'affichage du dos : grand = l'autre "sens" principal, petit = pinyin (sauf si pinyin est déjà devant)
if st.session_state.mode == "Hanzi":
    big_col, small_col = "Anglais", "Pinyin"
elif st.session_state.mode == "Pinyin":
    big_col, small_col = "Chinois", "Anglais"
else:  # English
    big_col, small_col = "Chinois", "Pinyin"

front_text = str(word[front_col])
big_text = str(word[big_col])
small_text = str(word[small_col])

if not st.session_state.revealed:
    card_html = f'<div class="card"><div class="front-text">{front_text}</div></div>'
else:
    card_html = (
        f'<div class="card">'
        f'<div class="big-text">{big_text}</div>'
        f'<div class="small-text">{small_text}</div>'
        f"</div>"
    )

st.markdown(card_html, unsafe_allow_html=True)

if st.button(" ", key="card_click"):
    if not st.session_state.revealed:
        st.session_state.revealed = True
    else:
        if st.session_state.pos + 1 >= len(df):
            new_shuffle()
        else:
            st.session_state.pos += 1
            st.session_state.revealed = False
    st.rerun()

st.divider()
if st.button("🔀 Recommencer avec un nouvel ordre"):
    new_shuffle()
    st.rerun()