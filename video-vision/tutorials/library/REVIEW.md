# Revue des 7 tutoriels YouTube "Zack D Films style with AI"

7 vidéos téléchargées et transcrites (voir `tutorials/downloads/*.info.json`
pour les métadonnées complètes). Toutes expliquent comment recréer le style
Zack D Films avec des outils IA gratuits ou peu chers. Complété par la
lecture de 2 PDF fournis par l'utilisateur (`F:\Tiktok\*.pdf`).

## Les 7 vidéos

| id | titre | durée | chaîne (marque visible) |
|---|---|---|---|
| -ywEXrGnAYI | How To Make 3D Animated Shorts Like Zack D Films Using AI (100% Free) | 3:26 | — |
| 2cdiRopMoeQ | How I Made Zack D–Style AI Shorts for FREE (Full Tutorial) | 5:36 | ReachMora |
| _r3nVG-aFs0 | I Made This ZACK D FILMS Animation With a FREE Prompt (Full Tutorial) | 11:18 | Discord "Pulse app" |
| OQdU-b9-xtg | I Used AI to Recreate Zack D–Style YouTube Videos | 6:26 | 10xdude |
| p1Te9SKaTiE | I Finally Cracked Zack D Films Animation with AI | 9:14 | (narration multilingue EN/UR) |
| xQq-ogS5va8 | How I Made Zack D Films–Style AI Shorts for FREE (Full Tutorial) | 10:11 | — |
| y3U3MA7ex7Y | How To Make STUNNING 3D Animated Shorts Like Zack.D Films | Full Workflow 2026 | 7:32 | EarnWithAI |

Malgré des créateurs différents, **la chaîne d'outils converge quasi
partout** : chatbot (idées + script + prompts) → générateur d'images →
générateur vidéo (image-to-video) → générateur de voix → CapCut (montage).

## La chaîne d'outils (vue d'ensemble)

| Étape | Outils vus | Le plus cité |
|---|---|---|
| Idées + script + prompts | ChatGPT, Claude AI (recommandé pour les prompts longs/complexes), DeepSeek | **ChatGPT ou Claude** avec un prompt système détaillé collé une fois en début de conversation |
| Images (texte→image) | **Google Flow** (Nano Banana / Nano Banana 2 / Nano Banana Pro), Gemini directement, Midjourney, Higgsfield, Dall-E | **Google Flow + Nano Banana Pro**, format 9:16 |
| Vidéo (image→vidéo) | **Google Flow (Veo 3 / 3.1 Fast / 3.1 Lite / OmniFlash)**, Grok ("Imagine" tab), OpenArt, Seedance 2.5 | Veo 3.1 dans Google Flow le plus fréquent ; Grok en 2e choix (10-20 clips/jour gratuits) |
| Voix off | **ElevenLabs**, Fish Audio (limite 500 caractères gratuit), Google AI Studio (voix + instructions de ton) | **ElevenLabs** |
| Montage | **CapCut** (quasi unanime) : timeline, auto-captions, fade in/out musique, suppression des silences | CapCut |
| Musique | YouTube Audio Library, Pixabay | — |

## Les 3 méthodes techniques pour la vidéo (différence importante)

En croisant les tutoriels, il y a **3 façons distinctes** de passer d'une
image à un clip animé, pas une seule :

### Méthode A — Image + prompt d'animation (la plus simple, la plus courante)
Une image de départ + un prompt de mouvement de caméra/sujet → un clip
court (4-10s). Utilisée par -ywEXrGnAYI, OQdU-b9-xtg (avec Grok), xQq-ogS5va8
(avec Google Flow "OmniFlash", 4s/clip). C'est ce qui correspond exactement
aux prompts 3 et 4 collés par l'utilisateur (text-to-image puis
image-to-video, un plan = un prompt indépendant, angle de caméra qui varie
à chaque scène). **Résultat : plans distincts, cuts entre eux** — cohérent
avec ce qu'on avait observé en échantillonnant les frames des vraies vidéos
Zack D Films.

### Méthode B — Première image + image de fin (interpolation)
Pour chaque "beat" (scène), on génère **deux images** : une frame de départ
et une frame de fin, avec le même personnage de référence. Le modèle vidéo
(Veo 3.1) interpole le mouvement entre les deux. Utilisée par _r3nVG-aFs0
(système avancé via Discord + Claude, "Scene Image Generator" qui sort un
prompt "first frame" et un prompt "end frame" par beat) et y3U3MA7ex7Y
(Google Flow, fonctionnalité "frames" : on charge une image dans le slot
"first frame", Flow génère la vidéo). C'est ce qui donne des mouvements de
caméra **fluides et intentionnels** (zoom, pan) à l'intérieur d'un même
plan, par opposition à un simple clip animé depuis une seule image de
départ.

### Méthode C — Extension depuis la dernière frame ("extend"/timeline)
On génère un premier clip (10s), puis on **prolonge** en réutilisant sa
dernière frame comme point de départ du clip suivant (bouton "Extend"
visible directement dans l'interface Google Flow), créant une séquence
longue et continue plutôt que des plans indépendants recollés au montage.
Décrite dans le PDF de DeeTion (Seedance 2.5, "timeline prompting", clips de
10s étendus) et dans le tutoriel p1Te9SKaTiE (fonction "extend video" pour
dépasser la limite de 30s en 3 exports de CapCut successifs).

**Ces 3 méthodes ne s'excluent pas** : on peut très bien enchaîner une
Méthode B (pour les plans qui ont besoin d'un mouvement précis) avec des
coupes dures façon Méthode A entre les scènes (changement de decor/sujet),
ce qui correspond exactement à ce qu'on avait observé dans les 66 vidéos
TikTok (cuts durs + a l'intérieur de certains plans un vrai mouvement de
caméra fluide).

## Le système de prompt le plus abouti (_r3nVG-aFs0, "MDA")

Le tutoriel le plus technique utilise un système en chaîne dans **Claude**
(recommandé car "gère mieux les prompts longs et structurés") :
1. Rejoindre un Discord, télécharger 3 fichiers : une **image de référence**
   du personnage/style, un **zip de frames de référence** (screenshots de
   vraies vidéos Zack D Films), et un **PDF "model script"** (structure de
   script).
2. Coller le prompt "**Model DNA Analyzer (MDA)**" dans Claude + déposer le
   zip → Claude construit une bibliothèque de référence (personnages,
   décors, types de plans, anatomie, couleurs).
3. Coller le prompt "**Model Script Analyzer**" + déposer le PDF → apprend
   à Claude la structure exacte de script (nombre de mots, rythme, ton).
4. Coller le prompt "**Topic Generator**" → génère des idées basées sur des
   **faits réels vérifiables** (pas d'hallucination), ex. "pourquoi les
   soldats rompent le pas sur un pont" → événement réel (pont de Broughton,
   1831).
5. Coller le prompt "**Character Profile Image Generator**" + le numéro du
   sujet choisi → génère un personnage cohérent avec le sujet (un soldat
   pour un sujet militaire, pas un personnage générique).
6. Coller le prompt "**Scene Image Generator**" → découpe le script en
   "beats", chaque beat = un prompt image de première frame + un prompt
   image de dernière frame (Méthode B ci-dessus).
7. Coller le prompt "**Video Motion Generator**" → un prompt de mouvement
   par beat, à utiliser avec les 2 frames dans Google Flow (Veo 3.1).

Point d'attention répété dans cette vidéo : **ne jamais sauter une étape**
(sinon "la chaîne casse et il faut tout recommencer"), **traiter les beats
dans l'ordre**, et **ne jamais cloner la voix d'un créateur existant** (risque
de démonétisation/plainte).

## Confirmation visuelle (frames)

- Interface **ChatGPT/Claude** : liste numérotée de scènes générées en une
  seule réponse structurée.
- Interface **Google Flow** : onglets latéraux *All Media / Images /
  Characters / Scenes / Tools* — un onglet "Characters" dédié à la
  cohérence du personnage. Sélecteur de modèle (**Nano Banana 2**, **Veo
  3.1 Lite/Fast**). Boutons **Extend / Insert / Remove / Camera** visibles
  directement sous un clip généré, confirmant que l'extension "dernière
  frame → nouveau clip" (Méthode C) est une fonctionnalité native de
  l'outil, pas un bricolage.
- Le prompt système lu dans l'interface Claude d'une des vidéos
  (y3U3MA7ex7Y) est **mot pour mot identique** au prompt "IMAGE-TO-VIDEO
  (ANIMATION)" que l'utilisateur a collé dans la conversation — confirme
  que ces prompts sont bien ceux réellement utilisés dans cette vidéo (pas
  une reconstruction a posteriori).

## Les prompts fournis (verbatim, à réutiliser tels quels)

Trois familles de prompts collectées, cohérentes entre elles mais de
complexité croissante. Voir aussi les 2 PDF sources (`ZACKD STYLE PROMPTS
2.pdf` = ReachMora, `Zack-D-Film Prompt (1).pdf` = DeeTion) pour le texte
intégral déjà lu et résumé ci-dessus.

### Set "EarnWithAI" (le plus détaillé, correspond à y3U3MA7ex7Y) — donné par l'utilisateur dans le chat
1. **Idea generator** — 10 titres viral, patterns fixes ("What happens
   if…", danger caché, survie, fait bio choquant…), 3-10 mots, sortie =
   titres seuls.
2. **Script generator** — 20-40s à l'oral, phrases ≤8 mots, structure
   Hook→Curiosity→Tension→Payoff, ton dramatique, pas de labels, sortie =
   script seul.
3. **Text-to-image prompt generator** — découpe en 7-8 scènes. Règle de
   cohérence du personnage (genre, peau, cheveux, vêtement précis, répété
   mot pour mot à chaque scène). **Style lock obligatoire** à coller dans
   chaque prompt : `semi-realistic 3D CGI, GTA V / The Last of Us cutscene
   quality, realistic skin texture with visible pores, natural cinematic
   lighting, detailed real-world environment, photorealistic 3D render, no
   cartoon, no cel shading, no Pixar, no simple background, no studio
   backdrop`. 8 angles de caméra à faire tourner (macro mains, over-shoulder
   flou, à travers une vitre, plongée/contre-plongée, plan moyen, intérieur
   serré, vue aérienne, push-in lent). Mots interdits listés (évite tout ce
   qui sent l'IA/le générique).
4. **Image-to-video (animation) prompt, pour Veo 3.1 Fast dans Google
   Flow** — 50 mots max, mouvement caméra ET mouvement sujet décrits
   séparément, un mouvement dominant par scène, intensité calée sur l'humeur
   de la scène (calme/tendu/action/révélation/émotion).

### Set ReachMora (plus simple, généraliste)
1. Idea generation — 10 histoires vraies étranges/choquantes, cinématiques,
   courtes.
2. Script + visuels — script 1 min dramatique, découpé en 4-6 scènes, prompt
   "3D-rendered, photorealistic", terminologie cinéma (wide shot, close-up,
   low-angle tracking shot), "feels like a game cutscene from a realistic 3D
   animated game".
3. (Optionnel) Réécriture de script à partir d'une transcription existante,
   pour ne pas juste copier une vidéo virale.
Outils recommandés : ChatGPT, Nano Banana/Gemini, ElevenLabs, Grok AI
(animateur vidéo), CapCut.

### Set DeeTion (le plus élaboré, orienté Seedance/Méthode C)
Entraînement du chat en 3 messages (contexte du clone de chaîne + exemples
de scripts réels + règles de génération), puis commandes courtes réutilisées
en boucle : **"More Ideas"** (nouvelles idées), **"Full Script"** (script +
prompts détaillés dans le style), **"Visuals"** (plans connectés par
mouvement de caméra, adaptés à l'attention courte du format short),
**"Prompt"** (prompts vidéo complets : style d'animation + environnement +
personnage + objet + mouvement de caméra). Règle clé : pour la 1ère scène,
générer à la fois un prompt texte→image, son prompt image→vidéo, ET un
prompt texte→vidéo pur, comparer, et garder la version choisie comme base
de cohérence pour la suite. Les scènes suivantes n'ont besoin **que** des
nouveaux éléments (le reste vient de l'extension de la frame précédente).

## À retenir pour la suite (build du système en code)
Voir `video-vision/GENERATION_GUIDE.md` pour la synthèse actionnable
combinant ces tutoriels avec l'analyse des 66 vraies vidéos TikTok
(`video-vision/library/REVIEW.md`).
