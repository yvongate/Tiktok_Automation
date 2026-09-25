# TikTok Video Generator (n8n + FFmpeg)

Générateur de vidéos courtes verticales (9:16) piloté par n8n, avec deux workflows
différents et FFmpeg pour le montage. Ce dossier regroupe tout ce qui était
éparpillé à la racine (`N8N With FFMPeg`, `n8nffmpeg kit`, les `.json`).

## Structure

```
tiktok-video-generator/
├── Dockerfile              # image n8n + FFmpeg (binaire statique)
├── docker-compose.yml      # service n8n, volumes, variables d'env
├── shared/
│   └── audio.mp3           # audio de fond utilisé par "Evolution Video"
└── workflows/
    ├── evolution-video.json           # workflow original (non modifié)
    ├── evolution-video.corrige.json   # version corrigée, à importer en priorité
    └── veo3.json                      # workflow VEO 3 (Google Veo via fal.ai)
```

## Installation

```powershell
cd "F:\Tiktok\tiktok-video-generator"
docker compose up -d --build
```

Ouvrir http://localhost:5678, créer le compte propriétaire, puis importer un
workflow depuis `workflows/` via le menu `⋯` → **Import from file**.

Vérifier que tout fonctionne :

```powershell
docker exec n8n ffmpeg -version
docker exec n8n ls /home/node/.n8n-files
```

## Les deux workflows

### 1. `evolution-video.corrige.json` — Ads Generator (évolution d'une espèce)

Génère une vidéo montrant l'évolution d'une espèce à travers plusieurs formes
intermédiaires (ex. "The Evolution Of Gorillas"), avec compteur d'années à
l'écran et musique de fond.

**Pipeline** :
1. Liste d'espèces (saisie dans le nœud `Execute`) → GPT-5.2 écrit un prompt
   d'image scientifique par espèce.
2. KIE.AI (`google/nano-banana`) génère une image par espèce (envoi, attente
   70 s, vérification, téléchargement).
3. Les espèces sont triées de la plus ancienne à la plus récente, puis
   regroupées par paires consécutives (+ une paire de bouclage fin → début).
4. GPT-5.2 écrit un prompt de transition/morphing par paire.
5. KIE.AI (`kling/v2-5-turbo-image-to-video-pro`) génère un clip de 5 s par
   paire, de l'image de départ à l'image d'arrivée (envoi, attente 600 s,
   vérification, téléchargement).
6. FFmpeg (dans le conteneur) : découpe à 5 s, concatène tous les clips,
   ajoute `shared/audio.mp3`, incruste les sous-titres (titre, espèce,
   période, compteur d'années) générés en `.ass` par un nœud Code.
7. Résultat : `final_<id>.mp4` copié à la racine de `shared/`.

**Credentials nécessaires** : OpenAI API, KIE.AI (Bearer Token).

**Corrections apportées par rapport à `evolution-video.json`** :
- Arrêt propre (`Stop and Error`) si KIE renvoie `fail`, au lieu d'attendre
  indéfiniment.
- Tri chronologique automatique des espèces avant numérotation.
- Copie automatique de la vidéo finale à la racine de `shared/`.
- Nœud `GPT 4.1` renommé `GPT 5.2 (Transitions)` (il utilisait déjà gpt-5.2).
- Données de test épinglées réduites à 3 espèces pour limiter le coût d'un
  premier essai (`Tiktaalik`, `Purgatorius`, `Gorilla gorilla`).

**Chemins de fichiers** : le workflow écrit dans `/home/node/.n8n-files/`,
monté sur `./shared` par le `docker-compose.yml` de ce dossier. Le nœud
`Execute Command` doit être autorisé (`NODES_EXCLUDE=[]`, déjà dans le
compose).

### 2. `veo3.json` — VEO 3 (personnage façon influenceur)

Génère une courte vidéo "selfie" (8 s environ) d'un personnage fictif/mythique
qui parle à la caméra sur un ton ironique, à partir d'une ligne d'un Google
Sheet. Contrairement au workflow précédent, Veo 3 fournit directement l'image
ET le son (voix, ambiance) : pas de montage FFmpeg.

**Pipeline** :
1. Lit dans un Google Sheet la première ligne dont `Status = New` (colonne
   `Context` = scénario, ex. "Bigfoot se plaint d'être flou").
2. GPT-4.1 transforme ce scénario en `title`, `post_caption` et un `prompt`
   Veo 3 détaillé (point de vue selfie obligatoire, personnage sans
   vêtements modernes, 1-2 répliques ironiques).
3. fal.ai (`fal-ai/veo3`) génère la vidéo en 9:16 (envoi, attente 15 s en
   boucle jusqu'à 50 tours, récupération de l'URL).
4. Le Google Sheet est mis à jour : `Status = Generated`, `URL`, `Title`,
   `Captions`.

**Credentials nécessaires** :
- OpenAI API.
- Google Sheets OAuth2 (nécessite un projet Google Cloud avec l'API Sheets
  activée, URI de redirection `http://localhost:5678/rest/oauth2-credential/callback`).
- fal.ai : credential "Header Auth", header `Authorization`, valeur
  `Key <votre_clé_fal>`.

**⚠️ À adapter avant usage** : le workflow pointe par défaut vers le Google
Sheet de l'auteur original (`documentId` et `sheetName` codés en dur dans les
nœuds `Google Sheets` et `Update Sheet`). Il faut créer votre propre feuille
avec les colonnes `Context`, `Title`, `Captions`, `URL`, `Status`, et
resélectionner votre document/onglet dans ces deux nœuds après import.

**Limites connues, non corrigées** :
- Si fal.ai renvoie un échec, le workflow le traite comme terminé et tente
  quand même de récupérer l'URL (erreur au lieu d'un arrêt propre).
- Une seule ligne traitée par exécution manuelle (`returnFirstMatch`) : pas
  de traitement en lot ni de déclencheur planifié.
- Veo 3 est facturé à la seconde et coûte nettement plus cher que la
  génération d'images de l'autre workflow — vérifier le tarif fal.ai avant
  de lancer plusieurs vidéos.

## Infrastructure (Dockerfile / docker-compose.yml)

- **Dockerfile** : part de `n8nio/n8n:latest` et copie les binaires FFmpeg
  statiques (`mwader/static-ffmpeg:7.1`) dans l'image. `apk add ffmpeg` ne
  fonctionne plus sur les images n8n récentes (pas de gestionnaire de
  paquets `apk`), d'où ce choix.
- **docker-compose.yml** :
  - volume nommé `n8n-data` → `/home/node/.n8n` (workflows, credentials,
    compte).
  - `./shared` → `/home/node/.n8n-files` (fichiers lus/écrits par les deux
    workflows).
  - `NODES_EXCLUDE=[]` pour activer le nœud `Execute Command`.
  - port `5678`.

## Pistes pour une version sans n8n (NestJS + Vite)

Les deux workflows suivent le même motif : **soumettre une tâche à une API
d'IA → attendre → interroger le statut → télécharger le résultat**. En code,
cela donne une fonction `submit()` + une boucle de polling par fournisseur
(KIE.AI, fal.ai), assemblées par un service NestJS avec une file d'attente
(BullMQ) pour les tâches longues. Le front (Vite) peut être hébergé sur
Vercel ; NestJS doit tourner sur un serveur qui reste actif en continu
(Render, Railway, Fly.io) car les traitements durent plusieurs minutes,
ce qui dépasse les limites des fonctions serverless. Aucun GPU local n'est
nécessaire : la génération d'images/vidéos se fait sur les serveurs de
KIE.AI, OpenAI et fal.ai ; seul FFmpeg (CPU) tourne localement, et
uniquement pour "Evolution Video".
