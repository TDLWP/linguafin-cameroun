# Langues Supportées et Protocole de Validation Linguistique — SAFINUM 2026

> **Projet** : SAFINUM Innovate Challenge 2026  
> **Livrable 5** : Langue(s) supportée(s), méthode de validation, métriques réelles de couverture et traitement des contenus automatiques  
> **Principe d'intégrité** : Données issues exclusivement des tests et des catalogues réels ; **aucune validation humaine n'est prétendue acquise**.

---

## 1. Langues Nationales Supportées

La solution cible deux langues nationales bantoues parlées dans les principaux bassins d'activité économique et d'échanges commerciaux au Cameroun, complétées par un glossaire comparé :

| Langue | Code ISO 639-3 | Statut dans la Solution | Aire Géographique | Base Lexicale Utilisée |
|---|---|---|---|---|
| **Duálá** | `dua` | **Langue Pilote Complète** (84 chaînes) | Région du Littoral (Douala, Wouri, Moungo) | Dictionnaire Duala-Français (P. Helmlinger) & corpus audio Mélac |
| **Ɓàsàa (Bassa'a)** | `bas` | **Langue Secondaire Complète** (84 chaînes) | Littoral & Centre (Sanaga-Maritime, Nyong-et-Kéllé) | Lexiques CEBELA & corpus audio Mélac |
| **Ghɔmálá’** | `bbj` | **Glossaire Financier** (52 termes) | Région de l'Ouest (Hauts-Plateaux) | Glossaire terminologique comparé |
| **Ewondo** | `ewo` | **Glossaire Financier** (52 termes) | Région du Centre (Yaoundé, Mfoundi, Lékié) | Glossaire terminologique comparé |

---

## 2. État Réel des Validations Linguistiques : 0 / 84 Validées par Locuteur Natif

Conformément à la règle 4 et à la règle 7 de `AGENTS.md` :  
> *"Ne jamais présenter une traduction `machine_suggested` comme authentique. Aucune ligne ne passe en `human_validated` sans validation humaine effective."*

### A. Constat Réel et Transparent
* **0 / 84 chaînes sont validées par un locuteur natif à date du 14 novembre 2026**.
* **100 % des propositions textuelles** du catalogue sont au statut `machine_suggested` (brouillons générés par IA).
* Le widget Shadow DOM affiche en permanence un bandeau d'avertissement visible et contrasté :  
  `« ⚠️ Traductions générées par IA, non validées par un locuteur natif. »`.

### B. Méthode en 3 Piliers : Brouillon IA + Recoupement Lexical + Garde-Fou d'Intégrité
Pour assurer la fiabilité sans locuteur natif disponible pendant la phase de développement initial :
1. **Brouillon IA Supervisé** : Rédaction des propositions par des modèles d'IA (Claude, Gemini, GPT-OSS) avec instruction de périphrases obligatoires pour les concepts financiers modernes :
   - *Bénéficiaire* ➔ `Périphrase : Nongi a moni` (Duala) / `Mut a nkôs` (Bassa'a)
   - *Annuler* ➔ `Périphrase : Kwele ebolo` (Duala) / `Tiba nsal` (Bassa'a)
   - *Solde disponible* ➔ `Périphrase : Moni mi titi o bolane` (Duala) / `Moni mi yé inyu salo` (Bassa'a)
   - *Plafond* ➔ `Périphrase : Su la moni ma lomabe` (Duala) / `Ngim moni i n-om` (Bassa'a)
   - Balisage explicite `INCERTAIN` pour toute forme sans attestation établie.
2. **Recoupement Lexical Réel (Cross-check Mélac)** : Découpage mot-à-mot et confrontation avec les lexiques réels du projet Mélac (`lexique_duala.json`, `lexique_bassa.json`, `lexique_manuel_bassa.json`, colonne `traduction` uniquement).
3. **Garde-fou d'Intégrité Financière (`protect.py`)** : Masquage par jetons inviolables des montants, devises, frais, dates, téléphones et bénéficiaires. Pour toute chaîne critique non attestée, le texte français d'origine est **conservé et affiché avec la proposition entre crochets** (`Texte source [Proposition]`) sans substitution.

---

## 3. Résultats Réels du Recoupement Lexical (`catalogue/crosscheck_rapport.csv`)

L'exécution réelle du script [`scripts/crosscheck_lexiques.py`](../scripts/crosscheck_lexiques.py) sur les 168 propositions de [`catalogue/translations.csv`](../catalogue/translations.csv) donne les chiffres mesurés suivants :

| Langue | Total Termes | Attesté (100% mots trouvés) | Partiellement attesté (≥1 mot) | Non attesté (0 mot trouvé) |
|---|:---:|:---:|:---:|:---:|
| **Duálá (`dua`)** | 84 | **0 / 84 (0,0 %)** | **0 / 84 (0,0 %)** | **84 / 84 (100,0 %)** |
| **Ɓàsàa (`bas`)** | 84 | **4 / 84 (4,8 %)** | **58 / 84 (69,0 %)** | **22 / 84 (26,2 %)** |
| **GLOBAL COMBINÉ** | **168** | **4 / 168 (2,4 %)** | **58 / 168 (34,5 %)** | **106 / 168 (63,1 %)** |

### Analyse des Résultats :
* **Duálá (`dua`)** : Dans `lexique_duala.json`, seules 7 entrées possèdent une valeur dans la colonne `traduction` (vocabulaire anatomique de Lingua Libre : *dìso, eyobo, mudùmbu, mulopo, niolo, sònga, toì*). En respectant strictement la consigne *(« colonne traduction uniquement, ne jamais en fabriquer »)*, aucun terme financier du parcours ne correspond à ces 7 mots anatomiques, d'où un taux d'attestation de 0,0 %.
* **Ɓàsàa (`bas`)** : Sur une base lexicale réelle de 994 mots uniques, **4 termes sont 100 % attestés** :
  1. `status_error` : **Erreur** ➔ `Mbebi` (*mot 'mbebi' trouvé*)
  2. `op_other_bank` : **Autre banque** ➔ `Bañga ipe` (*mots 'bañga' et 'ipe' trouvés*)
  3. `sum_label_operation` : **Opération** ➔ `Nsal` (*mot 'nsal' trouvé*)
  4. `receipt_status_success` : **Succès** ➔ `Loñge` (*mot 'loñge' trouvé*)
  De plus, **58 termes (69,0 %)** sont *partiellement attestés* (mots grammaticaux, racines verbales ou termes d'action présents dans le lexique).

---

## 4. Protocole de Validation Native avant la Finale (26-28 Novembre 2026)

La validation humaine certifiée est planifiée entre la soumission du prototype (14 novembre) et la finale du challenge (26-28 novembre 2026) :

1. **Outil de Collecte** : La fiche [`catalogue/fiche_validation.csv`](../catalogue/fiche_validation.csv) (84 lignes pour Duálá) et son équivalent Ɓàsàa sont mis à disposition des locuteurs natifs avec le format standardisé :
   `source,proposition,correction du validateur,OK/KO`
2. **Profil des Validateurs Recrutés** :
   - Deux locuteurs natifs Duálá (un universitaire/linguiste et un commerçant du marché Sandaga à Douala).
   - Deux locuteurs natifs Ɓàsàa (un enseignant CEBELA et un usager régulier de services Mobile Money en zone rurale).
3. **Critères de Passage en `human_validated`** :
   - Une chaîne ne passera au statut `human_validated` dans [`catalogue/translations.csv`](../catalogue/translations.csv) qu'après confirmation signée par le validateur avec horodatage et code validateur (`validateur_code`).
   - Toute proposition jugée trompeuse ou confuse pour des montants/frais sera immédiatement corrigée ou déclassée en `rejected`.

---

## 5. Moteur Local pour Contenu Inédit : Fulfulde (`cameroon-int8`)

> **Décision et Constat Formel** :  
> **Moteur Fulfulde (flagship-ai/cameroon-int8, CC BY-NC 4.0) intégré, testé sur 20 libellés, écarté du parcours de démonstration car les sorties observées présentent des signes d'incohérence (répétitions, anglais non traduit, contenu hors domaine). Qualité non mesurée, variété du Fulfulde non vérifiée, aucune relecture native.**  
> Le garde-fou d'intégrité a basculé en repli source sur 6 phrases contenant des valeurs financières.

* **Modèle** : `flagship-ai/cameroon-int8` (dossier `francais-fufulde` seul), inférence INT8 via **CTranslate2** (`4.9.0`) et **SentencePiece** (`0.2.3`).
* **Licence** : **CC BY-NC 4.0** (déclarée dans [`THIRD_PARTY.md`](../THIRD_PARTY.md)).
* **Reproductibilité** : Script autonome [`scripts/download_fulfulde_model.py`](../scripts/download_fulfulde_model.py) pour le téléchargement isolé du sous-dossier `francais-fufulde` (73,16 Mo).
* **Statut et Accessibilité** :
  - **Désactivé par défaut** dans le backend et absent du sélecteur standard de l'extension.
  - Accessible uniquement si l'utilisateur active explicitement l'interrupteur « **Mode expérimental** » dans le widget.
  - Bandeau d'alerte spécifique en cas d'activation : `« ⚠️ Sortie expérimentale non fiable (moteur non calibré, non relu par un locuteur natif). »`.

### Analyse des 20 Libellés Testés (`catalogue/evaluation_fulfulde_20.csv`)
L'évaluation sur 20 libellés réels démontre concrètement pourquoi le modèle est écarté de la démonstration nominale :
1. **Hallucinations et dérivations constatées** :
   - *Répétitions en boucle* : pour « Frais » ➔ `Ɓe njaɓi ɓe, ɓe njaɓi ɓe, ɓe njogi ɓe.` ; pour « Les frais s'élèvent... » ➔ `Ɓe mbaɗi ɗi ɗi ɗon mbaɗa ɗi ɗi ɗi ɗon mbaɗa.`
   - *Mots anglais laissés tels quels* : pour « Solde » ➔ `Balance` ; pour « Référence de transaction » ➔ `Transaction reference: TX-ujineeje`.
   - *Dérive religieuse hors contexte bancaire* : pour « Confirmer le transfert » ➔ `To gooŋgaay ɗowtanaago Allah, nden kam o wi'i:`.
   - *Sorties incohérentes* : pour « Historique des transactions » ➔ `Asee! Asee!`.
2. **Preuve d'efficacité du garde-fou d'intégrité financière (`protect.py`)** :
   - Sur les **6 phrases contenant des valeurs financières sensibles** (montants, frais, téléphones, références, dates), le modèle neuronal a omis les jetons synthétiques masqués.
   - Le module algorithmique `protect.py` a systématiquement détecté l'absence de jeton et a **basculé en repli source sécurisé**, protégeant 100 % des montants et données critiques contre toute altération.
   - Cette préservation technique découle uniquement du code de sécurité et **ne constitue en rien une validation de la qualité linguistique**.

---

## 6. Données Non Mesurées

Conformément à la règle de rigueur scientifique et d'intégrité :
* **Qualité intrinsèque de traduction du modèle Fulfulde** : **Non mesurée** (le score BLEU/chrF sur terminologie bancaire locale n'est pas étalonné).
* **Variété dialectale du Fulfulde** : **Non vérifiée** (variations Adamaoua vs Diamaré vs Maroua non confrontées à des locuteurs natifs régionaux).
* **Taux d'intelligibilité auprès de populations rurales analphabètes** : **Non mesuré** (nécessite des tests utilisateurs sur le terrain).
* **Temps moyen de remplissage de la fiche de validation par un locuteur natif** : **Non mesuré**.
* **Variations dialectales côtières (Malimba, Abo, Pongo)** : **Non mesuré** (prototype basé sur le Duálá standard).
* **Consommation de batterie lors de sessions de traduction prolongées** : **Non mesuré**.
* **Impact cognitif du format bilingue `Texte source [Proposition]` sur la vitesse de décision** : **Non mesuré**.
