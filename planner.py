##########################################################################################
# PLANIFICATEUR DE PLONGÉE
# Auteur: Jérôme Lehuen
# Version: 0.4 (15/09/2025)
##########################################################################################

import streamlit as st
import pandas as pd
import numpy as np
import os

##########################################################################################
# Configuration de la page
##########################################################################################

st.set_page_config(
    page_title="Planificateur de Plongée MN90",
    page_icon="🤿",
    layout="wide"
)

##########################################################################################
# Feuille de style CSS
##########################################################################################

st.markdown("""
<style>

    h1 { 
        font-size: 1.8rem !important; 
        margin-bottom: 0.5rem !important; 
        margin-top: 1.5rem !important;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%) !important;
        color: white !important;
        padding: 1rem !important;
        border-radius: 0.5rem !important;
        text-align: center !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
    h2 { 
        font-size: 1.3rem !important; 
        margin-bottom: 0.4rem !important; 
        margin-top: 0.6rem !important;
        background-color: #d1ecf1 !important;
        color: #0c5460 !important;
        padding: 0.8rem !important;
        border-radius: 0.5rem !important;
        text-align: center !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        border: 1px solid #bee5eb !important;
    }
    h3 { 
        font-size: 1.1rem !important; 
        margin-bottom: 0.3rem !important; 
        margin-top: 0.4rem !important;
    }
    
    [data-testid="metric-container"] {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 0.3rem 0.5rem;
        border-radius: 0.25rem;
        margin: 0.15rem 0;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        font-size: 0.8rem !important;
        font-weight: normal !important;
    }
    
    [data-testid="metric-container"] [data-testid="metric-label"] {
        font-size: 0.8rem !important;
    }
    
    .block-container { 
        padding-top: 1rem !important; 
        padding-bottom: 1rem !important;
    }
    
    .stAlert { 
        margin: 0.1rem 0 !important; 
        padding: 0.3rem !important; 
        font-size: 0.9rem !important;
    }
    
    .stSuccess, .stError, .stWarning, .stInfo { 
        margin: 0.05rem 0 !important; 
        padding: 0.25rem !important;
    }
    
    .stSlider { margin: 0.2rem 0 !important; }
    
    .stMarkdown { margin: 0.3rem 0 !important; }
    
    .stDataFrame { margin: 0.5rem 0 !important; }
    
    .stButton > button { 
        padding: 0.3rem 0.8rem !important; 
        margin: 0.2rem 0 !important;
    }
    
    .streamlit-expanderHeader { padding: 0.3rem !important; }
    
    .sidebar .sidebar-content { padding: 0.5rem 0.3rem; }
    
    .stColumn { padding: 0 0.5rem; }

</style>
""", unsafe_allow_html=True)

##########################################################################################
# Fonctions de calcul
##########################################################################################

@st.cache_data
def load_mn90_tables():
    """Charge les tables MN90 depuis le fichier CSV"""
    try:
        if os.path.exists('mn90_1.csv'):
            df = pd.read_csv('mn90_1.csv')
            return df
        else:
            st.error("Fichier mn90_1.csv non trouvé")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Erreur lors du chargement : {e}")
        return pd.DataFrame()

@st.cache_data
def load_azote_table():
    """Charge la table d'azote résiduelle depuis le fichier CSV"""
    try:
        if os.path.exists('mn90_2.csv'):
            df = pd.read_csv('mn90_2.csv', index_col='GPS')
            return df
        else:
            st.error("Fichier mn90_2.csv non trouvé")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Erreur lors du chargement de la table azote : {e}")
        return pd.DataFrame()

@st.cache_data
def load_majoration_table():
    """Charge la table de majoration depuis le fichier CSV"""
    try:
        if os.path.exists('mn90_3.csv'):
            df = pd.read_csv('mn90_3.csv')
            return df
        else:
            st.error("Fichier mn90_3.csv non trouvé")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Erreur lors du chargement de la table majoration : {e}")
        return pd.DataFrame()

def lookup_decompression(depth, duration, mn90_tables):
    """Recherche les paramètres de décompression dans les tables MN90"""
    try:
        if mn90_tables.empty:
            return {'15m': 0, '12m': 0, '9m': 0, '6m': 0, '3m': 0, 'gps': '', 'error': True}
        
        mask = (
            (depth > mn90_tables['P1']) & 
            (depth <= mn90_tables['P2']) & 
            (duration > mn90_tables['D1']) & 
            (duration <= mn90_tables['D2'])
        )
        
        matching_rows = mn90_tables[mask]
        
        if matching_rows.empty:
            st.warning(f"Aucune correspondance trouvée pour {depth}m / {duration}min")
            return {'15m': 0, '12m': 0, '9m': 0, '6m': 0, '3m': 0, 'gps': '', 'error': True}
        
        row = matching_rows.iloc[0]
        
        return {
            '15m': int(row['15m']) if pd.notna(row['15m']) else 0,
            '12m': int(row['12m']) if pd.notna(row['12m']) else 0,
            '9m': int(row['9m']) if pd.notna(row['9m']) else 0,
            '6m': int(row['6m']) if pd.notna(row['6m']) else 0,
            '3m': int(row['3m']) if pd.notna(row['3m']) else 0,
            'gps': str(row['GPS']) if pd.notna(row['GPS']) else '',
            'error': False
        }
        
    except Exception as e:
        st.error(f"Erreur dans la recherche de décompression : {e}")
        return {'15m': 0, '12m': 0, '9m': 0, '6m': 0, '3m': 0, 'gps': '', 'error': True}

def lookup_azote_residuel(gps, intervalle_surface, azote_table):
    """
    Recherche l'azote résiduelle dans la table MN90
    Utilise l'intervalle immédiatement inférieur si l'intervalle exact n'existe pas
    """
    try:
        if azote_table.empty:
            return {'azote': 0, 'error': True, 'message': 'Table azote non chargée'}
        
        # Vérifier que le GPS existe
        if gps not in azote_table.index:
            return {'azote': 0, 'error': True, 'message': f'GPS {gps} non trouvé dans la table'}
        
        # Obtenir la liste des intervalles disponibles (colonnes)
        intervalles_disponibles = [int(col) for col in azote_table.columns if col.isdigit()]
        intervalles_disponibles.sort()
        
        # Si l'intervalle exact existe, l'utiliser
        if intervalle_surface in intervalles_disponibles:
            azote_value = azote_table.loc[gps, str(intervalle_surface)]
            return {
                'azote': float(azote_value) if azote_value != 0 else 0,
                'intervalle_utilise': intervalle_surface,
                'methode': 'exact',
                'error': False,
                'message': f'Azote résiduelle pour GPS {gps} et intervalle {intervalle_surface}min'
            }
        
        # Trouver l'intervalle immédiatement inférieur (logique MN90)
        intervalle_inferieur = None
        for intervalle in reversed(intervalles_disponibles):
            if intervalle < intervalle_surface:  # Strictement inférieur
                intervalle_inferieur = intervalle
                break
        
        if intervalle_inferieur is not None:
            azote_value = azote_table.loc[gps, str(intervalle_inferieur)]
            # Vérifier si la valeur est 0 (au-delà de la limite de la table)
            if azote_value == 0:
                return {
                    'azote': 0,
                    'error': True,
                    'message': f'Intervalle de surface trop long ({intervalle_surface}min) - Au-delà des limites de la table MN90'
                }
            
            return {
                'azote': float(azote_value),
                'intervalle_utilise': intervalle_inferieur,
                'methode': 'inférieur',
                'error': False,
                'message': f'Azote résiduelle pour GPS {gps} (intervalle {intervalle_inferieur}min utilisé pour {intervalle_surface}min)'
            }
        
        # Intervalle trop court (inférieur au minimum de la table)
        return {
            'azote': 0,
            'error': True,
            'message': f'Intervalle de surface trop court ({intervalle_surface}min) - Minimum dans la table: {min(intervalles_disponibles)}min'
        }
        
    except Exception as e:
        return {'azote': 0, 'error': True, 'message': f'Erreur lors de la recherche d\'azote résiduelle : {e}'}

def lookup_majoration_from_tables(azote_residuel, profondeur, majo_table):
    """
    Recherche la majoration dans la table majo.csv selon les règles MN90
    """
    try:
        if majo_table.empty:
            return {'majoration': 0, 'error': True, 'message': 'Table majoration non chargée'}
        
        # Trouver la ligne : valeur MAJO égale ou juste supérieure à l'azote résiduel
        lignes_valides = majo_table[majo_table['MAJO'] >= azote_residuel]
        if lignes_valides.empty:
            return {'majoration': 0, 'error': True, 'message': f'Azote résiduelle trop élevée ({azote_residuel}) - Au-delà des limites de la table'}
        
        # Prendre la première ligne (valeur minimale >= azote_residuel)
        ligne_selectionnee = lignes_valides.iloc[0]
        majo_utilisee = ligne_selectionnee['MAJO']
        
        # Trouver la colonne : profondeur égale ou juste supérieure
        colonnes_profondeur = [col for col in majo_table.columns if col != 'MAJO' and col.isdigit()]
        colonnes_profondeur_int = [int(col) for col in colonnes_profondeur]
        colonnes_profondeur_int.sort()
        
        colonne_selectionnee = None
        for prof in colonnes_profondeur_int:
            if prof >= profondeur:
                colonne_selectionnee = str(prof)
                break
        
        if colonne_selectionnee is None:
            return {'majoration': 0, 'error': True, 'message': f'Profondeur trop importante ({profondeur}m) - Au-delà des limites de la table'}
        
        # Extraire la valeur de majoration
        majoration_value = ligne_selectionnee[colonne_selectionnee]
        
        return {
            'majoration': int(majoration_value),
            'majo_utilisee': majo_utilisee,
            'profondeur_utilisee': int(colonne_selectionnee),
            'error': False,
            'message': f'Majoration trouvée : {int(majoration_value)}min (MAJO:{majo_utilisee}, Prof:{colonne_selectionnee}m)'
        }
        
    except Exception as e:
        return {'majoration': 0, 'error': True, 'message': f'Erreur lors de la recherche de majoration : {e}'}

def calculate_air_consumption_excel_method(depth, duration, sac, ascent_speed, decompression_stops):
    """Calcul de la consommation d'air"""
    try:
        if depth <= 0 or duration <= 0 or sac <= 0:
            return {'error': 'Paramètres invalides'}
        
        # Pressions et consommations de base
        pressure_max = (depth / 10) + 1
        conso_max = sac * pressure_max
        conso_mi_prof = sac * (depth / 20 + 1)
        
        # Volume consommé pendant les paliers
        volume_paliers = 0
        duree_paliers = 0
        palier_details = []
        
        for depth_stop, time_stop in decompression_stops.items():
            if depth_stop not in ['error', 'gps'] and time_stop > 0 and depth_stop.endswith('m'):
                stop_depth = int(depth_stop.replace('m', ''))
                pressure_palier = (stop_depth / 10) + 1
                conso_litres_min = sac * pressure_palier
                volume = conso_litres_min * time_stop
                volume_paliers += volume
                duree_paliers += time_stop
                palier_details.append({
                    'profondeur': stop_depth,
                    'duree': time_stop,
                    'pression': pressure_palier,
                    'conso_min': conso_litres_min,
                    'volume': volume
                })
        
        # Volume pendant la plongée au fond
        volume_plongee = duration * conso_max
        
        # Volume pendant la remontée
        duree_remontee = depth / ascent_speed
        volume_remontee = duree_remontee * conso_mi_prof
        
        # Calculs DTR et temps total
        dtr = duree_remontee + duree_paliers
        temps_total_plongee = duration + dtr
        
        # Volume total consommé
        volume_total = volume_paliers + volume_plongee + volume_remontee
        
        return {
            'pressure_max': pressure_max,
            'conso_max': conso_max,
            'conso_mi_prof': conso_mi_prof,
            'duree_paliers': duree_paliers,
            'volume_paliers': round(volume_paliers, 1),
            'volume_plongee': round(volume_plongee, 1),
            'duree_remontee': round(duree_remontee, 2),
            'volume_remontee': round(volume_remontee, 1),
            'volume_total': round(volume_total, 1),
            'dtr': round(dtr, 1),
            'temps_total_plongee': round(temps_total_plongee, 1),
            'palier_details': palier_details,
            'error': False
        }
        
    except Exception as e:
        st.error(f"Erreur dans le calcul de consommation : {e}")
        return {'error': True}

def calculate_air_remaining(tank_capacity, tank_pressure, reserve, volume_total_litres, volume_plongee_litres):
    """Calcule l'air restant et la pression de décollage"""
    try:
        air_dispo_total = tank_capacity * tank_pressure
        
        # Calcul de la pression de décollage (après consommation au fond, avant remontée)
        air_apres_fond = air_dispo_total - volume_plongee_litres
        pression_decollage = air_apres_fond / tank_capacity
        
        # Calcul final après toute la plongée
        air_reste_litres = air_dispo_total - volume_total_litres
        bars_restants = air_reste_litres / tank_capacity
        
        # Si l'air restant est négatif, afficher 0
        bars_restants_display = max(0, bars_restants)
        pression_decollage_display = max(0, pression_decollage)
        
        suffisant = bars_restants >= reserve
        marge_ou_deficit = bars_restants - reserve
        
        return {
            'air_dispo_total': air_dispo_total,
            'air_reste_litres': round(air_reste_litres, 1),
            'bars_restants': round(bars_restants_display, 1),
            'bars_restants_real': round(bars_restants, 1),
            'pression_decollage': round(pression_decollage_display, 1),
            'pression_decollage_real': round(pression_decollage, 1),
            'suffisant': suffisant,
            'marge_ou_deficit': round(marge_ou_deficit, 1),
            'error': False
        }
    except Exception as e:
        return {'error': f'Erreur dans le calcul de l\'air restant : {e}'}

##########################################################################################
# Interface utilisateur
##########################################################################################

st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
st.title("Planificateur de Plongée MN90")

col1, col2 = st.columns([1, 1])

with col1:
    st.header("Paramètres de la plongée")
    
    profondeur = st.slider("Profondeur max (mètres)", min_value=5, max_value=60, value=20, step=1)
    duree = st.slider("Durée avant remontée (mn)", min_value=1, max_value=60, value=30, step=1)
    
    # SECTION PLONGÉES SUCCESSIVES
    
    plongee_successive = st.checkbox("Cette plongée fait partie d'un groupe de plongées successives")
    
    majoration = 0
    azote_info = None
    majoration_info = None
    
    if plongee_successive:
        col1a, col1b = st.columns(2)
        with col1a:
            gps_precedent = st.select_slider(
                "GPS de la plongée précédente", 
                options=["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P"],
                value="B",
                help="Groupe de Plongées Successives issu de la plongée précédente"
            )
        
        with col1b:
            intervalle_surface = st.slider(
                "Intervalle de surface (mn)", 
                min_value=15, 
                max_value=720, 
                value=60, 
                step=15,
                help="Temps écoulé entre la sortie d'eau de la plongée précédente et la nouvelle immersion"
            )
        
        # Charger les tables azote et majoration
        azote_table = load_azote_table()
        majo_table = load_majoration_table()
        
        if not azote_table.empty and not majo_table.empty:
            azote_result = lookup_azote_residuel(gps_precedent, intervalle_surface, azote_table)
            if not azote_result['error']:
                azote_info = azote_result
                majoration_result = lookup_majoration_from_tables(azote_result['azote'], profondeur, majo_table)
                if not majoration_result['error']:
                    majoration = majoration_result['majoration']
                    majoration_info = majoration_result
                else:
                    st.error(f"⚠ {majoration_result['message']}")
                    majoration = 0
            else:
                st.error(f"⚠ {azote_result['message']}")
                majoration = 0
        else:
            if azote_table.empty:
                st.error("⚠ Table d'azote résiduelle non disponible")
            if majo_table.empty:
                st.error("⚠ Table de majoration non disponible")
            majoration = 0
    
    # AUTRES PARAMÈTRES
    
    vitesse_remontee = st.slider("Vitesse de remontée (mètres/mn)", min_value=5, max_value=20, value=10, step=1)
    sac = st.slider("Consommation du plongeur (litres/mn)", min_value=10, max_value=30, value=20, step=1)
    capacite_bloc = st.slider("Capacité du bloc (litres)", min_value=10, max_value=20, value=15, step=1)
    pression_gonflage = st.slider("Pression de gonflage (bars)", min_value=150, max_value=300, value=200, step=10)
    reserve_securite = st.slider("Réserve de sécurité (bars)", min_value=30, max_value=80, value=50, step=5)

with col2:
    st.header("Planification de la plongée")
    
    # Afficher les informations de plongée successive si applicable
    if plongee_successive and azote_info and not azote_info['error']:
        info_text = f"""**GPS de la plongée précédente : {gps_precedent}**  
**Intervalle de surface : {intervalle_surface} minutes**   
**Taux d'azote résiduelle : {azote_info['azote']}**  
**Majoration appliquée : {majoration} minutes**"""
        
        st.subheader("Détermination de la majoration :")
        st.info(info_text)
    
    # Charger les tables MN90
    mn90_tables = load_mn90_tables()
    
    # Calculer la durée totale (durée + majoration)
    duree_totale = duree + majoration
    
    if not mn90_tables.empty:
        # Calculer les paliers de décompression
        decompression_stops = lookup_decompression(profondeur, duree_totale, mn90_tables)
        
        if not decompression_stops.get('error', False):
            # Calculer la consommation selon la méthode Excel
            air_calc = calculate_air_consumption_excel_method(
                profondeur, duree_totale, sac, vitesse_remontee, decompression_stops
            )
            
            if not air_calc.get('error', False):
                # Calculer l'air restant et la pression de décollage
                air_remaining = calculate_air_remaining(
                    capacite_bloc, pression_gonflage, reserve_securite, 
                    air_calc['volume_total'], air_calc['volume_plongee']
                )
                
                # Afficher les paliers de décompression
                st.subheader("Paliers de décompression obligatoires :")
                
                has_deco = any(time > 0 for key, time in decompression_stops.items() if key not in ['error', 'gps'])
                
                if has_deco:
                    paliers_message = ""
                    for depth, time in decompression_stops.items():
                        if depth not in ['error', 'gps'] and time > 0:
                            paliers_message += f"**Palier à {depth} : {time} minutes**  \n"
                    
                    gps_value = decompression_stops.get('gps', '')
                    if gps_value and gps_value != 'X':
                        paliers_message += f"**Groupe de plongées successives : {gps_value}**"
                    
                    if not gps_value or gps_value == 'X':
                        paliers_message = paliers_message.rstrip("  \n")
                    
                    st.info(paliers_message)
                else:
                    gps_value = decompression_stops.get('gps', '')
                    if gps_value and gps_value != 'X':
                        st.success(f"**Aucun palier de décompression requis**  \n**Groupe de plongées successives : {gps_value}**")
                    else:
                        st.success("**Aucun palier de décompression requis**")
                
                # Afficher les informations de temps
                col2a, col2b = st.columns(2)
                with col2a:
                    st.metric("Durée totale de remontée (DTR) :", f"{air_calc['dtr']} mn")
                with col2b:
                    st.metric("Durée totale de plongée :", f"{air_calc['temps_total_plongee']} mn")
                
                # Afficher les consommations
                st.subheader("Calculs de consommation en équivalent-surface :")
                
                col2a, col2b = st.columns(2)
                with col2a:
                    st.metric("Avant la remontée :", f"{air_calc['volume_plongee']} litres")
                    st.metric("Pendant les remontées :", f"{air_calc['volume_remontee']} litres")
                with col2b:
                    st.metric("Pendant les paliers :", f"{air_calc['volume_paliers']} litres")
                    st.metric("Consommation totale :", f"{air_calc['volume_total']} litres")
                
                # Résultat final
                
                if not air_remaining.get('error', False):
                    bars_restants_real = air_remaining.get('bars_restants_real', air_remaining['bars_restants'])
                    
                    if bars_restants_real >= reserve_securite:

                        # Situation 1: Plongée réalisable
                        message = f"""**Plongée réalisable**  
**Air disponible : {air_remaining['air_dispo_total']} litres**  
**Air consommé : {air_calc['volume_total']} litres**  
**Pression de décollage : {air_remaining['pression_decollage']} bars**  
**Pression restante : {air_remaining['bars_restants']} bars**  
**Marge de sécurité : +{air_remaining['marge_ou_deficit']} bars**"""
                        st.success(message)
                        
                    elif bars_restants_real > 0:

                        # Situation 2: Réserve insuffisante
                        message = f"""**Réserve insuffisante !**  
**Air disponible : {air_remaining['air_dispo_total']} litres**  
**Air consommé : {air_calc['volume_total']} litres**  
**Pression de décollage : {air_remaining['pression_decollage']} bars**  
**Pression restante : {air_remaining['bars_restants']} bars**  
**Déficit de réserve : -{abs(air_remaining['marge_ou_deficit'])} bars**"""
                        st.warning(message)
                        
                    else:

                        # Situation 3: Plongée impossible
                        message = f"""**Plongée impossible !!**  
**Air disponible : {air_remaining['air_dispo_total']} litres**  
**Air consommé : {air_calc['volume_total']} litres**  
**Pression de décollage : {air_remaining['pression_decollage']} bars**  
**Pression restante : {air_remaining['bars_restants']} bars**  
**Déficit total : -{abs(bars_restants_real)} bars**"""
                        st.error(message)
                    
                    # Détails techniques
                    with st.expander("Détails des calculs"):

                        ##########################################################################################
                        st.info("**Calculs de pression et de consommation**")
                        ##########################################################################################

                        pression_details = f"""
**Pression absolue maximale :** {air_calc['pressure_max']} bars  
*Calcul : Profondeur ÷ 10 + 1 = {profondeur} ÷ 10 + 1 = {air_calc['pressure_max']} bars*

**Consommation du plongeur en surface (SAC) :** {sac} litres/mn

**Consommation au fond :** {air_calc['conso_max']} litres/mn  
*Calcul : SAC × Pression absolue = {sac} × {air_calc['pressure_max']} = {air_calc['conso_max']} litres/mn*

**Consommation à mi-profondeur :** {air_calc['conso_mi_prof']:.1f} litres/mn  
*Calcul : SAC × (Profondeur ÷ 2 ÷ 10 + 1) = {sac} × ({profondeur} ÷ 2 ÷ 10 + 1) = {air_calc['conso_mi_prof']:.1f} litres/mn*"""
                        
                        st.markdown(pression_details)

                        ##########################################################################################
                        st.info("**Calculs des durées**")
                        ##########################################################################################

                        temps_details = ""
                        if majoration > 0:
                            temps_details = f"""
**Durée effective pour les calculs :** {duree} mn + {majoration} mn (majo) = {duree_totale} minutes  
*Voir plus bas pour le calcul de l'azote résiduelle et de la majoration*"""

                        temps_details += f"""
                        
**Durée de remontée (sans paliers) :** {air_calc['duree_remontee']:.1f} minutes  
*Calcul : Profondeur ÷ Vitesse de remontée = {profondeur} ÷ {vitesse_remontee} = {air_calc['duree_remontee']:.1f} minutes*

**Durée des paliers :** {air_calc['duree_paliers']} minutes

**Durée totale de remontée (DTR) :** {air_calc['dtr']} minutes  
*Calcul : Durée de remontée + Durée des paliers = {air_calc['duree_remontee']:.1f} + {air_calc['duree_paliers']} = {air_calc['dtr']} minutes*

**Durée totale de plongée :** {air_calc['temps_total_plongee']} minutes  
*Calcul : Durée au fond + DTR = {duree_totale} + {air_calc['dtr']} = {air_calc['temps_total_plongee']} minutes*"""
                        
                        st.markdown(temps_details)

                        ##########################################################################################
                        st.info("**Consommation d'air (en équivalent-surface)**")
                        ##########################################################################################

                        conso_details = f"""
**Volume consommé au fond :** {air_calc['volume_plongee']} litres  
*Calcul : Durée au fond × Consommation maximale = {duree_totale} × {air_calc['conso_max']} = {air_calc['volume_plongee']} litres*

**Volume consommé pendant la remontée :** {air_calc['volume_remontee']} litres  
*Calcul : Durée remontée × Consommation mi-prof = {air_calc['duree_remontee']:.1f} × {air_calc['conso_mi_prof']:.1f} = {air_calc['volume_remontee']} litres*

**Volume consommé pendant les paliers :** {air_calc['volume_paliers']} litres"""
                        
                        st.markdown(conso_details)
                        
                        if air_calc['palier_details']:
                            paliers_text = "**Détail par palier :**  \n"
                            for p in air_calc['palier_details']:
                                pression_palier = p['pression']
                                paliers_text += f"• **{p['profondeur']}m** : Pression {pression_palier} bars → {sac} × {pression_palier} = {p['conso_min']:.1f} L/min × {p['duree']} min = **{p['volume']} litres**  \n"
                            
                            st.markdown(paliers_text)

                        ##########################################################################################
                        st.info("**Bilan de l'air disponible**")
                        ##########################################################################################

                        bilan_details = f"""
**Voume total disponible :** {air_remaining['air_dispo_total']} litres  
*Calcul : Capacité bloc × Pression gonflage = {capacite_bloc} × {pression_gonflage} = {air_remaining['air_dispo_total']} litres*

**Volume consommé au fond :** {air_calc['volume_plongee']} litres

**Pression de décollage :** {air_remaining['pression_decollage']} bars  
*Calcul : (Air disponible - Air consommé au fond) ÷ Capacité bloc = ({air_remaining['air_dispo_total']} - {air_calc['volume_plongee']}) ÷ {capacite_bloc} = {air_remaining['pression_decollage']} bars*

**Volume total consommé :** {air_calc['volume_total']} litres  
*Somme : Au fond + Remontée + Paliers = {air_calc['volume_plongee']} + {air_calc['volume_remontee']} + {air_calc['volume_paliers']} = {air_calc['volume_total']} litres*

**Volume restant après la plongée :** {air_remaining['air_reste_litres']} litres  
*Calcul : Air disponible - Air consommé = {air_remaining['air_dispo_total']} - {air_calc['volume_total']} = {air_remaining['air_reste_litres']} litres*

**Pression restante dans le bloc :** {air_remaining['bars_restants']} bars  
*Calcul : Air restant ÷ Capacité bloc = {air_remaining['air_reste_litres']} ÷ {capacite_bloc} = {air_remaining['bars_restants']} bars*

**Réserve de sécurité requise :** {reserve_securite} bars  
**Marge ou déficit de pression :** {air_remaining['marge_ou_deficit']:+.1f} bars"""
                        
                        st.markdown(bilan_details)
                        
                        if plongee_successive and azote_info and not azote_info['error']:

                            ##########################################################################################
                            st.info("**Calcul de l'azote résiduelle et de la majoration**")
                            ##########################################################################################

                            azote_details = f"""
**GPS de la plongée précédente :** {gps_precedent}  
**Intervalle de surface demandé :** {intervalle_surface} minutes  
**Intervalle utilisé dans la table :** {azote_info['intervalle_utilise']} minutes  
**Méthode de recherche :** {azote_info['methode']}  
**Azote résiduelle trouvée :** {azote_info['azote']}"""

                            if majoration_info and not majoration_info['error']:
                                azote_details += f"""  
**Majoration appliquée :** {majoration} minutes"""
                            else:
                                azote_details += f"""  
**Majoration appliquée :** {majoration} minutes"""

                            azote_details += f"""

**Explication de la majoration :**  
L'azote résiduelle de {azote_info['azote']} indique qu'il reste de l'azote dissous dans vos tissus depuis la plongée précédente. Cette valeur est utilisée avec la profondeur de {profondeur}m pour déterminer la majoration de temps dans la table MN90.

**Logique de sélection de l'intervalle de surface :**  
Les tables MN90 utilisent l'intervalle immédiatement inférieur quand l'intervalle exact n'existe pas. Pour {intervalle_surface}min demandés, la table utilise {azote_info['intervalle_utilise']}min (valeur sécuritaire)."""

                            if majoration_info and not majoration_info['error']:
                                azote_details += f"""

**Logique de la table majoration :**  
Pour une azote résiduelle de {azote_info['azote']} et une profondeur de {profondeur}m, la table MN90 sélectionne :
- Azote = {majoration_info['majo_utilisee']} (valeur égale ou supérieure à {azote_info['azote']})
- Profondeur = {majoration_info['profondeur_utilisee']}m (valeur égale ou supérieure à {profondeur}m)
- Résultat : majoration de {majoration_info['majoration']} minutes"""
                            
                            st.markdown(azote_details)

                        ##########################################################################################
                        st.info("**Notes pédagogiques**")
                        ##########################################################################################

                        notes_pedago = f"""
**Pourquoi la pression influence la consommation ?**  
À {profondeur}m, vos poumons sont comprimés {air_calc['pressure_max']} fois plus qu'en surface. Pour les remplir, votre détendeur doit fournir de l'air à la même pression que l'eau environnante.

**Pourquoi calculer en équivalent-surface ?**  
Les volumes sont exprimés en "équivalent surface" pour effectuer les calculs à une pression standard de 1 bar. 1 litre d'air à {profondeur}m représente {air_calc['pressure_max']} litres en surface.

**Qu'est-ce que la pression de décollage ?**  
La pression de décollage ({air_remaining['pression_decollage']} bars) est la pression restante dans votre bloc au moment où vous commencez la remontée. C'est un indicateur utile pour vérifier si vous avez assez d'air pour effectuer la remontée et les paliers en toute sécurité.

**Pourquoi une consommation à mi-profondeur pour la remontée ?**  
Pendant la remontée, la pression diminue progressivement. La consommation à mi-profondeur ({air_calc['conso_mi_prof']:.1f} litres/mn) est une approximation de cette consommation décroissante."""
                        
                        st.markdown(notes_pedago)

##########################################################################################
# Section avertissements et conseils de sécurité
##########################################################################################

col3, col4 = st.columns(2)

with col3:
    st.markdown("""
    ### Avertissements importants :
    - Toujours utiliser des tables officielles certifiées MN90
    - Respecter les prérogatives de votre niveau de plongée
    - Respecter les consignes du Directeur de Plongée
    - Ne jamais plonger seul
    """)

with col4:
    st.markdown("""
    ### Conseils de sécurité :
    - Toujours prévoir une marge de sécurité supplémentaire
    - Effectuer si possible un palier de sécurité à 3 mètres
    - Vérifier votre équipement avant chaque plongée
    - Respecter les procédures de sécurité établies
    """)

##########################################################################################
# Note de responsabilité
##########################################################################################

st.markdown("""
<div style="margin-top: 2rem; padding: 1rem; border-top: 1px solid #e9ecef; text-align: center;">
    <p style="font-size: 0.75rem; color: #6c757d; margin: 0; line-height: 1.3;">
        <em><strong>Note importante :</strong> Cet outil est à vocation essentiellement pédagogique. 
        Les calculs et les résultats présentés n'engagent pas la responsabilité  de l'auteur quant à
        leur utilisation dans le cadre de plongées effectives. Utilisez toujours des tables officielles
        certifiées MN90 et consultez un professionnel qualifié pour vous aider à planifier vos plongées.</em>
    </p>
</div>
""", unsafe_allow_html=True)
