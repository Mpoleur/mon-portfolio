import streamlit as st

#set up de la page streamlit
st.set_page_config(
    # Title and icon for the browser's tab bar:
    page_title="Toolbar",
    page_icon="🛠️",
    layout="wide",
)

st.title("🛠️My toolbar")
st.write("Choisis l'app que tu veux ouvrir :")

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.subheader("📊 Portfolio Tracker")
        st.write("Suivi de mes investissements")
        if st.button("Ouvrir Portfolio"):
            st.switch_page("pages/portfolio.py")

with col2:
    with st.container(border=True):
        st.subheader("📋 Job Tracker")
        st.write("Suivi de mes candidatures")
        if st.button("Ouvrir Job Tracker"):
            st.switch_page("pages/2_Job_Tracker.py")

with col3:
    with st.container(border=True):
        st.subheader("🛒 Price comparator")
        st.write("Price comparator in Taiwan")
        if st.button("Ouvrir comparateur"):
            st.switch_page("pages/comparator.py")
