# Insect Identification API

API REST construite avec FastAPI, qui utilise l'API Claude (Anthropic) en vision pour identifier automatiquement un insecte ou nuisible à partir d'une image, et retourner des informations structurées : nom scientifique, niveau de menace, et méthodes de contrôle recommandées.

## Context: 
API construite dans le cadre d'un stage pour le backend d'une application mobile d'identification d'insectes

## Fonctionnalités

- Analyse d'image via URL ou image encodée en base64
- Identification de l'espèce (nom commun + nom scientifique)
- Évaluation du niveau de menace pour l'humain (échelle 0.1–1.0 + label : faible / modéré / élevé / critique)
- Suggestions de méthodes de contrôle et de produits
- Validation stricte du type de fichier et de la taille (max 5 Mo, JPEG/PNG/GIF/WebP)
- Gestion d'erreurs robuste (timeout Claude, rate limit, JSON malformé, image invalide)
- Réponse structurée et validée avec Pydantic

## Stack technique

- Python 3 / FastAPI
- Anthropic API (Claude, vision)
- Pydantic pour la validation des données
- httpx pour le téléchargement d'images distantes
- Docker pour le déploiement

## Installation locale

```bash
# Cloner le repo
git clone https://github.com/Yonkeu-Onyx/Claude_Insect_Identification_api.git
cd Claude_Insect_Identification_api

# Installer les dépendances
pip install -r requirements.txt

# Configurer la clé API (voir .env.example)
cp .env.example .env
# puis ajouter ta clé ANTHROPIC_API_KEY dans .env

# Lancer le serveur
uvicorn main:app --reload
```

L'API sera disponible sur `http://localhost:8000`, avec une documentation interactive auto-générée sur `http://localhost:8000/docs`.

## Utilisation

POST `/claude_analyze`

```json body example
{
  "image_url": "https://example.com/insecte.jpg"
}
```

ou avec une image en base64 :

```json
{
  "image_url": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
}
```

**Réponse :**

```json
{
  "success": true,
  "data": [
    {
      "common_name": "Coccinelle asiatique",
      "scientific_name": "Harmonia axyridis",
      "description": "...",
      "threat": 0.2,
      "label": "faible",
      "control": "...",
      "produits": ["..."]
    }
  ]
}
```

## Ce que j'ai appris sur ce projet

- Comment utiliser de manière effective les endpoints d'une api d'IA
- Comment integrer une IA a une application
- Structurer un prompt pour forcer Claude à retourner un JSON strictement formaté et parsable
- Valider et sécuriser un pipeline d'upload d'image (type MIME, taille max, décodage base64)
- Gérer proprement les erreurs spécifiques d'une API tierce (rate limit, timeout, erreurs de statut) plutôt qu'un simple `try/except` générique

