# Note Technique — Couche d'Accessibilité Linguistique SAFINUM 2026

> **Projet** : SAFINUM Innovate Challenge 2026  
> **Livrable 4** : Architecture, intégration, dépendances déclarées et limites  
> **Cible de référence** : `https://safinum.cm/hackathon-test` (Safinum Pay)  
> **Version documentée** : 1.3.0 (Transparence IA & Recoupement Lexical)

---

## 1. Architecture du Système

La solution SAFINUM Accessibility est structurée selon un modèle à double anneau découplé, alliant exécution locale réactive dans le navigateur et souveraineté totale du traitement linguistique.

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                               Navigateur Client (Chromium)                              │
│                                                                                         │
│   ┌─────────────────────────────────────┐         ┌─────────────────────────────────┐   │
│   │ Site Cible (https://safinum.cm/...) │         │ Widget d'Accessibilité          │   │
│   │ • SPA Vue 3 / Inertia.js            │         │ • Encapsulation Shadow DOM      │   │
│   │ • Aucune modification du code source│         │ • Isolation CSS et événements   │   │
│   │ • Nœuds textuels observés           │         │ • Bandeau permanent d'alerte IA │   │
│   └──────────────────┬──────────────────┘         └────────────────┬────────────────┘   │
│                      │                                             │                    │
│                      ▼                                             ▼                    │
│   ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│   │ Content Script Manifest V3 (Pur Vanilla JS ES6)                                 │   │
│   │ • TreeWalker (filtrage strict script/style/inputs/boutons)                      │   │
│   │ • MutationObserver avec anti-rebond (160 ms) et verrouillage anti-boucle        │   │
│   │ • Bilinguisme visible pour données critiques : Texte source [Proposition]       │   │
│   │ • Mode Démo Hors Ligne embarqué (catalogue_offline.json)                        │   │
│   └────────────────────────────────────────┬────────────────────────────────────────┘   │
└────────────────────────────────────────────┼────────────────────────────────────────────┘
                                             │ Appels HTTP JSON asynchrones (port 8000)
                                             ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           Backend Local Souverain (FastAPI)                             │
│                                                                                         │
│   ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│   │ Module protect.py (Pipeline d'Intégrité Financière)                             │   │
│   │ 1. Échappement préventif des faux jetons utilisateur                            │   │
│   │ 2. Masquage déterministe (URLs, Références, Téléphones, Montants, Comptes)     │   │
│   │ 3. Restauration exacte et contrôle multi-ensemble (Tokens_in == Tokens_out)     │   │
│   │ 4. Détection ReDoS immunisée (< 0,01 ms)                                        │   │
│   └────────────────────────────────────────┬────────────────────────────────────────┘   │
│                                            │                                            │
│   ┌────────────────────────────────────────▼────────────────────────────────────────┐   │
│   │ Chaîne de Résolution Séquentielle                                               │   │
│   │ [1] Mémoire de Traduction (machine_suggested — brouillons IA)                   │   │
│   │ [2] Glossaire Financier (52 termes terminologiques — machine_suggested)         │   │
│   │ [3] Moteur Automatique pour Inédits (marqué machine_suggested + bilinguisme)    │   │
│   │ [4] Repli Source Garanti (fallback_source)                                      │   │
│   └─────────────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Intégration sans Toucher au Code Source du Service Cible

La contrainte d'indépendance absolue du site cible est satisfaite par cinq mécanismes techniques :

1. **Extraction en Lecture Seule via `TreeWalker`** :  
   Le content script traverse le DOM avec `document.createTreeWalker(root, NodeFilter.SHOW_TEXT)`. Seuls les nœuds de texte pur visibles sont collectés.
2. **Sanctuarisation des Champs de Saisie et Boutons** :  
   Les balises `<input>`, `<textarea>`, `<select>` sont **systématiquement rejetées** (`NodeFilter.FILTER_REJECT`). Leurs valeurs, états réactifs Vue 3 et gestionnaires d'événements (`v-model`, validation de formulaire) ne sont jamais interceptés ni réécrits.
3. **Encapsulation Étanche en Shadow DOM** :  
   Le widget utilisateur est injecté dans un hôte unique `#safinum-accessibility-host` doté d'un `ShadowRoot` isolé (`attachShadow({ mode: 'open' })`). Aucune règle Tailwind CSS du site cible ne peut altérer l'interface du widget, et les styles du widget ne peuvent fuiter dans la page hôte.
4. **Surveillance Réactive avec Verrouillage d'Inhibition** :  
   Le `MutationObserver` écoute `#app` avec un anti-rebond de 160 ms pour absorber les rendus partiels d'Inertia.js. Pour éliminer tout risque de boucle de ré-observation infinie lors de l'écriture des traductions, un verrou mémoire `state.isMutating = true` bloque temporairement l'écouteur pendant la mise à jour des nœuds.
5. **Réversibilité Instantanée en Mémoire** :  
   Le texte français initial de chaque nœud est conservé en mémoire locale (`node._safinum_orig`) et sauvegardé dans l'attribut DOM `data-safinum-orig`. Un simple clic sur le widget restaure 100 % du texte d'origine en moins de 5 ms, sans rechargement de page ni requête réseau.

---

## 3. Dépendances et Composants Tiers Déclarés

Conformément à la règle permanente de sobriété technique (`AGENTS.md`) et au registre [`THIRD_PARTY.md`](../THIRD_PARTY.md) :

### A. Extension Navigateur (Client)
* **Zéro bibliothèque tierce** : Pur Vanilla JavaScript (ES6+ standard).
* **Architecture Manifest V3 & Service Worker** : Relais réseau isolé via `background.js` avec `host_permissions` restreintes (`127.0.0.1:8000`, `localhost:8000`), assurant le respect des règles W3C Private Network Access et Mixed Content sans affaiblir la sécurité du navigateur.
* **Empreinte totale du dossier `extension/`** : **113 152 octets (110,50 Ko)** (somme exacte des fichiers `background.js`, `content.js`, `manifest.json` et `offline_catalog.json`).

### B. Backend Local (Python 3.10+)
Toutes les dépendances sont déclarées dans [`backend/requirements.txt`](../backend/requirements.txt) :
* **FastAPI (`>=0.115.0`)** — Licence BSD-3-Clause : Routage HTTP asynchrone, validation OpenAPI 3.0.3, CORS restreint.
* **Uvicorn (`>=0.30.0`)** — Licence BSD-3-Clause : Serveur ASGI local.
* **Pydantic (`>=2.0.0`)** — Licence MIT : Validation stricte des contrats de données `/translate/batch`.
* **python-dotenv (`>=1.0.0`)** — Licence BSD-3-Clause : Isolation des variables d'environnement.
* **httpx (`>=0.27.0`)** — Licence BSD-3-Clause : Client HTTP utilisé pour les tests d'intégration unitaires.
* **CTranslate2 (`4.9.0`)** — Licence MIT & **SentencePiece (`0.2.3`)** — Licence Apache-2.0 : Runtime d'inférence neuronal local INT8 pour le Fulfulde.

### C. Modèle Local et Modèles d'IA Déclarés
Déclarés formellement dans [`THIRD_PARTY.md`](../THIRD_PARTY.md) :
* **cameroon-int8 (flagship-ai)** — Licence **CC BY-NC 4.0** : Moteur Fulfulde (flagship-ai/cameroon-int8, CC BY-NC 4.0) intégré, testé sur 20 libellés, écarté du parcours de démonstration car les sorties observées présentent des signes d'incohérence (répétitions, anglais non traduit, contenu hors domaine). Qualité non mesurée, variété du Fulfulde non vérifiée, aucune relecture native. Le garde-fou d'intégrité a basculé en repli source sur 6 phrases contenant des valeurs financières. Moteur désactivé par défaut (accessible uniquement via le mode expérimental).
* **Claude Sonnet 4.6 (Thinking)**, **Claude Opus 4.6 (Thinking)** (Anthropic / claude.ai), **Gemini 3.8 Flash (High/Medium)** et **GPT-OSS 120B (Medium)** (Antigravity) : Utilisés avec des rôles spécialisés strictement circonscrits (code, audit contradictoire, brouillons de traductions en langues locales). Leurs limites justifient le statut strict `machine_suggested` et le contrôle par masquage déterministe.

---

## 4. Préservation de l'Intégrité Financière

Le module [`backend/protect.py`](../backend/protect.py) applique un pipeline de sécurisation en 4 étapes :

1. **Échappement Préventif des Faux Jetons** : Tout motif `__SAFE_` présent dans le texte source utilisateur est temporairement transformé en `__ESCAPED_SAFE_` pour empêcher toute attaque par collision ou forgeage de jetons.
2. **Masquage Déterministe Hiérarchisé** :
   - `URL` : URLs complètes avec paramètres de requête (`https://...`).
   - `REF` : Références d'opérations bancaires (`SAF-2026-*`, `REF-*`).
   - `TEL` : Numéros de téléphone camerounais (+237 6xx, 2xx).
   - `ACCT` : Numéros de comptes au format CM et suites numériques bancaires.
   - `PCT` : Pourcentages et commissions (`1,5 %`, `2 %`).
   - `AMOUNT_WORDS` : Montants formulés en toutes lettres (`vingt-cinq mille francs CFA`).
   - `AMOUNT` : Montants chiffrés avec devises (`FCFA`, `XAF`, `CFA`, `EUR`, `USD`, `€`, `$` et espaces insécables Unicode `\u00A0`, `\u202F`).
   - `BENEF` : Noms de bénéficiaires identifiés contextuellement (`Bénéficiaire : ...`, `Vers ...`).
   - `NUMBER` : Nombres purs isolés issus du découpage de balises imbriquées (`25 000`, `0`).
3. **Contrôle Multi-Ensemble Strict** : Après traduction, le sac de jetons en sortie est comparé au sac d'entrée :
   Counter(jetons présents) == Counter(jetons attendus)
4. **Bilinguisme Non-Substitutif pour Chaînes Critiques** :  
   Pour toute chaîne à sensibilité financière ou sécuritaire (montants, frais, alertes, erreurs, récapitulatifs) non attestée par un locuteur natif, le système affiche le texte original français suivi de la proposition entre crochets sans remplacement :
   Rendu = Texte source + [Proposition]
5. **Repli Source Immédiat** : En cas d'altération de jeton, de timeout moteur ou d'incohérence, le système bascule immédiatement sur le texte original français (`fallback_source`).

---

## 5. Méthode d'Élaboration, Recoupement Lexical et Limites Réelles

### A. Statut de Validation : 0 / 84 Chaînes Validées par un Locuteur Natif
* **Décompte des chaînes du catalogue** : Le catalogue compte **84 expressions / segments techniques** répertoriés dans les fiches de validation CSV et dans `catalogue/translations.csv` (84 entrées par langue). En raison de l'homonyme français « Sécurité » (utilisé pour deux clés distinctes `status_security` et `sec_sidebar_title`), le dictionnaire hors-ligne `extension/offline_catalog.json` indexé par texte source comporte exactement **83 entrées sources uniques** par langue (pour 84 segments au total).
* **Aucune validation humaine n'est acquise à cette étape** (100 % statut `machine_suggested`).
* **Méthode adoptée** : **Brouillon IA + Recoupement lexical + Garde-fou d'intégrité**.
* **Résultats du recoupement lexical réel (`catalogue/crosscheck_rapport.csv`)** :
  - **Duálá (`dua`)** : 0 / 84 (0,0 %) attesté, 0 / 84 (0,0 %) partiellement attesté, 84 / 84 (100,0 %) non attesté dans la colonne `traduction` du lexique Mélac (qui ne compte que 7 mots anatomiques).
  - **Ɓàsàa (`bas`)** : 4 / 84 (4,8 %) totalement attesté (*Mbebi*, *Bañga ipe*, *Nsal*, *Loñge*), 58 / 84 (69,0 %) partiellement attesté, 22 / 84 (26,2 %) non attesté sur 994 mots réels.
  - **Combiné global** : 4 / 168 (2,4 %) attesté, 58 / 168 (34,5 %) partiel, 106 / 168 (63,1 %) non attesté.
* **Validation native finale** : Prévue avant la finale (26-28 novembre 2026) via la feuille de travail [`catalogue/fiche_validation.csv`](../catalogue/fiche_validation.csv) soumise à des locuteurs natifs certifiés.

### B. Limites Connues et Périmètre Non Mesuré
1. **Saisie dans les Formulaires (`input`, `textarea`)** :  
   Par conception de sécurité bancaire, les valeurs saisies par l'utilisateur ne sont jamais manipulées. Seuls les libellés (`label`), placeholders, aides à la saisie et boutons sont traduits.
2. **Synthèse Vocale (Text-To-Speech)** :  
   Bien que des enregistrements audio de référence existent dans le dépôt (`shared/data/duala/audio/`), le raccordement TTS n'est pas finalisé dans ce prototype.
3. **Performances Réelles Mesurées sur Banc d'Essai PC (Win 11 / Intel i7 / Edge)** :
   - Temps de premier rendu traduit : **234 ms** (offline) / **224 ms** (online) (médiane sur 12 itérations) — voir rapport complet [`docs/mesures_performance.md`](mesures_performance.md).
   - Latence API batch locale (`/translate/batch`) : **16 ms** (médiane sur 200 appels de 8 phrases) — voir [`docs/mesures_performance.md`](mesures_performance.md).
   - Temps de retour à la langue source (`revertToSource`) : **0,8 ms** (médiane sur 15 itérations) — voir [`docs/mesures_performance.md`](mesures_performance.md).
   - Convergence des mutations DOM : **0 mutation résiduelle** après 5 étapes bancaires (absence de boucle infinie prouvée) — voir [`docs/mesures_performance.md`](mesures_performance.md).
   - Temps d'exécution des tests unitaire backend : **0,31 s** pour 155 tests.
4. **Périmètre Non Mesuré (Véracité des Métriques)** :
   - Latence sur smartphone ARM d'entrée de gamme : **non mesuré**.
   - Consommation de batterie sur session prolongée : **non mesuré**.
   - Débit réel sur réseau 2G/EDGE en milieu rural : **non mesuré** (compensé par le mode hors-ligne à 0 requête réseau).
   - Taux d'intelligibilité des périphrases auprès d'utilisateurs ruraux non lettrés : **non mesuré**.
   - Qualité intrinsèque du modèle Fulfulde (`cameroon-int8`) sur terminologie bancaire : **non mesuré**.
   - Variété dialectale du Fulfulde (Adamaoua vs Diamaré) : **non vérifiée**.
