# Tiktok_Automation

Pipeline d'automatisation de génération de vidéos courtes (TikTok/YouTube
Shorts) façon "Voici pourquoi..." — finance et psychologie de l'argent,
rendu 3D photoréaliste, mascotte récurrente (Ferdinand).

## Structure

- **`video-vision/`** — pipeline actif (Python), voir
  `video-vision/GENERATION_GUIDE.md` pour la doc complète et à jour.
  Le script principal est `video-vision/zack-video-01/generate.py`.
- **`tiktok-video-generator/`** — premier prototype (n8n + Docker),
  conservé pour référence, non utilisé activement.

## Démarrage rapide

```bash
cd video-vision/zack-video-01
python generate.py --mode 60s --lang fr
```

Nécessite une clé API KIE.AI dans un fichier `api.txt` à la racine
(non versionné, voir `.gitignore`).
