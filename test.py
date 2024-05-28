import requests
import folium
import branca.colormap as cm
import streamlit as st
import pandas as pd
from streamlit_folium import folium_static
import urllib.request
from geopy.geocoders import BANFrance
from shapely.geometry import Point
import numpy as np 
import matplotlib.cm as cm
import matplotlib.colors as colors
import geopandas as gpd

st.markdown(
    """
    <style>
    .centered-title {
        text-align: center;
        font-size: 50px;
        font-weight: bold;
    }
    </style>
    <div class="centered-title">
        CatMap
    </div>
    """,
    unsafe_allow_html=True
)
st.write("""
# Géolocalisation des bâtiments des entreprises
## Fonds de cartes de risques physiques
""")

@st.cache_data
def get_state_geo_data():
    # Effectuer la requête HTTP pour obtenir les données JSON et les retourner
    return requests.get("https://static.data.gouv.fr/resources/contours-des-communes-de-france-simplifie-avec-regions-et-departement-doutre-mer-rapproches/20220219-095144/a-com2022.json").json()

# Charger les données JSON une seule fois au démarrage de l'application
state_geo = get_state_geo_data()


@st.cache_data
def get_df_lien():
    return pd.read_csv('https://github.com/AntoineChapron/G-olocalisation_des_entreprises/releases/download/df_lien.csv/df_lien.csv', sep=',')
df_lien = get_df_lien()

#df_lien = pd.read_csv('https://github.com/AntoineChapron/G-olocalisation_des_entreprises/releases/download/df_lien.csv/df_lien.csv', sep=',')

#state_geo = requests.get(
#    "https://static.data.gouv.fr/resources/contours-des-communes-de-france-simplifie-avec-regions-et-departement-doutre-mer-rapproches/20220219-095144/a-com2022.json"
#).json()



type2 = st.selectbox("Souhaitez-vous afficher des cartes prédictives ? :", ["Oui","Non"])
type = st.selectbox("Type :", ["Particulier","Entreprise"])
if type2 == "Non" :
    st.write("Pour chaque risque physique un score sur 5 est calculé en fonction du nombre de fois où ces catastrophes naturelles se sont produites par commune depuis le 15 août 1985. On utilise les données de la base GASPAR pour obtenir l'historique par commune. Pour les entreprises possédant plusieurs bâtiments dans plusieurs communes on fait la moyenne des scores des communes pour obtenir un score sur 5 par risque physique pour l'entreprise.")
    if type == "Particulier" : 
 
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
                line_opacity=0,
                legend_name="Classes de risque",
                ).add_to(risque)

            folium.LayerControl().add_to(risque)

            if address:
                # Géocodage de l'adresse saisie
                geolocator = BANFrance(user_agent="monapplicartecalanguedoc")
                location = geolocator.geocode(address)
                com_loc = location.raw.get('properties', {}).get('city')
                location = location[1]
                jointure = pd.read_csv('https://github.com/AntoineChapron/G-olocalisation_des_entreprises/raw/main/jointure.csv',sep=',')

                historique = communes_jointure.drop_duplicates()
                historique = historique[historique["lib_commune"] == com_loc]
                historique = historique[['lib_commune','dat_deb','dat_fin','classe_ris']]
                
                moyenne = jointure[jointure["lib_commune"] == com_loc]

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
                    return(moyenne_fin,risque,historique)
                else:
                    st.error("Adresse non trouvée. Veuillez vérifier votre saisie.")
            else:
                st.warning("Veuillez saisir une adresse.")

        risque_phys = st.selectbox("Sélection du risque:", ["Inondation", "Mouvement de terrain", "Sécheresse","Séisme",'Tempête'])
    
        address = st.text_input("Adresse postale :")

    
    
        if st.button("Submit"):
            moyenne_fin, risque, historique = location_risque(address, risque_phys)
            st.write("### Risque")
            st.write(moyenne_fin)
            st.write("## Carte interactive")
            folium_static(risque)
            st.write("Historique")
            st.write(historique)
    
    
    
    
    else :
        @st.cache_data
        def download_hdf5_file():
            # URL de téléchargement du fichier HDF5 sur GitHub (vous pouvez le remplacer par le chemin local après le téléchargement)
            url_hdf5 = 'https://github.com/AntoineChapron/G-olocalisation_des_entreprises/releases/download/geoloc_etabli/geoloc_etabli_siren.h5'

            # Téléchargez le fichier HDF5 localement
            filename_hdf5 = 'geoloc_etabli_siren.h5'
            st.write("Téléchargement du fichier HDF5...")
            with st.spinner('Téléchargement en cours...'):
                urllib.request.urlretrieve(url_hdf5, filename_hdf5)
            return filename_hdf5

        filename_hdf5 = download_hdf5_file()

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
 
        
            # Lire le fichier HDF5
            data_used = pd.read_hdf(filename_hdf5, 'results_table', where=['siren = "{}"'.format(numero_siren)])
            #data_used = pd.read_hdf('https://github.com/AntoineChapron/G-olocalisation_des_entreprises/releases/download/geoloc/geoloc_etabli_siren.h5', 'results_table', where=['siren = "{}"'.format(numero_siren)])
            data_used['plg_code_commune'] = data_used['plg_code_commune'].astype(str)

            data_used = pd.merge(data_used, df_lien, on="siret", how="inner" )

            resultat_used = pd.merge(data_used, communes_jointure, left_on='plg_code_commune',right_on='cod_commune', how='inner')

            resultat_used = resultat_used[['lib_commune','y_latitude','x_longitude','dat_deb','dat_fin','classe_ris']]
            resultat_used = resultat_used.drop_duplicates()
    

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


if type2 == "Oui" :

    type3 = st.selectbox("Sélection du risque :", ["Incendies","Submersion"])
    if type3 == "Incendies" :
        st.write("Pour avoir des valeurs prédictives on utilise les données de la base Copernicus. Ici la variable représente le nombre de jours par année et par raster à risque d'incendie élevé. On propose à l'utilisateur de choisir parmi 3 différents scénarios RCP et parmi 2 valeurs (mean et worst case). Ces valeurs représentent respectivement la moyenne et le pire des cas calculés par une combinaison de différents modèles climatiques.")
        st.write("Les 3 scénarios RCP (Representative Concentration Pathway) sont des scénarios de trajectoire du forçage radiatif jusqu'à l'horizon 2100. Ils permettent de modéliser le climat futur et représentent donc +2,6 W/m² pour le scénario RCP 2.6 et ainsi de suite. Ils sont des scénarios d’émission de gaz à effet de serre.")
        if type == "Particulier" : 
    
            def map_prev_inc(year, scenario, address):
                # Charger les données de la base de données
                if scenario == "Rcp 2.6 moyenne":
                    df_entier = pd.read_csv('https://github.com/AntoineChapron/G-olocalisation_des_entreprises/raw/main/scenario_inc/final_bdd_inc_rcp26.csv', sep=',', low_memory=False)
                elif scenario == "Rcp 4.5 moyenne":
                    df_entier = pd.read_csv('https://github.com/AntoineChapron/G-olocalisation_des_entreprises/raw/main/scenario_inc/final_bdd_inc_rcp45.csv', sep=',', low_memory=False)
                elif scenario == "Rcp 8.5 moyenne":
                    df_entier = pd.read_csv('https://github.com/AntoineChapron/G-olocalisation_des_entreprises/raw/main/scenario_inc/final_bdd_inc_rcp85.csv', sep=',', low_memory=False)
                elif scenario == "Rcp 2.6 worst case":
                    df_entier = pd.read_csv('https://github.com/AntoineChapron/G-olocalisation_des_entreprises/raw/main/scenario_inc/final_bdd_inc_rcp26wc.csv', sep=',', low_memory=False)
                elif scenario == "Rcp 4.5 worst case":
                    df_entier = pd.read_csv('https://github.com/AntoineChapron/G-olocalisation_des_entreprises/raw/main/scenario_inc/final_bdd_inc_rcp45wc.csv', sep=',', low_memory=False)
                elif scenario == "Rcp 8.5 worst case":
                    df_entier = pd.read_csv('https://github.com/AntoineChapron/G-olocalisation_des_entreprises/raw/main/scenario_inc/final_bdd_inc_rcp85wc.csv', sep=',', low_memory=False)
                else:
                    raise ValueError("Le paramètre risque_phys doit être 'inon','seis','mouv','sech' ou 'temp'.")
                
                
                #Charger l'historique des catnat dans la commune
                
                histo_concat = pd.read_csv('https://github.com/AntoineChapron/G-olocalisation_des_entreprises/raw/main/histo_concat.csv')
                
                
                #df_entier = pd.read_csv(f'C:/Users/antoine.chapron_adwa/Documents/geoloc_sites/final_bdd_inc_{scenario}.csv', sep=',')
                df_entier = df_entier.rename(columns={df_entier.columns[1]: 'nb_jours'})
                df_entier['time_bnds'] = pd.to_datetime(df_entier['time_bnds'])
                df = df_entier[df_entier['time_bnds'].dt.year == year]
                df.reset_index(drop=True, inplace=True)
    
                # Charger les données de contours géographiques de la France
                france_gdf = gpd.read_file('https://github.com/AntoineChapron/G-olocalisation_des_entreprises/raw/main/france-detailed-boundary_911.geojson')
    
                # Créer un GeoDataFrame contenant les points à vérifier
                points_gdf = gpd.GeoDataFrame(geometry=[Point(lon, lat) for lon, lat in zip(df['lon'], df['lat'])])
    
                # Vérifier si chaque point est à l'intérieur des frontières de la France
                points_inside_france = gpd.sjoin(points_gdf, france_gdf, how="inner", op='within')
    
                # Convertir les index des lignes de points_inside_france en une liste
                indices_points_france = points_inside_france.index.tolist()
    
                # Filtrer france_df pour ne garder que les lignes correspondant aux points à l'intérieur des frontières de la France
                france_df_filtered = df.iloc[indices_points_france]
    
                # Calculer la latitude et la longitude de l'adresse saisie
                geolocator = BANFrance(user_agent="monapplicartecalanguedoc")
                location = geolocator.geocode(address)
                
                # Garder l'historque sur la commune concernée
                com_loc = location.raw.get('properties', {}).get('city')
                histo_concat = histo_concat[histo_concat["lib_commune"] == com_loc]
                
                if location:
                    address_lat, address_lon = location.latitude, location.longitude
        
                    # Créer une carte Folium
                    m = folium.Map(location=[46,2], zoom_start=6)
                    norm = colors.Normalize(vmin=0, vmax=241)
                    cmap = cm.OrRd
        
                    # Dessiner des carrés pour représenter chaque raster avec une couleur relative au nombre de jours à risque d'incendie élevé
                    for index, row in france_df_filtered.iterrows():
                        color = colors.rgb2hex(cmap(norm(row['nb_jours'])))
                        folium.Rectangle(bounds=[(row['lat'] - 0.060, row['lon'] - 0.080), 
                                      (row['lat'] + 0.060, row['lon'] + 0.080)],
                             color=color,
                             fill_color=color,
                             fill_opacity=0.7,
                             fill=True,
                             stroke=False,
                             popup=str(row['nb_jours'])).add_to(m)

                    # Ajouter un marqueur pour l'adresse saisie
                    folium.Circle([address_lat, address_lon], popup=address).add_to(m)
        
                    # Trouver le point le plus proche de l'adresse saisie
                    nearest_point = france_df_filtered.iloc[np.argmin(np.sqrt((france_df_filtered['lat'] - address_lat)**2 + (france_df_filtered['lon'] - address_lon)**2))]
                    nb_jours = nearest_point['nb_jours']
        
                    return (st.write("## Nombre de jours à risque d'incendie :"),st.write(nb_jours),st.write("## Carte interactive"),folium_static(m), st.write("Historique"), st.write(histo_concat))
                else:
                    print("Adresse non trouvée. Veuillez vérifier votre saisie.")
                    return None, None
    

            scenario = st.selectbox("Sélection du scénario:", ["Rcp 2.6 moyenne", "Rcp 4.5 moyenne", "Rcp 8.5 moyenne","Rcp 2.6 worst case","Rcp 4.5 worst case","Rcp 8.5 worst case"])
            year = st.selectbox("Année:", [2010,2020,2030,2040,2050,2060,2070,2080,2090,2098])
            address = st.text_input("Adresse postale :")
    
            if st.button("Submit"):
                map_prev_inc(year,scenario,address)
    
    
    
        if type == "Entreprise" : 
            @st.cache_data
            def download_hdf5_file():
                # URL de téléchargement du fichier HDF5 sur GitHub (vous pouvez le remplacer par le chemin local après le téléchargement)
                url_hdf5 = 'https://github.com/AntoineChapron/G-olocalisation_des_entreprises/releases/download/geoloc_etabli/geoloc_etabli_siren.h5'

                # Téléchargez le fichier HDF5 localement
                filename_hdf5 = 'geoloc_etabli_siren.h5'
                st.write("Téléchargement du fichier HDF5...")
                with st.spinner('Téléchargement en cours...'):
                    urllib.request.urlretrieve(url_hdf5, filename_hdf5)
                return filename_hdf5

            filename_hdf5 = download_hdf5_file()

            def map_prev_inc_ent(year, scenario, numero_siren):
                # Charger les données de la base de données
                if scenario == "Rcp 2.6 moyenne":
                    df_entier = pd.read_csv('https://github.com/AntoineChapron/G-olocalisation_des_entreprises/raw/main/scenario_inc/final_bdd_inc_rcp26.csv', sep=',', low_memory=False)
                elif scenario == "Rcp 4.5 moyenne":
                    df_entier = pd.read_csv('https://github.com/AntoineChapron/G-olocalisation_des_entreprises/raw/main/scenario_inc/final_bdd_inc_rcp45.csv', sep=',', low_memory=False)
                elif scenario == "Rcp 8.5 moyenne":
                    df_entier = pd.read_csv('https://github.com/AntoineChapron/G-olocalisation_des_entreprises/raw/main/scenario_inc/final_bdd_inc_rcp85.csv', sep=',', low_memory=False)
                elif scenario == "Rcp 2.6 worst case":
                    df_entier = pd.read_csv('https://github.com/AntoineChapron/G-olocalisation_des_entreprises/raw/main/scenario_inc/final_bdd_inc_rcp26wc.csv', sep=',', low_memory=False)
                elif scenario == "Rcp 4.5 worst case":
                    df_entier = pd.read_csv('https://github.com/AntoineChapron/G-olocalisation_des_entreprises/raw/main/scenario_inc/final_bdd_inc_rcp45wc.csv', sep=',', low_memory=False)
                elif scenario == "Rcp 8.5 worst case":
                    df_entier = pd.read_csv('https://github.com/AntoineChapron/G-olocalisation_des_entreprises/raw/main/scenario_inc/final_bdd_inc_rcp85wc.csv', sep=',', low_memory=False)
                else:
                    raise ValueError("Le paramètre risque_phys doit être 'inon','seis','mouv','sech' ou 'temp'.")
                #df_entier = pd.read_csv(f'C:/Users/antoine.chapron_adwa/Documents/geoloc_sites/final_bdd_inc_{scenario}.csv', sep=',')
                df_entier = df_entier.rename(columns={df_entier.columns[1]: 'nb_jours'})
                df_entier['time_bnds'] = pd.to_datetime(df_entier['time_bnds'])
                df = df_entier[df_entier['time_bnds'].dt.year == year]
                df.reset_index(drop=True, inplace=True)
    
                # Charger les données de contours géographiques de la France
                france_gdf = gpd.read_file('https://github.com/AntoineChapron/G-olocalisation_des_entreprises/raw/main/france-detailed-boundary_911.geojson')
    
                # Créer un GeoDataFrame contenant les points à vérifier
                points_gdf = gpd.GeoDataFrame(geometry=[Point(lon, lat) for lon, lat in zip(df['lon'], df['lat'])])
    
                # Vérifier si chaque point est à l'intérieur des frontières de la France
                points_inside_france = gpd.sjoin(points_gdf, france_gdf, how="inner", op='within')
    
                # Convertir les index des lignes de points_inside_france en une liste
                indices_points_france = points_inside_france.index.tolist()
    
                # Filtrer france_df pour ne garder que les lignes correspondant aux points à l'intérieur des frontières de la France
                france_df_filtered = df.iloc[indices_points_france]
    
    
                # Créer une carte Folium
                m = folium.Map(location=[46,2], zoom_start=6)
                norm = colors.Normalize(vmin=0, vmax=241)
                cmap = cm.OrRd
        
                # Dessiner des carrés pour représenter chaque raster avec une couleur relative au nombre de jours à risque d'incendie élevé
                for index, row in france_df_filtered.iterrows():
                    color = colors.rgb2hex(cmap(norm(row['nb_jours'])))
                    folium.Rectangle(bounds=[(row['lat'] - 0.060, row['lon'] - 0.080), 
                                      (row['lat'] + 0.060, row['lon'] + 0.080)],
                                    color=color,
                                    fill_color=color,
                                    fill_opacity=0.7,
                                    fill=True,
                                    stroke=False,
                                    popup=str(row['nb_jours'])).add_to(m)

                #df_lien = pd.read_csv('C:/Users/antoine.chapron_adwa/Documents/geoloc_sites/df_lien.csv', sep=',')
                data_used = pd.read_hdf(filename_hdf5, 'results_table', where=['siren = "{}"'.format(numero_siren)])            
                data_used['plg_code_commune'] = data_used['plg_code_commune'].astype(str)
                data_used = pd.merge(data_used, df_lien, on="siret", how="inner" )
                communes_jointure = pd.read_csv('https://github.com/AntoineChapron/G-olocalisation_des_entreprises/raw/main/communes_jointure_seis.csv', sep=',', low_memory=False)
                resultat_used = pd.merge(data_used, communes_jointure, left_on='plg_code_commune',right_on='cod_commune', how='inner')
                
                # Historique catnat sur les communes concernées
                histo_concat = pd.read_csv('https://github.com/AntoineChapron/G-olocalisation_des_entreprises/raw/main/histo_concat.csv')
                
                histo_concat = pd.merge(histo_concat,data_used, left_on='cod_commune', right_on='plg_code_commune', how='inner').dropna()
                
                histo_concat = histo_concat[['lib_commune','lib_risque_jo','y_latitude','x_longitude','dat_deb','dat_fin']]
                
                #Affichage des points
                for index, row in resultat_used.iterrows():
                            folium.Circle([row['y_latitude'], row['x_longitude']], popup = row['lib_com']).add_to(m)
                return(st.write("## Carte interactive"),folium_static(m), st.write("Historique"), st.write(histo_concat))
        
        
            # Zone de saisie pour le numéro SIREN
            numero_siren = st.text_input("numéro SIREN (format XXXXXXXXX):")

            scenario = st.selectbox("Sélection du scénario:", ["Rcp 2.6 moyenne", "Rcp 4.5 moyenne", "Rcp 8.5 moyenne","Rcp 2.6 worst case","Rcp 4.5 worst case","Rcp 8.5 worst case"])
        
            year = st.selectbox("Année:", [2010,2020,2030,2040,2050,2060,2070,2080,2090,2098])

            # Bouton pour générer la carte
            if st.button("Submit"):
                map_prev_inc_ent(year, scenario, numero_siren)

    if type3 == "Submersion" :
        def map_prev_sub() :
            return(st.write("In progress"))
        
        if st.button("Submit"):
                map_prev_sub()
        


