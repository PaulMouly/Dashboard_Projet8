import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup

st.title("Prédiction de Crédit")

# Saisir SK_ID_CURR
sk_id_curr = st.text_input("Entrez SK_ID_CURR")

# Colonnes les plus importantes
colonnes_importantes = [
    'EXT_SOURCE_3',
    'EXT_SOURCE_2',
    'CC_CNT_DRAWINGS_ATM_CURRENT_MEAN',
    'FLAG_DOCUMENT_3',
    'CC_CNT_DRAWINGS_CURRENT_MEAN',
    'EXT_SOURCE_1',
    'INSTAL_AMT_PAYMENT_SUM',
    'CC_AMT_DRAWINGS_CURRENT_MEAN',
    'PREV_DAYS_FIRST_DRAWING_MAX',
    'INSTAL_PAYMENT_PERC_MEAN',
    'REG_CITY_NOT_LIVE_CITY',
    'AMT_INCOME_TOTAL',
    'CODE_GENDER',
    'CNT_CHILDREN',
    'AMT_CREDIT',
]

# Description des colonnes
descriptions = {
    'EXT_SOURCE_3': 'Source externe 3 - mesure de crédit.',
    'EXT_SOURCE_2': 'Source externe 2 - mesure de crédit.',
    'CC_CNT_DRAWINGS_ATM_CURRENT_MEAN': 'Nombre moyen de retraits aux guichets automatiques.',
    'FLAG_DOCUMENT_3': 'Indicateur si le document 3 est fourni.',
    'CC_CNT_DRAWINGS_CURRENT_MEAN': 'Nombre moyen de retraits actuels.',
    'EXT_SOURCE_1': 'Source externe 1 - mesure de crédit.',
    'INSTAL_AMT_PAYMENT_SUM': 'Somme des montants des paiements d\'installations.',
    'CC_AMT_DRAWINGS_CURRENT_MEAN': 'Montant moyen des retraits actuels.',
    'PREV_DAYS_FIRST_DRAWING_MAX': 'Nombre de jours avant le premier tirage.',
    'INSTAL_PAYMENT_PERC_MEAN': 'Pourcentage moyen de paiement d\'installations.',
    'REG_CITY_NOT_LIVE_CITY': 'Indicateur si la ville de résidence est différente de la ville d\'inscription.',
    'AMT_INCOME_TOTAL': 'Revenu total.',
    'CODE_GENDER': 'Code genre du client.',
    'CNT_CHILDREN': 'Nombre d\'enfants.',
    'AMT_CREDIT': 'Montant du crédit demandé.',
}

if st.button("Prédire"):
    if sk_id_curr:
        response = requests.post(f"https://projet7credit-11e509d90e55.herokuapp.com/predict", data={"SK_ID_CURR": sk_id_curr})

        if response.status_code == 200:
            # Parse the HTML response
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraire la prédiction, la probabilité et SK_ID_CURR
            sk_id = soup.find('p').text.split(": ")[1]  # Extraction du SK_ID_CURR
            prediction = soup.find_all('p')[1].text.split(": ")[1]  # Extraction de la prédiction
            probability = float(soup.find_all('p')[2].text.split(": ")[1])  # Extraction de la probabilité

            # Affichage dans Streamlit
            st.write(f"**SK_ID_CURR**: {sk_id}")
            st.write(f"**Prédiction**: {prediction}")
            st.write(f"**Probabilité de défaut**: {probability:.2f}")

            # Visualisation de la probabilité avec une barre colorée
            st.markdown("### Visualisation de la Probabilité")

            # Créer une barre de décision
            bar_length = 700  # Longueur de la barre
            threshold = 0.5
            
            # HTML pour afficher la barre colorée
            bar_html = f"""
            <div style="width: {bar_length}px; height: 30px; background-color: #f0f0f0; border-radius: 15px; overflow: hidden; position: relative;">
                <div style="width: {probability * bar_length:.1f}px; height: 30px; background-color: {'green' if probability < threshold else 'red'};"></div>
                <div style="position: absolute; left: {threshold * bar_length}px; top: 0; height: 30px; width: 2px; background-color: black;"></div>  <!-- Ligne de seuil -->
            </div>
            <div style="display: flex; justify-content: space-between; font-weight: bold;">
                <span style="color: green;">Crédit Validé</span>
                <span style="color: red;">Crédit Non Validé</span>
            </div>
            <div style="text-align: center; font-weight: bold; margin-top: 5px;">
                {probability:.2f}
            </div>
            <div style="text-align: center; margin-top: 5px;">
                <strong>Seuil => 0,5 </strong>  <!-- Label pour le seuil -->
            </div>
            """
            st.markdown(bar_html, unsafe_allow_html=True)

            # Interprétation de la probabilité
            if probability >= threshold:
                st.warning("Cela signifie que le crédit est susceptible d'être refusé.")
            else:
                st.success("Cela signifie que le crédit est susceptible d'être accordé.")

            # Afficher un texte explicatif sur le crédit
            st.markdown(""" 
            ### Explication sur le crédit
            La probabilité de défaut de crédit est une estimation de la possibilité qu'un emprunteur ne rembourse pas son prêt. 
            - **Probabilité faible**: Cela indique que l'emprunteur est perçu comme un bon candidat pour le crédit, avec une faible chance de défaut.
            - **Probabilité élevée**: Cela indique que l'emprunteur est à risque de ne pas rembourser le crédit, ce qui pourrait entraîner un refus de la demande.
            """)

            # Charger les données et afficher les caractéristiques
            try:
                client_data = pd.read_csv("API/data/X_predictionV1.csv")  # Mettez à jour le chemin si nécessaire

                if 'SK_ID_CURR' in client_data.columns:
                    client_info = client_data[client_data['SK_ID_CURR'] == int(sk_id_curr)]

                    if not client_info.empty:
                        # Afficher uniquement les colonnes importantes
                        st.write("Données du client pour SK_ID_CURR : **{}**".format(sk_id_curr))

                        # Créer un DataFrame avec les colonnes importantes
                        df = client_info[colonnes_importantes].copy()
                        
                        # Appliquer un style au tableau
                        styled_df = df.style.background_gradient(cmap='viridis').set_table_attributes('style="width: 80%; margin: auto;"')

                        # Définir des styles pour le tableau
                        styled_df.set_table_styles(
                            [{'selector': 'th',
                              'props': [('background-color', '#f2f2f2'), ('color', 'black'), ('border', '1px solid #dddddd')]},
                             {'selector': 'td',
                              'props': [('border', '1px solid #dddddd'), ('padding', '8px'), ('text-align', 'center')]}]
                        )

                        # Ajouter des couleurs aux lignes alternées
                        styled_df.set_table_styles(
                            [{'selector': 'tr:nth-child(even)',
                              'props': [('background-color', '#f9f9f9')]}]
                        )
                        
                        st.dataframe(styled_df)

                        # Ajouter la section des descriptions des colonnes
                        st.subheader("Descriptions des colonnes")
                        for column, desc in descriptions.items():
                            st.markdown(f"**{column}**: {desc}")
                    else:
                        st.warning("Aucune donnée trouvée pour l'identifiant SK_ID_CURR donné.")
                else:
                    st.error("La colonne 'SK_ID_CURR' n'existe pas dans les données.")
            except FileNotFoundError:
                st.error("Le fichier 'X_predictionV1.csv' est introuvable. Vérifiez le chemin.")
            except Exception as e:
                st.error(f"Une erreur s'est produite lors du chargement des données : {str(e)}")

        else:
            st.error(f"Erreur: {response.json()['error']}")
    else:
        st.warning("Veuillez entrer un SK_ID_CURR.")