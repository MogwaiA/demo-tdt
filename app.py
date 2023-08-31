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
import carte_by_eventid


st.set_page_config(
    page_title="Carte de Sismicité",
    page_icon=":earthquake:",
    layout="wide",  # Utiliser une mise en page plus large
    initial_sidebar_state="expanded",  # Barre latérale ouverte par défaut
)

carte_by_eventid




