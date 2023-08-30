import streamlit as st
import pandas as pd
from streamlit_folium import folium_static
import xml.etree.ElementTree as ET
import os
import folium
import requests
from datetime import datetime
import json
import matplotlib
from scipy.spatial.distance import cdist
from useful_functions import *

st.markdown("<h1 style='text-align: left;'>Analyse de la sismicité</h1>", unsafe_allow_html=True)


st.set_page_config(
    page_title="Carte de Sismicité",
    page_icon=":earthquake:",
    layout="wide",  # Utiliser une mise en page plus large
    initial_sidebar_state="expanded",  # Barre latérale ouverte par défaut
)



# Personnalisation de la mise en page avec du code HTML
st.markdown("<h1 style='text-align: left;'>Carte de Sismicité</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: left;'>Visualisation des données de sismicité</h2>", unsafe_allow_html=True)

seisme_id = st.text_input("Entrez l'ID du séisme :", '')

# Utilisation de colonnes pour organiser les widgets
col_1, col_2 = st.columns(2)

with col_1:
    ajouter_point_manuellement = st.checkbox("Ajouter un point manuellement")
        # Initialiser une liste pour stocker les points ajoutés manuellement
    if 'points_manuels' not in st.session_state:
        st.session_state.points_manuels = []

    # Si l'utilisateur a choisi d'ajouter un point manuellement
    if ajouter_point_manuellement:
        st.subheader("Ajout de points manuels")

        # Utilisation des colonnes pour diviser les widgets en deux parties
        col1, col2 = st.columns(2)
        latitude_manuelle = col1.number_input("Latitude :", value=0.0)
        longitude_manuelle = col2.number_input("Longitude :", value=0.0)

        if st.button("Ajouter le point"):
            st.session_state.points_manuels.append((latitude_manuelle, longitude_manuelle))
            st.success("Point ajouté avec succès!")
        

with col_2:
    

    # Afficher la liste des points ajoutés par l'utilisateur dans un tableau
    if len(st.session_state.points_manuels) > 0:
        st.subheader("Liste des points ajoutés manuellement")
        df_points_manuels = pd.DataFrame(st.session_state.points_manuels, columns=["Latitude", "Longitude"])

        # Ajouter une colonne de boutons de suppression
        df_points_manuels["Action"] = ""
        for idx in df_points_manuels.index:
            delete_button = st.button(f"Supprimer {idx}", key=f"supprimer_{idx}")
            df_points_manuels.at[idx, "Action"] = delete_button

        # Filtrer les lignes où le bouton de suppression n'a pas été cliqué
        df_points_manuels = df_points_manuels[df_points_manuels["Action"]]

        # Supprimer les coordonnées des points supprimés de st.session_state.points_manuels
        deleted_indices = df_points_manuels.index
        st.session_state.points_manuels = [
            (lat, lon) for idx, (lat, lon) in enumerate(st.session_state.points_manuels) if idx not in deleted_indices
        ]

        # Afficher le tableau mis à jour
        st.dataframe(df_points_manuels.drop(columns=["Action"]), index=False)


        
        
# Ajouter un bouton pour démarrer la visualisation
if st.button("Visualiser"):
    
    if seisme_id is not None and seisme_id!="":
        event = link_xml_event(seisme_id)
        if event is not None:
            if event[0] is not None:
                xml_file_path=event[0]
                title=event[1]
                time=event[2]
                mag=event[3]
                mmi=event[4]

                date = datetime.fromtimestamp(time/1000).strftime('%Y-%m-%d %H:%M:%S')            
                
                df = parse_link_grid_xml(xml_file_path)
                # Le reste du code pour la création de la carte et l'affichage des données
                sampled_df = df.sample(frac=0.05, random_state=42)
                minmmi = sampled_df["MMI"].min()
                maxmmi = sampled_df["MMI"].max()

                mmi_points_manuels=point_plus_proche(st.session_state.points_manuels,df)

                # Créer la carte avec Folium
                center_lat = sampled_df["Latitude"].mean()
                center_lon = sampled_df["Longitude"].mean()
                world_map = folium.Map(location=[center_lat, center_lon], zoom_start=5.3)

                # Ajouter un marqueur pour l'épicentre
                folium.Marker(
                    location=[center_lat, center_lon],
                    popup='Epicentre\nMMI :'+str(maxmmi),
                    icon=folium.Icon(color='black', prefix='fa', icon_size=100)
                ).add_to(world_map)

                # Ajouter les marqueurs pour les points manuels
                for (lat, lon), mmi in zip(st.session_state.points_manuels, mmi_points_manuels):
                    if mmi==0: 
                        popup_content='Hors de la zone sismique' 
                    else: 
                        popup_content = f'Point manuel\nMMI : {mmi}'
                    folium.Marker(
                        location=[lat, lon],
                        popup=popup_content,
                        icon=folium.Icon(color='darkblue', prefix='fa')
                    ).add_to(world_map)

                # Définir l'échelle de couleurs
                custom_colors = ['lightgreen', 'yellow', 'orange', 'red', 'darkred']
                color_scale = folium.LinearColormap(custom_colors, vmin=minmmi, vmax=maxmmi)

                

                # Ajouter les cercles colorés
                for index, row in sampled_df.iterrows():
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
                

            else:
                st.warning("Les informations sur les MMI et les impacts du séisme ne sont pas disponibles.")
        else:
            st.warning("L'évènemenent demandé est inconnu.")
    else :
        st.warning("Veuillez entrer un ID de séisme à étudier.")

