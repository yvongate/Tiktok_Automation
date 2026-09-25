# Video Vision

Outil pour "faire voir" une vidéo à Claude : extraction de frames + audio,
indépendant du projet `tiktok-video-generator` (pas de Docker, utilise le
FFmpeg déjà installé sur la machine).

## Pourquoi c'est nécessaire

Claude ne peut pas ouvrir un fichier `.mp4` directement. Il faut :
1. **Découper la vidéo en images** (frames) — Claude les lit comme des photos.
2. **Extraire l'audio et le transcrire en texte** — Claude ne peut pas
   "écouter" un `.mp3`, seulement lire du texte.

## Structure

```
video-vision/
├── extract.ps1          # vidéo -> frames (jpg) + audio.mp3
├── transcribe_local.py   # audio.mp3 -> transcript.txt, GRATUIT, local (faster-whisper)
├── transcribe.ps1        # audio.mp3 -> transcript.txt via API OpenAI (payant, nécessite une clé)
├── input/                # dépose tes vidéos ici (optionnel, voir usage)
└── output/
    └── <nom_video>/
        ├── frames/
        │   ├── frame_001.jpg
        │   └── ...
        ├── audio.mp3
        └── transcript.txt   (si transcription lancée)
```

## Usage

### 1. Extraire les frames + l'audio

```powershell
cd "F:\Tiktok\video-vision"
.\extract.ps1 -Video "chemin\vers\ta_video.mp4"
```

Ou plus simple : dépose la vidéo dans `input\`, puis :
```powershell
.\extract.ps1 -Video "ma_video.mp4"
```

**Options** :
- `-Frames 24` (défaut) : nombre de frames réparties uniformément sur toute
  la durée. 24 suffit pour la plupart des analyses (début, milieu, fin,
  transitions). Monte à 40-60 pour une vidéo longue ou si tu veux plus de
  détail — au-delà, ça devient coûteux et inutile pour l'analyse.
- `-Dense` : ignore `-Frames`, extrait 1 image par seconde. Utile pour une
  analyse image par image d'un clip très court (quelques secondes).
- `-NoAudio` : n'extrait pas l'audio.

**Pourquoi pas "plusieurs milliers de frames"** : Claude lit les images une
par une dans une conversation, chaque image consomme du contexte. Des
milliers de frames sont illisibles en pratique (et inutiles — une vidéo de
30s à 1 frame/2s donne déjà 15 images bien réparties). Le bon réglage est
un échantillon représentatif, pas un découpage exhaustif.

### 2. Transcrire l'audio (optionnel)

Deux options :

**Option A — Gratuite et locale (recommandée)** : `faster-whisper`, tourne
sur le CPU, sans clé API, sans connexion internet après le premier
téléchargement du modèle.

```powershell
python transcribe_local.py "output\ma_video\audio.mp3"
```

Paramètres utiles :
- `--model tiny` : le plus rapide, correct pour une vidéo courte et claire.
  `--model base` (défaut) : bon compromis vitesse/précision sur un CPU
  modeste. `--model small`/`medium` : plus précis mais nettement plus lent
  sans GPU — à éviter sur une machine peu puissante.
- `--lang fr` : force le français (sinon détection automatique, fiable en
  général).

Le premier lancement télécharge le modèle (quelques dizaines à quelques
centaines de Mo selon la taille choisie), les suivants sont hors-ligne.

**Option B — Via l'API OpenAI (payante)** : plus précise sur des audios
difficiles, mais facturée à la minute et nécessite une clé API.

```powershell
$env:OPENAI_API_KEY = "sk-..."
.\transcribe.ps1 -AudioPath "output\ma_video\audio.mp3"
```

Dans les deux cas, le résultat est écrit dans
`output\ma_video\transcript.txt`.

### 3. Donner le résultat à Claude

Une fois `extract.ps1` (et éventuellement `transcribe.ps1`) lancés, donne
simplement le chemin du dossier `output\<nom_video>\` dans la conversation.
Claude lit les frames avec son outil `Read` et le `transcript.txt` comme un
fichier texte normal, puis peut analyser cadrage, texte à l'écran,
transitions, cohérence avec la transcription, etc.

## Vidéos YouTube (tutoriels plus longs)

Pour des vidéos YouTube (tutos, plus longues qu'un clip TikTok), deux scripts
séparés téléchargent puis traitent en masse, résultat dans `tutorials/` :

```
tutorials/
├── downloads/          # vidéos .mp4 téléchargées + <id>.info.json (titre, auteur)
└── library/
    └── <id>/
        ├── frames/      # nombre de frames ADAPTÉ à la durée (voir plus bas)
        ├── audio.mp3
        ├── transcript.txt
        └── meta.json    # titre, auteur, durée, nb de frames
```

### 1. Télécharger

```powershell
cd "F:\Tiktok\video-vision"
python download_youtube.py "https://youtube.com/watch?v=..." "https://youtube.com/watch?v=..."
```

Plusieurs liens en une seule commande, séparés par des espaces. Limité à
1080p pour ne pas saturer le disque inutilement.

### 2. Traiter (frames + audio + transcription)

```powershell
python process_tutorials.py
```

Traite toutes les vidéos présentes dans `tutorials\downloads\`. Contrairement
à `process_library.py` (12 frames fixes, clips courts), le nombre de frames
s'adapte à la durée :

- `--frames-per-min 2` (défaut) : ~2 frames par minute de vidéo.
- `--max-frames 60` (défaut) : plafond, même pour une vidéo de 2h — au-delà,
  ça devient illisible pour moi en une passe.
- `--model base` (défaut) : voir les options dans la section transcription
  locale plus haut. Pour une vidéo longue, la transcription prend plus de
  temps (roughly proportionnel à la durée) — normal de le lancer en fond.

### 3. Donner le résultat à Claude

Comme pour `library/`, donne le chemin de `tutorials\library\<id>\` (ou juste
l'ID/l'URL) et le contexte de ce que tu veux en tirer.

## Nettoyage

Le dossier `output\<nom_video>\` peut être supprimé une fois l'analyse
terminée — rien n'y est conservé de façon permanente, ce sont des fichiers
de travail.
