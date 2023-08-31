import streamlit as st

def rapports_seismes():
    # Personnalisation de la mise en page avec du code HTML
    st.markdown("<h1 style='text-align: left;'>Rapports en temps réel</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: left;'>Visualisation des sites impactés</h2>", unsafe_allow_html=True)

    # Ajouter un widget de chargement de fichier
    uploaded_file = st.file_uploader("Charger un fichier CSV ou Excel", type=["csv", "xlsx"])

    if uploaded_file is not None:
        # Charger les données à partir du fichier
        df = load_data(uploaded_file)

        # Afficher les données
        st.dataframe(df)