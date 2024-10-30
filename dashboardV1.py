import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
import seaborn as sns
import matplotlib.pyplot as plt

st.title("Prédiction de Crédit")

# Chargement des données client
client_data = pd.read_csv("data/application_train.csv")

# Saisir SK_ID_CURR
if 'sk_id_curr' not in st.session_state:
    st.session_state.sk_id_curr = ""

st.session_state.sk_id_curr = st.text_input("Entrez SK_ID_CURR", value=st.session_state.sk_id_curr)

sk_id_curr = st.session_state.sk_id_curr

# Colonnes les plus importantes (mises à jour)
colonnes_importantes = [
    'EXT_SOURCE_3',              
    'EXT_SOURCE_2',                 
    'EXT_SOURCE_1',              
    'REG_CITY_NOT_LIVE_CITY',    
    'AMT_INCOME_TOTAL',          
    'CODE_GENDER',               
    'CNT_CHILDREN',              
    'AMT_CREDIT',                
    'NAME_CONTRACT_TYPE',        
    'FLAG_OWN_CAR',              
    'FLAG_OWN_REALTY',           
    'AMT_ANNUITY',              
    'DAYS_BIRTH',                
    'DAYS_EMPLOYED',            
    'OCCUPATION_TYPE',          
    'NAME_EDUCATION_TYPE',       
    'NAME_FAMILY_STATUS',      
    'ORGANIZATION_TYPE',        
    'DAYS_LAST_PHONE_CHANGE'   
]

# Description des colonnes
descriptions = {
    'EXT_SOURCE_3': 'Source externe 3 - mesure de crédit (indicatif du risque de crédit).',
    'EXT_SOURCE_2': 'Source externe 2 - mesure de crédit (indicatif du risque de crédit).',
    'EXT_SOURCE_1': 'Source externe 1 - mesure de crédit (indicatif du risque de crédit).',
    'REG_CITY_NOT_LIVE_CITY': 'Indicateur si la ville de résidence est différente de la ville d\'inscription.',
    'AMT_INCOME_TOTAL': 'Revenu total du client.',
    'CODE_GENDER': 'Code genre du client (M pour homme, F pour femme).',
    'CNT_CHILDREN': 'Nombre d\'enfants du client.',
    'AMT_CREDIT': 'Montant du crédit demandé par le client.',
    'NAME_CONTRACT_TYPE': 'Type de contrat pour lequel le prêt est demandé (crédit à la consommation, hypothèque, etc.).',
    'FLAG_OWN_CAR': 'Indicateur si le client possède une voiture.',
    'FLAG_OWN_REALTY': 'Indicateur si le client possède un bien immobilier.',
    'AMT_ANNUITY': 'Montant de l\'annuité de remboursement du crédit.',
    'DAYS_BIRTH': 'Âge du client exprimé en nombre de jours (valeur négative).',
    'DAYS_EMPLOYED': 'Nombre de jours d\'emploi du client (valeur négative si actuellement employé).',
    'OCCUPATION_TYPE': 'Type d\'emploi du client.',
    'NAME_EDUCATION_TYPE': 'Niveau d\'éducation du client.',
    'NAME_FAMILY_STATUS': 'État matrimonial du client.',
    'ORGANIZATION_TYPE': 'Type d\'organisation dans laquelle le client est employé.',
    'DAYS_LAST_PHONE_CHANGE': 'Nombre de jours depuis le dernier changement de numéro de téléphone mobile.',
}

# Choix du filtre de comparaison
option = st.selectbox(
    'Choisissez un filtre de comparaison:',
    ('Tous les clients', 'Genre (Homme/Femme)', 'Statut familial', 'Niveau d\'éducation')
)

# Si l'utilisateur choisit 'Genre (Homme/Femme)', montrer un selectbox pour le genre
if option == 'Genre (Homme/Femme)':
    genre = st.selectbox('Choisissez le genre:', ['M', 'F'])
elif option == 'Statut familial':
    # Si l'utilisateur choisit 'Statut familial', montrer un selectbox pour le statut
    statut_famille = st.selectbox('Choisissez le statut familial:', client_data['NAME_FAMILY_STATUS'].unique())
elif option == 'Niveau d\'éducation':
    # Si l'utilisateur choisit 'Niveau d'éducation', montrer un selectbox pour le niveau
    niveau_education = st.selectbox('Choisissez le niveau d\'éducation:', client_data['NAME_EDUCATION_TYPE'].unique())


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

            # Extraire l'importance des caractéristiques
            importances = {}
            importance_elements = soup.find_all('li')  
    
            for element in importance_elements:
                parts = element.text.split(": ")
                if len(parts) == 2:
                    feature_name = parts[0].strip()
                    feature_importance = float(parts[1].strip())
                    importances[feature_name] = feature_importance

            # Affichage dans Streamlit
            st.write(f"**SK_ID_CURR**: {sk_id}")
            st.write(f"**Prédiction**: {prediction}")
            st.write(f"**Probabilité de défaut**: {probability:.2f}")

            # Visualisation de la probabilité avec une barre colorée
            st.markdown("### Visualisation de la Probabilité")

            # Création d'une barre de décision
            bar_length = 700  
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

            # Affichage du texte explicatif sur le crédit
            st.markdown(""" 
            ### Explication sur le crédit
            La probabilité de défaut de crédit est une estimation de la possibilité qu'un emprunteur ne rembourse pas son prêt. 
            - **Probabilité faible**: Cela indique que l'emprunteur est perçu comme un bon candidat pour le crédit, avec une faible chance de défaut.
            - **Probabilité élevée**: Cela indique que l'emprunteur est à risque de ne pas rembourser le crédit, ce qui pourrait entraîner un refus de la demande.
            """)

            # Chargement des données et affichage des caractéristiques
            try:
                client_data = pd.read_csv("data/application_train.csv") 

                if 'SK_ID_CURR' in client_data.columns:
                    client_info = client_data[client_data['SK_ID_CURR'] == int(sk_id_curr)]

                    if not client_info.empty:
                        # Affichage uniquement les colonnes importantes
                        st.write("Données du client pour SK_ID_CURR : **{}**".format(sk_id_curr))

                        # Création d'un DataFrame avec les colonnes importantes
                        df = client_info[colonnes_importantes].copy()
                        
                        # Appliquation d'un style au tableau
                        styled_df = df.style.background_gradient(cmap='viridis').set_table_attributes('style="width: 80%; margin: auto;"')

                        # Définir les styles pour le tableau
                        styled_df.set_table_styles(
                            [{'selector': 'th',
                              'props': [('background-color', '#f2f2f2'), ('color', 'black'), ('border', '1px solid #dddddd')]},
                             {'selector': 'td',
                              'props': [('border', '1px solid #dddddd'), ('padding', '8px'), ('text-align', 'center')]}]
                        )

                        # On ajoute des couleurs aux lignes alternées
                        styled_df.set_table_styles(
                            [{'selector': 'tr:nth-child(even)',
                              'props': [('background-color', '#f9f9f9')]}]
                        )
                        
                        st.dataframe(styled_df)

                        # On ajoute la section des descriptions des colonnes
                        st.subheader("Descriptions des colonnes")
                        for column, desc in descriptions.items():
                            st.markdown(f"**{column}**: {desc}")

                        # On ajoute l'image de l'importance globale
                        st.subheader("Importance des caractéristiques globales")
                        st.image("images/feature_importances_globales.png", caption="Top 20 des caractéristiques les plus importantes (globale)", use_column_width=True)

                        # Affichage de l'importance des caractéristiques
                        st.subheader("Importance des caractéristiques locales")
                        importance_df = pd.DataFrame(list(importances.items()), columns=['Feature', 'Importance'])
                        importance_df = importance_df.sort_values(by='Importance', ascending=False)

                        # Graphique de l'importance des caractéristiques
                        fig, ax = plt.subplots(figsize=(10, 6))
                        sns.barplot(data=importance_df.head(10), x='Importance', y='Feature', ax=ax, palette='viridis')
                        ax.set_title("Top 10 des caractéristiques les plus importantes (locale)")
                        st.pyplot(fig)

                        # PARTIE GRAPHIQUE

                        # Filtration des données en fonction du choix de l'utilisateur
                        if option == 'Genre (Homme/Femme)':
                            comparaison_group = client_data[client_data['CODE_GENDER'] == genre]
                        elif option == 'Statut familial':
                            comparaison_group = client_data[client_data['NAME_FAMILY_STATUS'] == statut_famille]
                        elif option == 'Niveau d\'éducation':
                            comparaison_group = client_data[client_data['NAME_EDUCATION_TYPE'] == niveau_education]
                        else:
                            comparaison_group = client_data
                        
                        # Colonnes numériques à comparer (par exemple EXT_SOURCE, revenu, âge, etc.)
                        variables_numeriques = ['AMT_INCOME_TOTAL', 'DAYS_BIRTH', 'AMT_CREDIT', 'EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3']

                        # Affichage d'un graphique boxplot pour comparer les distributions de chaque variable
                        for variable in variables_numeriques:
                            st.markdown(f"### Comparaison pour la variable: {variable}")
    
                            # Création du boxplot pour comparer la distribution
                            fig, ax = plt.subplots(figsize=(10, 5))
                            sns.boxplot(data=comparaison_group, x=comparaison_group[variable], ax=ax)
    
                            # On ajoute la valeur du client sur le graphique
                            client_val = client_info[variable].values[0]
                            plt.axvline(client_val, color='red', linestyle='--', label=f'Client {sk_id_curr}')
    
                            # Titre et légende
                            plt.title(f'Distribution de {variable} pour le groupe sélectionné')
                            plt.legend()
                            st.pyplot(fig)

                        # Affichage aussi des histogrammes
                        for variable in variables_numeriques:
                            st.markdown(f"### Histogramme pour la variable: {variable}")
    
                            # Création de l'histogramme pour comparer la distribution
                            fig, ax = plt.subplots(figsize=(10, 5))
                            sns.histplot(data=comparaison_group, x=comparaison_group[variable], kde=True, ax=ax, color="blue", bins=20)
    
                            # J'y ajoute la valeur du client sur le graphique
                            client_val = client_info[variable].values[0]
                            plt.axvline(client_val, color='red', linestyle='--', label=f'Client {sk_id_curr}')
    
                            # Titre et légende
                            plt.title(f'Histogramme de {variable} pour le groupe sélectionné')
                            plt.legend()
                            st.pyplot(fig)

                        st.subheader("Graphiques Bivariés pour Analyse Croisée")
                        paires_variables = [
                            ('AMT_INCOME_TOTAL', 'AMT_CREDIT'),
                            ('DAYS_BIRTH', 'AMT_CREDIT'),
                            ('CNT_CHILDREN', 'AMT_INCOME_TOTAL')
                        ]


                        for var_x, var_y in paires_variables:
                            st.markdown(f"### Comparaison Bivariée : {var_x} vs {var_y}")
                            fig, ax = plt.subplots(figsize=(8, 6))
                            sns.scatterplot(data=comparaison_group, x=var_x, y=var_y, ax=ax, alpha=0.3, color="blue")
                            client_x = client_info[var_x].values[0]
                            client_y = client_info[var_y].values[0]
                            plt.scatter(client_x, client_y, color='red', s=100, label=f'Client {sk_id_curr}', edgecolor='black')
                            plt.xlabel(var_x)
                            plt.ylabel(var_y)
                            plt.title(f'Comparaison Bivariée entre {var_x} et {var_y}')
                            plt.legend()
                            st.pyplot(fig)


                    else:
                        st.warning("Aucune donnée trouvée pour l'identifiant SK_ID_CURR donné.")
                else:
                    st.error("La colonne 'SK_ID_CURR' n'existe pas dans les données.")
            except FileNotFoundError:
                st.error("Le fichier 'X_predictionV1.csv' est introuvable. Vérifiez le chemin.")
            except Exception as e:
                st.error(f"Une erreur s'est produite lors du chargement des données : {str(e)}")

        else:
            st.error("Erreur: Ce numéro de client n'existe pas ou est invalide.")
    else:
        st.warning("Veuillez entrer un SK_ID_CURR.")