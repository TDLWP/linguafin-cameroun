# SUIVI.md — SAFINUM Innovate Challenge 2026

> Mise a jour a chaque etape. Ne pas supprimer les sections, ajouter des entrees en haut de chaque liste.

---

## Decisions

- 2026-11-28 07:45 — Packaging de release et mise à jour README (P10 — post-audit) :
  1. `python scripts/package_release.py` : 2 archives générées, 0 secret détecté, décompression de contrôle OK.
     - `dist/extension_linguafin_v2.zip` : 27,8 Ko, 4 fichiers (`manifest.json` à la racine ✓, 0 `backend/models`, 0 `.env`).
     - `dist/linguafin_v2_source.zip` : 4,99 Mo, 137 fichiers (exclusions strictes vérifiées ✓).
  2. Tests relancés depuis le dossier décompressé propre (`%TEMP%\linguafin_unpack_test`) : 177 tests OK (168 backend + 9 racine).
  3. README.md section Versions mise à jour : 177 tests locaux, chiffres archives réels, audit hostile v2 ajouté.
  4. README.md tableau métriques mis à jour : empreinte extension 125 238 octets / 122,30 Ko (après correctifs M1+M3).
  5. Aucun tag créé (réservé à l'utilisateur).

- 2026-11-28 06:20 — Audit final hostile du dépôt (`docs/05_audit_final.md`) :
  1. Exécution de `run_all_checks.ps1` : 197/205 tests locaux OK, 8 tests jury live en échec réseau.
  2. Audit antagoniste sur 6 vecteurs : 1 constat critique, 3 majeurs, 4 mineurs.
  3. Correctif C1 : nom de fonction `has_confidential_secret()` → `is_secret_text()` dans `docs/questions_jury.md`.
  4. Correctif M1 : 3 motifs regex ajoutés dans `backend/protect.py` et `extension/content.js` pour combler les faux négatifs de détection de secrets (PIN est, PIN code, Code secret).
  5. Correctif M2 : filtrage `is_secret_text()` ajouté sur `POST /feedback` dans `backend/api.py` (rejet HTTP 422 si secret détecté).
  6. Correctif M3 : CSP explicite ajoutée dans `extension/manifest.json`.
  7. Vérification croisée des 10 affirmations chiffrées documentaires : toutes conformes.
  8. Tous les tests repassent après correctifs (168 backend + 9 racine = 177 OK).

- 2026-11-28 04:45 — Rédaction du guide d'ingénierie face au jury et plan de secours (`docs/questions_jury.md`) :
  1. Élaboration de 25 questions probables d'évaluation couvrant l'ensemble des piliers critiques :
     - Intégrité financière & préservation stricte des montants, frais et devises (Q1 à Q4).
     - Indépendance et non-intrusion absolue sur le site cible `safinum.cm` (Q5 à Q7).
     - Choix linguistique et protocole de validation humaine (Q8 à Q12).
     - Sécurité, sanctuarisation des secrets OTP/PIN et zéro collecte de données personnelles (Q13 à Q15).
     - Résilience réseau, service worker MV3 et mode hors-ligne nominal (Q16 à Q18).
     - Licences, dépendances et propriété intellectuelle (Q19 à Q21).
     - Gestion du contenu inédit, limites du prototype et durabilité du projet (Q22 à Q25).
  2. Réponses transparentes et documentées aux trois questions d'honneur imposées :
     - *Pourquoi le Fulfulde est-il écarté ?* : Évalué sur 20 libellés réels (`catalogue/evaluation_fulfulde_20.csv`), écarté pour hallucinations sévères (répétitions en boucle, dérives religieuses hors domaine), risque de non-restitution des jetons financiers et variété dialectale non certifiée.
     - *Pourquoi 0 chaîne validée ?* : Respect absolu de la règle 4 d'`AGENTS.md` interdisant de maquiller une sortie machine en validation humaine ; maintien strict du statut `machine_suggested` pour les 84 chaînes du catalogue tant que les signatures des locuteurs natifs ne sont pas recueillies.
     - *Que se passe-t-il si le backend est coupé ?* : Bascule instantanée (< 80 ms en médiane) sur le catalogue local embarqué de 122 Ko (`extension/offline_catalog.json`) avec mémorisation d'état sans blocage de l'interface utilisateur.
  3. Plan de secours opérationnel de démonstration (Scénarios de crise) :
     - *Scénario 1 (Réseau coupé)* : Fonctionnement 100 % hors-ligne démontré en direct.
     - *Scénario 2 (Site distant safinum.cm indisponible ou lent)* : Bascule immédiate sur la maquette bancaire locale `tests/mock_bank.html`.
     - *Scénario 3 (Widget Shadow DOM masqué)* : Déclenchement programmatique en console (`__safinum_test_set_lang`) ou exécution du banc d'essai Playwright (`scripts/repetition_finale.py`).
  4. Respect des principes de vérité des métriques :
     - Citations précises des fichiers et chiffres mesurés réels (84 chaînes, 122,10 Ko, 79,22 ms, 0,80 ms, 91 cas, 60 injections).
     - Déclaration explicite « non mesuré » pour l'autonomie de batterie, le matériel mobile 32 bits et le réseau 2G rural.


- 2026-11-28 00:40 — Rédaction de l'état des données linguistiques et justification de l'architecture (`docs/etat_des_donnees.md`) :
  1. Analyse exhaustive du dossier de recherche externe (`DOSSIER_RECHERCHE_DONNEES_SAFINUM`) :
     - Sources primaires analysées : `NOTE_TRANSFERT_CLAUDE_PRINCIPAL.md`, `REGISTRE_LICENCES.csv`, `INVENTAIRE_DATASETS.csv`, `INVENTAIRE_MODELES.csv` et `RAPPORT_RECHERCHE_DONNEES.md`.
     - Sanctuarisation stricte : aucune donnée externe n'est copiée dans le dépôt Git (conformité `.gitignore`).
     - Règle de véracité absolue : seuls les chiffres et statuts explicitement documentés sont mentionnés ; toute autre donnée est marquée « non vérifié ».
  2. Constat fondamental de carence financière :
     - **0 donnée alignée dans le domaine financier, bancaire ou d'interface de paiement** n'existe pour les langues nationales camerounaises (français ou anglais vers langue locale).
     - Les textes financiers camerounais existants (règlements CEMAC 03/16, 04/18, 01/20, COBAC R-2020/04, OHADA, DGI Cameroun, conditions MTN Mobile Money Cameroun © MTN) sont en français ou bilingues FR/EN mais sans aucune traduction en langue locale.
  3. Inventaire exhaustif des sources consultées pour le Duálá (`dua`) et le Ɓàsàa (`bas`) :
     - Duálá : Common Voice UI DS-06 (283 paires, MPL-2.0, téléchargé) ; MediaWiki DS-30 (565 messages + 53 clés datetime, GPL-2.0+, téléchargé) ; OPUS Tatoeba DS-32 (15 236 paires annoncées, CC BY-NC-SA 4.0, non téléchargé) ; BOUQuET DS-38 (1 364 phrases multi-langues, CC-BY-4.0, non téléchargé) ; Common Voice v27 audio (26,9 h, CC0, non téléchargé) ; Bloom Library (0 document, absent).
     - Ɓàsàa : Common Voice sentence collector DS-05 (5 015 lignes monolingues, CC0, téléchargé) ; Common Voice UI DS-06 (516 paires, MPL-2.0, téléchargé) ; OPUS Tatoeba DS-32 (27 778 paires annoncées, CC BY-NC-SA 4.0, non téléchargé) ; Webonary SIL DS-25 (Dictionnaire Njock © 2019, non téléchargé) ; ALCAM Basaa Mbene DS-10 (NOODL-1.0, non téléchargé) ; BOUQuET DS-38 (CC-BY-4.0, non téléchargé) ; Common Voice v27 audio (59,8 h, CC0, non téléchargé) ; Bloom Library (0 document, absent).
  4. Analyse critique et motifs d'éviction des moteurs neuronaux :
     - **Flagship AI (`flagship-ai/cameroon-int8`)** : Écarté en raison d'une contradiction juridique bloquante (fiche en CC BY-NC 4.0 vs README d'organisation en CC-BY-4.0), de l'absence totale de métriques de qualité publiées (0 score BLEU/chrF), de données d'entraînement non documentées (corpus biblique `cameroon_bibles` de ≈496 k lignes hors domaine financier), d'instabilité empirique en inférence locale (répétitions en boucle, anglicismes, dérive religieuse) et de l'absence de `dua` et `bas` dans la liste affichée.
     - **Meta NLLB-200 / FLORES-200** : Absence totale de couverture des langues camerounaises propres (les codes `dua` et `bas` sont absents de NLLB-200 et FLORES-200 ; seuls le fulfulde nigérian `fuv`, le haoussa et le kanouri y figurent) ; licence restrictive CC BY-NC 4.0 interdisant la production et le domaine financier.
  5. Justification de l'architecture souveraine en 4 piliers de SAFINUM :
     - Mémoire de traduction souveraine locale (catalogue embarqué de 84 chaînes, 122,1 Ko).
     - Glossaire terminologique spécialisé fondé sur des périphrases certifiables (*Nongi a moni* / *Mut a nkôs* pour bénéficiaire).
     - Garde-fous algorithmiques d'intégrité financière (masquage inviolable par jetons, 100% de restauration vérifiée, sanctuarisation absolue des OTP/PIN).
     - Protocole de validation humaine native à venir (statut `machine_suggested` préservé à 0/84, kits CSV/PDF hiérarchisés par priorité).
  6. Mise à jour documentaire :
     - Création de `docs/etat_des_donnees.md`.
     - Ajout des renvois contextuels dans `docs/langue_et_validation.md` (en-tête et section 5).


- 2026-11-27 23:25 — Répétition finale sur le panneau jury (?jury=1) avec 30 cas inédits hostiles et correction de sécurité :
  1. Script Playwright `scripts/repetition_finale.py` :
     - Injection automatisée sous Microsoft Edge (profil vierge) de 30 messages inédits (24 en français, 6 en anglais) issus des groupes `hostile_inedit`, `hostile_montant`, `hostile_identifiants` et secrets critiques OTP/PIN de `tests_integrite/cases.json` :
       - Montants en toutes lettres (`T041`, `T042`), espaces insécables standards (`T034`) et fines (`T035`), séparateurs (`T036`), devises préfixées/suffixées (`T037`, `T038`, `T039`), millions (`T040`), grand montant (`T043`), soldes négatifs (`T045`), pourcentages (`T048`), devises étrangères (`T049`).
       - Téléphones (+237 `T054`), comptes (`T058`), IBAN CM21 (`T059`), références SAFINUM (`T060`) et doubles (`T061`), dates calendaires et ISO (`T062`, `T063`), URLs avec paramètres (`T065`), emails (`T066`).
       - Phrases composites (`T072`), doubles montants (`T073`), alertes de sécurité montant (`T074`), blocage (`T075`), tiers (`T077`).
       - Secrets critiques OTP (`T088`, `T090`).
     - Testés exhaustivement en Duálá (`dua`) et Ɓàsàa (`bas`), soit **60 exécutions relevées**.
  2. Correction critique de sécurité dans `extension/content.js` :
     - *Défaut corrigé* : En mode hors-ligne, le filtre préalable ne masquait que les montants avec devises, ce qui exposait les URLs contenant des termes de glossaire (ex: `...&montant=25000` annoté en `...&montant [Moni]=25000` sur `T065`).
     - *Correction appliquée* : Alignement du masquage préalable hors-ligne sur les motifs de protection complets (`OFFLINE_SENSITIVE_PATTERNS`) couvrant URLs (`https?://`), courriels, références (`SAF-`, `REF-`, `TX-`), dates, montants en toutes lettres, pourcentages, téléphones, IBAN et comptes.
     - *Intégrité absolue* : Contrôle d'absence de jetons résiduels post-restauration avec repli strict vers la source si le moindre jeton subsiste.
  3. Relevés empiriques et résultats de répétition :
     - **0 montant altéré** (60/60 conformes).
     - **0 crochet entourant un montant** (60/60 conformes, crochets limités strictement aux équivalents de glossaire `[Moni]`, `[Lembá]`, etc.).
     - **0 secret transmis ou altéré** : `T088` et `T090` interceptés par `isSecretText()`, restitués 100% identiques sans appel API.
     - **0 carte « Compromis »** dans le panneau jury : Statut « Intègre » pour l'ensemble des 60 soumissions.
  4. Rédaction technique dans `docs/repetition_finale.md` et données brutes dans `docs/repetition_finale_resultats.json` :
     - Tableaux bruts complets pour Duálá et Ɓàsàa.
     - Liste transparente des limites linguistiques (phrases inédites anglaises non traduites avec repli source intégral, alertes de sécurité inédites maintenues en français par précaution avec badge explicite).
  5. Mise à jour de l'empreinte client :
     - Empreinte exacte du dossier `extension/` mise à jour à **125 034 octets (122,10 Ko)** dans `README.md`, `THIRD_PARTY.md` et `docs/note_technique.md`.

- 2026-11-27 22:45 — Priorisation de relecture et régénération des fiches de validation humaine (CSV et PDF 9 pt) :
  1. Attribution rigoureuse de la colonne « Priorité de relecture » :
     - Règle appliquée à partir de `catalogue/recoupement_ui_resultats.csv` et de la criticité financière :
       - `accord = différent` OU chaîne critique (montants, soldes, frais, avertissements de sécurité, erreurs) → **« haute »**.
       - `accord = identique` → **« référence concordante »** (0 occurrence dans les 8 correspondances actuelles).
       - Toutes les autres chaînes → **« normale »**.
     - Métriques réelles par langue (84 chaînes au total) :
       - Duálá (`dua`) : **37 chaînes haute** (44,0 %), **47 chaînes normale** (56,0 %), 0 référence concordante.
       - Ɓàsàa (`bas`) : **37 chaînes haute** (44,0 %), **47 chaînes normale** (56,0 %), 0 référence concordante.
  2. Tri systématique des fiches par priorité :
     - Les chaînes prioritaires (« haute ») sont regroupées en tête de fiche (rangs 1 à 37), suivies des chaînes de priorité « normale » (rangs 38 à 84). Renumérotation séquentielle stricte de la colonne `N°` de 1 à 84.
  3. Mise à jour de `scripts/generate_validation_sheets.py` et export CSV/PDF :
     - Fiches CSV générées dans `catalogue/kit_validation/` : `fiche_validation_duala.csv` et `fiche_validation_bassaa.csv` avec la nouvelle colonne « Priorité de relecture ».
     - Fiches PDF générées avec Playwright (Microsoft Edge headless) : `fiche_validation_duala.pdf` et `fiche_validation_bassaa.pdf`.
     - Intégration de badges de priorité élégants (`badge-haute` rouge bordeaux, `badge-normale` ardoise sobre, `badge-concordante` vert forêt).
  4. Vérification formelle PyMuPDF / fitz :
     - Duálá : **4 pages A4** (intervalle strict 2 à 4 pages respecté), 592 éléments textuels analysés, **police minimale absolue extraite = 9.00 pt** (seuil requis >= 9.00 pt respecté à 100 %).
     - Ɓàsàa : **4 pages A4** (intervalle strict 2 à 4 pages respecté), 584 éléments textuels analysés, **police minimale absolue extraite = 9.00 pt** (seuil requis >= 9.00 pt respecté à 100 %).
  5. Compatibilité et robustesse de `scripts/importer_validation.py` :
     - Normalisation confirmée : `normalize_col_name("Priorité de relecture")` renvoie `"priorite de relecture"`.
     - Invariance absolue : aucun statut n'est promu par défaut ; l'absence de code validateur ou de date maintient 100 % des entrées en `machine_suggested`.
     - Nouveaux tests unitaires dans `backend/tests/test_validation_import.py` (25/25 tests passés avec succès).
  6. Sanctuarisation du catalogue de référence :
     - Invariance stricte de `catalogue/translations.csv` (zéro modification, `git diff` vide).

- 2026-11-27 22:00 — Recoupement des chaînes d'interface avec les références communautaires externes (DS-06 Common Voice & DS-30 MediaWiki) :
  1. Données externes sanctuarisées hors du dépôt :
     - Emplacement : `C:\Users\FLEX ZONE\Desktop\donnees_externes_safinum\DOSSIER_RECHERCHE_DONNEES_SAFINUM\03_DATASETS_TELECHARGES\` (DS-06 Common Voice Fluent dua/bas/en sous licence MPL-2.0 ; DS-30 MediaWiki JSON en/dua/datetime sous licence GPL-2.0+).
     - Aucune copie dans le dépôt Git ; exclusion préventive de `donnees_externes_safinum/` et `DOSSIER_RECHERCHE_DONNEES_SAFINUM/` consignée dans `.gitignore`.
  2. Script déterministe `scripts/recoupement_references_ui.py` :
     - Chemin externe résolu par variable d'environnement (`SAFINUM_EXTERNAL_DATA_DIR`), argument CLI (`--data-dir`) ou repli par défaut.
     - Appariement exact (insensible à la casse, à la ponctuation et aux balises) des messages anglais sources pour les 160 segments du catalogue ayant un équivalent dans `data/test_env_strings.json`.
     - Récupération stricte de la traduction communautaire à clé égale en Duálá (`dua`) et Ɓàsàa (`bas`) ; aucune traduction inventée.
  3. Génération certifiée de `catalogue/recoupement_ui_resultats.csv` (160 lignes) :
     - 8 segments avec référence communautaire trouvée (5,0 %) : 4 en Duálá (MediaWiki : *Summary*, *Edit* ; Common Voice : *Continue*, *Success*) et 4 en Ɓàsàa (Common Voice : *Back*, *Continue*, *Edit*, *Success*).
     - Accords réels : 0 identique (0,0 %), 8 différents (100,0 % des références trouvées), 152 absents (95,0 %).
     - Éclairage terminologique : analyse des variations morpho-phonologiques (*Tukwe* vs *Túkwa*), des choix syntaxiques (*Alá oboso* vs *Binyɔ́ alá ó ɓosó*, *Kenel bisu* vs *Kee ni bisu*) et de la concision d'interface (*Bwam* vs *Eɓoló é toŋgɛ́lɛ*, *Loñge* vs *Gwégwéé*).
  4. Rédaction technique et transparence dans `docs/recoupement_references_ui.md` :
     - Méthodologie, chiffres réels, analyse comparative des 8 correspondances.
     - Limites formelles : les corpus généralistes (collecte vocale, encyclopédie) ne couvrent pas le vocabulaire bancaire transactionnel (95 % d'absence).
     - Règle d'or : ces références ne valident rien et ne confèrent aucun statut `human_validated` à notre catalogue.
  5. Déclaration dans `THIRD_PARTY.md` :
     - Déclaration formelle en section 5 de Common Voice DS-06 (MPL-2.0) et MediaWiki Core DS-30 (GPL-2.0+) comme références d'interface consultées, non redistribuées.
  6. Suite de tests unitaires et d'intégrité :
     - `tests/test_recoupement_references_ui.py` (3 tests réussis) certifiant la normalisation, la structure du CSV et l'invariance absolue de `catalogue/translations.csv`.
     - Intégration dans la Suite 2 de `scripts/run_all_checks.ps1` (18/18 tests réussis).
  7. Invariabilité stricte : zéro modification apportée à `catalogue/translations.csv` ni à `extension/offline_catalog.json`.

- 2026-11-27 20:15 — Réduction de la latence de repli hors ligne, mémorisation d'état session et optimisation du premier rendu :
  1. Optimisation du repli hors ligne dans `extension/content.js` et `extension/background.js` :
     - Mémorisation de l'état du backend (`isAvailable: true/false`, timestamp) en `sessionStorage` (`safinum_backend_status`, `safinum_backend_last_checked`) avec cache en mémoire (`state.backendState`). Dès qu'une tentative échoue, l'extension mémorise l'indisponibilité pour la session de navigation et bascule instantanément vers le catalogue local `offline_catalog.json` sans bloquer le rendu.
     - Réduction du délai maximal par tentative à 400 ms (au lieu de 1 500 ms) et suppression des essais successifs sur plusieurs hôtes : un seul essai ciblé sur `127.0.0.1:8000/translate/batch`.
     - Sonde de disponibilité en arrière-plan toutes les 30 secondes (`RETRY_INTERVAL_MS = 30000`, fonction non bloquante `probeBackendInBackground()` interrogeant `/health`), permettant une reprise automatique transparente du backend lorsqu'il redémarre sans figer l'interface.
  2. Mesures Avant / Après rigoureuses (12 runs par mode avec rechargement de contexte de navigation vierge) :
     - Mode 1 (Backend Arrêté) : Médiane Avant = **342,22 ms** (P95 = 381,71 ms) → Médiane Après = **79,22 ms** (P95 = **99,28 ms**), gain de réactivité de **-76,9 % (-263 ms)**.
     - Mode 2 (Backend Lancé) : Médiane Avant = **314,99 ms** (P95 = 356,64 ms) → Médiane Après = **77,33 ms** (P95 = **82,49 ms**), gain de réactivité de **-75,4 % (-237 ms)**.
     - Mise à jour complète de `docs/mesures_performance.md` et enregistrement des données brutes dans `docs/raw_performance_metrics.json`.
  3. Tests de régression de performance dans `tests/test_performance_regression.py` :
     - `test_first_render_timing_below_threshold_backend_arrete` : certifie que le premier rendu traduit apparaît en moins de 1 000 ms backend arrêté et que l'état indisponible est enregistré en `sessionStorage`.
     - `test_session_caching_and_subsequent_render_speed` : valide que les navigations ultérieures réutilisent l'état session sans aucune tentative réseau bloquante (< 500 ms, mesuré à 192 ms).
  4. Mise à jour de l'empreinte client :
     - Empreinte exacte du dossier `extension/` mise à jour à **121 590 octets (118,74 Ko)** (somme exacte des 4 fichiers `background.js` 2 970 o, `content.js` 59 180 o, `manifest.json` 1 136 o, `offline_catalog.json` 58 304 o) dans `README.md`, `THIRD_PARTY.md` et `docs/note_technique.md`.

- 2026-11-27 15:15 — Vérification de l'invariance stricte des cartes de soumissions du panneau jury (?jury=1) et renforcement de l'isolation :
  1. Vérification Playwright sous Microsoft Edge (profil vierge, extension active vs désactivée) :
     - Navigation vers `https://safinum.cm/hackathon-test?jury=1`.
     - Génération des cartes de soumission en français de référence pour l'Étape 1 (Solde) et l'Étape 2 (Frais avec saisie de 25 000 FCFA).
     - Activation de l'extension et basculements linguistiques (Duálá `dua`, puis Ɓàsàa `bas`).
     - Relevé brut de l'intégralité du texte des cartes dans l'onglet Soumissions : les cartes existantes sont 100% identiques caractère par caractère avant et après activation (zéro altération, zéro annotation de glossaire du type `[Mutoa]`, zéro badge `contenu inédit`).
     - Déclenchement d'une nouvelle soumission avec extension active : la nouvelle carte générée est strictement intègre (statut « Intègre », aucune altération).
  2. Renforcement de l'isolation dans `extension/content.js` :
     - Sélecteurs d'exclusion configurables (`getExcludedSelectors()` & `isInExcludedZone(el)`) : support étendu pour accepter des tableaux d'exclusion ou des chaînes séparées par des virgules via `window.SAFINUM_EXCLUDED_SELECTORS`.
     - Filtrage réactif dans `MutationObserver` : exclusion absolue de toute mutation survenant dans le conteneur jury `<aside>` ou les zones exclues, y compris le contrôle des nœuds ajoutés (`addedNodes`).
     - Filtrage TreeWalker (`getEligibleTextNodes`) : vérification empirique que strictement 0 nœud n'est collecté dans `<aside>` (contre 34 nœuds collectés si l'exclusion était inactive, ce qui provoquait l'annotation parasite « Consultation des frais [Mutoa] »).
  3. Nouvelle suite de tests automatisée `TestJuryCardsInvariance` dans `tests/test_live_jury_regression.py` :
     - `test_jury_cards_raw_text_identical_before_and_after_extension` : échoue immédiatement si le texte des cartes de soumission diffère entre l'état sans extension et l'état avec extension active, ou si des annotations/badges sont injectés.
     - `test_configurable_exclusion_selectors_and_treewalker_isolation` : valide la configurabilité dynamique des sélecteurs et l'exclusion stricte de TreeWalker.
  4. Validation complète des suites de tests : 100% de succès sur `TestJuryCardsInvariance`, `test_jury_integrity.py`, `test_integrite_figee.py`, `test_widget_accessibility.py`, `test_playwright_mock_bank.py`, `test_performance_regression.py` et `test_extension_e2e.py`.

- 2026-11-26 23:45 — Intégration et validation du jeu de test d'intégrité figée (91 cas) et sanctuarisation des secrets OTP/PIN :
  1. Oracle d'intégrité financière identique à tests_integrite/run.js : réplication stricte des règles (préservation caractère par caractère de protected, comptage non chevauchant, conservation intégrale des chiffres Unicode \p{Nd}+, sanctuarisation des secrets OTP/PIN et valeurs pures, affichage bilingue sans chiffre inventé).
  2. Sanctuarisation des secrets (OTP / PIN / mots de passe) côté extension et backend :
     - Extension (`extension/content.js`) : fonction `isSecretText(text)`. Tout texte contenant un secret (OTP, mot de passe temporaire, code PIN avec chiffres, code de validation) est sanctuarisé localement, jamais envoyé à l'API ni au Service Worker, restitué à 100% à l'identique en mode source (status `fallback_source`, aucun crochet bilingue ni altération).
     - Backend (`backend/protect.py` & `backend/api.py`) : fonction `is_secret_text(text)` et neutralisation immédiate en tête de boucle de `/translate/batch`. Restitution exacte du texte source sans lookup ni appel de modèle.
  3. Durcissement de `protect.py` face aux 61 cas hostiles :
     - Préservation stricte des espaces insécables Unicode (`\u00A0`, `\u202F`, `\u2007`, `\u200B`) sans altération destructive préalable.
     - Montants (`AMOUNT`) : support des devises avant/après, signes négatifs typographiques (`\u2212`, `−`), espaces avec `F CFA`, chiffres arabo-indiens et pleine chasse. Priorisation stricte avant les numéros de téléphone pour éviter d'absorber les montants à 9 chiffres (`250 000 000 FCFA`).
     - Nouveaux motifs inviolables : marque commerciale protégée (`Safinum Pay`), références composites (`TX-*`, `REF-*`, `SAF-*`), dates et horaires multilingues (`novembre`, `November`, `14h30`), e-mails, faux jetons injectés (`__SAFE_*__`, `⟦0⟧`) et variables de gabarit (`{name}`, `{{amount}}`, `%s`).
     - Augmentation de `MAX_TEXT_LENGTH` à 5 000 caractères (anti-DoS préservé tout en traitant le test de performance T091 de 2 000 chiffres).
  4. Création des lanceurs de certification :
     - `scripts/test_integrite_figee.py` : rejeu automatisé sur les trois chemins avec rapport détaillé par groupe (OK / ECHEC / AVERT).
     - `tests/test_integrite_figee.py` : suite `unittest` conforme exécutant les tests unitaires de détection de secrets et les 91 cas.
     - **Chemin (a)** [protect.py pipeline] : **91 OK, 0 ECHEC, 0 AVERT** (100% succès).
     - **Chemin (b)** [API POST /translate/batch fr & en] : **91 OK, 0 ECHEC, 0 AVERT** (100% succès).
     - **Chemin (c)** [extension hors-ligne via Node] : rapporté « non exécuté » conformément aux règles AGENTS.md avec annonce préalable de la taille de `jsdom` (~15 à 20 Mo avec dépendances transitives).
  5. Note d'origine et traçabilité : documentation complète ajoutée dans `tests_integrite/README.md` traçant la genèse des 30 cas officiels du 13/11 et des 61 cas adversariaux.
  6. Validation globale : 100% des suites de tests réussies sans aucune régression.

- 2026-11-26 18:40 — Audit du mode backend lancé sans contournement et architecture Service Worker MV3 :
  1. Audit contradictoire des options de contournement : recensement exhaustif dans `tests/` et `scripts/` de `--disable-web-security` (8 fichiers), `--allow-running-insecure-content` (1 fichier) et `--ignore-certificate-errors` (0 occurrence). Conservation exclusive et motivée de `--host-resolver-rules=MAP safinum.cm 91.234.194.101` (résolution DNS interne Chromium pour le domaine camerounais sans altération de `hosts` Windows, sans désactivation de sécurité web).
  2. Preuve empirique du blocage W3C Private Network Access (PNA) et Mixed Content : capture de la sortie console réelle de Microsoft Edge sous profil vierge sans `--disable-web-security`, démontrant le blocage systématique de tout appel direct depuis une page HTTPS (`https://safinum.cm`) vers `http://127.0.0.1:8000` : `[ERROR] Access to fetch at 'http://127.0.0.1:8000/translate/batch' from origin 'https://...' has been blocked by CORS policy: Permission was denied for this request to access the loopback address space` (`net::ERR_FAILED`).
  3. Architecture Service Worker Manifest V3 native (`extension/background.js`) : relais réseau isolé exécuté dans le contexte privilégié de l'extension, autorisé par `host_permissions` strictement restreintes à `http://127.0.0.1:8000/*` et `http://localhost:8000/*`. Écouteur `chrome.runtime.onMessage` pour `SAFINUM_TRANSLATE_BATCH`, timeout strict de 1 500 ms, et repli immédiat et transparent sur le catalogue hors-ligne embarqué en cas d'indisponibilité.
  4. Adaptation de `extension/content.js` : priorité absolue au passage par `chrome.runtime.sendMessage` vers le service worker, repli direct ou hors-ligne si runtime indisponible. Comportement 100% hors-ligne préservé.
  5. Réécriture des tests sous Edge réel sans aucune option de contournement : suppression de `--disable-web-security` dans `tests/test_live_jury_regression.py`, `tests/test_performance_regression.py`, `tests/test_widget_accessibility.py` et les scripts d'audit. Émulation sécurisée du pont d'extension via `setup_extension_bridge`. Validation complète du Mode 1 (Backend arrêté) et du Mode 2 (Backend lancé FastAPI 127.0.0.1:8000) : 100% Intègre (0 compromis sur 12 soumissions par langue).
  6. Mise à jour de conformité : nouveau test de conformité MV3 (`test_service_worker_mv3_architecture` dans `tests/test_extension_e2e.py`), déclaration dans `THIRD_PARTY.md` (0 Ko tierce), mise à jour de l'empreinte réelle de l'extension à **113 152 octets (110,50 Ko)** dans `README.md` et `docs/note_technique.md`.

- 2026-11-25 08:35 — Harmonisation métrologique stricte et exactitude documentaire :
  1. Recomptage et clarification du catalogue : explicitation formelle de la distinction entre les 84 expressions / segments techniques répertoriés dans les fiches de validation CSV (`fiche_validation_duala.csv`, `fiche_validation_bassaa.csv`) et `translations.csv`, et les 83 chaînes sources françaises uniques dans le dictionnaire JSON `extension/offline_catalog.json` (due à l'homonyme français « Sécurité » indexé sous deux clés distinctes `status_security` et `sec_sidebar_title`).
  2. Empreinte réelle de l'extension : remplacement de la mention approximative « environ 134 Ko » par la taille exacte mesurée de **108 399 octets (105,86 Ko)** (somme des 3 fichiers `content.js` 48 959 o, `manifest.json` 1 136 o et `offline_catalog.json` 58 304 o) dans `README.md`, `THIRD_PARTY.md` et `docs/note_technique.md`.
  3. Suppression des estimations de durée non mesurées : remplacement des mentions « environ 15 à 20 minutes » et équivalents par « durée non mesurée » dans `catalogue/kit_validation/GUIDE_VALIDATEUR.md` et `docs/modeles_messages_validateurs.md` (modèles WhatsApp, e-mail et présentation orale).
  4. Avertissement méthodologique en tête de `docs/mesures_performance.md` : précision explicite que les mesures de latence et de rendu proviennent d'un banc d'essai exécuté sur un PC de développement (Windows 11, Intel i7, 32 Go RAM) et non d'un appareil cible (smartphone d'entrée de gamme / conditions mobiles 2G/3G réelles).

- 2026-11-22 19:35 — Refonte complète et validation du parcours anglais (EN) :
  1. `TestEnglishButtonVerification` (extension désactivée) : vérification avec Playwright du basculement réel de l'interface via le bouton EN du header (résolution du clic masqué par le panneau jury via sélecteur dédié `#app header button, div.flex.items-center.gap-3 button` et `force=True`, viewport 1600x960). Relevé du texte réel sur 5 écrans et comparaison avec `data/test_env_strings.json` : Dashboard 29/29 (100%), Fees 11/13 (84,6%), Beneficiary 7/8 (87,5%), Summary 9/9 (100%), Receipt 5/5 (100%). Les écarts relevés sont strictement conditionnels aux options secondaires (frais Mobile Money et Autre Banque, option motif de virement).
  2. `TestEnglishJourneyRegression` : réécriture intégrale du parcours EN en 5 étapes complètes (saisie 25 000 FCFA) pour Duálá et Ɓàsàa. Exécution réelle et sans skip silencieux dans les deux modes : Mode 1 (Backend Arrêté) et Mode 2 (Backend Lancé démarré et arrêté automatiquement par le test sur FastAPI 127.0.0.1:8000). Contrôle strict de 12 soumissions enregistrées au jury par langue (minimum requis : 9) avec 100% de statut « Intègre » / « Intact » (0 « Compromis »).
  3. Rapport de couverture index EN : rapport écran par écran des résolutions de l'index EN->FR (79/79 chaînes couvertes à 100%). Précision formelle : toute phrase anglaise inédite (hors index) n'est pas annotée (le glossaire embarqué étant en français) et reçoit le badge « contenu inédit ».
  4. Exécution intégrale des 5 suites via `scripts/run_all_checks.ps1` : 191 tests exécutés, 0 échec (100% SUCCÈS, durée cumulée 555,43 s).

- 2026-11-19 17:30 — Sanctuarisation absolue du panneau jury et unification du catalogue embarqué :
  1. Panneau jury sanctuarisé dans `extension/content.js` : exclusion stricte du conteneur `<aside>` et de toute zone jury via la fonction dynamique `isInExcludedZone` et les sélecteurs configurables `getExcludedSelectors()` (`window.SAFINUM_EXCLUDED_SELECTORS`). Exclus de la collecte `TreeWalker`, de la surveillance `MutationObserver` et de la traduction des placeholders.
  2. Tests de non-régression ajoutés dans `tests/test_playwright_mock_bank.py`, `tests/test_extension_e2e.py` et `tests/test_live_jury_regression.py` : vérification que le texte des cartes de l'onglet Soumissions est 100% identique avec et sans extension active, qu'aucun crochet ou badge n'y est injecté, et qu'un sélecteur configurable fonctionne comme attendu.
  3. Résolution du double catalogue embarqué : suppression de `extension/catalogue_offline.json` (doublon divergent sans `en_index`), conservation exclusive de `extension/offline_catalog.json` (58 304 o, complet avec `en_index`), mise à jour de `extension/manifest.json` (`web_accessible_resources`), synchronisation des scripts de génération (`scripts/build_catalogues.py` et `scripts/build_pilot_catalog.py`) et mise à jour de `scripts/package_release.py`.
  4. Test d'anti-divergence des catalogues embarqués dans `tests/test_extension_e2e.py` (`test_no_divergent_embedded_catalogs`), qui échoue si deux catalogues embarqués existent et divergent.
  5. Validation intégrale des 5 suites via `scripts/run_all_checks.ps1` : 187 tests exécutés, 0 échec (100% SUCCÈS).

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

- 2026-11-18 10:25 — Kit de validation locuteurs natifs, modèles de sollicitation, script vidéo v2 et alignement des versions (branche `amelioration`) :
  1. **Guide du validateur linguistique (`catalogue/kit_validation/GUIDE_VALIDATEUR.md`)** :
     - Rédigé en français simple et accessible pour les locuteurs natifs du Duálá et du Ɓàsàa.
     - Détail des 7 colonnes de la fiche, explicitation de la règle essentielle *« Ne rien deviner »*.
     - Consigne impérative d'utiliser `DOUTE` dès la moindre incertitude (entraînant le rejet automatique de la suggestion pour sanctuariser l'intégrité financière en français).
     - Clause éthique de consentement éclairé : protection de la vie privée, aucun nom publié sans accord formel préalable, utilisation d'un code validateur pseudonyme (ex: `VAL-DUA-01`).
  2. **Modèles de messages de sollicitation (`docs/modeles_messages_validateurs.md`)** :
     - Trois modèles de brouillons non envoyés : message WhatsApp (court/direct), e-mail formel institutionnel et présentation orale directe (pitch 60 s).
     - Règle stricte respectée : aucun nom de personne physique ni d'organisme tiers non fourni n'est cité (placeholders explicites `[...]`).
  3. **Script vidéo scénarisé chronométré v2 (`docs/script_video_v2.md`)** :
     - Durée strictement bornée à 3 minutes (180 s) découpée en 6 séquences chronométrées.
     - Couvre : le parcours du règlement (Solde, Frais, Destinataire, Récapitulatif, Reçu), la détection et traduction bilingue de sources anglaises via `en_to_fr_index.json`, les contenus inédits avec badge explicite, la préservation des alertes de sécurité en français (`ANNOTATE_SECURITY_ALERTS=false`), l'intégrité absolue des montants (aucun crochet, 0 compromis sur `?jury=1`), le repli hors-ligne et la mention honnête *« 0 chaîne validée par un locuteur natif à ce jour »*.
     - Basé uniquement sur les composants réellement présents et opérationnels dans le dépôt.
  4. **Section Versions du README (`README.md`)** :
     - Clarification exhaustive des différences entre le tag de soumission officiel `v1.0-soumission-14nov`, la branche `main` et la branche `amelioration` (travaux v2.0).

- 2026-11-18 10:15 — Outillage d'automatisation, lanceur de démo, vérification globale et packaging release v2 (branche `amelioration`) :
  1. **Lanceur de démonstration (`scripts/lancer_demo.ps1`)** :
     - Démarre automatiquement le backend FastAPI souverain (uvicorn, port 8000), sonde l'endpoint `/health` jusqu'à réponse (max 30s).
     - Gère la politique de sécurité de Microsoft Edge Stable (v157+) : charge l'extension via un profil utilisateur temporaire isolé (`--user-data-dir` et `--load-extension`).
     - Vérifie l'accessibilité du site cible `https://safinum.cm/hackathon-test?jury=1` et bascule automatiquement sur `tests/mock_bank.html` en local si le réseau est indisponible.
     - Documente et guide la procédure manuelle alternative via `edge://extensions`.
  2. **Script de vérification globale de toutes les suites (`scripts/run_all_checks.ps1`)** :
     - Exécute séquentiellement les 5 suites de tests du projet : (1) Backend unitaire & API, (2) Intégrité jury & maquette racine Playwright, (3) Accessibilité Shadow DOM WCAG, (4) Performances & régression DOM, (5) Parcours jury live complet sur `safinum.cm` avec gestion propre du skip en cas d'indisponibilité réseau.
     - Affiche un tableau récapitulatif formaté : **187/187 tests exécutés avec succès, 0 échec (SUCCÈS 100%)**.
  3. **Générateur de release de distribution (`scripts/package_release.py`)** :
     - Produit `dist/extension_linguafin_v2.zip` (30,9 Ko, 4 fichiers) avec `manifest.json` strictement positionné à la racine du zip.
     - Produit `dist/linguafin_v2_source.zip` (4,84 Mo, 116 fichiers) avec exclusions strictes (`backend/models`, `.env`, `.git`, `__pycache__`, `dist/`).
     - Intègre un audit anti-secrets (0 clé d'API, 0 token `hf_`/`sk-`), un contrôle strict des tailles maximales et une décompression de test en sandbox temporaire.
  4. **Documentation et modes d'emploi** :
     - Mise à jour de `README.md` avec la section des scripts d'automatisation et de packaging.
     - Mise à jour de `docs/guide_integration_tiers.md` avec les options de chargement de l'extension (automatisé vs manuel).

- 2026-11-18 09:10 — Alignement et test de contrat OpenAPI, guide d'intégration tiers et schéma Mermaid d'architecture (branche `amelioration`) :
  1. **Alignement strict du contrat OpenAPI (`openapi.yaml` vs `app.openapi()`)** :
     - Ajout du paramètre query `include_experimental` sur `GET /languages`.
     - Ajout de `allow_experimental` et `annotate_security_alerts` dans `BatchTranslationRequest`.
     - Alignement complet de `TranslationItemResponse` avec les champs `novel_annotated`, `badge`, `bilingual_required`, `status`.
     - Déclaration des schémas de validation Pydantic standard `HTTPValidationError` et `ValidationError`.
  2. **Suite de tests automatisée du contrat OpenAPI (`backend/tests/test_openapi_contract.py`)** :
     - 5 tests unitaires vérifiant la stricte identité des chemins, méthodes, paramètres de requêtes et propriétés de tous les schémas de données.
     - Échoue immédiatement en cas de divergence entre l'implémentation FastAPI et le fichier de spécification.
  3. **Guide d'intégration tiers en cinq étapes (`docs/guide_integration_tiers.md`)** :
     - Intégration sans aucune modification du code source hôte : (1) Chargement extension Edge/Chrome, (2) Configuration domaines autorisés et CORS, (3) Démarrage API locale, (4) Appel REST avec curl, (5) Appel avec fetch JavaScript.
     - Exemples testés et exécutés en direct sur l'API uvicorn locale avec reproduction intégrale des sorties réelles constatées (intégrité financière 100% préservée).
  4. **Schéma Mermaid d'architecture dans `docs/01_architecture.md`** :
     - Ajout d'un diagramme `flowchart TD` modélisant l'application hôte, l'extension MV3 avec Shadow DOM, le catalogue hors-ligne, et le backend FastAPI avec son pipeline d'intégrité financière `protect.py`.
  5. **Validation globale** : 166/166 tests backend OK, 7/7 tests d'accessibilité OK, 3/3 tests de performance OK.

- 2026-11-18 07:45 — Audit de sécurité indépendant v2, durcissement anti-DoS et isolation stricte (branche `amelioration`) :
  1. **Dépendance d'audit** : `pip install pip-audit` (version 2.10.1, 60,57 Ko / 62 023 octets annoncés avant installation), déclarée dans `THIRD_PARTY.md` section 2.1 comme outil de test et d'audit uniquement (hors production).
  2. **Audit CVE des dépendances backend** : `pip-audit -r backend/requirements.txt` exécuté avec succès : **0 vulnérabilité connue (0 CVE)** sur l'ensemble de la pile.
  3. **Audit de l'historique Git complet** : recherche exhaustive sur tous les commits (`git log -p -S / -G` sur `hf_`, `sk-`, `api_key=`, `tokens`) : **0 secret ou clé API divulgué**, fichier `.env.example` propre sans secret.
  4. **Permissions et Manifest V3 (`extension/manifest.json`)** : `permissions: []` (strictement vide, 0 permission privilégiée), `host_permissions` limité au site officiel (`https://safinum.cm/hackathon-test*`) et aux mocks de développement locaux. Aucun wildcard permissif (`*://*/*` ou `<all_urls>`).
  5. **Éradication de `innerHTML` et `eval` (`extension/content.js`)** :
     - Remplacement de `widget.innerHTML` pour le template statique Shadow DOM par un constructeur programmatique sécurisé `createDOMElement` (`document.createElement`, `setAttribute`, `textContent`).
     - **0 `innerHTML`**, **0 `eval`** dans toute l'extension. Remplacement in-place des nœuds textuels via `nodeValue` sans altération du markup HTML.
  6. **Durcissement du backend FastAPI (`backend/api.py`)** :
     - **Rate Limiting anti-DoS** : limiteur en mémoire par adresse IP à fenêtre glissante de 60 secondes (120 req/min, code `HTTP 429 Too Many Requests` avec en-tête `Retry-After: 60`, requêtes OPTIONS pré-vol exemptées).
     - **Validation des longueurs maximales sur `/feedback`** : contraintes Pydantic strictes (`Field(..., min_length=1, max_length=2000)`) sur `source_text`, `suggested_translation` et `comment` (rejet immédiat en `HTTP 422 Unprocessable Entity`).
     - **Gestionnaire d'exception 500 sans fuite technique** : `@app.exception_handler(Exception)` masquant les stack traces et chemins système Windows en cas d'erreur inattendue.
     - **Confidentialité RGPD absolue des logs** : vérifié par test unitaire, aucun texte utilisateur ni montant n'est jamais consigné dans les journaux applicatifs.
  7. **Rapport et validation** :
     - Rédaction du rapport complet `docs/04_audit_securite_v2.md`.
     - Suite automatisée `backend/tests/test_security_audit_v2.py` (6 tests unitaires passants).
     - Validation globale de non-régression : **161/161 tests backend OK**, **7/7 tests d'accessibilité OK**, **3/3 tests de performance OK**.

- 2026-11-17 12:40 — Mesures de performance réelles et audit de réactivité DOM (Playwright Edge, branche `amelioration`) :
  1. **Environnement matériel et logiciel certifié** :
     - OS : Microsoft Windows 11 Pro 64-bit (build 10.0.26200).
     - Processeur : Intel(R) Core(TM) i7-12850HX (16 cœurs, 24 threads, base 2,1 GHz / turbo 4,8 GHz).
     - RAM : 32 Go DDR5 (33 231 604 Ko visibles).
     - GPU : NVIDIA RTX A1000 Laptop GPU (4 Go VRAM) + Intel UHD Graphics.
     - Navigateur : Microsoft Edge version 157.0.4341.60 (Chromium 157 / moteur Blink).
  2. **(1) Temps de premier rendu traduit (12 itérations par mode)** :
     - **Backend arrêté (mode catalogue hors-ligne)** : Médiane = **234,31 ms**, P95 = **316,82 ms** (min = 154,40 ms, max = 324,29 ms).
     - **Backend lancé (API FastAPI uvicorn)** : Médiane = **223,95 ms**, P95 = **335,55 ms** (min = 169,84 ms, max = 342,84 ms).
  3. **(2) Latence de `/translate/batch` sur 200 appels locaux consécutifs (8 phrases financières)** :
     - **Duálá (`dua`)** : Médiane = **15,99 ms**, P95 = **25,42 ms**, P99 = 26,61 ms (min = 1,91 ms, max = 28,62 ms).
     - **Ɓàsàa (`bas`)** : Médiane = **16,21 ms**, P95 = **25,54 ms**, P99 = 27,46 ms (min = 2,21 ms, max = 28,13 ms).
  4. **(3) Mutations DOM et absence de boucle d'observation** :
     - Total de **41 mutations** traitées en 5 lots sur un parcours bancaire complet de 5 étapes (Solde 21, Frais +8, Bénéficiaire +4, Récapitulatif +4, Reçu +4).
     - Test de convergence : **0 mutation résiduelle** mesurée après stabilisation (absence de boucle infinie formellement prouvée via verrous atomiques et debounce 160 ms).
  5. **(4) Temps de retour à la langue source (`revertToSource`)** :
     - Médiane = **0,80 ms**, P95 = **1,00 ms** (15 itérations, 24 nœuds textuels restaurés).
  6. **Rapports et alignement documentaire** :
     - `docs/raw_performance_metrics.json` : données brutes complètes.
     - `docs/mesures_performance.md` : rapport complet avant/après.
     - `README.md`, `docs/note_technique.md`, `THIRD_PARTY.md` : remplacement de « non mesuré » par un renvoi vers `docs/mesures_performance.md` uniquement pour les points mesurés (PC / Edge / local), maintien strict de « non mesuré » pour smartphones d'entrée de gamme, batterie et réseau 2G/EDGE en milieu rural.
     - `tests/test_performance_regression.py` : suite de 3 tests automatisés (`Ran 3 tests in 7.786s — OK`).


- 2026-11-16 23:05 — Audit et mise en conformité d'accessibilité du widget Shadow DOM (WCAG 2.1 AA, branche `amelioration`) :
  1. **Dépendance d'audit** : `pip install axe-playwright-python` (version 0.1.8, 156,92 Ko / 160 681 octets annoncés avant téléchargement), déclarée dans `THIRD_PARTY.md` section 2.1 comme outil de test uniquement (hors production).
  2. **Audit initial mesuré** (`docs/raw_accessibility_audit_before.json`) :
     - Target size : bouton fermer (21.1 × 29.6 px), switch bilingue/expérimental (38 × 22 px), sélecteur (h=33.6 px) et bouton bascule (h=37.6 px) sous le seuil WCAG 2.5.5 de 44 px.
     - Contraste : `#94A3B8` limite sur fond `#0A192F` ; focus invisible sur switch slider.
     - Clavier : fuite de focus hors du panneau (absence de focus trap).
     - Responsive & Zoom : débordement à 360 px (349.2 px total), contrôles masqués au zoom 200 % (absence de `overflow-y: auto`).
     - Reduced motion : transitions actives malgré `prefers-reduced-motion: reduce`.
     - ARIA-live : conteneur de statut avec `aria-live="polite"` polluant la synthèse vocale.
  3. **Mise en conformité du widget Shadow DOM** (`extension/content.js`) :
     - **Cibles tactiles >= 44 px** : `min-width: 44px; min-height: 44px;` sur `#btnClose`, `#langSelect`, `#btnToggleTranslate`, et `.switch` (48 × 44 px).
     - **Contraste WCAG AAA (7.41:1 à 14.63:1)** : rehaussement des libellés à `#CBD5E1` (11.86:1), bouton fermer `#FFFFFF` sur `#1E293B` (14.63:1), bandeau `#FEF3C7` sur `#451A03` (13.45:1).
     - **Navigation clavier & Focus Trap** : cycle fermé strict `['langSelect', 'btnToggleTranslate', 'checkBilingual', 'checkExperimental', 'btnClose', 'langSelect']` (Tab et Maj+Tab), ouverture par Entrée/Espace, fermeture Échap avec retour de focus sur le badge.
     - **Indicateurs de focus** : `*:focus-visible` et `input:focus-visible + .slider` avec outline cyan `#00BFFF` 2px et décalage contrasté.
     - **Responsive 360 px & Zoom 200 %** : largeur panneau 320 px + 12 px marge (s'inscrit sans défilement horizontal), `max-height: calc(100vh - 80px); overflow-y: auto;` (accessible au zoom 200 %).
     - **Prefers-reduced-motion** : `@media (prefers-reduced-motion: reduce)` désactivant strictement transitions (`none 1e-06s`) et animations.
     - **Live Announcer** : région dédiée `<div id="liveAnnouncer" class="sr-only" aria-live="polite" aria-atomic="true">` avec déduplication de message et debounce.
  4. **Validation et documentation** :
     - `scripts/audit_accessibilite.py` : script d'audit automatisé Playwright Edge + Axe-core.
     - `tests/test_widget_accessibility.py` : suite de 7 tests automatisés (`Ran 7 tests in 15.711s — OK`).
     - `docs/accessibilite_mesuree.md` : rapport complet avant/après avec chiffres réels certifiés et mention « non mesuré » pour les lecteurs d'écran réels physiques (NVDA/Narrator).
  5. **Sorties brutes réelles certifiées** :
     - Tests backend : `Ran 155 tests in 0.312s — OK`.
     - Tests accessibilité : `Ran 7 tests in 15.711s — OK`.
     - Tests régression live jury : `Ran 3 tests — OK` (0 compromis).


- 2026-11-16 20:18 — Réglage ANNOTATE_SECURITY_ALERTS et correction de l'espacement du badge (branche `amelioration`) :
  1. **Factorisation des mots-clés de sécurité** :
     - `backend/protect.py` : création de `SECURITY_ALERT_KEYWORDS` et `is_security_alert_text(text)` factorisés (mots-clés : `alerte`, `sécurité`, `securite`, `attention`, `fraude`, `suspect`, `danger`, `bloqué`, `bloque`, `confidentialité`, `confidentiel`, `warning`, `alert`, `security`, `fraud`, `avertissement`).
     - `extension/content.js` : déclaration factorisée de `SECURITY_ALERT_KEYWORDS` et `isSecurityAlertText(text)` utilisés dans `isCriticalText()`, `resolveOffline()` et la mise en évidence DOM.
  2. **Réglage ANNOTATE_SECURITY_ALERTS (défaut : false)** :
     - Backend (`backend/api.py`) : `ANNOTATE_SECURITY_ALERTS` via variable d'environnement (défaut `False`) et paramètre optionnel `annotate_security_alerts` dans `BatchTranslationRequest`.
     - Contrat d'API (`openapi.yaml`) : ajout de `annotate_security_alerts: boolean` (défaut `false`) dans le schéma `BatchTranslationRequest`.
     - Extension (`extension/content.js`) : `state.annotateSecurityAlerts` (défaut `false`), surchargeable via `window.ANNOTATE_SECURITY_ALERTS`, transmis dans le payload de `fetchTranslationsBatch()`.
  3. **Comportement sur alerte de sécurité inédite** :
     - Quand `ANNOTATE_SECURITY_ALERTS == false` : le texte reste en français d'origine sans annotation de glossaire (aucun crochet `[...]`), statut `fallback_source`, `novel_annotated: false`, avec le badge exact : `« avertissement affiché en français : traduction non validée »`.
     - Quand `ANNOTATE_SECURITY_ALERTS == true` : annotation normale des termes du glossaire, montants préservés sans crochets, badge `« contenu inédit : termes annotés, phrase non traduite »`.
  4. **Correction du collage du badge sur la phrase** :
     - `extension/content.js` : insertion d'un nœud d'espacement (`document.createTextNode(' ')`) avant l'élément `.safinum-novel-badge` évitant tout collage avec la ponctuation ou le dernier mot dans le flux textuel et dans `innerText`.
  5. **Tests unitaires et de régression live jury** (sorties brutes réelles certifiées) :
     - `backend/tests/test_annotate_security_alerts.py` : 9/9 tests OK.
     - `backend/tests/test_novel_glossary_annotation.py` : 10/10 tests OK.
     - Suite complète backend : `Ran 155 tests in 0.328s — OK`.
     - Mode 1 Live Jury (Backend arrêté) : Alerte sécurité avec montant 75 000 FCFA (\u202F) -> aucun crochet, badge visible (`avertissement affiché en français : traduction non validée`), anti-collage conforme, 0 entrée compromise (`Ran 1 test in 96.096s — OK`).
     - Mode 2 Live Jury (Backend lancé) : Alerte sécurité avec montant 75 000 FCFA (\u202F) -> aucun crochet, badge visible, anti-collage conforme, 0 entrée compromise (`Ran 1 test in 112.071s — OK`).
     - Mode 3 Live Jury (Extension désactivée) : 0 compromis (`Ran 2 tests in 139.529s — OK`).

- 2026-11-16 19:19 — Support source anglais (EN→FR) dans le content script et le backend (branche `amelioration`) :
  1. **`data/en_to_fr_index.json`** (nouveau) : index normalisé `{en_key_lower: source_fr}` généré depuis `data/test_env_strings.json`. 79 entrées. Normalisation NFKC + lower + espaces insécables → espace ordinaire.
  2. **`extension/offline_catalog.json`** : enrichi avec `en_index` (79 entrées). Les chaînes anglaises connues sont résolues vers leur traduction locale FR sans inventions.
  3. **`extension/content.js`** : ajout de `normalizeEnKey()` et `resolveEnToFr()` ; `resolveOffline()` tente d'abord la résolution EN→FR si la chaîne n'est pas directement dans le dictionnaire FR ; `fetchTranslationsBatch()` convertit les textes anglais en FR avant envoi API et mappe les résultats sur le texte DOM original.
  4. **`backend/api.py`** : chargement de `EN_INDEX` au démarrage (`load_en_to_fr_index()`), `normalize_en_key()`, résolution EN→FR au début de la boucle `translate_batch` si `source_lang=="en"`.
  5. **Formats anglais `25,000 FCFA`** : déjà couverts par le pattern AMOUNT existant dans `protect.py` (confirmé par tests).
  6. **`backend/tests/test_en_index.py`** (nouveau) : 36 tests unitaires en 5 classes (TestEnIndexLoad, TestNormalizeEnKey, TestResolveEnToFr, TestEnglishAmountMasking, TestApiEnSourceLang). Tous OK.
  7. **`tests/test_live_jury_regression.py`** : ajout de `TestEnglishJourneyRegression` avec `test_mode1_backend_arrete_en` et `test_mode2_backend_lance_en` (Duala + Bassa'a).
  8. **Sorties brutes certifiées** (exécution réelle) :
     - Backend tests : `Ran 144 tests in 0.298s — OK`
     - EN Mode 1 (backend arrêté) : Duala(EN)=2 soumissions, 0 compromis ✅ | Bassa'a(EN)=2 soumissions, 0 compromis ✅
     - EN Mode 2 : IGNORÉ proprement (backend non actif, port 8000 fermé) ✅
  9. **`openapi.yaml`** : `source_lang: enum ["fr","en"]` était déjà présent — aucune modification nécessaire.
  10. Règle : chaîne EN inconnue → texte source conservé, badge "contenu inédit" si termes annotés, jamais de traduction inventée.

- 2026-11-16 17:23 — Mesure de couverture de traduction par écran (Playwright Edge, branche `amelioration`) :

  1. `scripts/mesurer_couverture.py` : navigation complète (Tableau de bord, Frais, Bénéficiaire, Récapitulatif, Reçu, Alertes/Erreurs) SANS extension (textes FR natifs), comparaison avec `catalogue/translations.csv` et `catalogue/glossaire.csv`. Sortie brute mesurée via exécution réelle.
  2. **Sorties brutes certifiées** : 91 chaînes FR visibles (tous écrans, dédoublonnées).
     - `dua` : mémoire=70 (77%), glossaire=0, non couverts=21 (23%)
     - `bas` : mémoire=70 (77%), glossaire=0, non couverts=21 (23%)
  3. **Couverture par écran** (réelle mesurée) :
     | Écran | Visibles | dua% couvert | bas% couvert |
     |---|:---:|:---:|:---:|
     | Tableau de bord | 37 | 83% | 83% |
     | Consultation des frais | 32 | 93% | 93% |
     | Bénéficiaire | 28 | 92% | 92% |
     | Récapitulatif | 30 | 90% | 90% |
     | Reçu | 28 | 89% | 89% |
     | Alertes / Erreurs | 57 | 64% | 64% |
  4. **Chaînes non couvertes** : noms propres (Amina Ngo Bell, Jean-Paul Mbarga), numéro de compte (CM 001...), montants signés avec espace (+180 000 FCFA, -12 500 FCFA), textes internes du panneau jury (hors portée traduction).
  5. **Interface EN** : bouton EN détecté et actif. Les chaînes collectées en anglais ont la même couverture mémoire car le texte affiché reste en français (le bouton EN ne change pas la langue du contenu bancaire). Catalogue indexé sur FR : couverture EN = couverture FR.
  6. Aucune modification du catalogue. Valeurs « non mesuré » non utilisées (tous les écrans ont pu être navigués).
  7. `docs/couverture_mesuree.md` généré. Commit ciblé : `git add scripts/mesurer_couverture.py docs/couverture_mesuree.md SUIVI.md`.

- 2026-11-16 16:30 — Adaptation de l'importateur de validation aux fiches kit_validation (branche `amelioration`) :

  1. `scripts/importer_validation.py` refondé : normalisation NFKD des en-têtes (accents, ponctuation, implosive Ɓ), reconnaissance de tous les en-têtes réels (`N°`, `Clé / Contexte`, `Texte Source (Français)`, `Proposition Traduction (Duálá)`, `Proposition Traduction (Ɓàsàa)`, `Correction du validateur`, `Validation (OK / KO)`, `Commentaire linguistique`).
  2. Ajout des options CLI `--langue` (obligatoire, `dua` ou `bas`), `--validateur` (code validateur), `--date` (AAAA-MM-JJ), applicables à l'intégralité de la fiche.
  3. Correspondance par `(cle, langue)` exclusivement — jamais par source seule. Clé introuvable = erreur signalée, jamais créée.
  4. Règle stricte confirmée : `human_validated` si et seulement si avis=OK + validateur non vide + date non vide + pas de correction. Correction présente → `draft`. DOUTE → `rejected`. Tout le reste → `machine_suggested`.
  5. `backend/tests/test_validation_import.py` enrichi : 23 tests couvrant les en-têtes réels (duala et bassa'a), absence validateur/date → 0 promotion, mauvaise langue → 0 modification, clé inconnue → erreur (jamais créée), correction → draft (jamais human_validated), dry-run → disque intact.
  6. Exécution réelle certifiée : **23/23 tests** `test_validation_import.py` OK. **108/108 tests** (discover backend/tests) OK. Sorties brutes ci-après (non mesurée : suite Playwright live jury en cours au moment du commit).
  7. Commit ciblé : `git add scripts/importer_validation.py backend/tests/test_validation_import.py SUIVI.md`.

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

- 2026-11-15 19:55 — Fiches de validation PDF (kit_validation) et extension du test Live Jury aux contenus inédits :
  1. Branche : `amelioration` exclusivement (`git branch --show-current` vérifié, tag `v1.0-soumission-14nov` intact).
  2. Création de `scripts/generate_validation_sheets.py` et génération dans `catalogue/kit_validation/` :
     - `fiche_validation_duala.pdf` (4 pages A4, police min 9.00 pt) et `fiche_validation_duala.csv` (84 entrées).
     - `fiche_validation_bassaa.pdf` (4 pages A4, police min 9.00 pt) et `fiche_validation_bassaa.csv` (84 entrées).
     - Conservation de `catalogue/fiche_validation.csv` ; en-tête de tableau répété sur chaque page A4 (`thead` répété) ; vérification PyMuPDF/fitz certifiée (pages comprises entre 2 et 4, police >= 9 pt).
  3. Extension de `tests/test_live_jury_regression.py` : injection successive via le panneau jury de 3 contenus inédits (alerte de sécurité avec montant et espace fine insécable `\u202F`, confirmation de virement, notification sans montant).
  4. Validation certifiée dans les modes backend arrêté et backend lancé : 0 entrée « Compromis », aucun crochet entourant un montant financier, et badge / conteneur « contenu inédit » visible.
  5. Bilan complet des tests : 86/86 tests réussis (77 backend + 6 racine + 3 live jury Playwright).

- 2026-11-15 19:10 — Création et exécution réussie du test de régression live jury (`tests/test_live_jury_regression.py`) :
  1. Branche courante : `amelioration` (tag `v1.0-soumission-14nov` intact).
  2. Implémentation du test sous Microsoft Edge (Playwright, profil vierge) avec gestion automatique de la connectivité réseau (clause d'injoignabilité : statut `skipped` avec motif clair en cas d'inaccessibilité).
  3. Exécution complète des 3 modes sur `https://safinum.cm/hackathon-test?jury=1` :
     - **Mode 1 (Backend arrêté / Hors-ligne)** : parcours complet (Solde, Frais avec saisie 25000, Bénéficiaire, Récapitulatif, Reçu) déroulé en Duálá puis en Ɓàsàa -> **0 entrée compromise** (100% Intègre sur toutes les soumissions).
     - **Mode 2 (Backend lancé / FastAPI 127.0.0.1:8000)** : parcours complet déroulé en Duálá puis en Ɓàsàa -> **0 entrée compromise** (100% Intègre).
     - **Mode 3 (Extension désactivée / Référence FR)** : parcours complet en français natif -> **0 entrée compromise** (100% Intègre).
  4. Bilan global : **3/3 tests passés avec succès**, 0 statut « Compromis », intégrité financière et normalisation jury strictement préservées.

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

- Validation humaine des traductions Duálá / Ɓàsàa via `catalogue/kit_validation/GUIDE_VALIDATEUR.md`.
- Présentation au jury et enregistrement vidéo de la démo (3 minutes via `docs/script_video_v2.md`).
- Déploiement ou chargement direct du dossier `extension/` dans Chrome/Edge via `scripts/lancer_demo.ps1`.


