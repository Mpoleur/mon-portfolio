import streamlit as st

st.title("🏠 Mon Hub d'Apps")
st.write("Choisis l'app que tu veux ouvrir :")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Portfolio Tracker")
    st.write("Suivi de mes investissements")
    if st.button("Ouvrir Portfolio"):
        st.switch_page("portfolio.py")

with col2:
    st.subheader("📋 Job Tracker")
    st.write("Suivi de mes candidatures")
    if st.button("Ouvrir Job Tracker"):
        st.switch_page("pages/2_Job_Tracker.py")

