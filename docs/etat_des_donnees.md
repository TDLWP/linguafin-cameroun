# État des Données Linguistiques et Justification de l'Architecture — SAFINUM 2026

> **Projet** : SAFINUM Innovate Challenge 2026  
> **Source de référence** : Dossier d'investigation externe `DOSSIER_RECHERCHE_DONNEES_SAFINUM` (`NOTE_TRANSFERT_CLAUDE_PRINCIPAL.md`, `REGISTRE_LICENCES.csv`, `INVENTAIRE_DATASETS.csv`, `INVENTAIRE_MODELES.csv`, `RAPPORT_RECHERCHE_DONNEES.md`).  
> **Règle de véracité stricte** : Tous les chiffres et statuts ci-dessous proviennent exclusivement de données primaires inspectées ou de pages vérifiées lors de la recherche. Tout élément non attesté formellement est explicitement indiqué comme **non vérifié**.

---

## 1. Constat Fondamental : Absence de Données Alignées dans le Domaine Financier

L'exploration systématique des dépôts ouverts, publications scientifiques et référentiels linguistiques mondiaux conduit à une conclusion sans équivoque :

> **Aucune donnée alignée (bilingue ou multilingue) dans le domaine financier, bancaire ou d'interface de paiement n'existe pour les langues nationales camerounaises** (français ou anglais vers une langue locale).

### Détail des constats :
1. **Corpus bilingues existants hors domaine** : Les rares corpus parallèles disponibles pour les langues camerounaises relèvent exclusivement du texte religieux (traductions bibliques), de la presse générale d'actualité (ex. MAFAND-MT pour le ghomálá' avec des métriques faibles : BLEU ≤ 2,72 en fr→bbj) ou de la linguistique descriptive académique (phrases orales transcrites).
2. **Textes financiers camerounais identifiés** :
   - Textes institutionnels et réglementaires : Règlements CEMAC (03/16, 04/18 sur les services de paiement, 01/20 sur la protection des consommateurs), instructions COBAC (R-2020/04), Traité et Actes uniformes OHADA, Code Général des Impôts (DGI Cameroun). Ces textes sont rédigés en français ou disponibles en version bilingue français/anglais, mais **sans aucune traduction en langue camerounaise**.
   - Conditions générales d'opérateurs réels : Conditions MTN Mobile Money Cameroun (`momo.mtn.com/terms-conditions`, consultées le 16/11/2026) en français et anglais (19 articles de chaque côté citant CEMAC 04/18 et 01/20). Ce document est sous droit d'auteur exclusif (`© MTN / Mobile Money Corporation`), sans licence ouverte de réutilisation.
3. **Conséquence pour le projet SAFINUM** : Aucun modèle de traduction automatique (MT) généraliste ou commercial ne peut être déployé tel quel pour garantir l'intégrité sémantique et financière de transactions bancaires en langues nationales sans risque critique de contresens ou d'altération de montants.

---

## 2. Inventaire des Sources Consultées pour le Duálá (`dua`) et le Ɓàsàa (`bas`)

L'inventaire ci-dessous recense l'ensemble des ressources répertoriées pour les deux langues cibles du prototype, avec leur licence formelle, leur statut exact d'accès/téléchargement et leurs limites d'utilisation.

### A. Ressources pour le Duálá (`dua`)

| Identifiant & Ressource | Contenu & Volume Exact Vérifié | Licence | Statut de Téléchargement | Domaine & Limites |
|---|---|---|---|---|
| **DS-06** Common Voice UI (Mozilla) | **283 paires** EN→dua différentes de l'anglais | **MPL-2.0** | **Téléchargé et vérifié** | Interface web vocale générique (menus, boutons) ; aucun vocabulaire financier. |
| **DS-30** MediaWiki Core i18n (`dua.json`) | **565 messages** alignés par clé sur l'anglais (+ 53 clés datetime) | **GPL-2.0+** | **Téléchargé et vérifié** | Interface logicielle wiki (connexion, annuler, confirmation, suppression, erreurs) ; utile pour amorçage UI ; aucun terme bancaire. |
| **DS-32** OPUS Tatoeba-Challenge (`dua-eng`) | **15 236 paires** annoncées (v2021) ; 15 020 (v2020) | Compilation **CC BY-NC-SA 4.0** (sources non vérifiées) | **Non téléchargé** (listes lues) | Anglais-source uniquement ; origine des phrases non vérifiée (probablement religieux / JW300) ; non financier. |
| **DS-38** BOUQuET (Meta FAIR / Mozilla / IADH) | Sous-ensemble duala issu d'un jeu de 275 variétés (**1 364 phrases** partagées sur le groupe de langues camerounaises) | **CC-BY-4.0** (fiche) ; code d'évaluation MIT | **Non téléchargé** (accès conditionné sur HF) | Jeu d'évaluation multi-registres (dialogues, narrations, web) ; non financier ; non destiné à l'entraînement. |
| **DS-04** Common Voice v27 (`dua`) | 26,9 h de voix ; CER 5,4 rapporté par Omnilingual ASR (non reproduit) | **CC0** | **Non téléchargé** (métadonnées seules consultées) | Audio et transcriptions monolingues ; aucune traduction. |
| **DS-24** Bloom Library (`bloom-lm`) | **0 document** (duala absent) | Variable par histoire | **Non téléchargé** | Langue absente de la base. |

### B. Ressources pour le Ɓàsàa (`bas`)

| Identifiant & Ressource | Contenu & Volume Exact Vérifié | Licence | Statut de Téléchargement | Domaine & Limites |
|---|---|---|---|---|
| **DS-05** Common Voice Basaa Sentence Collector | **5 015 lignes** de texte monolingue (`sentence-collector.txt`) | **CC0** | **Téléchargé et vérifié** | Phrases courtes générales pour collecte vocale ; aucune traduction FR/EN ; non financier. |
| **DS-06** Common Voice UI (Mozilla) | **516 paires** EN→bas | **MPL-2.0** | **Téléchargé et vérifié** | Interface logicielle vocale ; boutons et états d'interface ; aucun terme financier. |
| **DS-32** OPUS Tatoeba-Challenge (`bas-eng`) | **27 778 paires** annoncées (v2023-09-26) ; 27 200 (2020) ; 28 750 (2021) | Compilation **CC BY-NC-SA 4.0** | **Non téléchargé** (listes lues) | Anglais-source uniquement ; contenu non inspecté (JW300 probable, non vérifié) ; licence non commerciale. |
| **DS-25** Webonary SIL (Dictionnaire basaa) | Dictionnaire basaa-français-anglais-allemand (P.E. Njock, © 2019) ; nombre d'entrées non relevé | **© du compilateur** (aucune licence ouverte) | **Non téléchargé** (page Copyright lue) | Lexique général descriptif ; aucun terme financier spécialisé ; droits d'intégration non accordés. |
| **DS-10** ALCAM Basaa Mbene (MDC / IADH) | Lexique multimodal et phrases illustratives avec audio | **NOODL-1.0** | **Non téléchargé** (extrait de recherche) | Usages génératifs et commerciaux interdits sans accord écrit ; données de recherche descriptive. |
| **DS-38** BOUQuET (Meta FAIR / Mozilla / IADH) | Sous-ensemble basaa (traductions humaines de référence) | **CC-BY-4.0** | **Non téléchargé** (accès conditionné) | Jeu d'évaluation multi-domaines ; non financier. |
| **DS-04** Common Voice v27 (`bas`) | 59,8 h de voix ; CER 9,7 rapporté par Omnilingual ASR (non reproduit) | **CC0** | **Non téléchargé** (métadonnées seules consultées) | Données vocales monolingues ; pas de paires de traduction. |
| **DS-24** Bloom Library (`bloom-lm`) | **0 document** (basaa absent) | Variable par histoire | **Non téléchargé** | Langue absente de la base. |

---

## 3. Analyse Critique des Moteurs Neuronaux Existants

### A. Éviction du Moteur Flagship AI (`flagship-ai/cameroon-int8`)

Le bundle `flagship-ai/cameroon-int8` (développé par Flagship SARL / Lingo / NativeAI) est le seul modèle prétendant offrir une traduction clé en main pour une soixantaine de langues camerounaises (119 directions avec le français comme langue pivot). Il a été formellement **écarté du cœur d'exécution de SAFINUM** pour des motifs juridiques et techniques rédhibitoires :

1. **Contradiction juridique insurmontable sur la licence** :
   - La fiche officielle du modèle Hugging Face impose expressément la licence **CC BY-NC 4.0** avec la mention explicite : *« research and non-commercial use »*.
   - Le README de l'organisation Flagship affirme à l'inverse que l'ensemble de leurs ressources est en *CC-BY-4.0*.
   - Cette contradiction légale non résolue expose tout déploiement applicatif ou commercial à un risque juridique direct.
2. **Absence totale de métriques de qualité publiées** :
   - La fiche du modèle ne publie **aucun score BLEU, chrF ni métrique d'évaluation standardisée** sur aucune des paires annoncées.
   - Les données d'entraînement réelles ne sont pas documentées sur la fiche officielle. Une copie de fiche (`shadow-walker1/ghomala-francais`) mentionne un corpus compilé d'écritures bibliques et de brochures, confirmé par le dépôt `cameroon_bibles` (≈496 k lignes de textes bibliques). Le modèle est donc entraîné sur un registre religieux ou formel traditionnel, totalement inadapté au vocabulaire technique moderne.
3. **Instabilité et hallucinations constatées en inférence locale** :
   - L'évaluation expérimentale sur 20 libellés réels (paire `francais-fufulde`) a révélé des anomalies sévères : répétitions de syntagmes en boucle (*« Ɓe njaɓi ɓe, ɓe njaɓi ɓe... »*), maintien de mots anglais non traduits (*« Balance »*, *« Transaction reference »*), et dérives religieuses hors contexte (*« To gooŋgaay ɗowtanaago Allah... »* pour *« Confirmer le transfert »*).
   - De surcroît, le modèle omet les jetons de protection financière masqués dans le texte source, déclenchant le repli sécurisé d'intégrité.
4. **Absence du Duálá et du Ɓàsàa** :
   - Ni le Duálá ni le Ɓàsàa ne figurent dans la liste des 59 langues affichées sur la fiche du bundle `cameroon-int8`.

### B. Non-Couverture par Meta NLLB-200 / FLORES-200

Le modèle open-source de référence de Meta AI, NLLB-200 (No Language Left Behind), ainsi que son benchmark d'évaluation FLORES-200, ont également été écartés :

1. **Non-couverture des langues camerounaises cibles** :
   - Les codes ISO 639-3 `dua` (Duálá) et `bas` (Ɓàsàa) sont **totalement absents** de NLLB-200 et de FLORES-200.
   - Parmi l'ensemble des langues parlées au Cameroun, FLORES-200 n'inclut que :
     - Le fulfulde nigérian (`fuv_Latn`), linguistiquement distinct du fulfulde adamawa (`fub`) pratiqué au Cameroun.
     - Le haoussa (`hau_Latn`).
     - Le kanouri central (`knc_Latn`).
   - Aucune langue camerounaise propre du Sud, du Littoral ou de l'Ouest (duala, basaa, ewondo, ghomálá', medumba, etc.) n'y figure.
2. **Restrictions de la carte modèle** :
   - Licence **CC BY-NC 4.0** (usage de recherche non commercial).
   - La carte officielle NLLB spécifie formellement : *« Modèle de recherche non destiné à la production ni aux textes de domaine spécialisé (médical, juridique) ; traductions non certifiables »*.

---

## 4. Approche Retenue : Architecture Souveraine en 4 Piliers

Face au vide documentaire et à l'inadéquation des modèles neuronaux pour les transactions sensibles, SAFINUM a adopté une architecture déterministe garantissant une intégrité financière absolue :

```
                     ┌────────────────────────────────────────┐
                     │ Texte source (Web / Interface Bancaire)│
                     └───────────────────┬────────────────────┘
                                         │
                                         ▼
                     ┌────────────────────────────────────────┐
                     │    Garde-Fou d'Intégrité Financière    │
                     │  (Masquage strict par jetons __NUM_X__ │
                     │   et Sanctuarisation des secrets OTP)  │
                     └───────────────────┬────────────────────┘
                                         │
                                         ▼
                     ┌────────────────────────────────────────┐
                     │    Mémoire de Traduction Souveraine    │
                     │ (Catalogue embarqué offline 84 chaînes)│
                     └───────────────────┬────────────────────┘
                                         │
                                         ▼
                     ┌────────────────────────────────────────┐
                     │    Glossaire Financier Spécialisé      │
                     │  (Périphrases certifiables en langues) │
                     └───────────────────┬────────────────────┘
                                         │
                                         ▼
                     ┌────────────────────────────────────────┐
                     │    Vérification de Restauration        │
                     │ (100% jetons vérifiés ou repli source) │
                     └───────────────────┬────────────────────┘
                                         │
                                         ▼
                     ┌────────────────────────────────────────┐
                     │  Affichage Bilingue Sécurisé [ShadowDOM│
                     │      (Statut machine_suggested)        │
                     └────────────────────────────────────────┘
```

### 1. Mémoire de Traduction Locale (84 chaînes)
- L'interface d'un service financier numérique (consultation de solde, virement, confirmation, frais, erreurs de saisie) repose sur un ensemble fini de messages transactionnels récurrents.
- Un catalogue de **84 chaînes bilingues** a été constitué pour le Duálá et le Ɓàsàa, embarqué directement dans l'extension navigateur (`extension/offline_catalog.json`, 122,1 Ko d'empreinte totale) pour un fonctionnement 100 % hors-ligne sans dépendance réseau.

### 2. Glossaire Financier et Périphrases Terminologiques
- Les concepts financiers modernes sans équivalent lexical direct dans les langues traditionnelles sont traités par des périphrases fonctionnelles claires, cohérentes et compréhensibles :
  - *Bénéficiaire* ➔ `Nongi a moni` (Duala : « celui qui reçoit l'argent ») / `Mut a nkôs` (Bassa'a : « la personne de réception »).
  - *Annuler* ➔ `Kwele ebolo` (Duala) / `Tiba nsal` (Bassa'a : « arrêter l'action »).
  - *Plafond* ➔ `Su la moni ma lomabe` (Duala : « limite de l'argent envoyé ») / `Ngim moni i n-om` (Bassa'a).
  - *Solde disponible* ➔ `Moni mi titi o bolane` (Duala) / `Moni mi yé inyu salo` (Bassa'a).
- Les termes d'interface génériques (boutons, actions) s'appuient sur les recoupements de référence vérifiés issus de Common Voice (MPL-2.0) et MediaWiki (GPL-2.0+).

### 3. Garde-Fous d'Intégrité Algorithmique Inviolable (`protect.py` & `content.js`)
- **Masquage préalable** : Tous les montants, devises (XAF, FCFA, EUR), pourcentages, frais, numéros de compte, téléphones, dates, heures, codes de référence et identifiants sont remplacés par des jetons inviolables (`__NUM_0__`, `__CURR_0__`, etc.) avant toute traduction.
- **Restauration stricte** : Après traduction, chaque jeton est réinséré à sa place exacte. Si un seul jeton est manquant, altéré ou dupliqué, le système **rejette la traduction et affiche le texte source original sans erreur silencieuse**.
- **Sanctuarisation des secrets (OTP / PIN)** : Les codes confidentiels et mots de passe temporaires sont interceptés par des expressions régulières dédiées ; ils ne sont **jamais traduits, jamais modifiés et jamais envoyés sur le réseau**.

### 4. Protocole de Validation Humaine à Venir
- Conformément à la règle permanente n° 4 d'`AGENTS.md`, **aucune traduction n'est prétendue authentique ou validée** :
  - **0 / 84 chaînes** sont actuellement validées par locuteur natif (100 % au statut `machine_suggested`).
  - Un kit de validation complet est prêt pour la campagne terrain (`catalogue/kit_validation/` contenant fiches CSV hiérarchisées par priorité de relecture et livrets PDF 9 pt prêts à imprimer).
  - Le script `scripts/importer_validation.py` assure l'ingestion traçable (code validateur, horodatage, statut `human_validated` ou `rejected`).

---

## 5. Tableau Récapitulatif de Traçabilité des Métriques

| Dimension | Valeur Documentée | Source Primaire | Statut d'Attestation |
|---|---|---|---|
| Données parallèles financières FR/EN→langues CM | **0 chaîne** | Rapport de recherche (§4) | **Vérifié (absence totale)** |
| Paires d'interface Common Voice EN→Duala | **283 paires** | DS-06 (`DERIVE_paires_UI...`) | **Vérifié (téléchargé)** |
| Paires d'interface MediaWiki EN→Duala | **565 messages** | DS-30 (`languages/i18n/dua.json`) | **Vérifié (téléchargé)** |
| Phrases de collecte Common Voice Basaa | **5 015 lignes** | DS-05 (`sentence-collector.txt`) | **Vérifié (téléchargé)** |
| Paires d'interface Common Voice EN→Basaa | **516 paires** | DS-06 (`DERIVE_paires_UI...`) | **Vérifié (téléchargé)** |
| Paires OPUS Tatoeba EN→Duala / Basaa | 15 236 (`dua`) / 27 778 (`bas`) | DS-32 (listes Helsingin yliopisto) | **Listes vérifiées, données non téléchargées** |
| Corpus MAFAND-MT `fr-bbj` | 4 795 paires (BLEU fr→bbj ≤ 2,72) | DS-01 (fichiers train/dev/test) | **Vérifié (téléchargé)** |
| Nombre de langues bundle Flagship AI | 59 déclarées (119 directions) | MD-01 (`cameroon-int8`) | **Vérifié (fiche lue), non téléchargé** |
| Métriques de qualité MT Flagship AI | **Aucune publiée** | MD-01 | **Vérifié (absence sur fiche)** |
| Couverture Duala / Basaa par Meta NLLB-200 | **0 % (absents de FLORES-200)** | MD-07 (dépôt flores cloné) | **Vérifié (absence formelle)** |
| Chaînes du catalogue SAFINUM validées par natif | **0 / 84 (0,0 %)** | `catalogue/translations.csv` | **Vérifié (audit interne)** |
| Empreinte totale du dossier client `extension/` | **125 034 octets (122,10 Ko)** | Somme réelle des fichiers | **Vérifié (mesure réelle)** |
| Taux de compréhension en zone rurale | Non mesuré | N/A | **Non mesuré** |
| Durée moyenne de validation par fiche | Non mesurée | N/A | **Non mesurée** |
