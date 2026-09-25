# Guide de génération — chaîne "Voici pourquoi" (finance/psychologie de l'argent)

Document de référence unique, à relire avant toute session de travail sur
le générateur. Reflète l'état **réel actuel** du pipeline (`zack-video-01/
generate.py`) au 26/09/2026 — ce fichier a été entièrement réécrit ce
jour-là pour remplacer une version obsolète (phase n8n / niche Zack D
Films "évolution des espèces" / sous-titres encore présents / pas de
mascotte). L'historique détaillé de cette phase antérieure reste dans
`library_zack_d_films/REVIEW.md` et `tutorials/library/REVIEW.md` si
besoin de contexte, mais **le pipeline actif a complètement changé de
niche et d'architecture depuis**.

## 1. Le format en une phrase
Un short vertical (durée variable, ~35s à ~90s selon le mode et ce que le
script demande naturellement), narré en voix off, qui part d'une sensation
banale sur l'argent que tout le monde a vécue ("Voici pourquoi ton salaire
disparaît si vite") et révèle la raison cachée derrière (biais
psychologique, stratégie commerciale, mécanisme bancaire) — **pas** une
histoire chiffrée façon "Tom accumule des gains" (ancienne version,
abandonnée après retour utilisateur : *"tu es trop dans les nombres"*).
Rendu 3D photoréaliste (style "Zack D Films" conservé), personnage
récurrent (Ferdinand le renard), pas de sous-titres, CTA final systématique.

## 2. Le personnage : Ferdinand
Mascotte fixe de la chaîne, décidée pour remplacer une idée initiale de
reprendre Picsou (refusée : droits d'auteur Disney + incompatible avec le
rendu 3D photoréaliste). Description figée dans `generate.py` (constante
`CHARACTER`), réutilisée mot pour mot sur **toutes** les vidéos :

> Ferdinand, an anthropomorphic red fox standing and posing like a human,
> sleek reddish-orange fur with a white muzzle and chest and black-tipped
> ears and paws, sharp intelligent amber eyes, wearing a tailored deep-red
> three-piece suit with a gold pocket-watch chain and a black silk pocket
> square, sleek well-groomed fur, confident bourgeois posture, no logos

Règle d'apparition (`MASCOT RULE` dans `build_scenes_system`) : Ferdinand
apparaît **obligatoirement** sur la toute première scène (hook) et la
toute dernière (payoff+CTA), même si le texte du script ne le nomme pas —
c'est un choix purement visuel de branding. D'autres personnages humains
peuvent apparaître ailleurs dans l'histoire (ex. l'exemple illustratif),
sans jamais remplacer Ferdinand comme hôte des scènes d'ouverture/clôture.

## 3. Format des idées et du script

### Idées (`build_idea_system`)
Chaque titre commence obligatoirement par "Voici pourquoi" (FR) / "Here's
why" (EN), suivi d'une observation quotidienne ultra-relatable. Rotation
sur 8 angles : argent/quotidien, psychologie de consommation, cerveau &
argent (biais cognitifs), banques & crédit, internet/tech (économie de
l'attention), travail & richesse, curiosité forte, vie locale (optionnel,
pas systématique).

### Script (`build_script_system`)
Structure en 6 étapes (plus l'ancienne structure "Tom" à 8 étapes) :
1. **Hook** — reprend quasi mot pour mot le titre ("Voici pourquoi...")
2. **La sensation quotidienne** — décrite directement au spectateur ("tu")
3. **La raison cachée** — le mécanisme réel, en mots simples
4. **Exemple concret** (optionnel, seulement si ça aide vraiment)
5. **Chute / reformulation**
6. **CTA** — toujours l'angle "effort" ("si tu as aimé, ça demande du
   travail...") avec formulation qui varie à chaque fois

Règles clés :
- **Chiffres redevenus optionnels** ("NUMBERS RULE (relaxed)") — un chiffre
  seulement s'il aide vraiment à visualiser, jamais de chaîne de chiffres
  forcée. C'est l'inverse exact de l'ancienne règle "Tom" qui exigeait un
  chiffre à chaque étape.
- **Vocabulaire simple** : compréhensible par un ado de 13 ans, tout terme
  technique expliqué dans la même phrase.
- **Balises d'émotion** (`[whispers]`, `[urgency]`, `[curious]`,
  `[dramatic]`, etc.) : 2 à 4 par script, jamais plus d'une par phrase.
  Confirmé supporté nativement par `google/gemini-3-1-flash-tts` (et par
  `gemini-2.5-pro-tts`) — pas besoin d'ElevenLabs pour ça.
- **Pas de plafond de mots strict** — on ne peut pas fiablement prédire la
  durée orale à partir d'un nombre de mots (langue, débit, pauses, balises
  varient trop). La durée émerge de la mesure réelle de la voix (§4).

## 4. Architecture du pipeline (voix générée scène par scène)

**Constat de départ** : générer la voix en un seul bloc puis découper le
script "à l'aveugle" en N scènes de durée fixe (5s chacune) crée un
décalage progressif entre ce qui est dit et ce qui est montré — chaque
scène affichée dure 5s pile, mais une phrase peut se dire en 1,5s ou 6s.
Comme Gemini TTS ne renvoie **pas** de minutage mot-par-mot (contrairement
à l'endpoint ElevenLabs `with-timestamps`, non confirmé compatible avec
`eleven_v3`), la solution retenue est de générer **une voix séparée pour
chaque scène** :

1. **Idée** → 10 titres "Voici pourquoi", on choisit le premier.
2. **Script** → texte complet avec balises.
3. **(Mode `60s` uniquement) Contrôle de durée** : un appel voix "de
   contrôle" (pas la voix finale) mesure la durée naturelle du script. Si
   < 60s, régénération d'un script plus étoffé (jusqu'à 3 tentatives
   supplémentaires) — **garantie dure ≥60s** pour l'éligibilité
   monétisation TikTok.
4. **Découpage en scènes** : chaque scène porte son `spoken_text` exact
   (sous-chaîne verbatim du script, balises incluses) en plus des prompts
   visuels — pas de plafond strict de nombre de scènes, juste une
   indication approximative.
5. **Génération scène par scène**, dans l'ordre :
   - Voix pour `spoken_text` de cette scène → durée réelle mesurée.
   - Image (nano-banana).
   - Vidéo (Runway par défaut, toujours en preset **5s** — voir piège
     ci-dessous) à partir de l'image.
   - `fit_clip_to_duration()` : **rogne** le clip vidéo si l'audio de la
     scène est plus court que 5s, ou **gèle la dernière image** en
     complément si l'audio dépasse 5s (rare, phrase longue) — le clip
     final dure exactement la durée de sa propre voix.
6. **Montage** : concaténation de tous les segments audio (= la voix
   finale) et de tous les clips vidéo déjà calés, puis fusion. L'écart
   résiduel n'est plus que l'arrondi d'encodage (dixièmes de seconde), pas
   un vrai décalage de plusieurs secondes comme avec l'ancienne approche.

**Effet de bord observé** : la somme des voix générées séparément (15
appels TTS) est ~10-15% plus longue que la même lecture en un seul bloc
continu (chaque clip TTS a un peu plus de "souffle" en début/fin isolé).
Sans conséquence négative pour la garantie ≥60s (ça ne fait qu'aider à la
dépasser), mais la vidéo finale peut être notablement plus longue que
l'estimation du contrôle de durée à l'étape 3.

**`--mode`** ne contrôle donc plus une durée ciblée, seulement l'AMPLEUR
narrative : `short` = histoire resserrée sans exemple ni durée garantie ;
`60s` = histoire complète avec exemple optionnel et durée ≥60s garantie.

## 5. Modèles retenus (état au 26/09/2026)

| Rôle | Modèle | Pourquoi |
|---|---|---|
| Idée/script/scènes (LLM) | `gpt-5.2` via KIE.AI | Claude indisponible sur KIE.AI lors des premiers tests (panne backend, résolue depuis mais jamais re-basculé) |
| Image | `google/nano-banana` | Le moins cher, qualité suffisante une fois animée |
| **Vidéo (défaut)** | **`runway`** via KIE.AI | ~31% moins cher que Seedance à 720p, qualité photoréaliste comparable ou supérieure (texte incrusté aussi fiable que Seedance). **Toujours demander le preset "5s"** — le preset "10s" s'est révélé peu fiable en test réel (4 échecs "internal error" sur 4 scènes en 10s dans un run, 0 échec sur les scènes en 5s) |
| Vidéo (repli) | `bytedance/seedance-1.5-pro` | `--video-model seedance`, gardé en solution de secours |
| Voix | `google/gemini-3-1-flash-tts` | Supporte les balises d'émotion inline (`[whispers]`, etc.) - confirmé sur la fiche KIE.AI. **`style: "Newscaster"`** (pas `"Deadpan"` — Deadpan signifie littéralement "sans émotion", ça écrasait l'effet des balises). Comparé à Gemini 2.5 Pro TTS : prix strictement identique sur KIE.AI ; Pro n'a d'avantage que sur du contenu >1-2min, non pertinent ici (nos clips font tous <90s) |

**ElevenLabs (v2 et v3)** : écarté. v2 était en panne sur KIE.AI lors des
tests initiaux ; v3 direct coûte ~85% plus cher ($0.10 vs $0.054/1000 car.)
et sa compatibilité avec le minutage mot-par-mot (`with-timestamps`) n'est
pas confirmée par leur propre doc — n'aurait probablement pas résolu le
problème de synchro qui a motivé l'architecture voix-par-scène du §4.

### Schémas API à jour
```json
// Idée / script / scènes (LLM) — synchrone, pas de polling
// POST https://api.kie.ai/gpt-5-2/v1/chat/completions
{"model": "gpt-5.2", "messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]}

// Image
{"model": "google/nano-banana", "input": {"prompt": "...", "image_size": "9:16", "output_format": "png"}}

// Vidéo — Runway (défaut)
{
  "model": "runway",
  "input": {
    "prompt": "...",
    "image_url": "<url image générée>",
    "duration": "5",
    "quality": "720p",
    "aspect_ratio": "9:16",
    "watermark": ""
  }
}

// Vidéo — Seedance (repli, --video-model seedance)
{
  "model": "bytedance/seedance-1.5-pro",
  "input": {
    "prompt": "...", "input_urls": ["<url image>"], "aspect_ratio": "9:16",
    "resolution": "720p", "duration": 5, "fixed_lens": false, "generate_audio": false
  }
}

// Voix off — un appel PAR SCÈNE (voir §4), pas un seul appel pour tout le script
{
  "model": "google/gemini-3-1-flash-tts",
  "input": {
    "speakers": [{"speaker_id": "Speaker 1", "voice_name": "Zephyr", "audio_profile": "dramatic narrator", "style": "Newscaster", "pace": "Natural", "accent": "Neutral"}],
    "dialogue_turns": [{"speaker_id": "Speaker 1", "text": "<spoken_text de CETTE scène>"}]
  }
}
```
Endpoint image/vidéo/voix : `POST https://api.kie.ai/api/v1/jobs/createTask`,
suivi de `GET /api/v1/jobs/recordInfo?taskId=...` en polling. Le LLM répond
de façon synchrone sur son propre endpoint.

**Pièges connus** :
- Slug nano-banana de base = `google/nano-banana` (préfixe `google/`
  obligatoire) — `nano-banana` seul renvoie 422.
- `style` du TTS n'accepte qu'une valeur simple parmi une liste fermée
  (`Vocal Smile`, `Newscaster`, `Whisper`, `Empathetic`, `Promo/Hype`,
  `Deadpan`) — une valeur composée renvoie 422. Nuances de ton dans
  `audio_profile` (texte libre), pas dans `style`.
- Preset vidéo Runway "10s" peu fiable — toujours utiliser "5" (voir §4).

## 6. Règles visuelles (scènes) — résumé
Détail complet dans `build_scenes_system()`, issu de l'analyse
frame-by-frame de `library_finance/REVIEW.md` :
- **Style lock** 3D photoréaliste (GTA V / Last of Us) collé sur chaque
  `image_prompt`.
- **Chiffres visibles** : seulement si le texte de la scène en contient un
  (plus systématique comme avant) — écrit physiquement dans le décor.
- **Mécanisme littéralisé** : la révélation du mécanisme mise en scène
  comme une métaphore visuelle concrète (étiquette de prix qui change,
  notification de téléphone, etc.), pas juste un personnage qui parle.
- **Scènes vivantes** (`SCENE LIVELINESS RULE`) : chaque scène doit avoir
  au moins un élément de vie — prop lié au texte, personnages en
  arrière-plan, ou activité ambiante. Jamais un personnage seul posé dans
  un décor vide (retour utilisateur explicite sur ce point).
- **Caméra quasi toujours fixe**, micro-mouvements seulement (clignement,
  respiration), sauf sur les plans tendus/révélation/final.
- **Pas de sous-titres** (retirés entièrement, demande explicite).

## 7. Filets de sécurité connus (bugs récurrents et correctifs)
GPT-5.2 (via ce endpoint KIE.AI) enveloppe parfois sa réponse dans un
balisage parasite malgré la consigne "no preamble" — plusieurs formes
observées, toutes corrigées défensivement dans `generate.py` :
- Fragment de balise orpheline en tête de script (`"ious] Comment..."` au
  lieu de `"[curious] Comment..."`) → nettoyé par regex + **validation
  stricte** que le script commence bien par le trigger phrase, avec
  réessai automatique sinon (`generate_valid_script()`).
- Wrapper document/canvas (`:::writing{...}` ... `:::`, ou
  `CodeBlock language="json">`) → `strip_json_fences()` extrait
  maintenant simplement le premier objet JSON valide (du premier `{` au
  dernier `}`), peu importe ce qu'il y a autour, plutôt que de traquer
  chaque variante au cas par cas.

Robustesse réseau :
- `http_json()` rattrape les erreurs réseau (timeout, connexion coupée),
  pas seulement les erreurs HTTP — un simple hoquet ne fait plus planter
  le pipeline.
- `download()` a maintenant des retries (avant : aucune gestion d'erreur,
  un `RemoteDisconnected` en fin de téléchargement faisait tout planter).
- `create_and_wait()` retente le cycle **complet** (nouvelle soumission
  incluse) si une tâche échoue côté serveur après avoir été acceptée
  (`state: "fail"`, ex. "internal error" sur Runway) — `wait_for_result()`
  seul abandonnait avant sans retenter.
- Reprise par scène : chaque scène vérifie l'existence de son clip ET de
  sa voix avant de regénérer — un run interrompu (Ctrl+C, crash réseau)
  reprend exactement où il s'est arrêté sans regaspiller de crédits.

## 8. Historique des pivots majeurs (pour contexte, pas pour usage actif)
1. **n8n → Python** : abandon du workflow n8n (`tiktok-video-generator/`)
   au profit d'un pipeline code direct (`zack-video-01/generate.py`).
2. **Niche "Zack D Films" (faits bio/évolution) → finance** : analyse de
   31 vraies vidéos finance (`library_finance/REVIEW.md`), rendu 3D
   conservé, domaine des idées changé.
3. **Structure "Tom accumule des chiffres" → "Voici pourquoi"** : la
   structure narrative chiffrée façon Zack D ne convenait pas à la
   psychologie de l'argent — pivot vers un format explicatif direct
   (25/09-26/09/2026), sur demande explicite avec liste de référence de
   l'utilisateur.
4. **Mascotte** : proposition initiale Picsou refusée (droits d'auteur) →
   Ferdinand (renard original).
5. **Sous-titres retirés** entièrement (demande explicite).
6. **Architecture voix** : un seul bloc → scènes calées sur durée mesurée
   globalement → voix par scène individuelle (§4), pour la synchro fine.
7. **Modèle vidéo** : Seedance seul → Runway par défaut (moins cher,
   validé sur plusieurs runs complets), Seedance en repli.

## 9. Fichiers clés
- **`zack-video-01/generate.py`** — pipeline complet, seule source de
  vérité sur le comportement actuel (ce document peut dériver, le code
  non). Usage : `python generate.py [--mode short|60s] [--lang en|fr]
  [--video-model runway|seedance]`.
- `library_finance/REVIEW.md` — analyse des 31 vraies vidéos finance
  source, y compris la section micro-détails visuels/animation et le
  post-scriptum sur les décisions réellement prises.
- `kie-test/` — scripts de test isolés (validation de schémas API avant
  intégration dans le pipeline principal).
