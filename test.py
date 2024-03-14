import requests
import folium
import branca.colormap as cm
import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
from streamlit_folium import folium_static
import urllib.request
from geopy.geocoders import BANFrance

st.write("""
# Géolocalisation des bâtiments des entreprises
## Fonds de cartes de risques physiques
""")


df_lien = pd.read_csv('https://github.com/AntoineChapron/G-olocalisation_des_entreprises/releases/download/df_lien.csv/df_lien.csv', sep=',')

state_geo = requests.get(
    "https://static.data.gouv.fr/resources/contours-des-communes-de-france-simplifie-avec-regions-et-departement-doutre-mer-rapproches/20220219-095144/a-com2022.json"
).json()
type = st.selectbox("Type :", ["Particulier","Entreprise"])

if type == "Particulier" : 
 
    @st.cache_data(hash_funcs={folium.Map: id})
    def location_risque(address,risque_phys):
        
        risque = folium.Map(location=[46.603354, 1.888334], zoom_start=6)

        if risque_phys == "Inondation":
            communes_jointure = pd.read_csv('https://github.com/AntoineChapron/G-olocalisation_des_entreprises/raw/main/communes_jointure_inon.csv', sep=',', low_memory=False)
        elif risque_phys == "Séisme":
            communes_jointure = pd.read_csv('https://github.com/AntoineChapron/G-olocalisation_des_entreprises/raw/main/communes_jointure_seis.csv', sep=',', low_memory=False)
        elif risque_phys == "Mouvement de terrain":
            communes_jointure = pd.read_csv('https://github.com/AntoineChapron/G-olocalisation_des_entreprises/raw/main/communes_jointure_mouv.csv', sep=',', low_memory=False)
        elif risque_phys == "Sécheresse":
            communes_jointure = pd.read_csv('https://github.com/AntoineChapron/G-olocalisation_des_entreprises/raw/main/communes_jointure_sech.csv', sep=',', low_memory=False)
        elif risque_phys == "Tempête":
            communes_jointure = pd.read_csv('https://github.com/AntoineChapron/G-olocalisation_des_entreprises/raw/main/communes_jointure_temp.csv', sep=',', low_memory=False)
        else:
            raise ValueError("Le paramètre risque_phys doit être 'inon','seis','mouv','sech' ou 'temp'.")

        communes_jointure['code_commune'] = communes_jointure['cod_commune'].astype(str)

        folium.Choropleth(
            geo_data=state_geo,
            name="Risque",
            data= communes_jointure,
            columns=["cod_commune", "classe_ris"],
            key_on="feature.properties.codgeo",
            fill_color="Reds",
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name="Classes de risque",
            ).add_to(risque)

        folium.LayerControl().add_to(risque)

        if address:
            # Géocodage de l'adresse saisie
            geolocator = BANFrance(user_agent="monapplicartecalanguedoc")
            location = geolocator.geocode(address)
            address_parts = location.address.split(' ')
            location = location[1]
            jointure = pd.read_csv('https://github.com/AntoineChapron/G-olocalisation_des_entreprises/raw/main/jointure.csv',sep=',')

            moyenne = jointure[jointure["lib_commune"] == address_parts[-1]]

            moyenne_fin = [["Risque", "Inondation", "Mouvement de terrain", "Sécheresse", "Séisme", "Tempête"],
                ["Moyenne /5", round(moyenne['classe_ris_inon'].mean(),2) , round(moyenne['classe_ris_mouv'].mean(),2), 
                round(moyenne['classe_ris_sech'].mean(),2), round(moyenne['classe_ris_seis'].mean(),2), round(moyenne['classe_ris_temp'].mean(),2)]]
            moyenne_fin = pd.DataFrame(moyenne_fin)
            if location:
                  st.success(f"L'adresse {address} a été trouvée.")
                  st.write("Latitude :", location[0])
                  st.write("Longitude :", location[1])

                 # Affichage de la carte Folium
                  folium.Circle(location, popup=address).add_to(risque)
                  return(moyenne_fin,risque)
            else:
                st.error("Adresse non trouvée. Veuillez vérifier votre saisie.")
        else:
              st.warning("Veuillez saisir une adresse.")

    risque_phys = st.selectbox("Sélection du risque:", ["Inondation", "Mouvement de terrain", "Sécheresse","Séisme",'Tempête'])
    
    address = st.text_input("Adresse postale :")

    
    
    if st.button("Submit"):
        moyenne_fin, risque = location_risque(address, risque_phys)
        st.write("### Risque")
        st.write(moyenne_fin)
        st.write("## Carte interactive")
        folium_static(risque)
    
    
    
    
else :
    @st.cache(suppress_st_warning = True)
    def batiments_risque(numero_siren,risque_phys):
        risque = folium.Map(location=[46.603354, 1.888334], zoom_start=6)

        if risque_phys == "Inondation":
            communes_jointure = pd.read_csv('https://github.com/AntoineChapron/G-olocalisation_des_entreprises/raw/main/communes_jointure_inon.csv', sep=',', low_memory=False)
        elif risque_phys == "Séisme":
            communes_jointure = pd.read_csv('https://github.com/AntoineChapron/G-olocalisation_des_entreprises/raw/main/communes_jointure_seis.csv', sep=',', low_memory=False)
        elif risque_phys == "Mouvement de terrain":
            communes_jointure = pd.read_csv('https://github.com/AntoineChapron/G-olocalisation_des_entreprises/raw/main/communes_jointure_mouv.csv', sep=',', low_memory=False)
        elif risque_phys == "Sécheresse":
            communes_jointure = pd.read_csv('https://github.com/AntoineChapron/G-olocalisation_des_entreprises/raw/main/communes_jointure_sech.csv', sep=',', low_memory=False)
        elif risque_phys == "Tempête":
            communes_jointure = pd.read_csv('https://github.com/AntoineChapron/G-olocalisation_des_entreprises/raw/main/communes_jointure_temp.csv', sep=',', low_memory=False)
        else:
            raise ValueError("Le paramètre risque_phys doit être 'inon','seis','mouv','sech' ou 'temp'.")

        communes_jointure['code_commune'] = communes_jointure['cod_commune'].astype(str)

        folium.Choropleth(
            geo_data=state_geo,
            name="Risque",
            data= communes_jointure,
            columns=["cod_commune", "classe_ris"],
            key_on="feature.properties.codgeo",
            fill_color="Reds",
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name="Classes de risque",
            ).add_to(risque)

        folium.LayerControl().add_to(risque)
 
        # URL de téléchargement du fichier HDF5 sur GitHub (vous pouvez le remplacer par le chemin local après le téléchargement)
        url_hdf5 = 'https://github.com/AntoineChapron/G-olocalisation_des_entreprises/releases/download/geoloc/geoloc_etabli_siren.h5'

        # Téléchargez le fichier HDF5 localement
        filename_hdf5 = 'geoloc_etabli_siren.h5'
        st.write("Téléchargement du fichier HDF5...")
        with st.spinner('Téléchargement en cours...'):
            urllib.request.urlretrieve(url_hdf5, filename_hdf5)

        # Lisez le fichier HDF5
        data_used = pd.read_hdf(filename_hdf5, 'results_table', where=['siren = "{}"'.format(numero_siren)])
        #data_used = pd.read_hdf('https://github.com/AntoineChapron/G-olocalisation_des_entreprises/releases/download/geoloc/geoloc_etabli_siren.h5', 'results_table', where=['siren = "{}"'.format(numero_siren)])
        data_used['plg_code_commune'] = data_used['plg_code_commune'].astype(str)

        data_used = pd.merge(data_used, df_lien, on="siret", how="inner" )

        resultat_used = pd.merge(data_used, communes_jointure, left_on='plg_code_commune',right_on='cod_commune', how='inner')

        resultat_used = resultat_used[['lib_commune','y_latitude','x_longitude','dat_deb','dat_fin','classe_ris']]
    
    

        for index, row in resultat_used.iterrows():
            folium.Circle([row['y_latitude'], row['x_longitude']], popup = row['lib_commune']).add_to(risque)

        jointure = pd.read_csv('https://github.com/AntoineChapron/G-olocalisation_des_entreprises/raw/main/jointure.csv',sep=',')

        moy_used = pd.merge(data_used, jointure, left_on='plg_code_commune',right_on='cod_commune', how='inner')

        moy_used = moy_used.drop_duplicates(subset='cod_commune', keep='first')

        moyenne = [["Risque", "Inondation", "Mouvement de terrain", "Sécheresse", "Séisme", "Tempête"],
            ["Moyenne /5", round(moy_used['classe_ris_inon'].mean(),2) , round(moy_used['classe_ris_mouv'].mean(),2), 
             round(moy_used['classe_ris_sech'].mean(),2), round(moy_used['classe_ris_seis'].mean(),2), round(moy_used['classe_ris_temp'].mean(),2)]]
        moyenne = pd.DataFrame(moyenne)
        return(st.write("### Risque"),st.write(moyenne),st.write("## Carte interactive"),folium_static(risque), st.write("Base de données utilisée"),st.write(resultat_used))




    # Zone de saisie pour le numéro SIREN
    numero_siren = st.text_input("numéro SIREN (format XXXXXXXXX):")

    # Menu déroulant pour sélectionner le risque
    risque_phys = st.selectbox("Sélection du risque:", ["Inondation", "Mouvement de terrain", "Sécheresse","Séisme",'Tempête'])  # Remplacer par vos propres risques

    # Bouton pour générer la carte
    if st.button("Submit"):
        batiments_risque(numero_siren,risque_phys)





