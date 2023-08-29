import streamlit as st
import pandas as pd
from streamlit_folium import folium_static
import xml.etree.ElementTree as ET
import os
import folium
import requests

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
    response = requests.get(url, proxies=proxies)
    url = json.loads(response.text)['properties']["products"]["shakemap"][0]["contents"]["download/grid.xml"]["url"]
    return url

# Construire le chemin complet du fichier que vous voulez charger
id = 'hv73287947'

xml_file_path=link_xml_event(id)

df = parse_link_grid_xml(xml_file_path)
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
    popup='Epicentre',
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

for index, row in sites.iterrows():
    lat = row["Latitude"]
    lon = row["Longitude"]
    folium.Marker(
        location=(lat, lon),
        popup='Site',
        icon=folium.Icon(color='darkred',prefix='fa')
    ).add_to(world_map)

# Charger l'application Streamlit
st.title("Carte de Sismicité")
st.subheader("Visualisation des données de sismicité")

# Afficher la carte Folium dans Streamlit
folium_static(world_map)

# Afficher l'échelle de couleurs
color_scale.caption = "Modified Mercalli Intensity (MMI)"
color_scale.add_to(world_map)
st.markdown(world_map, unsafe_allow_html=True)
