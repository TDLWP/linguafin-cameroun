# Mesures de Performance du Système SAFINUM

> **Avertissement méthodologique** : Les mesures de performance rapportées dans ce document proviennent d'un banc d'essai exécuté sur un **PC de développement** (Windows 11, Intel Core i7-12850HX, 32 Go RAM) sous navigateur automatisé (Microsoft Edge / Playwright) et **non d'un appareil cible** (smartphone d'entrée de gamme ou terminal mobile sous réseau réel 2G/3G). Les performances en conditions réelles dépendront des capacités matérielles du terminal et de la connectivité locale.  
> **Document de référence** : Relevé empirique des performances d'exécution, de latence réseau locale, de réactivité DOM et de stabilité du pipeline d'accessibilité SAFINUM.  
> **Outils de mesure** : Playwright (Microsoft Edge), `time.perf_counter()`, `performance.now()`, API Python `urllib` et serveur FastAPI sous `uvicorn`.  
> **Date des mesures** : 16 novembre 2026.  
> **Données brutes complètes** : Consignées dans [`docs/raw_performance_metrics.json`](raw_performance_metrics.json).

---

## 1. Environnement de Banc d'Essai et Matériel Utilisé

Toutes les métriques rapportées ci-après ont été mesurées sur la station de développement standard du projet sous environnement réel Windows :

| Composant | Spécification Réelle |
|---|---|
| **Système d'exploitation** | **Microsoft Windows 11 Pro** (64-bit, build 10.0.26200) |
| **Processeur (CPU)** | **Intel(R) Core(TM) i7-12850HX** (16 cœurs physiques, 24 threads, fréquence de base 2,10 GHz, Turbo jusqu'à 4,80 GHz) |
| **Mémoire vive (RAM)** | **32 Go DDR5** (33 231 604 Ko visibles) |
| **Processeur graphique (GPU)** | **NVIDIA RTX A1000 Laptop GPU** (4 Go VRAM GDDR6 dédiée) + **Intel(R) UHD Graphics** |
| **Navigateur Web** | **Microsoft Edge version 157.0.4341.60** (canal officiel, moteur Chromium Blink) |
| **Environnement d'exécution** | Python 3.11.9, Playwright 1.54.0, FastAPI 0.115.5, Uvicorn 0.32.0 |

---

## 2. Temps entre Chargement de Page et Premier Rendu Traduit

### 2.1 Protocole de mesure
- **Page testée** : [`tests/mock_bank.html`](../tests/mock_bank.html) contenant l'ensemble des éléments financiers et formulaires d'un tableau de bord bancaire (Solde, Frais, Bénéficiaire, Récapitulatif, Reçu, Alertes).
- **Point de départ ($t_0$)** : Fin du chargement initial du DOM (`domcontentloaded`) au moment où l'extension débute l'analyse textuelle.
- **Point d'arrivée ($t_1$)** : Apparition du premier élément traduit dans le DOM portant l'attribut `data-safinum-translated="true"`.
- **Répétitions** : 12 exécutions indépendantes avec rechargement de contexte de navigation vierge par mode.

### 2.2 Résultats mesurés (12 itérations)

| Métrique | Mode 1 : Backend Arrêté *(Offline nominal)* | Mode 2 : Backend Lancé *(API Locale FastAPI)* |
|---|:---:|:---:|
| **Médiane ($P_{50}$)** | **234,31 ms** | **223,95 ms** |
| **95ᵉ percentile ($P_{95}$)** | **316,82 ms** | **335,55 ms** |
| **90ᵉ percentile ($P_{90}$)** | **260,06 ms** | **322,29 ms** |
| **Minimum** | **154,40 ms** | **169,84 ms** |
| **Maximum** | **324,29 ms** | **342,84 ms** |
| **Moyenne arithmétique** | **227,22 ms** | **254,78 ms** |
| **Écart-type ($\sigma$)** | 56,88 ms | 65,65 ms |

### 2.3 Échantillons bruts individuels (en millisecondes)
- **Backend Arrêté (12 runs)** : `[193.19, 234.31, 154.40, 254.43, 324.29, 316.82, 175.87, 260.06, 238.30, 167.18, 238.25, 169.55]`
- **Backend Lancé (12 runs)** : `[222.55, 197.26, 225.51, 312.45, 169.84, 335.55, 316.20, 214.89, 223.95, 342.84, 322.29, 174.05]`

> **Constat** : Dans les deux modes, le premier rendu traduit apparaît en **moins de 250 ms en médiane** et **moins de 350 ms au $P_{95}$**. Le mode hors-ligne ne subit aucune pénalité de latence et garantit une disponibilité immédiate sans réseau.

---

## 3. Latence de l'API `/translate/batch` sur 200 Appels Locaux

### 3.1 Protocole de mesure
- **Serveur API** : FastAPI lancé localement sur `http://127.0.0.1:8000` via Uvicorn (1 worker).
- **Payload testé** : 8 phrases financières représentatives du parcours bancaire complet :
  1. *"Solde disponible"*
  2. *"Frais de transfert"*
  3. *"Bénéficiaire du transfert"*
  4. *"Récapitulatif de l'opération"*
  5. *"Confirmer le transfert"*
  6. *"Total à débiter"*
  7. *"Ce bénéficiaire n'a jamais été utilisé auparavant."*
  8. *"Consultez votre solde et effectuez vos transferts en toute sécurité."*
- **Série** : 5 requêtes de préchauffage (warm-up), suivies de **200 appels HTTP POST consécutifs** mesurés par `time.perf_counter()`.
- **Langues évaluées** : Duálá (`dua`) et Ɓàsàa (`bas`).

### 3.2 Résultats statistiques réels (200 appels par langue)

| Métrique de latence | Duálá (`dua`) | Ɓàsàa (`bas`) | Seuil exigé |
|---|:---:|:---:|:---:|
| **Médiane ($P_{50}$)** | **15,99 ms** | **16,21 ms** | $< 50\text{ ms}$ |
| **95ᵉ percentile ($P_{95}$)** | **25,42 ms** | **25,54 ms** | $< 100\text{ ms}$ |
| **90ᵉ percentile ($P_{90}$)** | **22,23 ms** | **21,38 ms** | — |
| **99ᵉ percentile ($P_{99}$)** | **26,61 ms** | **27,46 ms** | — |
| **Minimum** | **1,91 ms** | **2,21 ms** | — |
| **Maximum** | **28,62 ms** | **28,13 ms** | — |
| **Moyenne** | **15,22 ms** | **15,41 ms** | — |
| **Écart-type ($\sigma$)** | 5,59 ms | 5,47 ms | — |

> **Constat** : La latence médiane du batch de 8 phrases est de **16 ms**, et **95 % des requêtes répondent en moins de 26 ms**. Le pipeline Pydantic + masquage par jetons + mémoire de traduction offre un débit local supérieur à 60 requêtes batch / seconde.

---

## 4. Nombre de Mutations DOM et Absence de Boucle d'Observation

### 4.1 Protocole de validation
Pour s'assurer que l'extension ne déclenche pas de cascade infinie de ré-observation du DOM lorsqu'elle insère ses traductions ou ses badges, un espion de mutations (`MutationObserver` wrapper) a été injecté au niveau de la racine applicative `#app`.

Le parcours complet en 5 étapes bancaires a été déroulé séquentiellement :
- **Étape 1** : Chargement initial et traduction du tableau de bord (Solde).
- **Étape 2** : Événement dynamique de consultation des frais (mise à jour du montant `25000`, des frais `500 FCFA` et ajout d'une note de tarification).
- **Étape 3** : Événement dynamique de sélection du bénéficiaire (injection d'une carte avec le bénéficiaire `Jean-Paul Mbarga`).
- **Étape 4** : Événement dynamique d'affichage du récapitulatif (injection du bloc de conditions et avertissements).
- **Étape 5** : Événement dynamique de confirmation et reçu électronique (injection de la bannière de confirmation).

### 4.2 Relevé des mutations traitées par étape

| Étape du parcours | Nature de l'opération | Mutations observées | Batches de traitement |
|---|---|:---:|:---:|
| **Étape 1 (Solde)** | Traduction initiale de la page | **21 mutations** | 1 batch |
| **Étape 2 (Frais)** | Mise à jour dynamique frais & total | **+8 mutations** | 1 batch |
| **Étape 3 (Bénéficiaire)** | Insertion de la carte bénéficiaire | **+4 mutations** | 1 batch |
| **Étape 4 (Récapitulatif)** | Insertion du bloc récapitulatif | **+4 mutations** | 1 batch |
| **Étape 5 (Reçu)** | Insertion du bandeau de confirmation | **+4 mutations** | 1 batch |
| **TOTAL PARCOURS** | **5 étapes bancaires complètes** | **41 mutations** | **5 batches** |

### 4.3 Preuve d'absence de boucle infinie d'observation (Test de convergence)
- **Mesure de stabilisation** : Après achèvement des 5 étapes, le système a été laissé au repos sans interaction pendant 2 000 ms.
- **Mutations observées entre $t = 1\text{ s}$ et $t = 2\text{ s}$** : **0 mutation résiduelle**.
- **Mécanismes de verrouillage garantissant cette convergence** :
  1. **Attribut de verrouillage** : Les éléments traduits reçoivent `data-safinum-translated="true"`, et les badges `data-safinum-ignore="true"`.
  2. **Drapeaux atomiques internes** : `state.isMutating = true` et `state.isProcessing = true` bloquent toute récursion pendant que l'extension écrit dans le DOM.
  3. **Debounce temporel** : Temporisation de 160 ms (`clearTimeout(state.mutationTimer)`) regroupant les micro-mutations en un unique lot de traitement.
  4. **Exclusion Shadow DOM** : Toutes les mutations du widget d'accessibilité (`#safinum-accessibility-host`) sont filtrées en amont et ignorées.

---

## 5. Temps de Retour à la Langue Source (`revertToSource`)

### 5.1 Protocole de mesure
- Sur la page entièrement traduite (24 nœuds textuels modifiés), l'utilisateur active le retour au français original via le widget (clic sur le bouton de bascule `#btnToggleTranslate` ou changement de sélecteur vers `fr`).
- La fonction `revertToSource()` restaure les textes originaux mémorisés dans `node._safinum_orig`, retire les classes de surbrillance (`safinum-highlight-amount`, `safinum-highlight-security`) et supprime les badges de contenus inédits.
- Le temps d'exécution synchrone est mesuré par `performance.now()`.
- **Répétitions** : 15 itérations consécutives.

### 5.2 Résultats mesurés (15 itérations)

| Métrique | Valeur mesurée |
|---|:---:|
| **Médiane ($P_{50}$)** | **0,80 ms** |
| **95ᵉ percentile ($P_{95}$)** | **1,00 ms** |
| **Minimum** | **0,60 ms** |
| **Maximum** | **1,20 ms** |
| **Moyenne** | **0,81 ms** |
| **Éléments restaurés** | **24 nœuds textuels + placeholders** |

> **Constat** : La restauration du texte original est **quasi instantanée (< 1 ms en médiane)** car elle s'effectue en mémoire DOM locale sans aucun appel réseau ni parsing complexe.

---

## 6. Périmètre Non Mesuré (Véracité des Métriques)

Conformément à la règle de véracité du projet, les aspects suivants n'ont pas fait l'objet de mesures dans notre environnement de banc d'essai et restent explicitement qualifiés de **« non mesuré »** :

| Domaine non mesuré | Raison technique | Statut formel |
|---|---|:---:|
| **Smartphone ARM d'entrée de gamme (ex: 1 à 2 Go RAM, SoC 32-bit)** | Banc d'essai exécuté sur PC de développement (Windows 11 / Intel i7 / 32 Go RAM). | **non mesuré** |
| **Consommation de batterie sur session prolongée** | Nécessite un profilage matériel physique sur terminal mobile réel. | **non mesuré** |
| **Débit réel sur réseau 2G/EDGE en milieu rural camerounais** | Le banc d'essai teste le réseau local (`127.0.0.1`) et le mode hors-ligne embarqué (0 requête réseau). | **non mesuré** |
| **Taux d'intelligibilité auprès de populations rurales analphabètes** | Nécessite une campagne d'évaluation terrain post-challenge avec animateurs linguistiques. | **non mesuré** |
| **Lecteurs d'écran physiques réels (NVDA, Windows Narrator, JAWS)** | L'accessibilité est validée par `axe-core` et assertions Playwright ; aucun testeur humain appareillé n'a été déployé. | **non mesuré** |
