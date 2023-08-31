import streamlit as st
from useful_functions import *

def rapports_seismes():
    # Personnalisation de la mise en page avec du code HTML
    st.markdown("<h1 style='text-align: left;'>Rapports en temps réel</h1>", unsafe_allow_html=True)


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

        
        st.subheader("Top 10 des évènements les plus importants")
        top_mmi_rows = event_list.nlargest(10, 'properties.mmi')
        
        
        top_mmi_rows_renamed = top_mmi_rows.rename(
            columns={'id': 'ID', 'properties.mmi': 'MMI', 'properties.url': 'Lien vers USGS'}
        )

        selected_radio_text = st.radio(
            "Sélectionner un ID :",
            [f"ID : {row['ID']} (MMI : {row['MMI']})" for _, row in top_mmi_rows_renamed.iterrows()]
        )

        # Extraire l'ID du texte sélectionné
        selected_id = selected_radio_text.split(':')[1].split('(')[0].strip()
        
        selected_row = top_mmi_rows_renamed[top_mmi_rows_renamed['ID'] == selected_id].iloc[0]
        st.write("Lien vers USGS :")
        st.markdown(f"[{selected_row['Lien vers USGS']}]({selected_row['Lien vers USGS']})")

        
    st.markdown("<h3 style='text-align: left;'>Sites à observer :</h3>", unsafe_allow_html=True)

    # Ajouter un widget de chargement de fichier
    uploaded_file = st.file_uploader("Charger une liste de coordonnées géographiques", type=["csv", "xlsx"])

    if uploaded_file is not None:
        # Charger les données à partir du fichier
        df = load_data(uploaded_file)
        liste_coordonnees = list(zip(df['Latitude'], df['Longitude']))
        value=list(df["TIV"])

        # Récupérer les informations des MMI du séisme
        event = link_xml_event(selected_id)
        xml_file_path=event[0]
        title=event[1]
        time=event[2]
        date = datetime.fromtimestamp(time/1000).strftime('%Y-%m-%d %H:%M:%S')
        mag=event[3]
        mmi=event[4]
        
        # Lire le grid.xml
        grid_event = parse_link_grid_xml(xml_file_path)
        sampled_grid = grid_event.sample(frac=0.05, random_state=42)
        minmmi = grid_event["MMI"].min()
        maxmmi = grid_event["MMI"].max()
        center_lat = grid_event["Latitude"].mean()
        center_lon = grid_event["Longitude"].mean()

        # Croiser entre le grid et la liste des sites observés
        mmi_sites=point_plus_proche(liste_coordonnees,grid_event)

        # Création de la map
        world_map = folium.Map(location=[center_lat, center_lon], zoom_start=5.3)
        folium.Marker(
            location=[center_lat, center_lon],
             popup='Epicentre\nMMI :'+str(maxmmi),
            icon=folium.Icon(color='black', prefix='fa', icon_size=100)
        ).add_to(world_map)

        # Ajouter les marqueurs pour les sites
        for (lat, lon), mmi,value in zip(liste_coordonnees, mmi_sites,value):
            if mmi==0: 
                popup_content='Hors de la zone sismique' 
            else: 
                popup_content = f'Site \nMMI : {mmi}\nTIV : {round(value/10^3,1)k€}'
            folium.Marker(
                location=[lat, lon],
                popup=popup_content,
                icon=folium.Icon(color='darkblue', prefix='fa')
            ).add_to(world_map)
        
        # Définir l'échelle de couleurs
        custom_colors = ['lightgreen', 'yellow', 'orange', 'red', 'darkred']
        color_scale = folium.LinearColormap(custom_colors, vmin=minmmi, vmax=maxmmi)

        # Ajouter les cercles colorés
        for index, row in sampled_grid.iterrows():
            lat = row["Latitude"]
            lon = row["Longitude"]
            mmi = row["MMI"]
            folium.CircleMarker(
                location=(lat, lon),
                radius=20,
                color=None,
                fill=True,
                fill_color=color_scale(mmi),
                fill_opacity=0.01,
            ).add_to(world_map)

        color_scale.caption = "Modified Mercalli Intensity (MMI)"
        color_scale.add_to(world_map)

        # Charger l'application Streamlit
        st.title(title)
        st.subheader("Evènement du "+ str(date) +" de magnitude "+str(mag)+" de MMI moyen "+str(mmi)+".")

        # Afficher la carte Folium dans Streamlit
        folium_static(world_map)



        
        
  






