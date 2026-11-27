# Recoupement des Chaînes d'Interface avec les Références Communautaires Externes

> **Cadre méthodologique** : Étude comparative entre le catalogue de localisation SAFINUM (`catalogue/translations.csv`) et les corpus d'interface communautaires en langues camerounaises issus de deux projets libres majeurs : **Common Voice (Mozilla)** et **MediaWiki (Wikimedia)**.  
> **Avertissement critique** : Ces données externes constituent un repère terminologique comparatif pour des éléments d'interface génériques (boutons de navigation, statuts généraux). **Elles ne constituent en aucun cas une validation linguistique de nos propositions** : la qualité des sources externes n'est pas mesurée, leur domaine est étranger aux services financiers, et **aucune traduction du catalogue SAFINUM n'est promue au statut `human_validated` sur cette base**.

---

## 1. Contexte et Emplacement des Données Externes

Conformément aux règles strictes du projet (`AGENTS.md`) :
- **Emplacement des données externes** : `C:\Users\FLEX ZONE\Desktop\donnees_externes_safinum\DOSSIER_RECHERCHE_DONNEES_SAFINUM\03_DATASETS_TELECHARGES\`
- **Sanctuarisation du dépôt** : Les données externes sont conservées **strictement en dehors du dépôt Git**. Aucun fichier source tiers n'y a été copié. Le dossier `donnees_externes_safinum/` et ses sous-dossiers sont explicitement exclus dans le fichier `.gitignore`.
- **Reproductibilité** : Le script [`scripts/recoupement_references_ui.py`](../scripts/recoupement_references_ui.py) prend en charge le chemin des données externes via la variable d'environnement `SAFINUM_EXTERNAL_DATA_DIR` ou via l'argument CLI `--data-dir`.

---

## 2. Jeux de Données et Licences

| Ressource | Identifiant | Projet d'Origine | Format & Langues | Licence | Statut dans le Dépôt |
|---|---|---|---|---|---|
| **Common Voice Interface Strings** | `DS-06` | Mozilla Foundation | Fluent (`.ftl`) — `en`, `dua`, `bas` (+ 41 autres langues camerounaises) | **MPL-2.0** (Mozilla Public License 2.0) | Référence externe consultée, **non redistribuée** |
| **MediaWiki Core Localization** | `DS-30` | Wikimedia Foundation | JSON (`en.json`, `dua.json`, `datetime_bas.json`, `datetime_dua.json`) | **GPL-2.0+** (GNU General Public License v2 ou ultérieure) | Référence externe consultée, **non redistribuée** |

Déclarés formellement dans le registre des composants tiers [`THIRD_PARTY.md`](../THIRD_PARTY.md) (Section 5).

---

## 3. Méthodologie du Recoupement

1. **Périmètre d'évaluation** :
   - Les 84 segments du catalogue [`catalogue/translations.csv`](../catalogue/translations.csv) pour les deux langues cibles démontrées : Duálá (`dua`) et Ɓàsàa (`bas`), soit 168 entrées.
   - Sélection stricte des segments disposant d'un équivalent anglais vérifié dans [`data/test_env_strings.json`](../data/test_env_strings.json) (80 clés × 2 langues = **160 segments évalués** ; les 4 clés d'actions génériques sans entrée dans ce JSON — Confirmer, Annuler, Transfert, Erreur — sont exclues du périmètre d'alignement anglais).

2. **Protocole d'appariement déterministe** :
   - Pour chaque segment évalué, recherche d'une **correspondance EXACTE** (insensible à la casse, à la ponctuation et aux balises) entre la chaîne source anglaise de notre interface et un message anglais des corpus de référence (fichiers `.ftl` de Common Voice ou `.json` de MediaWiki).
   - En cas d'appariement sur la clé anglaise, récupération de la traduction communautaire à clé égale dans le fichier de localisation correspondant pour la langue cible (`dua` ou `bas`).
   - Aucune traduction n'est extrapolée ni inventée.

3. **Classification de l'accord** :
   - **`identique`** : La traduction communautaire coïncide exactement avec notre proposition (après normalisation de la casse et des espaces).
   - **`different`** : Une référence communautaire existe pour ce message anglais, mais la formulation diffère de notre proposition.
   - **`absent`** : Aucun message anglais équivalent n'existe dans les sources externes, ou le message n'a pas été traduit dans la langue cible par la communauté.

---

## 4. Chiffres Réels Mesurés

Les résultats complets sont consignés ligne par ligne dans [`catalogue/recoupement_ui_resultats.csv`](../catalogue/recoupement_ui_resultats.csv).

### 4.1 Tableau Récapitulatif Global

| Métrique | Duálá (`dua`) | Ɓàsàa (`bas`) | Total Combiné | Pourcentage |
|---|:---:|:---:|:---:|:---:|
| **Segments évalués (avec source EN)** | 80 | 80 | **160** | 100,0 % |
| **Segments avec référence communautaire trouvée** | 4 | 4 | **8** | **5,0 %** |
| — Dont formulations **identiques** | 0 | 0 | **0** | **0,0 %** |
| — Dont formulations **différentes** | 4 | 4 | **8** | **100,0 % des références** |
| **Segments sans référence communautaire (`absent`)** | 76 | 76 | **152** | **95,0 %** |

---

### 4.2 Analyse Détaillée des 8 Correspondances Obtenues

| Clé | Langue | Source FR | Source EN | Notre Proposition | Référence Communautaire | Source | Accord | Analyse Linguistique |
|---|:---:|---|---|---|---|:---:|:---:|---|
| `wizard_step4` | `dua` | Récapitulatif | Summary | **Mbondo a tomba** | **O patápɛm** | MediaWiki (`filedesc`) | `different` | **Périphrase financière vs résumé éditorial** : *Mbondo a tomba* (« récapitulation du transfert/passage ») qualifie l'opération financière ; MediaWiki emploie *O patápɛm* (« en bref / résumé »), terme générique adapté aux articles wiki. |
| `btn_continue` | `dua` | Continuer | Continue | **Alá oboso** | **Binyɔ́ alá ó ɓosó** | Common Voice (`continue`) | `different` | **Même racine verbale** : Les deux sources emploient le syntagme verbal *ala oboso* (« aller de l'avant / poursuivre »). Common Voice préfixe le pronom d'adresse respectueux/pluriel *Binyɔ́* (« Vous »), tandis que notre interface retient la forme verbale directe adaptée à un bouton d'action. |
| `btn_edit` | `dua` | Modifier | Edit | **Tukwe** | **Túkwa** | MediaWiki (`edit`) | `different` | **Variante morphologique du même verbe** : *Túkwa* / *Tukwe* est le même verbe signifiant « changer, modifier ». Variation dialectale/orthographique mineure sur la finale. |
| `receipt_status_success` | `dua` | Succès | Success | **Bwam** | **Eɓoló é toŋgɛ́lɛ** | Common Voice (`success`) | `different` | **Statut concis vs locution descriptive** : *Bwam* (« Bon / Bien / Réussite ») est le statut d'état d'interface standard ; Common Voice traduit par la proposition complète *Eɓoló é toŋgɛ́lɛ* (« Le travail a réussi »). |
| `btn_back` | `bas` | Retour | Back | **Témb** | **ni mbus** | Common Voice (`card-button-back`) | `different` | **Verbe d'action vs locution directionnelle** : *Témb* (« Retourner / Revenir ») est un verbe d'action clair pour un bouton ; Common Voice utilise la locution adverbiale spatiale *ni mbus* (« en arrière »). |
| `btn_continue` | `bas` | Continuer | Continue | **Kenel bisu** | **Kee ni bisu** | Common Voice (`continue`) | `different` | **Même racine lexicale** : *Kee* et *Kenel* sont des formes dérivées du verbe « avancer / conduire » associées à *bisu* (« en avant »). Concordance sémantique forte. |
| `btn_edit` | `bas` | Modifier | Edit | **Héñha** | **Juble bitilna** | Common Voice (`edit`) | `different` | **Action générale vs action textuelle** : *Héñha* (« Changer / Modifier ») est le terme bancaire généraliste ; Common Voice utilise *Juble bitilna* (« Corriger les écrits / les phrases »), hautement spécialisé pour la saisie vocale. |
| `receipt_status_success` | `bas` | Succès | Success | **Loñge** | **Gwégwéé** | Common Voice (`success`) | `different` | **Statut d'état vs célébration** : *Loñge* (« Bon / Valide / En règle ») désigne la validation de la transaction ; Common Voice utilise l'exclamation *Gwégwéé* (« Victoire / Réjouissance »). |

---

## 5. Limites et Enseignements

1. **Absence quasi-totale de vocabulaire financier dans les corpus génériques (95,0 % absents)** :
   - Les 152 segments absents (76 par langue) correspondent aux termes spécifiques aux services financiers numériques : *Solde disponible*, *Frais de transfert*, *Bénéficiaire*, *Compte débité*, *Plafond*, *Date de valeur*, *Avis de sécurité*.
   - Ni Common Voice (collecte de phrases orales génériques) ni MediaWiki (encyclopédie collaborative) ne couvrent la terminologie bancaire transactionnelle en langues camerounaises.

2. **Qualité et statut des sources externes non évalués** :
   - Les traductions de Common Voice proviennent d'initiatives de crowdsourcing sur Pontoon ; celles de MediaWiki de Translatewiki.
   - Aucune évaluation de cohérence terminologique n'a été conduite sur ces corpus par des linguistes certifiés dans le cadre de notre projet.

3. **Invariabilité stricte du catalogue et honnêteté intellectuelle** :
   - Conformément aux règles fondamentales du projet SAFINUM 2026 : **aucune de ces références n'a été utilisée pour modifier notre catalogue ni pour promouvoir une entrée en `human_validated`**.
   - Seul le protocole formel de relecture par locuteurs natifs documenté dans [`catalogue/kit_validation/GUIDE_VALIDATEUR.md`](../catalogue/kit_validation/GUIDE_VALIDATEUR.md) et exécuté via `scripts/importer_validation.py` confère le statut `human_validated`.
