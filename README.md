# Parc Astérix - Temps d'attente

Application web qui affiche les temps d'attente des attractions du Parc Astérix en temps réel, classées par catégorie.

## Fonctionnalités

- Récupération des données depuis l'API Queue-Times.com
- Classification des attractions en 4 catégories :
  - 🎢 Sensations fortes
  - 👨‍👩‍👧‍👦 Attractions familiales
  - 🧒 Petits Gaulois (pour enfants)
  - 🏛️ Autres attractions
- Tri des attractions par temps d'attente
- Affichage du statut (ouvert/fermé) de chaque attraction
- Indication de la fraîcheur des données

## Déploiement

Cette application est conçue pour être facilement déployée sur Render.com :

1. Connectez votre compte GitHub à Render
2. Créez un nouveau Web Service en pointant vers ce dépôt
3. Render détectera automatiquement la configuration dans le fichier `render.yaml`

## Développement local

Pour exécuter l'application en local :

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer le serveur
python app.py
```

L'application sera disponible à l'adresse http://localhost:5000

## Technologies utilisées

- Flask : framework web Python
- Requests : bibliothèque HTTP pour Python
- HTML/CSS : interface utilisateur
- Render.com : hébergement

## Source des données

Les données proviennent de l'API Queue-Times.com et sont mises à jour périodiquement. Elles peuvent ne pas refléter exactement la situation en temps réel dans le parc.
