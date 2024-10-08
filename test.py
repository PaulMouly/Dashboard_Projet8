import streamlit as st
import requests

st.title("Prédiction de Crédit")

# Saisir SK_ID_CURR
sk_id_curr = st.text_input("Entrez SK_ID_CURR")

if st.button("Prédire"):
    if sk_id_curr:
        response = requests.post(f"https://projet7credit-11e509d90e55.herokuapp.com/predict", data={"SK_ID_CURR": sk_id_curr})
        
        if response.status_code == 200:
            st.markdown(response.text, unsafe_allow_html=True)  # Affiche le HTML renvoyé par l'API
        else:
            st.error(f"Erreur: {response.json()['error']}")
    else:
        st.warning("Veuillez entrer un SK_ID_CURR.")
