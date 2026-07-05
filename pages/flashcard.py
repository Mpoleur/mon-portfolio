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

CSV_PATH = "Voc.csv"

MODES = ["English", "Pinyin", "Hanzi"]
COL_FOR_MODE = {"English": "Anglais", "Pinyin": "Pinyin", "Hanzi": "Chinois"}


@st.cache_data
def load_vocab():
    return pd.read_csv(CSV_PATH)


df = load_vocab()

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


st.markdown(
    """
    <style>
    .card {
        border: 2px solid #4472C4;
        border-radius: 18px;
        background-color: #f8f9fb;
        min-height: 220px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        padding: 30px 20px;
        margin-bottom: 20px;
    }
    .front-text { font-size: 40px; font-weight: 700; color: #1a1a1a; }
    .big-text   { font-size: 52px; font-weight: 700; color: #1a1a1a; }
    .small-text { font-size: 20px; color: #666666; margin-top: 12px; }
    div.stButton > button {
        height: 60px;
        width: 100%;
        font-size: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🀄 Flashcards")

mode = st.selectbox("Mode", MODES, index=MODES.index(st.session_state.mode))
if mode != st.session_state.mode:
    st.session_state.mode = mode
    st.session_state.revealed = False

st.caption(f"Word {st.session_state.pos + 1} / {len(df)}")

current_idx = st.session_state.order[st.session_state.pos]
word = df.iloc[current_idx]

front_col = COL_FOR_MODE[st.session_state.mode]
if st.session_state.mode == "Hanzi":
    big_col, small_col = "Anglais", "Pinyin"
elif st.session_state.mode == "Pinyin":
    big_col, small_col = "Chinois", "Anglais"
else:
    big_col, small_col = "Chinois", "Pinyin"

front_text = str(word[front_col])
big_text = str(word[big_col])
small_text = str(word[small_col])

if not st.session_state.revealed:
    card_html = f'<div class="card"><div class="front-text">{front_text}</div></div>'
    button_label = "👉 Show answer"
else:
    card_html = (
        f'<div class="card">'
        f'<div class="big-text">{big_text}</div>'
        f'<div class="small-text">{small_text}</div>'
        f"</div>"
    )
    button_label = "➡️ Next word"

st.markdown(card_html, unsafe_allow_html=True)

if st.button(button_label, use_container_width=True):
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
if st.button("🔀 Shuffle"):
    new_shuffle()
    st.rerun()