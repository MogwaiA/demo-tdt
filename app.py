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
from tab_eventid import carte_par_eventid
from tab_rapportseismes import rapports_seismes


st.set_page_config(
    page_title="Carte de Sismicité",
    page_icon=":earthquake:",
    layout="wide",  # Utiliser une mise en page plus large
    initial_sidebar_state="expanded",  # Barre latérale ouverte par défaut
)

tabs = {
      "Carte par séisme": carte_par_eventid,
      "Rapports": rapports_seismes
}

# Afficher les onglets
selected_tab = st.sidebar.radio("Sélectionnez un onglet", list(tabs.keys()))
tabs[selected_tab]()


