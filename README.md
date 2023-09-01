Ce fichier README a été généré le 2023-09-01 par Merwan AMIMEUR

Dernière mise-à-jour le : 2023-09-01.

# INFORMATIONS GENERALES

## Données utilisées :
Données publiques du site USGS : https://www.usgs.gov/

## Adresse de contact :
 
merwan.amimeur@gmail.com

# INFORMATIONS METHODOLOGIQUES

## Objectif du projet : 

Ce projet a pour objectif de créer une version application d'un outil d'alerting en cas de tremblement de terre.
Il se découpe en deux volet :
 - Une option pour croiser une liste de coordonnées géographiques avec les tremblements de terre ayant eu lieu.
 - Une option pour observer un tremblement de terre en particulier et vérifier si un point se situe dans le périmètre d'impact de ce dernier.

## Description des sources et méthodes utilisées pour collecter et générer les données :
Les données sont récupérer automatiquement via des requêtes sur l'API du site USGS : 
https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={start_time_str}&endtime={end_time_str}&minmmi={mmi}
Permettant de récupérer tous les tremblements de terre ayant un MMI >= mmi, et dans la période de temps définie entre start_time_str et end_time_str.

Par ailleurs, l'utilisateur peut lui-même uploader une liste de coordonnées géographiques afin de croiser avec les informations USGS.

## Méthodes de traitement des données :


## Vérifications d’assurance-qualité faites sur les données :

## Autres informations contextuelles :
<Toute information que vous considérez importante pour évaluer la qualité du jeu de données ou pour sa réutilisation : par exemple, des informations concernant les logiciels nécessaires pour interpréter les données.
Si applicable et non-inclus préalablement, ajouter les noms complets et les versions de tous les logiciels, de tous les paquets et de toutes les librairies nécessaires pour lire et interpréter les données *e.g.* pour compiler les scripts.>

# APERCUS DES DONNEES ET FICHIERS


## Convention de nommage des fichiers :

## Arborescence/plan de classement des fichiers :


# INFORMATIONS SPECIFIQUES AUX DONNEES POUR : [NOM DU FICHIER]

<Le cas échéant, reproduire cette section pour chaque dossier ou fichier.
Les éléments se répétant peuvent être expliqués dans une section initiale commune.>

<Pour les données tabulaires, fournir un dictionaire des données/manuel de codage contenant les information suivantes :>
## Liste des variables/entêtes de colonne :

Pour chaque nom de variable ou entête de colonne, indiquer :
 
	-- le nom complet de la variable sous forme “lisible par les humains” ; 
	-- la description de la variable ; 
	-- unité de mesure, si applicable ; 
	-- séparateur décimal *i.e.* virgule ou point, si applicable ; 
	-- valeurs autorisées : liste ou plage de valeurs, ou domaine ;
	-- format, si applicable, e.g. date>

## Code des valeurs manquantes : 
<Definir les codes ou symboles utilisés pour les valeurs manquantes.>

## Informations additionnelles : 
<Toute information que vous jugez utile pour mieux comprendre le fichier>
