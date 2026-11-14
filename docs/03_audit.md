# docs/03_audit.md — Rapport d'Audit Hostile & Red Team (SAFINUM 2026)

> **Rôle** : Jury d'évaluation technique & Auditeur de sécurité offensif (Red Team).  
> **Date** : 14 novembre 2026  
> **Cible auditée** : Extension MV3, Backend FastAPI, Moteur de protection financière (`protect.py`, `engine.py`, `content.js`).  
> **Objectif** : Tenter de casser l'intégrité financière, l'extension navigateur, le backend souverain et éprouver les contenus inédits piégés.

---

## 1. Matrice Globale des Vulnérabilités Identifiées

| Réf. | Catégorie | Description de la Faille | Sévérité Initiale | Statut |
|---|---|---|---|---|
| **VULN-01** | Intégrité financière | Nombres nus / montants sans symbole monétaire non masqués (découpage DOM multi-balises) | **Critique** | Corrigé |
| **VULN-02** | Intégrité financière | Biais d'anthroponymie : bénéficiaires inconnus non masqués hors liste figée | **Critique** | Corrigé |
| **VULN-03** | Intégrité financière | Tronquage de montants sur espaces insécables HTML (`&nbsp;`) et devises régionales (`CFA`, `frs`) | **Majeure** | Corrigé |
| **VULN-04** | Extension | Boucle d'observation infinie potentielle : `m.target.closest` indéfini sur nœud texte | **Majeure** | Corrigé |
| **VULN-05** | Extension | Risque de double traduction et altération du texte source lors des re-rendus Vue 3 | **Majeure** | Corrigé |
| **VULN-06** | Extension | Non-application de l'affichage bilingue obligatoire sur alertes de sécurité inédites | **Majeure** | Corrigé |
| **VULN-07** | Backend / DoS | Déni de service ReDoS sur regex `AMOUNT` (159 ms pour 1800 caractères) | **Majeure** | Corrigé |
| **VULN-08** | Backend / Sécurité | Risque d'injection et de collision par forgeage de jetons réservés (`__SAFE_*__`) | **Majeure** | Corrigé |
| **VULN-09** | Contenus inédits | Altération potentielle des URLs contenant des identifiants et montants chiffrés | **Majeure** | Corrigé |
| **VULN-10** | Contenus inédits | Non-détection des montants financiers formulés en toutes lettres | **Majeure** | Corrigé |
| **VULN-11** | Extension | Permissions et hôtes trop permissifs dans le Manifest V3 (`storage`, ports jokers) | **Mineure** | Corrigé |
| **VULN-12** | Backend | Périmètre trop restreint des mots-clés d'alerte critique (`is_critical`) | **Mineure** | Corrigé |

---

## 2. Analyse Détaillée des Failles par Axe d'Attaque

### Axe 1 : Intégrité des Montants, Frais et Bénéficiaires

#### [CRITIQUE] VULN-01 : Absence de masquage des nombres isolés (balises imbriquées)
* **Preuve de concept (PoC)** :  
  Sur le site cible, un montant peut être découpé en deux balises :  
  `<span class="amount">25 000</span> <span class="currency">FCFA</span>`.  
  Dans le content script, chaque nœud textuel est extrait séparément. Le nœud `"25 000"` ne comportant pas de symbole de devise, le regex `AMOUNT` ne déclenchait aucun masquage (`mask_sensitive_data("25 000")` renvoyait 0 jeton). En cas de passage dans un moteur NMT, le nombre était exposé à une réécriture ou suppression.
* **Impact** : Violation directe de la règle permanente d'intégrité financière (Règle 2).
* **Correctif appliqué** :  
  Ajout d'un motif de protection déterministe `NUMBER` masquant tout nombre entier ou décimal isolé ou formaté avec séparateurs de milliers (`__SAFE_NUM_N__`).

#### [CRITIQUE] VULN-02 : Hardcoding des bénéficiaires et fuite de noms inconnus
* **Preuve de concept (PoC)** :  
  Le motif `BENEF` contenait une énumération statique : `\b(?:Jean-Paul Mbarga|Amina Ngo Bell|Amina)\b`.  
  Toute transaction vers un nouveau bénéficiaire (`"Samuel Eto'o"`, `"Mamadou Diallo"`, `"Paul Biya"`) n'était aucunement masquée :  
  `mask_sensitive_data("Bénéficiaire : Samuel Eto'o")` renvoyait `token_map = {}`. Le nom du tiers était envoyé en clair au moteur de traduction automatique.
* **Impact** : Risque d'altération du bénéficiaire lors de la traduction et fuite de données nominales.
* **Correctif appliqué** :  
  Mise en place d'une détection contextuelle des anthroponymes précédés d'indicateurs de rôle (`Bénéficiaire :`, `Destinataire :`, `Vers `, `Pour `) combinée à la reconnaissance des noms propres à majuscules multiples et particules.

#### [MAJEURE] VULN-03 : Échec de masquage sur entités HTML et devises régionales
* **Preuve de concept (PoC)** :  
  - La chaîne `"250&nbsp;000 FCFA"` était tronquée : seul `"000 FCFA"` était masqué, isolant `"250"`.
  - Les montants rédigés avec `"CFA"` sans le préfixe F (ex: `"25 000 CFA"`) ou `"1000frs"` n'étaient pas reconnus par le pattern `AMOUNT`.
* **Impact** : Altération partielle du montant en cas de présence d'entités HTML.
* **Correctif appliqué** :  
  Normalisation préalable des entités HTML (`&nbsp;` ➔ espace insécable) et extension du pattern `AMOUNT` aux variantes `CFA`, `francs CFA`, `frs`, `GBP`, `£`.

---

### Axe 2 : Extension Navigateur (MV3 & Content Script)

#### [MAJEURE] VULN-04 : Boucle d'observation sur mise à jour des statistiques
* **Preuve de concept (PoC)** :  
  Dans `content.js`, le filtre `m.target.closest('#safinum-accessibility-host')` échouait silencieusement lorsque la mutation portait sur un nœud de type `Text` (car `Text.prototype.closest` est indéfini en standard DOM). Lors de la mise à jour des compteurs du widget, un événement `characterData` relançait le timer d'observation, risquant une surcharge CPU.
* **Impact** : Instabilité du fil d'exécution de la SPA et cycles superflus.
* **Correctif appliqué** :  
  Résolution de l'élément cible via `(m.target.nodeType === Node.ELEMENT_NODE ? m.target : m.target.parentElement)` et pose d'un verrou d'inhibition `state.isMutating = true` durant toute écriture DOM.

#### [MAJEURE] VULN-05 : Risque de double traduction lors des re-rendus réactifs
* **Preuve de concept (PoC)** :  
  Si Vue 3 démonte et recrée un nœud textuel préalablement traduit, le nouveau nœud n'a pas la propriété JavaScript `_safinum_orig`. Il adoptait alors la valeur déjà traduite comme valeur source. Tout appel ultérieur à `revertToSource()` réinjectait le texte traduit au lieu du français d'origine.
* **Impact** : Perte de la réversibilité instantanée vers le français.
* **Correctif appliqué** :  
  Stockage redondant du texte d'origine dans l'attribut DOM persistant `data-safinum-orig` sur le conteneur parent, relu prioritairement avant toute ré-assignation.

#### [MAJEURE] VULN-06 : Non-respect de l'affichage bilingue visible pour contenus critiques
* **Preuve de concept (PoC)** :  
  Pour un avertissement de sécurité inédit traduit en `machine_suggested`, le backend renvoyait bien `bilingual_required = True`, mais `content.js` omettait de lire ce champ et se contentait d'un attribut `title` masqué (visible uniquement au survol).
* **Impact** : L'utilisateur n'avait pas le texte français directement sous les yeux en parallèle d'un avertissement de sécurité généré automatiquement.
* **Correctif appliqué** :  
  Prise en compte de `bilingual_required` dans `content.js` : injection immédiate et visible du texte source sous forme `[Original : ...]` directement accolé au texte traduit.

#### [MINEURE] VULN-11 : Permissions et hôtes trop larges dans le Manifest V3
* **Preuve de concept (PoC)** :  
  Le `manifest.json` déclarait `"storage"` (non utilisé) et des jokers d'hôtes `http://localhost:*/*` et `http://127.0.0.1:*/*` s'injectant sur tous les ports locaux sans discernement.
* **Correctif appliqué** :  
  Suppression de la permission `"storage"` et restriction des hôtes aux ports explicitement autorisés (`8000`, `3000`, `5500`, `5173`).

---

### Axe 3 : Backend FastAPI & Robustesse d'Exécution

#### [MAJEURE] VULN-07 : Vulnérabilité ReDoS sur le pattern de détection `AMOUNT`
* **Preuve de concept (PoC)** :  
  Le motif `\d+(?:[\s\u00A0\u202F,\.]\d+)*` présentait une imbrication de quantificateurs provoquant un backtracking catastrophique. Sur une chaîne de 1800 caractères de chiffres séparés d'espaces, le temps d'exécution atteignait **159,38 ms** par élément, soit plus de 15 secondes pour un lot de 100 éléments.
* **Impact** : Déni de service possible du backend FastAPI mono-processus.
* **Correctif appliqué** :  
  Refonte intégrale du regex avec des groupes déterministes non-récursifs (`\d{1,3}(?:[\s\u00A0\u202F\u2007,\.]\d{3})*|\d+`). Temps de matching réduit à **< 0,01 ms** sur la charge d'attaque (gain > 15 000x).

#### [MAJEURE] VULN-08 : Forgeage et injection de jetons sensibles (`__SAFE_*__`)
* **Preuve de concept (PoC)** :  
  Si un utilisateur ou un tiers injectait une chaîne contenant déjà un jeton de type `__SAFE_AMOUNT_0__`, cela pouvait perturber le comptage multi-ensemble ou créer une collision avec les jetons légitimes générés lors de la même passe.
* **Impact** : Faux échec d'intégrité ou tentative de manipulation de jetons.
* **Correctif appliqué** :  
  Passe d'échappement préventif systématique : tout jeton préexistant dans la source est neutralisé en `__ESCAPED_SAFE_*__` avant l'étape de masquage, puis fidèlement restitué lors de la finalisation.

---

### Axe 4 : Contenus Inédits Piégés

#### [MAJEURE] VULN-09 : Corruption d'URLs contenant des identifiants et montants
* **Preuve de concept (PoC)** :  
  Dans une URL telle que `https://safinum.cm/tx/12345/view?amount=25000`, les nombres internes étaient susceptibles d'être segmentés par les règles de montants ou de numéros.
* **Impact** : Liens de suivi de transaction cassés lors de la traduction.
* **Correctif appliqué** :  
  Ajout d'une règle prioritaire de masquage global `URL` (`__SAFE_URL_N__`) protégeant l'intégralité du lien et de ses paramètres avant toute autre analyse.

#### [MAJEURE] VULN-10 : Montants financiers exprimés en toutes lettres
* **Preuve de concept (PoC)** :  
  La chaîne `"Transfert de vingt-cinq mille francs CFA"` n'était couverte par aucun pattern numérique, exposant la valeur textuelle à une altération lors de la traduction automatique.
* **Impact** : Contresens financier majeur possible en texte libre.
* **Correctif appliqué** :  
  Ajout du motif `AMOUNT_WORDS` détectant les combinaisons numérales cardinales en français associées à une devise ou un pourcentage.

---

## 3. Plan de Remédiation et Vérification

Toutes les failles **Critiques** et **Majeures** sont corrigées dans :
1. `backend/protect.py` (nouveaux patterns, élimination ReDoS, échappement jetons, URLs, nombres isolés, montants en lettres).
2. `backend/api.py` (mots-clés d'alerte élargis, contrôle bilingue).
3. `extension/content.js` (anti-boucle observer, mémoire d'original persistant, injection bilingue visible).
4. `extension/manifest.json` (permissions minimales et hôtes restreints).
5. `backend/tests/test_adversarial.py` (nouvelle suite de tests automatisés hostile validant l'ensemble des 10 vecteurs d'attaque).
