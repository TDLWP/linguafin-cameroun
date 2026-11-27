# THIRD_PARTY.md — Déclaration des Bibliothèques, Dépendances Tierces et Modèles d'IA

> **Projet** : SAFINUM Innovate Challenge 2026  
> **Conformité AGENTS.md** : Toute bibliothèque tierce et tout modèle d'IA utilisé doivent être explicitement déclarés avec leurs rôles et limites.

---

## 1. Extension Navigateur (Client)

| Composant | Version | Licence | Rôle | Taille approximative |
|---|---|---|---|---|
| **Vanilla JavaScript (ES6+)** | Standard | N/A (Natif) | Logique du content script, TreeWalker, MutationObserver | 0 Ko (Natif) |
| **Service Worker Manifest V3** | Standard W3C | N/A (Natif) | Relais réseau sécurisé vers backend local (`background.js`, respect PNA / CORS) | 0 Ko (Natif) |
| **Shadow DOM API** | W3C Standard | N/A (Natif) | Encapsulation étanche du widget d'accessibilité | 0 Ko (Natif) |
| **Web Storage / In-Memory** | Standard | N/A (Natif) | Cache local des traductions par langue | 0 Ko (Natif) |

> **Constat** : L'extension navigateur ne comporte **strictement aucune bibliothèque tierce**, aucun framework (zéro React, zéro Vue, zéro jQuery, zéro Tailwind injecté). Empreinte totale du dossier `extension/` : **125 034 octets (122,10 Ko)** (somme exacte des fichiers `background.js`, `content.js`, `manifest.json` et `offline_catalog.json`).

---

## 2. Backend Local (FastAPI / Python)

Toutes les dépendances sont déclarées dans [`backend/requirements.txt`](backend/requirements.txt) :

| Bibliothèque | Version | Licence | Usage | Taille approximative |
|---|---|---|---|---|
| **FastAPI** | `>=0.115.0` | BSD-3-Clause | Framework API REST asynchrone (endpoints `/health`, `/languages`, `/translate/batch`, `/feedback`) | ~1.5 Mo |
| **Uvicorn** | `>=0.30.0` | BSD-3-Clause | Serveur ASGI local haute performance | ~3.0 Mo |
| **Pydantic** | `>=2.0.0` | MIT | Typage strict et validation des requêtes/réponses | ~8.0 Mo |
| **python-dotenv** | `>=1.0.0` | BSD-3-Clause | Chargement sécurisé des variables d'environnement (`.env`) | ~100 Ko |
| **httpx** | `>=0.27.0` | BSD-3-Clause | Client HTTP de test pour `TestClient` (tests unitaires) | ~1.0 Mo |
| **CTranslate2** | `4.9.0` | MIT | Moteur d'inférence C++/Python optimisé INT8 pour modèles Transformer | 19.46 Mo |
| **SentencePiece** | `0.2.3` | Apache-2.0 | Tokeniseur / Détokeniseur sous-mot pour modèles de traduction | 1.58 Mo |

> **Constat** : Toutes les bibliothèques backend sont sous licences libres permissives (MIT, BSD-3-Clause, Apache-2.0).

---

## 2.1 Outils de Test et d'Audit d'Accessibilité (Tests Uniquement — Hors Production)

| Bibliothèque | Version | Licence | Usage | Taille exacte / approx. |
|---|---|---|---|---|
| **playwright** | `>=1.40.0` | Apache-2.0 | Automatisation des tests E2E navigateur (Microsoft Edge) | ~35 Mo |
| **axe-playwright-python** | `0.1.8` | MIT | Audit d'accessibilité WCAG automatisé sur Shadow DOM (tests uniquement) | 156,92 Ko (160 681 octets) |
| **pip-audit** | `2.10.1` | Apache-2.0 | Audit statique des vulnérabilités des dépendances Python (CVE) (tests uniquement) | 60,57 Ko (62 023 octets) |

> **Précision** : `axe-playwright-python` et `pip-audit` sont utilisés **strictement comme outils de test et d'audit automatisé**. Ils ne sont pas embarqués dans l'extension client ni requis pour le backend en production.

---

## 3. Modèles de Traduction Automatique Locale (Contenu Inédit)

| Modèle | Source / Auteur | Sous-dossier | Licence | Usage et Statut | Taille exacte |
|---|---|---|---|---|---|
| **cameroon-int8** | flagship-ai (Hugging Face) | `francais-fufulde/` seul | **CC BY-NC 4.0** | Moteur Fulfulde (flagship-ai/cameroon-int8, CC BY-NC 4.0) intégré, testé sur 20 libellés, écarté du parcours de démonstration car les sorties observées présentent des signes d'incohérence (répétitions, anglais non traduit, contenu hors domaine). Qualité non mesurée, variété du Fulfulde non vérifiée, aucune relecture native. | 80 807 193 octets (77,06 Mo) |

### Limites Observées et Décision Technique :
1. **Écartement de la démonstration nominale** : Moteur désactivé par défaut dans le backend et absent du sélecteur standard du widget (accessible uniquement via un interrupteur expérimental avec bandeau d'alerte spécifique).
2. **Hallucinations et incohérences constatées** : L'évaluation sur 20 libellés réels a mis en évidence des boucles de répétition, des termes anglais non traduits, des dérives sémantiques religieuses et des formulations hors domaine.
3. **Protection financière validée** : Le garde-fou d'intégrité (`protect.py`) a basculé en repli source sur 6 phrases contenant des valeurs financières (montants, frais, téléphones, références, dates), garantissant l'absence totale de corruption des données.

---

## 4. Modèles d'IA Utilisés (via Antigravity et claude.ai)

Conformément à la règle de transparence stricte, seuls les modèles d'IA réellement utilisés via **Antigravity** et **claude.ai** sont déclarés ci-dessous avec leurs rôles effectifs et leurs limites :

| Modèle d'IA | Environnement / Accès | Rôle Réel dans le Projet | Limites Connues et Déclarées |
|---|---|---|---|
| **Claude Sonnet 4.6 (Thinking)** | claude.ai | **Code** : Conception et développement du backend FastAPI, de l'extension Manifest V3, de l'algorithme de masquage déterministe (`backend/protect.py`), des scripts de test et de téléchargement. | Dépendance aux spécifications fournies ; requiert des tests automatisés rigoureux pour vérifier l'absence de régression. |
| **Claude Opus 4.6 (Thinking)** | claude.ai | **Audit** : Analyse contradictoire approfondie (Red Team), conception des scénarios d'attaque hostile contre l'intégrité financière, audit DOM et identification des failles de sécurité. | Analyse heuristique nécessitant une validation par exécution de tests unitaires et d'intégration réels. |
| **Gemini 3.8 Flash (High/Medium)** | Antigravity | **Brouillons de traductions** : Génération initiale des propositions en langues locales (Duálá, Ɓàsàa) en statut strict `machine_suggested` ; élaboration des périphrases explicatives du glossaire financier pour termes sans équivalent direct. | Risque d'hallucinations lexicales et de calques syntaxiques du français ; aucune validation par locuteur natif intégrée, justifiant le format bilingue non substitutif pour les données sensibles. |
| **GPT-OSS 120B (Medium)** | Antigravity | **Audit** : Exploration contradictoire de cas limites (formats de montants atypiques, tests de robustesse et recoupement lexical). | Biais potentiel sur les structures complexes ; incapacité à garantir l'intégrité financière sans le filtre algorithmique strict `protect.py`. |

### Limites Fondamentales et Mesures d'Atténuation
1. **Zéro Confiance Aveugle dans l'IA** : Aucune sortie brute d'un modèle n'est considérée comme une traduction authentique (statut obligatoire `machine_suggested`).
2. **Garde-fou Algorithmique Inviolable** : Les montants, devises, frais, dates, références et bénéficiaires sont **systématiquement masqués avant toute sollicitation d'un modèle d'IA**, empêchant formellement toute altération par hallucination du modèle.
3. **Validation Humaine Obligatoire** : Les brouillons générés sont soumis à la validation de locuteurs natifs certifiés via [`catalogue/fiche_validation.csv`](catalogue/fiche_validation.csv) avant la finale du 26-28 novembre 2026.

---

## 5. Jeux de Données et Corpus Linguistiques (Catalogues et Lexiques)

Conformément aux exigences de conformité et de traçabilité, chaque jeu de données dont des extraits figurent dans `catalogue/` (directement ou via les scripts de recoupement lexical) est déclaré ci-dessous avec sa licence (uniquement si vérifiée) :

| Jeu de Données | Source / Référentiel | Exploitation dans le Projet | Licence | Statut de Vérification |
|---|---|---|---|---|
| **Lingua Libre** | Wikimedia Commons / Lingua Libre (enregistrements audio et transcriptions Duálá par locuteurs natifs) | Vocabulaire attesté pour le recoupement lexical Duálá (`catalogue/crosscheck_rapport.csv` via `shared/data/duala/lexique_duala.json`) | **CC BY-SA 4.0** | **Licence vérifiée** (Licence officielle Wikimedia Commons / Lingua Libre) |
| **SimbaBench** | UBC-NLP / SimbaBench_dataset (Hugging Face) | Vocabulaire attesté pour le recoupement lexical Ɓàsàa (`catalogue/crosscheck_rapport.csv` via `shared/data/bassa/lexique_bassa.json`) | **CC-BY-4.0** | **Licence vérifiée** (Déclarée explicitement sur le dépôt Hugging Face) |
| **AfroLingu-MT** | UBC-NLP / AfroLingu-MT (Hugging Face) | Échantillon de phrases parallèles Bassa pour analyse lexicale exploratoire | **licence non vérifiée** | Non spécifiée (métadonnée `license: None` sur Hugging Face) |
| **cameroon-int8 (francais-fufulde)** | flagship-ai (Hugging Face) | Modèle de traduction CTranslate2 INT8 et vocabulaire SentencePiece testé sur 20 libellés (`catalogue/evaluation_fulfulde_20.csv`) | **CC BY-NC 4.0** | **Licence vérifiée** (Déclarée explicitement sur le dépôt Hugging Face) |
| **Common Voice (DS-06)** | Mozilla Foundation | Chaînes d'interface (`.ftl`) pour `dua` et `bas` consultées pour recoupement comparatif UI ([`docs/recoupement_references_ui.md`](docs/recoupement_references_ui.md)) | **MPL-2.0** | **Références consultées, non redistribuées** (données externes hors dépôt) |
| **MediaWiki Core (DS-30)** | Wikimedia Foundation | Messages d'interface du noyau (`.json`) pour `dua` et `bas` consultés pour recoupement comparatif UI ([`docs/recoupement_references_ui.md`](docs/recoupement_references_ui.md)) | **GPL-2.0+** | **Références consultées, non redistribuées** (données externes hors dépôt) |

---

## 6. Périmètre Non Mesuré

* **Taux d'erreur grammaticale intrinsèque des modèles d'IA sur le Duálá ancien vs moderne** : **Non mesuré**.
* **Consommation énergétique de l'inférence des modèles sur serveurs distants** : **Non mesuré**.
* **Latence moyenne d'un appel API en direct vers les moteurs LLM en conditions de réseau rural camerounais** : **Non mesuré** (le prototype s'exécute en local/offline ; les mesures de latence locale de `/translate/batch` sont documentées dans [`docs/mesures_performance.md`](docs/mesures_performance.md)).

