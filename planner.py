##########################################################################################
# PLANIFICATEUR DE PLONGÉE
# Auteur: Jérôme Lehuen
# Version: 0.1 (14/09/2025)
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
# Titre principal avec marge blanche
##########################################################################################

st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
st.title("Planificateur de Plongée MN90")

@st.cache_data
def load_mn90_tables():
    """Charge les tables MN90 depuis le fichier CSV"""
    try:
        if os.path.exists('mn90.csv'):
            df = pd.read_csv('mn90.csv')
            return df
        else:
            st.error("Fichier mn90.csv non trouvé")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Erreur lors du chargement : {e}")
        return pd.DataFrame()

def lookup_decompression(depth, duration, mn90_tables):
    """Recherche les paramètres de décompression dans les tables MN90"""
    try:
        if mn90_tables.empty:
            return {'15m': 0, '12m': 0, '9m': 0, '6m': 0, '3m': 0, 'error': True}
        
        mask = (
            (depth > mn90_tables['P1']) & 
            (depth <= mn90_tables['P2']) & 
            (duration > mn90_tables['D1']) & 
            (duration <= mn90_tables['D2'])
        )
        
        matching_rows = mn90_tables[mask]
        
        if matching_rows.empty:
            st.warning(f"Aucune correspondance trouvée pour {depth}m / {duration}min")
            return {'15m': 0, '12m': 0, '9m': 0, '6m': 0, '3m': 0, 'error': True}
        
        row = matching_rows.iloc[0]
        
        return {
            '15m': int(row['15m']) if pd.notna(row['15m']) else 0,
            '12m': int(row['12m']) if pd.notna(row['12m']) else 0,
            '9m': int(row['9m']) if pd.notna(row['9m']) else 0,
            '6m': int(row['6m']) if pd.notna(row['6m']) else 0,
            '3m': int(row['3m']) if pd.notna(row['3m']) else 0,
            'error': False
        }
        
    except Exception as e:
        st.error(f"Erreur dans la recherche de décompression : {e}")
        return {'15m': 0, '12m': 0, '9m': 0, '6m': 0, '3m': 0, 'error': True}

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
            if time_stop > 0 and depth_stop.endswith('m'):
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

def calculate_air_remaining(tank_capacity, tank_pressure, reserve, volume_total_litres):
    """Calcule l'air restant"""
    try:
        air_dispo_total = tank_capacity * tank_pressure
        air_reste_litres = air_dispo_total - volume_total_litres
        bars_restants = air_reste_litres / tank_capacity
        
        # Si l'air restant est négatif, afficher 0
        bars_restants_display = max(0, bars_restants)
        
        suffisant = bars_restants >= reserve
        marge_ou_deficit = bars_restants - reserve
        
        return {
            'air_dispo_total': air_dispo_total,
            'air_reste_litres': round(air_reste_litres, 1),
            'bars_restants': round(bars_restants_display, 1),
            'bars_restants_real': round(bars_restants, 1),  # Valeur réelle pour les calculs
            'suffisant': suffisant,
            'marge_ou_deficit': round(marge_ou_deficit, 1),
            'error': False
        }
    except Exception as e:
        return {'error': f'Erreur dans le calcul de l\'air restant : {e}'}

##########################################################################################
# Interface utilisateur
##########################################################################################

col1, col2 = st.columns([1, 1])

with col1:
    st.header("Paramètres de la plongée")
    
    profondeur = st.slider("Profondeur max (mètres)", min_value=5, max_value=60, value=20, step=1)
    duree = st.slider("Durée avant remontée (mn)", min_value=1, max_value=60, value=30, step=1)
    majoration = st.slider("Majoration du temps de plongée (mn)", min_value=0, max_value=196, value=0, step=1)
    vitesse_remontee = st.slider("Vitesse de remontée (mètres/mn)", min_value=5, max_value=20, value=10, step=1)
    sac = st.slider("Consommation du plongeur (litres/mn)", min_value=10, max_value=30, value=20, step=1)
    capacite_bloc = st.slider("Capacité du bloc (litres)", min_value=10, max_value=20, value=15, step=1)
    pression_gonflage = st.slider("Pression de gonflage (bars)", min_value=150, max_value=300, value=200, step=10)
    reserve_securite = st.slider("Réserve de sécurité (bars)", min_value=30, max_value=80, value=50, step=5)

with col2:
    st.header("Planification de la plongée")
    
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
                # Calculer l'air restant
                air_remaining = calculate_air_remaining(
                    capacite_bloc, pression_gonflage, reserve_securite, air_calc['volume_total']
                )
                
                # Afficher les informations de temps
                col2a, col2b = st.columns(2)
                with col2a:
                    st.metric("Durée totale de remontée (DTR) :", f"{air_calc['dtr']} mn")
                with col2b:
                    st.metric("Durée totale de plongée :", f"{air_calc['temps_total_plongee']} mn")
                
                # Afficher les paliers de décompression
                st.subheader("Paliers de décompression obligatoires :")
                
                has_deco = any(time > 0 for key, time in decompression_stops.items() if key != 'error')
                
                if has_deco:
                    # Combiner tous les paliers en un seul bloc
                    paliers_message = ""
                    for depth, time in decompression_stops.items():
                        if depth != 'error' and time > 0:
                            paliers_message += f"**{depth}** : {time} minutes  \n"
                    # Supprimer le dernier retour à la ligne
                    paliers_message = paliers_message.rstrip("  \n")
                    st.info(paliers_message)
                else:
                    st.success("Aucun palier de décompression requis")
                
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
                st.subheader("Conclusion :")
                
                if not air_remaining.get('error', False):
                
                    # Affichage du résultat selon 3 situations distinctes
                    bars_restants_real = air_remaining.get('bars_restants_real', air_remaining['bars_restants'])
                    
                    if bars_restants_real >= reserve_securite:
                    
                        # Situation 1: Plongée réalisable
                        message = f"""**Plongée réalisable**  
**Air disponible : {air_remaining['air_dispo_total']} litres**  
**Air consommé : {air_calc['volume_total']} litres**  
**Pression restante : {air_remaining['bars_restants']} bars**  
**Marge de sécurité : +{air_remaining['marge_ou_deficit']} bars**"""
                        st.success(message)
                        
                    elif bars_restants_real > 0:
                    
                        # Situation 2: Réserve insuffisante (air positif mais < réserve)
                        message = f"""**Réserve insuffisante !**  
**Air disponible : {air_remaining['air_dispo_total']} litres**  
**Air consommé : {air_calc['volume_total']} litres**  
**Pression restante : {air_remaining['bars_restants']} bars**  
**Déficit de réserve : {abs(air_remaining['marge_ou_deficit'])} bars**"""
                        st.warning(message)
                        
                    else:
                    
                        # Situation 3: Plongée impossible (déficit en air)
                        message = f"""**Plongée impossible !**  
**Air disponible : {air_remaining['air_dispo_total']} litres**  
**Air consommé : {air_calc['volume_total']} litres**  
**Pression restante : {air_remaining['bars_restants']} bars**  
**Déficit total : {abs(bars_restants_real)} bars**"""
                        st.error(message)
                    
                    # Détails techniques en Markdown avec des sauts de ligne compacts
                    with st.expander("Détails des calculs"):
                        
                        # Affichage de la durée effective utilisée pour les calculs
                        if majoration > 0:
                            st.info(f"**Durée effective pour les calculs :** {duree} mn + {majoration} mn = {duree_totale} mn")

                        # Section 1: Calculs de pression et consommation
                        st.markdown("### 🤿 **Calculs de pression et consommation**")
                        pression_details = f"""**Pression absolue maximale :** {air_calc['pressure_max']} bars  
*Formule : (Profondeur ÷ 10) + 1 = ({profondeur} ÷ 10) + 1 = {air_calc['pressure_max']} bars*  
*La pression augmente de 1 bar tous les 10 mètres (pression atmosphérique + pression hydrostatique)*

**Consommation au fond :** {air_calc['conso_max']} litres/min  
*Formule : SAC × Pression absolue = {sac} × {air_calc['pressure_max']} = {air_calc['conso_max']} litres/min*  
*Plus on descend, plus on consomme d'air proportionnellement à la pression*

**Consommation à mi-profondeur :** {air_calc['conso_mi_prof']:.1f} litres/min  
*Formule : SAC × ((Profondeur ÷ 2) ÷ 10 + 1) = {sac} × (({profondeur} ÷ 2) ÷ 10 + 1) = {air_calc['conso_mi_prof']:.1f} litres/min*  
*Consommation moyenne pendant la remontée (pression décroissante)*"""
                        st.markdown(pression_details)

                        # Section 2: Calculs de temps et DTR
                        st.markdown("### ⏱️ **Calculs de temps et DTR**")
                        temps_details = f"""**Durée de remontée libre :** {air_calc['duree_remontee']:.1f} minutes  
*Formule : Profondeur ÷ Vitesse de remontée = {profondeur} ÷ {vitesse_remontee} = {air_calc['duree_remontee']:.1f} min*  
*Temps nécessaire pour remonter à vitesse constante sans les paliers*

**Durée des paliers :** {air_calc['duree_paliers']} minutes  
*Somme de tous les temps de paliers obligatoires selon les tables MN90*

**DTR (Durée Totale Remontée) :** {air_calc['dtr']} minutes  
*Formule : Temps de remontée + Temps des paliers = {air_calc['duree_remontee']:.1f} + {air_calc['duree_paliers']} = {air_calc['dtr']} min*

**Temps total de plongée :** {air_calc['temps_total_plongee']} minutes  
*Formule : Durée au fond + DTR = {duree_totale} + {air_calc['dtr']} = {air_calc['temps_total_plongee']} min*  
*Temps total depuis l'immersion jusqu'au retour en surface*"""
                        st.markdown(temps_details)

                        # Section 3: Calculs de consommation en équivalent surface
                        st.markdown("### 🫧 **Consommation d'air (équivalent surface)**")
                        conso_details = f"""**Volume consommé au fond :** {air_calc['volume_plongee']} litres  
*Formule : Durée au fond × Consommation maximale = {duree_totale} × {air_calc['conso_max']} = {air_calc['volume_plongee']} litres*

**Volume consommé pendant la remontée :** {air_calc['volume_remontee']} litres  
*Formule : Durée remontée × Consommation mi-prof = {air_calc['duree_remontee']:.1f} × {air_calc['conso_mi_prof']:.1f} = {air_calc['volume_remontee']} litres*

**Volume consommé pendant les paliers :** {air_calc['volume_paliers']} litres"""
                        st.markdown(conso_details)
                        
                        # Détail des paliers en format compact
                        if air_calc['palier_details']:
                            paliers_text = "**Détail par palier :**  \n"
                            for p in air_calc['palier_details']:
                                pression_palier = p['pression']
                                paliers_text += f"• **{p['profondeur']}m** : Pression {pression_palier} bars → {sac} × {pression_palier} = {p['conso_min']:.1f} L/min × {p['duree']} min = **{p['volume']} litres**  \n"
                            st.markdown(paliers_text)

                        # Section 4: Bilan air
                        st.markdown("### ⚡ **Bilan de l'air disponible**")
                        bilan_details = f"""**Air total disponible :** {air_remaining['air_dispo_total']} litres  
*Formule : Capacité bloc × Pression gonflage = {capacite_bloc} × {pression_gonflage} = {air_remaining['air_dispo_total']} litres*

**Volume total consommé :** {air_calc['volume_total']} litres  
*Somme : Au fond + Remontée + Paliers = {air_calc['volume_plongee']} + {air_calc['volume_remontee']} + {air_calc['volume_paliers']} = {air_calc['volume_total']} litres*

**Air restant après plongée :** {air_remaining['air_reste_litres']} litres  
*Calcul : Air disponible - Air consommé = {air_remaining['air_dispo_total']} - {air_calc['volume_total']} = {air_remaining['air_reste_litres']} litres*

**Pression restante dans le bloc :** {air_remaining['bars_restants']} bars  
*Formule : Air restant ÷ Capacité bloc = {air_remaining['air_reste_litres']} ÷ {capacite_bloc} = {air_remaining['bars_restants']} bars*

**Réserve de sécurité requise :** {reserve_securite} bars  
**Marge ou déficit de pression :** {air_remaining['marge_ou_deficit']:+.1f} bars"""
                        st.markdown(bilan_details)

                        # Section 5: Notes pédagogiques
                        st.markdown("### 📚 **Notes pédagogiques**")
                        notes_pedago = f"""**Pourquoi la pression influence la consommation ?**  
À {profondeur}m, vos poumons sont comprimés par {air_calc['pressure_max']} fois plus que en surface. Pour les remplir, votre détendeur doit fournir de l'air à la même pression que l'eau environnante.

**Pourquoi calculer l'équivalent surface ?**  
Les volumes sont exprimés en "équivalent surface" car c'est ainsi qu'on mesure l'air dans une bouteille. 1 litre d'air à {profondeur}m représente {air_calc['pressure_max']} litres prélevés du bloc.

**Pourquoi une consommation à mi-profondeur pour la remontée ?**  
Pendant la remontée, la pression diminue progressivement. La consommation à mi-profondeur ({air_calc['conso_mi_prof']:.1f} L/min) est une approximation de cette consommation décroissante."""
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
        <em><strong>Note importante :</strong> Cet outil a une vocation essentiellement pédagogique. 
        Les calculs et les résultats présentés ne sont pas garantis et l'auteur n'engage pas sa responsabilité 
        quant à leur utilisation dans le cadre de plongées effectives. Utilisez toujours des tables 
        officielles certifiées et consultez un professionnel qualifié pour planifier vos plongées.</em>
    </p>
</div>
""", unsafe_allow_html=True)
