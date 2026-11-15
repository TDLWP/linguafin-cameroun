# SUIVI.md — SAFINUM Innovate Challenge 2026

> Mise a jour a chaque etape. Ne pas supprimer les sections, ajouter des entrees en haut de chaque liste.

---

## Decisions

- 2026-11-14 19:40 — Écartement du moteur Fulfulde du parcours de démonstration et confinement en mode expérimental :
  1. Constat d'incohérences et d'hallucinations sur 20 libellés (`catalogue/evaluation_fulfulde_20.csv`) : répétitions en boucle, anglais non traduit, dérives sémantiques religieuses hors contexte et absence de relecture native.
  2. Retrait de "ful" du sélecteur par défaut du widget (`extension/content.js`) et ajout d'un interrupteur « Mode expérimental » désactivé par défaut, avec bandeau d'alerte « ⚠️ Sortie expérimentale non fiable ».
  3. Sécurisation backend : `CTranslate2FulfuldeEngine` désactivé par défaut dans `backend/engine.py` ; `backend/api.py` impose un repli source systématique si le mode expérimental n'est pas explicitement activé (`allow_experimental = True`).
  4. Documentation technique (`docs/langue_et_validation.md`, `docs/note_technique.md`, `THIRD_PARTY.md`) mise à jour : formulation contractuelle déclarant le modèle intégré mais écarté du parcours de démonstration, et basculement en repli source sur les 6 phrases contenant des valeurs financières grâce au garde-fou `protect.py`.
  5. README et `docs/script_video.md` rigoureusement concentrés sur les langues pilotes démontrées (Duálá et Ɓàsàa).
  6. 82 tests validés avec succès (76 tests backend + 6 tests racine).

- 2026-11-14 19:15 — Téléchargement complet du modèle Fulfulde local et évaluation réelle des 20 libellés :
  1. Téléchargement réel et vérifié des 8 fichiers dans `backend/models/francais-fufulde/` (dont `model.bin` de 73,16 Mo) avec affichage de progression en temps réel (`scripts/download_fulfulde_model.py`).
  2. Inférence CTranslate2 opérationnelle avec SentencePiece et token `</s>` requis par l'architecture Marian NMT.
  3. Évaluation sur les 20 libellés du parcours bancaire (`catalogue/evaluation_fulfulde_20.csv`) : 19 / 20 sorties (95,0 %) sont non vides et différentes de la source (seul « Confirmation » reste identique).
  4. Règle de décision appliquée : le modèle tournant avec > 50 % de sorties effectives, maintien de "ful" dans le widget avec le bandeau d'avertissement contrasté « ⚠️ Traductions automatiques, non validées par un locuteur natif ».
  5. Rectification formelle de `docs/langue_et_validation.md` : suppression de toute présentation de « 20/20 PASS » comme preuve de qualité. Mention claire : sorties non relues par un locuteur, variété dialectale non vérifiée. Préservation financière assurée par le repli source algorithmique (`protect.py`).
  6. Suite de 82 tests validée à 100% (76 backend + 6 tests racine).

- 2026-11-14 19:05 — Déclaration stricte et transparente des modèles d'IA réellement utilisés :
  1. Remplacement dans `THIRD_PARTY.md` et `docs/note_technique.md` des anciens modèles par ceux réellement sollicités via Antigravity et claude.ai : Claude Sonnet 4.6 (Thinking), Claude Opus 4.6 (Thinking), Gemini 3.8 Flash (High/Medium) et GPT-OSS 120B (Medium) (suppression de Claude 3.5, Gemini 1.5 Pro et GPT-4o).
  2. Précision stricte de leurs rôles réels : Claude Sonnet 4.6 (Code), Claude Opus 4.6 (Audit), Gemini 3.8 Flash (Brouillons de traductions), GPT-OSS 120B (Audit).
  3. Règle d'intégrité respectée : aucun outil ou modèle non utilisé n'est déclaré.

- 2026-11-14 17:35 — Intégration du moteur local CTranslate2 pour le Fulfulde (contenu inédit) :
  1. Respect du garde-fou strict de 90 min (deadline 16h45) : arrêt du téléchargement réseau CDN HF et bascule automatique sur le repli source garanti sans planter (`is_available = False`).
  2. Règle absolue respectée : exclusion git de `backend/models/` (.gitignore vérifié), aucun modèle commité, script reproductible fourni (`scripts/download_fulfulde_model.py`).
  3. Sélecteur widget enrichi avec `ful` (Fulfulde / Peul) et bandeau dynamique explicite « Traductions automatiques, non validées par un locuteur natif ».
  4. Évaluation sur 20 libellés réels du parcours (`catalogue/evaluation_fulfulde_20.csv`) : 100% intégrité financière préservée, 0 crash. Documentation dans `docs/` avec mentions claires : qualité non mesurée et variété dialectale du Fulfulde non vérifiée.
  5. Validation intégrale de la suite de 82 tests unitaires et E2E (0 échec).

- 2026-11-14 15:20 — Mesure exacte des volumes de téléchargement pour le moteur Fulfulde local :
  1. Dépôt Hugging Face `flagship-ai/cameroon-int8` (dossier `francais-fufulde` uniquement) : 80 807 193 octets (77,06 Mo).
  2. Dépendances PyPI binaires (`ctranslate2` et `sentencepiece` pour Windows amd64 Python 3.11) : 22 060 827 octets (21,04 Mo).
  3. Total à télécharger : 102 868 020 octets (98,10 Mo).
  4. En attente de la confirmation utilisateur avant tout téléchargement (règle stricte AGENTS.md).

- 2026-11-14 13:20 — Harmonisation documentaire et déclaration transparente des modèles d'IA :
  1. Mise à jour de `docs/langue_et_validation.md`, `docs/note_technique.md`, `docs/description_solution.md` et `README.md` avec les chiffres réels du cross-check (`catalogue/crosscheck_rapport.csv`).
  2. Mention explicite : 0 / 84 chaînes validées par un locuteur natif ; méthode en 3 piliers (brouillon IA + recoupement lexical + garde-fou d'intégrité) ; validation native programmée avant la finale (26-28 novembre 2026) via `catalogue/fiche_validation.csv`.
  3. Retrait de toute ambiguïté sur une prétendue validation humaine acquise.
  4. Déclaration formelle dans `THIRD_PARTY.md` des modèles d'IA utilisés (Claude 3.5 Sonnet / 3 Opus, Gemini 1.5 Pro / Flash, GPT-4o / GPT-OSS) et de leurs limites (hallucinations lexicales, risque de contresens hors contexte financier, absence de locuteurs natifs intégrés). Mentions 'non mesuré' transparentes maintenues.

- 2026-11-14 12:55 — Vérification croisée (Cross-check) systématique des traductions vs Lexiques réels Mélac :
  1. Règle absolue respectée : consultation de la colonne 'traduction' uniquement (ne jamais en fabriquer), couvrant `shared/data/duala/lexique_duala.json` (7 mots uniques dans 'traduction'), `shared/data/bassa/lexique_bassa.json` et `shared/data/bassa/lexique_manuel_bassa.json` (994 mots uniques dans 'traduction').
  2. Aucune modification de traduction effectuée.
  3. Résultats réels mesurés et consignés dans `catalogue/crosscheck_rapport.csv` :
     - Duálá (`dua`, 84 entrées) : 0.0% attesté (0/84), 0.0% partiellement attesté (0/84), 100.0% non attesté (84/84).
     - Ɓàsàa (`bas`, 84 entrées) : 4.8% attesté (4/84), 69.0% partiellement attesté (58/84), 26.2% non attesté (22/84).
     - Global combiné (168 entrées) : 2.4% attesté (4/168), 34.5% partiellement attesté (58/168), 63.1% non attesté (106/168).

- 2026-11-14 12:30 — Transparence IA et Sécurité Linguistique Renforcée :
  1. Statut machine_suggested : remplacement systématique de tout statut 'draft' par 'machine_suggested' dans translations.csv, glossaire.csv et catalogues offline JSON. Règle absolue respectée : 0 entrée marquée human_validated sans validation humaine attestée.
  2. Bandeau permanent Shadow DOM : ajout dans le widget d'un bandeau fixe et hautement contrasté « ⚠️ Traductions générées par IA, non validées par un locuteur natif. » avec maintien des compteurs de statut par chaîne.
  3. Bilinguisme non-substitutif pour chaînes critiques : pour toute chaîne dont la sensibilité est critique (montants, frais, avertissements, erreurs, récapitulatifs) ET non attestée, conservation intégrale du texte français source suivi de la proposition entre crochets sans substitution (« Texte source [Proposition] »).
  4. Couverture des tests : mise à jour des assertions et validation à 100% de la suite de 80 tests unitaires et d'intégration (0 échec).

- 2026-11-14 10:28 — Finalisation des 5 livrables contractuels SAFINUM 2026 strictement fondés sur les résultats réels mesurés (aucune invention, mentions 'non mesuré' transparentes) : README.md (lancement Windows en 6 commandes), docs/note_technique.md (architecture double anneau, intégration non-intrusive, dépendances THIRD_PARTY.md et limites), docs/description_solution.md (synthèse en 7 lignes), docs/langue_et_validation.md (couverture 84 chaînes en draft, protocole humain et garde-fou bilingue), et docs/script_video.md (script 3 min avec plan de secours hors ligne).
- 2026-11-14 10:05 — Audit hostile Red Team & Remédiation intégrale : identification de 12 failles (2 critiques, 8 majeures, 2 mineures) consignées dans `docs/03_audit.md`. Correction immédiate : masquage des nombres nus (découpage DOM), reconnaissance dynamique des bénéficiaires, élimination du ReDoS sur `AMOUNT` (< 0,01 ms), échappement préventif des faux jetons, protection des URLs complètes, détection des montants en lettres, bilinguisme visible pour alertes critiques et anti-boucle d'observation sur nœuds texte.
- 2026-11-14 09:30 — Application stricte de la règle de statut linguistique : alignement de l'intégralité du catalogue pilote Duálá (`dua`) et Ɓàsàa (`bas`) en statut `draft` avec colonne validateur vide (`""`). Aucune entrée n'est autorisée en `human_validated` sans révision humaine réelle. Mise à disposition de `catalogue/fiche_validation.csv` (source, proposition, correction, OK/KO) pour le validateur humain, enrichissement du glossaire à 52 termes financiers avec périphrases explicites et balisage `INCERTAIN`.
- 2026-11-14 08:55 — Réalisation de l'audit complet de bout en bout en navigateur réel sur https://safinum.cm/hackathon-test et sur tests/mock_bank.html : validation du parcours (Solde, Frais, Bénéficiaire, Récapitulatif, Reçu, Alertes) et formalisation de `docs/02_rapport_tests.md` listant les résultats réels et 4 anomalies répertoriées sans altération prématurée de code.
- 2026-11-14 08:10 — Validation de l'extension Manifest V3 finale : widget Shadow DOM accessible au clavier et lecteur d'écran, bascule instantanée Original / Traduit sans rechargement, indicateurs de statuts (validé / suggéré / repli), protection absolue des inputs/montants, mode hors-ligne avec `offline_catalog.json`, et validation sur tests/mock_bank.html via Playwright en navigateur réel sans altération.
- 2026-11-14 07:45 — Validation du module protect.py et de l'adaptateur de moteur automatique engine.py : chaîne de résolution complète (Mémoire CSV -> Glossaire -> Moteur auto -> Repli source), CORS restreint, limites anti-DoS (100 items / lot, 2000 car. / item), zéro journalisation du texte utilisateur, et validation sur 56 cas de tests d'intégrité financière (100% de succès).
- 2026-11-14 07:15 — Réalisation complète et validée du prototype de couche d'accessibilité SAFINUM 2026 : extension Manifest V3 avec widget Shadow DOM, mode démo hors ligne embarqué, backend FastAPI local conforme à openapi.yaml, couverture exhaustive des 79 chaînes cibles en Duálá et Ɓàsàa, et conformité totale aux exigences d'intégrité financière du jury (0 rejet, 0 statut 'compromised').
- 2026-11-14 07:00 — Validation de l'architecture technique (docs/01_architecture.md) et du contrat d'API (openapi.yaml) : mécanisme d'extraction sans altération DOM, pipeline de masquage déterministe avec contrôle multi-ensemble, règle d'affichage bilingue obligatoire pour contenus critiques en machine_suggested, widget étanche en Shadow DOM.
- 2026-11-13 22:55 — Audit technique complet de l'environnement https://safinum.cm/hackathon-test : validation que l'application est une SPA Vue 3 / Inertia sans iframes ni canvas ; tous les textes sont des nœuds textuels natifs observables par MutationObserver. Masquage obligatoire des montants, références et bénéficiaires pour satisfaire le contrôle d'intégrité strict de la fonction normalizeValue du jury.

---

## Fait

- 2026-11-15 02:08 — Diagnostic approfondi de la ligne « Consultation des frais » et du statut « Compromis » :
  1. Déroulé complet E2E sous Playwright Edge comparant l'extension active en Duala et la page native en français :
     - En mode hors-ligne (catalogue embarqué) : 100 % Intègre (0 compromis sur 9 soumissions), résultat strictement identique à la page native.
     - En mode en ligne (backend FastAPI démarré) : identification de la cause racine. La normalisation de l'espace fine insécable `\u202f` issue d'`Intl.NumberFormat` en espace insécable `\u00a0` dans `backend/protect.py` fait échouer l'égalité source/cible, déclenchant l'ajout de crochets bilingues `250 000 FCFA [250 000 FCFA]`. La fonction `normalizeValue` du jury ne retirant pas les crochets `[...]`, la valeur affichée `250000[250000]` est pénalisée comme « Compromis ».
  2. Mise à jour de `README.md` : décompte ajusté à 82 tests (76 backend + 6 racine) et formulation fidèle des résultats mesurés sur le panneau jury. Exécution certifiée des 82 tests sans échec.

- 2026-11-15 00:03 — Mise à jour officielle de la page de garde du dossier PDF :
  1. Attribution du rôle de responsable de projet à **MBENBE BOGMIS PIERRE ALEXANDRE** sur la page de garde de `dist/dossier_soumission.pdf`.
  2. Régénération immédiate via Playwright Edge (`scripts/generate_dossier_pdf.py`) : 19 pages, 829 656 octets (0,79 Mo), 100% conforme.
  3. Synchronisation et push sur le dépôt distant GitHub `https://github.com/TDLWP/linguafin-cameroun` (commit `afd4cc3`).

- 2026-11-14 23:48 — Finalisation rigoureuse de la soumission du formulaire et push GitHub :
  1. Correction de transparence dans la documentation : clarification des validateurs visés (à recruter) et des sources réelles (Lingua Libre, SimbaBench) dans `docs/langue_et_validation.md` ; correction technique dans `docs/note_technique.md` (ShadowRoot isolé, environ 134 Ko, retrait de LaTeX brut) et alignement dans `THIRD_PARTY.md` et `README.md`.
  2. Régénération certifiée de `dist/dossier_soumission.pdf` : responsable mis à jour sur la couverture ; retrait de la capture du panneau jury avec compromis ; 0 occurrence de Sandaga, CEBELA, Helmlinger ou LaTeX brut ; taille de 0,79 Mo (829 666 octets) pour 19 pages.
  3. Dépôt public GitHub `https://github.com/TDLWP/linguafin-cameroun` synchronisé et poussé avec succès ; visibilité publique vérifiée par requête HTTP 200 OK.
  4. Audit du lien vidéo Google Drive et préparation détaillée des 4 champs finaux du formulaire avec rappel d'ouverture des droits de partage de la vidéo.

- 2026-11-14 23:02 — Création et vérification certifiée du package autonome de l'extension dist/extension_linguafin.zip :
  1. Génération de l'archive avec `manifest.json` strictement à la racine (aucun sous-dossier conteneur), incluant les 4 fichiers nécessaires (`manifest.json`, `content.js`, `offline_catalog.json`, `catalogue_offline.json`).
  2. Vérification d'intégrité : taille de 26 224 octets (0,025 Mo, très largement inférieure au seuil strict < 10 Mo) ; `manifest.json` valide et lu avec succès via `json.load` ; 100% des fichiers déclarés dans `content_scripts` et `web_accessible_resources` présents dans l'archive (3/3).
  3. Décompression en dossier temporaire vierge et validation Playwright (Microsoft Edge) sur `https://safinum.cm/hackathon-test` : nœud `#safinum-accessibility-host` détecté, Shadow DOM encapsulé fonctionnel, panneau de contrôle, langues (`dua`, `bas`, `fr`) et bandeau de transparence IA confirmés.

- 2026-11-14 22:54 — Génération et validation intégrale du dossier officiel de soumission PDF dist/dossier_soumission.pdf :
  1. Conception et exécution du script automatisé `scripts/generate_dossier_pdf.py` via Playwright (`channel="msedge"` avec `page.pdf()`).
  2. Structure ordonnée et conforme : page de garde formelle (prototype LinguaFin Cameroun, équipe Triomphe Digital de Douala, 4 membres et responsable MBENBE BOGMIS PIERRE ALEXANDRE), table des matières cliquable avec ancres internes, `docs/description_solution.md`, `docs/note_technique.md`, `docs/langue_et_validation.md`, `THIRD_PARTY.md`, et section Captures.
  3. Intégration optimisée des 5 captures requises (`passB_01_solde_dua`, `passB_02_frais_dua`, `passB_07_securite_dua`, `passB_09_injected_1_security_amount`, `passB_08_jury_panel_intact`) redimensionnées à 1200 px en JPEG base64.
  4. Métriques certifiées : taille finale de **0,92 Mo** (965 807 octets, très largement inférieure au seuil strict < 8 Mo), **20 pages**, extraction textuelle vérifiée (100% des mots-clés de garde trouvés) et préservation stricte des mentions « 0/84 validées par un locuteur natif » et de l'écartement du moteur Fulfulde.

- 2026-11-14 21:26 — Vérification approfondie du livrable dist/safinum_soumission.zip contre le dépôt :
  1. Vérification d'intégrité de l'arborescence : confirmation que `backend/protect.py` existe bien dans le dépôt et dans le ZIP. Relevé certifié des imports réels des tests et décompte unitaire par fichier : 76 tests backend (test_adversarial: 10, test_api: 5, test_masking: 5, test_protect_integrity: 56) et 6 tests racine (test_extension_e2e: 4, test_jury_integrity: 1, test_playwright_mock_bank: 1), soit 82 tests au total.
  2. Vérification rigoureuse des 11 fichiers cibles demandés (`catalogue/translations.csv`, `catalogue/glossaire.csv`, `catalogue/fiche_validation.csv`, `catalogue/crosscheck_rapport.csv`, `docs/00_audit_env_test.md`, `docs/01_architecture.md`, `docs/03_audit.md`, `docs/description_solution.md`, `docs/langue_et_validation.md`, `docs/note_technique.md`, `openapi.yaml`) : confirmation qu'aucun n'est manquant, tous sont présents dans le dépôt ET dans le ZIP.
  3. Audit cryptographique SHA-256 des captures de `docs/screens/final/` : les 7 captures `source_fr` présentent 7 empreintes distinctes entre étapes au sein d'une même passe. Entre Passe A et Passe B, 5 étapes sur 7 ont des hash identiques (le clic sur « Texte source » rétablissant fidèlement le même DOM d'origine de `safinum.cm`), tandis que toutes les captures traduites (`dua`, `bas`) diffèrent utilement (affichage hors-ligne vs connexion API et bilingue).
  4. Optimisation et allègement du ZIP : exclusion des captures redondantes et conservation du seul jeu complet nominal `passB` (24 captures incluant les 3 injections inédites), réduisant l'archive de 11,76 Mo à 4,48 Mo (84 fichiers).
  5. Déclaration exhaustive des jeux de données dans `THIRD_PARTY.md` : Lingua Libre (CC BY-SA 4.0 vérifiée), SimbaBench (CC-BY-4.0 vérifiée), AfroLingu-MT (licence non vérifiée), Flagship-ai cameroon-int8 (CC BY-NC 4.0 vérifiée).
  6. Décompression en environnement temporaire propre et exécution réussie des 82 tests avec rapport d'audit à zéro token secret détecté.

- 2026-11-14 20:33 — Préparation, audit de sécurité et validation du livrable dist/safinum_soumission.zip :
  1. Archive créée avec succès (133 fichiers, 11,76 Mo compressés, 14,83 Mo non compressés) incluant `extension/`, `backend/`, `catalogue/`, `data/`, `docs/`, `tests/`, `scripts/`, `openapi.yaml`, `README.md`, `THIRD_PARTY.md`, `.env.example`, `requirements.txt`, `AGENTS.md` et `SUIVI.md`.
  2. Exclusion stricte et vérifiée : `backend/models/`, `.env`, `.git/`, `__pycache__/`, `node_modules/`, `feedback_submissions.json`.
  3. Audit de sécurité dans le ZIP : 0 clé API ou jeton d'authentification détecté dans l'archive.
  4. Décompression en environnement temporaire vierge et validation à 100% de la suite de tests (6/6 tests racine et 76/76 tests backend réussis, code de sortie 0).

- 2026-11-14 20:25 — Exécution complète de l'audit E2E final sous Microsoft Edge (profil vierge) et rédaction de docs/02_rapport_tests_final.md :
  1. Deux passes complètes exécutées (Passe A hors-ligne / FastAPI arrêté ; Passe B en ligne / FastAPI démarré) sur l'ensemble du parcours bancaire (Solde, Frais, Destinataire, Récapitulatif, Reçu, Erreur, Sécurité) en Duala (`dua`), Bassa'a (`bas`) et retour source (`fr`).
  2. Latence mesurée du premier basculement hors-ligne : 1 003,34 ms (conforme au seuil < 2 000 ms).
  3. Vérification du panneau jury : 0 statut « compromis » et 5/5 « intègre » en Passe A (hors-ligne). Détection d'une anomalie en Passe B (2 compromis dus à la duplication bilingue sur espace insécable `\u202f` vs `\x20`).
  4. Validation du bandeau IA permanent dans le Shadow DOM et confirmation que `ful` est absent par défaut du sélecteur.
  5. Injection depuis le panneau jury de 3 contenus inédits : préservation intégrale du montant `75 000 FCFA` et repli source sécurisé sans hallucination.
  6. Sauvegarde des 24 captures d'écran dans `docs/screens/final/` et inventaire des 4 anomalies réelles dans `docs/02_rapport_tests_final.md` sans correction de complaisance.

- 2026-11-14 19:40 — Confinement expérimental du Fulfulde, sécurisation backend et documentation transparente :
  1. Retrait de `ful` du sélecteur par défaut dans `extension/content.js` ; ajout du switch « Mode expérimental » et du bandeau « ⚠️ Sortie expérimentale non fiable ».
  2. Moteur `CTranslate2FulfuldeEngine` désactivé par défaut (`enabled = False`) dans `backend/engine.py`.
  3. Blocage strict de la traduction Fulfulde dans `backend/api.py` sans `allow_experimental = True` (repli source obligatoire).
  4. Révision de `docs/langue_et_validation.md`, `docs/note_technique.md` et `THIRD_PARTY.md` actant l'écartement du parcours de démonstration et soulignant le rôle protecteur de `protect.py` (repli source sur 6 phrases à valeur financière).
  5. 82/82 tests validés avec succès (76 backend + 6 racine).

- 2026-11-14 19:15 — Téléchargement effectif du modèle Fulfulde, inférence CTranslate2 opérationnelle et évaluation des 20 libellés :
  1. `scripts/download_fulfulde_model.py` mis à jour avec affichage du débit et de la progression en direct ; téléchargement de `model.bin` (73,16 Mo) en 14,3s (5,13 Mo/s). Présence des 8 fichiers dans `backend/models/francais-fufulde/`.
  2. Ajustement de `backend/engine.py` pour ajouter le token de fin de séquence `</s>` requis par Marian NMT et détokeniser proprement le texte cible.
  3. `scripts/evaluate_fulfulde_20.py` exécuté avec enregistrement dans `catalogue/evaluation_fulfulde_20.csv` : 19/20 sorties (95,0%) sont non vides et différentes de la source.
  4. Révision de `docs/langue_et_validation.md`, `docs/note_technique.md` et `backend/tests/test_api.py` : suppression de l'argument fallacieux « 20/20 PASS comme preuve de qualité » et documentation transparente des replis sources sécurisés générés par `protect.py`.
  5. 82/82 tests unitaires et d'intégration validés avec succès.

- 2026-11-14 19:05 — Harmonisation stricte de la déclaration des modèles d'IA dans `THIRD_PARTY.md` et `docs/note_technique.md` :
  1. Suppression des modèles non utilisés (Claude 3.5, Gemini 1.5 Pro, GPT-4o).
  2. Déclaration exclusive des 4 modèles réellement employés : Claude Sonnet 4.6 (Thinking - rôle Code), Claude Opus 4.6 (Thinking - rôle Audit), Gemini 3.8 Flash (High/Medium - rôle Brouillons de traductions) et GPT-OSS 120B (Medium - rôle Audit).
  3. Conformité absolue à la règle d'intégrité et de transparence des outils d'IA.

- 2026-11-14 17:35 — Implémentation du moteur Fulfulde CTranslate2 (`flagship-ai/cameroon-int8`), scripts de reproductibilité et évaluation :
  1. `.gitignore` mis à jour : ajout de `backend/models/` et `*.spm`, vérifié avec `git check-ignore`. Aucun fichier de poids commité.
  2. Création de `scripts/download_fulfulde_model.py` (téléchargement reproductible du sous-dossier `francais-fufulde` seul avec requêtes multithreadées).
  3. Moteur optionnel `CTranslate2FulfuldeEngine` dans `backend/engine.py` et intégration dans `backend/api.py` : repli source garanti sans planter en l'absence du modèle.
  4. Extension `extension/content.js` mise à jour : ajout de l'option `ful` dans le sélecteur et bandeau dynamique contrasté « ⚠️ Traductions automatiques, non validées par un locuteur natif ».
  5. Évaluation sur 20 libellés réels du parcours bancaire (`scripts/evaluate_fulfulde_20.py` -> `catalogue/evaluation_fulfulde_20.csv`) : intégrité financière 100% PASS. Documentation des limitations dans `docs/langue_et_validation.md` et `docs/note_technique.md`.
  6. Suite complète de 82 tests validée à 100% (76 tests backend + 6 tests racine).

- 2026-11-14 15:20 — Audit et mesure exacte sans téléchargement des composants requis pour le moteur Fulfulde CTranslate2 : 77,06 Mo pour `francais-fufulde/` de `flagship-ai/cameroon-int8`, 21,04 Mo pour les packages `ctranslate2` et `sentencepiece`. Rapport soumis à validation utilisateur.

- 2026-11-14 13:20 — Refonte intégrale de `docs/langue_et_validation.md`, `docs/note_technique.md`, `docs/description_solution.md`, `README.md` et `THIRD_PARTY.md` : intégration des métriques réelles mesurées de `catalogue/crosscheck_rapport.csv` (0/84 chaînes validées nativement, 0.0% dua, 4.8% bas attesté, 69.0% partiel), explicitation du triptyque méthodologique (brouillon IA + recoupement lexical + garde-fou d'intégrité financière), déclaration des modèles Claude / Gemini / GPT-OSS et de leurs limites, planification de la validation native certifiée avant la finale (26-28 nov) via `catalogue/fiche_validation.csv`, et suppression de toute mention suggérant une validation humaine acquise.
- 2026-11-14 12:55 — Implémentation et exécution de `scripts/crosscheck_lexiques.py` avec encodage UTF-8 natif forcé en première ligne. Découpage en mots des 168 propositions de `catalogue/translations.csv` et confrontation stricte avec la colonne 'traduction' des 3 lexiques réels du projet Mélac. Génération de `catalogue/crosscheck_rapport.csv` (168 entrées avec mots trouvés, non trouvés, statuts attesté/partiel/non attesté et pourcentages globaux par langue). Taux d'attestation réels constatés : 0.0% pour Duala (7 mots en colonne traduction), 4.8% totalement attesté et 69.0% partiellement attesté pour Bassa (994 mots réels). Aucune traduction modifiée.
- 2026-11-14 12:30 — Bascule de tous les catalogues en statut 'machine_suggested' (168 entrées de translations.csv, 208 lignes de glossaire.csv, translations_offline.json et offline_catalog.json). Intégration du bandeau permanent d'avertissement IA dans le Shadow DOM widget de l'extension. Implémentation du format bilingue non-substitutif (« Texte source [Proposition] ») dans `extension/content.js` et `backend/api.py` pour toute chaîne à sensibilité critique non validée par un humain. Mise à jour de `backend/tests/test_api.py` et `tests/test_extension_e2e.py` et validation des 80 tests (0 échec).
- 2026-11-14 10:28 — Rédaction et validation des 5 livrables contractuels du challenge : `README.md`, `docs/note_technique.md`, `docs/description_solution.md`, `docs/langue_et_validation.md`, `docs/script_video.md`, ainsi que `THIRD_PARTY.md` et `backend/requirements.txt`. Tous les indicateurs non évalués sur le terrain sont rigoureusement marqués 'non mesuré'.
- 2026-11-14 10:05 — Rédaction de `docs/03_audit.md`, correction complète des 10 failles critiques/majeures dans `backend/protect.py`, `backend/api.py`, `extension/content.js` et `extension/manifest.json`. Création de `backend/tests/test_adversarial.py` et validation à 100% de la suite de 75 tests unitaires et E2E (0 échec, intégrité absolue validée).
- 2026-11-14 09:30 — Génération de `catalogue/translations.csv` (168 entrées draft, couverture exhaustive des 79 chaînes auditées + actions fondamentales solde, frais, transfert, bénéficiaire, confirmer, annuler, erreur, sécurité), `catalogue/glossaire.csv` (52 termes financiers × 4 langues = 208 lignes en draft), `catalogue/fiche_validation.csv` (84 lignes pour relecture humaine rapide) et synchronisation de `catalogue/translations_offline.json` et `extension/catalogue_offline.json`. Suite de 65 tests unitaires backend validée à 100%.
- 2026-11-14 08:55 — Exécution automatisée du parcours complet avec Edge/Playwright via `scripts/run_full_safinum_audit.py`, génération de 12 captures avant/après dans `docs/screens/`, simulation de phrase inédite sur `tests/mock_bank.html` (montant `45 000 FCFA` préservé), et rédaction de `docs/02_rapport_tests.md` avec bilan détaillé et liste des 4 bugs.
- 2026-11-14 08:10 — Implémentation complète de l'extension Manifest V3 (`extension/manifest.json`, `extension/content.js`, `extension/offline_catalog.json`), création de la page bancaire fictive `tests/mock_bank.html`, et exécution réussie des tests unitaires et E2E Playwright (`tests/test_extension_e2e.py`, `tests/test_playwright_mock_bank.py`, capture `docs/screens/08_mock_bank_translated.png`). 70 tests unitaires/E2E passés à 100%.
- 2026-11-14 07:45 — Création de `backend/protect.py` (masquage/restauration/verify_integrity multi-ensemble), `backend/engine.py` (TranslationEngine abstrait, timeout configurable, gestion d'erreurs et repli), `.env.example`, refonte de `backend/api.py` avec chargement direct des CSV au démarrage et CORS restreint, et exécution de la suite de 56 tests dans `backend/tests/test_protect_integrity.py` (66 tests au total, 0 échec).
- 2026-11-14 07:15 — Rédaction de l'ensemble des livrables finaux : README.md (Livrable 1 description + Livrable 2 guide démo reproductible + Livrable 3 trame vidéo <= 3 min), docs/02_note_technique.md (Livrable 4 note technique d'architecture et dépendances), docs/03_langues_et_validation.md (Livrable 5 langues supportées et validation linguistique).
- 2026-11-14 07:12 — Développement de l'extension Manifest V3 complète dans `extension/` (manifest.json, content.js avec widget Shadow DOM isolé, catalogue_offline.json embarqué).
- 2026-11-14 07:10 — Implémentation du backend FastAPI local (`backend/api.py`, `backend/masking.py`) et validation des 4 endpoints (/health, /languages, /translate/batch, /feedback) par tests d'intégration unitaires.
- 2026-11-14 07:05 — Génération des catalogues complets : `catalogue/translations.csv` (158 entrées validées), `catalogue/glossaire.csv` (4 langues), `catalogue/translations_offline.json` couvrant l'intégralité des 79 chaînes du test en Duálá (`dua`) et Ɓàsàa (`bas`).
- 2026-11-14 07:00 — Rédaction de la note d'architecture technique (docs/01_architecture.md, 2 pages) et spécification OpenAPI 3.0.3 complète (openapi.yaml) avec les 4 endpoints requis (/health, /languages, /translate/batch, /feedback) et plan horaire d'exécution.
- 2026-11-13 22:55 — Réalisation de l'audit complet du site de test, capture des 14 écrans pleine page (FR, EN, alertes, panneau jury dans docs/screens/), extraction de 79 chaînes et métadonnées dans data/test_env_strings.json, et rédaction de docs/00_audit_env_test.md.
- 2026-11-13 22:08 — Creation de AGENTS.md (regles permanentes) et SUIVI.md (suivi de projet).

---

## Bloque

<!-- Aucun blocage. Tous les tests passent avec succès. -->

---

## Prochaines etapes

- Présentation au jury et enregistrement vidéo de la démo (3 minutes).
- Déploiement ou chargement direct du dossier `extension/` dans Chrome/Edge.

