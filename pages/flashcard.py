import streamlit as st
import pandas as pd
import random

#############################
# Remove side bar
#############################

st.markdown("""
<style>
    [data-testid="stSidebar"] {
        display: none !important;
    }
    [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

#############################
# Page set up
#############################

st.set_page_config(
    page_title="Flashcard",
    page_icon="🀄",
    initial_sidebar_state=None,
)

#############################
# Get data frame from csv
#############################

CSV_PATH = "voc.csv"

MODES = ["English", "Pinyin", "Hanzi"]
COL_FOR_MODE = {"English": "Anglais", "Pinyin": "Pinyin", "Hanzi": "Chinois"}


@st.cache_data
def load_vocab():
    return pd.read_csv(CSV_PATH)


df_all = load_vocab()

if "mode" not in st.session_state:
    st.session_state.mode = "English"


def new_shuffle(n):
    order = list(range(n))
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

#default_books = ["1-1"]
default_chap = ['5']
books = sorted(df_all["Books"].unique())
chapters = sorted(
    df_all["Chapter"].unique(),
    key=lambda x: (0, int(x)) if str(x).isdigit() else (1, str(x))
)

with st.expander("Choose your lessons", expanded=False):
#    book = st.pills("Selected books", books, default=default_books, selection_mode="multi")
    chapter = st.pills("Selected chapters", chapters, default=default_chap, selection_mode="multi")

mode = st.selectbox("Mode", MODES, index=MODES.index(st.session_state.mode))
if mode != st.session_state.mode:
    st.session_state.mode = mode
    st.session_state.revealed = False

# --- Dataframe filtré selon la sélection ---
df = df_all[df_all["Chapter"].isin(chapter)].reset_index(drop=True)

if df.empty:
    st.warning("No selection!")
    st.stop()

# --- Si la sélection a changé (ou 1er chargement), on régénère order/pos à la bonne taille ---
selection_key = tuple(sorted(chapter))
if st.session_state.get("selection_key") != selection_key:
    st.session_state.selection_key = selection_key
    new_shuffle(len(df))

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
            new_shuffle(len(df))
        else:
            st.session_state.pos += 1
            st.session_state.revealed = False
    st.rerun()

st.divider()
if st.button("🔀 Shuffle"):
    new_shuffle(len(df))
    st.rerun()

if st.session_state.mode == "Hanzi":
    st.link_button("Get Help",f"https://dictionary.writtenchinese.com/#sk={front_text}&svt=pinyin")
elif st.session_state.mode == "Pinyin":
    st.link_button("Get Help",f"https://dictionary.writtenchinese.com/#sk={big_text}&svt=pinyin")
else:
    st.link_button("Get Help",f"https://dictionary.writtenchinese.com/#sk={big_text}&svt=pinyin")


# better website https://zhongchinese.com/articles/vocabulary/course-in-contemporary-chinese-vocabulary-book-1/