from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime, timezone, timedelta
import os
import functools
import time
import json

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 300  # Cache navigateur de 5 minutes

# Cache en mémoire simple (sera réinitialisé si l'app s'endort après 15 min d'inactivité)
CACHE_TIMEOUT = 300  # 5 minutes pour éviter trop d'appels API
api_cache = {}

# Décorateur pour mise en cache légère
def timed_cache(timeout=CACHE_TIMEOUT):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = str(args) + str(kwargs)
            if cache_key in api_cache:
                result, timestamp = api_cache[cache_key]
                if time.time() - timestamp < timeout:
                    return result
            result = func(*args, **kwargs)
            api_cache[cache_key] = (result, time.time())
            return result
        return wrapper
    return decorator

@timed_cache(timeout=CACHE_TIMEOUT)
def fetch_api_data():
    """Récupère les données de l'API avec mise en cache légère"""
    url = "https://queue-times.com/parks/9/queue_times.json"
    try:
        # Timeout court pour éviter de bloquer trop longtemps (RAM limitée)
        response = requests.get(url, timeout=3)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        # Gestion d'erreur simplifiée pour économiser les ressources
        print(f"Erreur API: {str(e)[:100]}")
        return {"rides": [], "last_updated": None}

@app.route('/')
def index():
    # Récupérer les données de l'API avec mise en cache
    data = fetch_api_data()

    # Définition des catégories d'attractions
    sensations_fortes = [
        "Toutatis", "OzIris", "Tonnerre 2 Zeus", "Goudurix", "La Trace du Hourra", 
        "Discobélix", "La Tour de Numérobis", "Le Cheval de Troie", "Les Chaises Volantes", "La Galère"
    ]

    familiales = [
        "Pégase Express", "Le Vol d'Icare", "L'Oxygénarium", "Menhir Express", "Romus et Rapidus",
        "La Revanche des Pirates", "Le Grand Splatch", "La revanche des pirates - Le Grand Splatch", 
        "Le Défi de César", "Attention Menhir !", "Les Espions de César", "Les Chaudrons", 
        "La Petite Tempête", "SOS Tournevis", "Cétautomatix", "L'Hydre de Lerne", 
        "La Rivière d'Elis", "Epidemaïs Croisières"
    ]

    petits_gaulois = [
        "Le Mini Carrousel", "Les Petites Chaises Volantes", "Les Petits Chars tamponneurs", 
        "Les Petits Drakkars", "Aérodynamix", "Enigmatix", "Etamine", "Hydrolix", "Lavomatix", 
        "L'Escadrille des As", "Le Petit Train", "Les Chevaux du Roy", "Sanglier d'Or playground"
    ]

    # Extraire toutes les attractions directement depuis la clé 'rides'
    rides = []
    for ride in data.get("rides", []):
        # Déterminer la catégorie
        category = "Autre"
        if ride["name"] in sensations_fortes:
            category = "Sensations fortes"
        elif ride["name"] in familiales:
            category = "Familiale"
        elif ride["name"] in petits_gaulois:
            category = "Petits Gaulois"
        
        rides.append({
            "name": ride["name"],
            "wait_time": ride["wait_time"],
            "is_open": ride["is_open"],
            "category": category
        })

    # Trier les attractions par catégorie et temps d'attente
    sensations = sorted([r for r in rides if r["category"] == "Sensations fortes"], 
                        key=lambda r: (not r["is_open"], r["wait_time"]))
    
    familles = sorted([r for r in rides if r["category"] == "Familiale"], 
                      key=lambda r: (not r["is_open"], r["wait_time"]))
    
    enfants = sorted([r for r in rides if r["category"] == "Petits Gaulois"], 
                     key=lambda r: (not r["is_open"], r["wait_time"]))
    
    autres = sorted([r for r in rides if r["category"] == "Autre"], 
                    key=lambda r: (not r["is_open"], r["wait_time"]))

    # Récupérer l'heure de la dernière mise à jour
    last_updated = data.get("last_updated")
    if not last_updated and data.get("rides") and len(data["rides"]) > 0:
        last_updated = data["rides"][0].get("last_updated")

    # Obtenir l'heure actuelle en UTC
    now = datetime.now(timezone.utc)

    # Formater la date
    if last_updated:
        try:
            dt = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
            age_delta = now - dt
            age_minutes = int(age_delta.total_seconds() / 60)
            
            formatted_date = dt.astimezone(timezone(timedelta(hours=2))).strftime("%d/%m/%Y à %H:%M:%S")
            
            if age_minutes < 15:
                freshness = f"Données récentes (il y a {age_minutes} minutes)"
            elif age_minutes < 60:
                freshness = f"Données datant d'il y a {age_minutes} minutes"
            elif age_minutes < 24*60:
                hours = age_minutes // 60
                mins = age_minutes % 60
                freshness = f"Données datant d'il y a {hours}h{mins:02d}"
            else:
                freshness = "Données anciennes (plus de 24h)"
        except:
            formatted_date = last_updated
            freshness = "Date de mise à jour inconnue"
    else:
        formatted_date = "aujourd'hui"
        freshness = "Fraîcheur des données inconnue"

    return render_template('index.html', 
                          sensations=sensations, 
                          familles=familles, 
                          enfants=enfants, 
                          autres=autres,
                          last_updated=formatted_date,
                          freshness=freshness)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
