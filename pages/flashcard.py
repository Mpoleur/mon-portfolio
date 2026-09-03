import streamlit as st
import pandas as pd
import random
import functools
import pypinyin
import colortones

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

#############################
# Tone-coloring for Hanzi (via the "colortones" library)
# https://github.com/travisgk/colortones
#############################
# colortones segments text with jieba + pypinyin and applies real tone-sandhi
# rules (e.g. 不 / 一, third-tone sandhi) before assigning a color per
# syllable. It's built for full sentences though, so it can raise on the
# odd short/mixed-script vocab entry (e.g. "KTV", or characters missing
# from its transcription table) -- in that case we fall back to a plain
# per-character tone lookup with pypinyin so the app never crashes.

SCHEME_NAMES = ["pleco", "default", "hanping", "mdbg", "dummit", "sinosplice"]


@functools.lru_cache(maxsize=None)
def _get_scheme(name):
    return colortones.load_color_scheme(name)


@functools.lru_cache(maxsize=None)
def _fallback_char_tone(ch):
    """Tone (1-4, 5=neutral) of a single character via plain pypinyin,
    with no sandhi/context awareness. None if `ch` isn't Chinese."""
    result = pypinyin.pinyin(
        ch, style=pypinyin.Style.TONE3, heteronym=False, neutral_tone_with_five=True
    )
    if not result or not result[0]:
        return None
    syllable = result[0][0]
    if syllable == ch:
        return None  # not a recognized Chinese character
    if syllable and syllable[-1].isdigit():
        return int(syllable[-1])
    return None


@functools.lru_cache(maxsize=4096)
def colorize_hanzi(text, scheme_name):
    """Wraps each Chinese character of `text` in a <span> colored by tone,
    using colortones' sandhi-aware analysis when it can parse the text,
    and a simple per-character fallback otherwise."""
    color_scheme = _get_scheme(scheme_name)

    try:
        paragraph = colortones.process_text(text)
        pieces = []
        for clause in paragraph.sentences:
            for word in clause.words:
                for syllable in word.syllables:
                    hanzi = syllable["hanzi"]
                    if syllable.is_punct():
                        pieces.append(hanzi)
                    else:
                        color = color_scheme[syllable["inflection-num"]][1]
                        pieces.append(f'<span style="color:{color}">{hanzi}</span>')
        return "".join(pieces)
    except Exception:
        pieces = []
        for ch in text:
            tone = _fallback_char_tone(ch)
            if tone in (1, 2, 3, 4, 5):
                color = color_scheme[tone][1]
                pieces.append(f'<span style="color:{color}">{ch}</span>')
            else:
                pieces.append(ch)
        return "".join(pieces)


@st.cache_data
def load_vocab():
    return pd.read_csv(CSV_PATH)


df_all = load_vocab()

if "mode" not in st.session_state:
    st.session_state.mode = "English"
if "tone_scheme" not in st.session_state:
    st.session_state.tone_scheme = "pleco"


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
    if len(chapter) ==1:
        chap = "".join(chapter)
        if chap !="x":
            st.link_button("Open lesson",f"https://zhongchinese.com/articles/vocabulary/book-1-lesson-{chap}-vocabulary/")
        else:
            pass
    else:
        pass

col_mode, col_scheme = st.columns(2)
with col_mode:
    mode = st.selectbox("Mode", MODES, index=MODES.index(st.session_state.mode))
    if mode != st.session_state.mode:
        st.session_state.mode = mode
        st.session_state.revealed = False
with col_scheme:
    tone_scheme = st.selectbox(
        "Tone colors", SCHEME_NAMES, index=SCHEME_NAMES.index(st.session_state.tone_scheme)
    )
    if tone_scheme != st.session_state.tone_scheme:
        st.session_state.tone_scheme = tone_scheme

_scheme = _get_scheme(st.session_state.tone_scheme)
_legend_html = "&nbsp;&nbsp;".join(
    f'<span style="color:{_scheme[num][1]}; font-weight:700;">●</span> {label}'
    for num, label in [(1, "1st - -"), (2, "2nd - ´ "), (3, "3rd- V"), (4, "4th - `"), (5, "neutral")]
)
st.markdown(
    f'<div style="font-size:14px; color:#666; margin-bottom:6px;">Tones: {_legend_html}</div>',
    unsafe_allow_html=True,
)

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


def _display_text(col_name):
    """Return the cell text, tone-colored when it's the Hanzi column."""
    raw = str(word[col_name])
    if col_name == "Chinois":
        return colorize_hanzi(raw, st.session_state.tone_scheme)
    return raw


front_text = _display_text(front_col)
big_text = _display_text(big_col)
small_text = _display_text(small_col)

# Plain (uncolored) hanzi text, used for the "Get Help" dictionary link below.
plain_front_text = str(word[front_col])
plain_big_text = str(word[big_col])


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
    st.link_button("Get Help",f"https://dictionary.writtenchinese.com/#sk={plain_front_text}&svt=pinyin")
elif st.session_state.mode == "Pinyin":
    st.link_button("Get Help",f"https://dictionary.writtenchinese.com/#sk={plain_big_text}&svt=pinyin")
else:
    st.link_button("Get Help",f"https://dictionary.writtenchinese.com/#sk={plain_big_text}&svt=pinyin")




# better website https://zhongchinese.com/articles/vocabulary/course-in-contemporary-chinese-vocabulary-book-1/