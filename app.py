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

st.set_page_config(
    page_title="Carte de Sismicité",
    page_icon=":earthquake:",
    layout="wide",  # Utiliser une mise en page plus large
    initial_sidebar_state="expanded",  # Barre latérale ouverte par défaut
)



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
    
def point_plus_proche(liste,grid):
    liste_mmi=[]
    for lat, lon in liste:
        lat0 = lat
        lon0 = lon

        #Borne du rectangle décrit dans le grid.xml
        lat_min, lat_max = grid["Latitude"].min(), grid["Latitude"].max()
        lon_min, lon_max = grid["Longitude"].min(), grid["Longitude"].max()
        
        # Calcul des bornes du carré défini par latitude et longitude (arrondies à la dixième près)
        lat_floor, lat_roof = lat0-0.5,lat0+0.5
        lon_floor, lon_roof = lon0-0.5,lon0+0.5
        
        # Filtrage des points de la grille qui sont à l'intérieur du carré
        filtered_grid = grid[
            (grid['Latitude'] >= lat_floor) & (grid['Latitude'] <= lat_roof) &
            (grid['Longitude'] >= lon_floor) & (grid['Longitude'] <= lon_roof)
        ]
        
        if lat_min <= lat0 <= lat_max and lon_min <= lon0 <= lon_max:
            distance = cdist([(lat0, lon0)], filtered_grid[['Latitude', 'Longitude']], metric='euclidean')[0]
            index_plus_proche = filtered_grid.iloc[distance.argmin()].name
            mmi_value = filtered_grid.loc[index_plus_proche, 'MMI']
            
            liste_mmi.append(mmi_value)
        
        else:
            liste_mmi.append(0)
    return liste_mmi
    



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

# Personnalisation de la mise en page avec du code HTML
st.markdown("<h1 style='text-align: left;'>Carte de Sismicité</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: left;'>Visualisation des données de sismicité</h2>", unsafe_allow_html=True)

 seisme_id = st.text_input("Entrez l'ID du séisme :", '')

# Utilisation de colonnes pour organiser les widgets
col1, col2 = st.columns(2)
with col2:
    ajouter_point_manuellement = st.checkbox("Ajouter un point manuellement")
        # Initialiser une liste pour stocker les points ajoutés manuellement
    if 'points_manuels' not in st.session_state:
        st.session_state.points_manuels = []

    if len(st.session_state.points_manuels) > 0:
        st.subheader("Liste des points ajoutés manuellement")
        df_points_manuels = pd.DataFrame(st.session_state.points_manuels, columns=["Latitude", "Longitude"])
        st.table(df_points_manuels)

with col1:

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



        
        
# Ajouter un bouton pour démarrer la visualisation
if st.button("Visualiser"):
    
    if seisme_id is not None:
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

