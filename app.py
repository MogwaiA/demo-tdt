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

# Fonction pour parser le fichier XML et obtenir le DataFrame
def parse_file_grid_xml(xml_file_path):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    data = []

    for grid_data in root.findall('.//{http://earthquake.usgs.gov/eqcenter/shakemap}grid_data'):
        for point in grid_data.text.strip().split('\n'):
            values = point.split()
            lon, lat, mmi_value = map(float, values[:3])
            data.append((lon, lat, mmi_value))

    df = pd.DataFrame(data, columns=['Longitude', 'Latitude', 'MMI'])
    return df

def parse_link_grid_xml(lien_grid_xml,proxies=None):
    try:
        # Télécharger le contenu du lien
        response = requests.get(lien_grid_xml,proxies=proxies)
        response.raise_for_status()  # Lève une exception si la requête échoue

        contenu_xml = response.content

        # Définir les noms d'espace
        namespaces = {
            'ns': 'http://earthquake.usgs.gov/eqcenter/shakemap'
        }

        # Analyser le contenu XML
        root = ET.fromstring(contenu_xml)

        # Initialiser une liste pour stocker les données
        data = []

        # Parcourir et extraire les données
        for grid_data in root.findall('.//ns:grid_data', namespaces):
            for point in grid_data.text.strip().split('\n'):
                values = point.split()
                lon, lat, mmi_value = map(float, values[:3])
                data.append((lon, lat, mmi_value))

        # Créer un DataFrame
        df = pd.DataFrame(data, columns=['Longitude', 'Latitude', 'MMI'])

        return df
    except requests.exceptions.RequestException as e:
        print("Une erreur de requête s'est produite:", e)
        return None



def link_xml_event(id, proxies=None):
    url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&eventid={id}"
    try:
        response = requests.get(url, proxies=proxies)
        response.raise_for_status()  # Lève une exception si la requête échoue
        data = response.json()  # Convertir la réponse JSON en dictionnaire

        # Accéder aux informations nécessaires dans la structure JSON
        url = data.get('properties', {}).get('products', {}).get('shakemap', [{}])[0].get('contents', {}).get('download/grid.xml', {}).get('url', None)
        title=json.loads(response.text)['properties']["title"]
        time=json.loads(response.text)['properties']["time"]
        mag=json.loads(response.text)['properties']["mag"]
        mmi=json.loads(response.text)['properties']["mmi"]
        return url,title,time,mag,mmi
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        return None

# Charger l'application Streamlit
st.title("Carte de Sismicité")
st.subheader("Visualisation des données de sismicité")

# Ajouter un widget de saisie de texte pour l'ID du séisme
seisme_id = st.text_input("Entrez l'ID du séisme :", '')  

# Ajouter un bouton pour démarrer la visualisation
if st.button("Visualiser"):
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


            # Charger l'application Streamlit
            st.title(title)
            st.subheader("Evènement du "+ str(date) +" de magnitude "+str(mag)+" de MMI moyen "+str(mmi)+".")

            color_scale.caption = "Modified Mercalli Intensity (MMI)"
            color_scale.add_to(world_map)

            # Afficher la carte Folium dans Streamlit
            folium_static(world_map)

            # Ajouter un widget de saisie de coordonnées
            latitude_input = st.number_input("Latitude du point :", min_value=-90.0, max_value=90.0)
            longitude_input = st.number_input("Longitude du point :", min_value=-180.0, max_value=180.0)
            #nom_site = st.number_input("Nom du site :", "")

            # Ajouter un bouton pour ajouter le point à la carte
            if st.button("Ajouter le point"):
                folium.Marker(
                    location=[latitude_input, longitude_input],
                    popup='Site observé',
                    icon=folium.Icon(color='blue', prefix='fa')
                ).add_to(world_map)
            

        else:
            st.warning("Les informations sur les MMI et les impacts du séisme ne sont pas disponibles.")
    else:
        st.warning("L'évènemenent demandé est inconnu.")
