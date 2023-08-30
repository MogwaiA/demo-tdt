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