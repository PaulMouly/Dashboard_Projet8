import streamlit as st
import requests
from bs4 import BeautifulSoup

st.title("Prédiction de Crédit")

# Saisir SK_ID_CURR
sk_id_curr = st.text_input("Entrez SK_ID_CURR")

if st.button("Prédire"):
    if sk_id_curr:
        response = requests.post(f"https://projet7credit-11e509d90e55.herokuapp.com/predict", data={"SK_ID_CURR": sk_id_curr})

        if response.status_code == 200:
            # Parse the HTML response
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraire la prédiction et SK_ID_CURR
            sk_id = soup.find('p').text
            prediction = soup.find_all('p')[1].text

            # Affichage dans Streamlit
            st.write(f"**{sk_id}**")
            st.write(f"**{prediction}**")

            # Afficher une image statique en fonction de la prédiction
            if "Crédit Validé" in prediction:
                st.image("/path/to/credit_valide_image.png")  # Replace with the actual path
            else:
                st.image("/path/to/credit_non_valide_image.png")  # Replace with the actual path

        else:
            st.error(f"Erreur: {response.json()['error']}")
    else:
        st.warning("Veuillez entrer un SK_ID_CURR.")