import streamlit as st
from useful_functions import *

def rapports_seismes():
    # Personnalisation de la mise en page avec du code HTML
    st.markdown("<h1 style='text-align: left;'>Rapports en temps réel</h1>", unsafe_allow_html=True)

    col_1, col_2 = st.columns(2)

    with col_1:
        st.markdown("<h3 style='text-align: left;'>Sites à observer :</h3>", unsafe_allow_html=True)

        # Ajouter un widget de chargement de fichier
        uploaded_file = st.file_uploader("Charger une liste de coordonnées géographiques", type=["csv", "xlsx"])

        if uploaded_file is not None:
            # Charger les données à partir du fichier
            df = load_data(uploaded_file)

    with col_2:
        # Widget pour choisir la période
        st.markdown("<h3>Choisir une période :</h3>", unsafe_allow_html=True)
        period = st.selectbox(
            "Sélectionnez la période",
            ["Un jour", "Trois jours", "Une semaine", "Un mois", "6 mois", "Un an"]
        )

        # Afficher le message d'avertissement
        if period in ["Un mois", "6 mois", "Un an"]:
            st.warning("Attention : plus la période choisie est longue, plus le temps d'exécution sera élevé.")

        # Convertir la période en nombre de jours
        period_days = {
            "Un jour": 1,
            "Trois jours": 3,
            "Une semaine": 7,
            "Un mois": 30,
            "6 mois": 180,
            "Un an": 365
        }
        selected_days = period_days[period]

        st.write(f"Période sélectionnée : {period} ({selected_days} jours)")
    
    event_list=download_list_event(selected_days)

    col1, col2 = st.columns(2)

    with col1:
        # Affichage d'une synthèse des données téléchargées
        st.subheader("Histogramme du nombre d'id par mmi")
        mmi_counts = event_list['properties.mmi'].value_counts()
        plt.bar(mmi_counts.index, mmi_counts.values)
        plt.xlabel('MMI')
        plt.ylabel('Nombre d\'évènements')
        st.pyplot(plt)
    
    with col2:
    # Afficher un tableau avec les 5 plus gros mmi
    st.subheader("Top 5 des évènements les plus importants")
    top_mmi_rows = event_list.nlargest(5, 'properties.mmi')
    st.table(top_mmi_rows[['id', 'properties.mmi', 'properties.url']])

  






