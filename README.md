# Goatantix

Un "Pédantix" appliqué aux paroles de rap : devine le titre d'un son mot par mot, avec un score de proximité sémantique à chaque essai.

## Architecture

- `backend/` — FastAPI + Postgres. Collecte les sons d'un artiste depuis Genius, les stocke en JSON brut (`backend/data/raw/<artiste>/<id>.json`) puis en base, entraîne des word-vectors maison sur le corpus pour le scoring, et sert l'API de jeu.
- `frontend/` — Vue 3 + Vite. Sélection d'artiste, affichage des paroles masquées, formulaire de guess, historique coloré par proximité.

## Pré-requis

- Un token Genius API : créer une app sur https://genius.com/api-clients, récupérer le "Client Access Token".
- Docker (pour Postgres local).

## Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# éditer .env : mettre GENIUS_ACCESS_TOKEN

docker-compose up -d          # lance Postgres sur localhost:5432

# importer un artiste (répéter pour chaque artiste souhaité)
python scripts/collect.py "Damso" --max-songs 60

# (ré)entraîner les vecteurs sémantiques sur tout ce qui est en base
python scripts/train_embeddings.py

uvicorn app.main:app --reload --port 8000
```

Scripts utiles :
- `scripts/collect.py "Artiste" --max-songs N` : scrape Genius + importe en base.
- `scripts/import_data.py` : réimporte tous les JSON déjà présents sur disque (utile après un reset de la base, sans retaper l'API Genius).
- `scripts/train_embeddings.py` : reconstruit le modèle de proximité sémantique à partir de tout le corpus en base. À relancer après chaque nouvel import.

## Frontend

```bash
cd frontend
npm install
npm run dev     # http://localhost:5173
```

`frontend/.env` pointe vers `VITE_API_URL=http://localhost:8000` par défaut.

## Comment fonctionne le scoring

Pas de word2vec/gensim ici (pas encore de wheels compatibles pour les toutes dernières versions de Python au moment de l'écriture) : les vecteurs sont construits à la main dans `backend/app/embeddings.py` via une matrice de co-occurrence pondérée par fenêtre glissante → PPMI → SVD tronquée. C'est la recette "distributionnelle" classique (celle qui a précédé word2vec/GloVe), largement suffisante pour un corpus de la taille d'un ou plusieurs catalogues d'artistes.

Le score affiché est la similarité cosinus entre le mot proposé et le vecteur moyen des mots du titre ; le rang correspond à sa position si on classait tout le vocabulaire par proximité décroissante avec ce titre (comme sur Cemantix/Pédantix).

## Limites connues / pistes d'amélioration

- Plus le corpus (nombre d'artistes importés) est petit, moins les vecteurs sémantiques sont fins — importer plusieurs artistes avant de juger la qualité du scoring.
- La matrice de co-occurrence est dense (O(vocab²)) : pour un très gros corpus (des dizaines d'artistes), passer à une version sparse (scipy.sparse) deviendrait nécessaire.
- Les paroles sont protégées par le droit d'auteur : usage pensé pour un prototype personnel, pas pour une republication publique du texte intégral des sons.
