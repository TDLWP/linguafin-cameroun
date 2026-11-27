> **Versions du dépôt** :
> - **Tag `v1.0-soumission-14nov`** : Version officielle soumise au SAFINUM Innovate Challenge le 14 novembre 2026 (23h59).
> - **Branche `main`** : Version de base de la soumission, incluant le correctif immédiat post-envoi (suppression des crochets bilingues autour des montants purs).
> - **Branche `amelioration` (Travaux v2.0)** : Travaux d'amélioration continue, d'accessibilité et de durcissement menés après la soumission (ne faisant pas partie de la soumission initiale) :
>   - **Garantie d'intégrité jury** : 0 compromis sur 100 % du parcours bancaire officiel et sur les contenus inédits injectés.
>   - **Bilinguisme source EN / FR** : Détection et normalisation des segments bancaires anglophones (`data/en_to_fr_index.json`).
>   - **Sécurité des alertes critiques** : Sanctuarisation des avertissements de sécurité en français (`ANNOTATE_SECURITY_ALERTS=false`) avec badge explicite et correction d'espacement des badges.
>   - **Audit de sécurité indépendant v2** : 0 CVE (`pip-audit`), 0 secret dans l'historique Git, permissions minimales Manifest V3, éradication d'`innerHTML`/`eval` dans l'extension, rate limiting en mémoire et anonymisation des logs.
>   - **Accessibilité Shadow DOM mesurée (WCAG AA)** : Navigation clavier complète, piège de focus, contrastes ≥ 4,5:1, cibles tactiles ≥ 44 px, support mobile 360 px, zoom 200 % et `prefers-reduced-motion`.
>   - **Métriques de performance réelles** : Premier rendu traduit mesuré à 224 ms (online) / 234 ms (offline), latence batch de 16 ms, absence de boucle DOM prouvée ([`docs/mesures_performance.md`](docs/mesures_performance.md)).
>   - **Alignement de contrat OpenAPI** : Tests automatisés `openapi.yaml` vs API FastAPI (`backend/tests/test_openapi_contract.py`).
>   - **Kit de validation linguistique natif** : Fiches PDF/CSV prêtes pour la relecture humaine, guide du validateur ([`catalogue/kit_validation/GUIDE_VALIDATEUR.md`](catalogue/kit_validation/GUIDE_VALIDATEUR.md)) et modèles de sollicitation ([`docs/modeles_messages_validateurs.md`](docs/modeles_messages_validateurs.md)).
>   - **Architecture Service Worker MV3 & Sécurité Réseau Stricte** : Relais réseau isolé via `background.js` avec `host_permissions` ciblées (`127.0.0.1:8000` et `localhost:8000`), respectant les normes W3C Private Network Access et Mixed Content sans aucun affaiblissement de la sécurité du navigateur (zéro option de contournement `--disable-web-security`).
>   - **Automatisation & Packaging v2** : Scripts `lancer_demo.ps1`, `run_all_checks.ps1` (192 tests passants, 0 échec) et `package_release.py` (archives officielles `dist/` certifiées anti-secrets).

# SAFINUM 2026 — Couche d'Accessibilité Linguistique pour Services Financiers

> **Challenge** : SAFINUM Innovate Challenge 2026  
> **Date limite de soumission** : Samedi 14 novembre 2026, 23h59 (Cameroun)  
> **Cible de test** : `https://safinum.cm/hackathon-test` (Safinum Pay)  
> **Langue pilote** : Duálá (`dua`) — **Langue secondaire** : Ɓàsàa (`bas`)  
> **Statut linguistique** : **0 / 84 chaînes validées par un locuteur natif** (100 % statut `machine_suggested` ; 84 segments dans les fiches CSV / `translations.csv`, 83 chaînes sources françaises uniques dans le dictionnaire JSON `offline_catalog.json` suite à l'homonyme « Sécurité »).  
> **Méthode** : Brouillon IA + Recoupement lexical (Mélac) + Garde-fou d'intégrité financière. Validation native planifiée avant la finale (26-28 nov.) via `catalogue/fiche_validation.csv`.

---

## 1. Installation et Lancement Rapide sous Windows (6 Commandes)

Ouvrez un terminal **PowerShell** sous Windows 11 et exécutez la séquence suivante :

```powershell
# 1. Se positionner dans le répertoire du projet
cd "C:\Users\FLEX ZONE\Models_Langues"

# 2. Installer les dépendances Python du backend local (FastAPI, Uvicorn, Pydantic)
python -m pip install -r backend/requirements.txt

# 3. Vérifier l'intégrité financière et exécuter la suite de tests unitaires (80 tests)
python -m unittest discover backend/tests; python -m unittest tests/test_jury_integrity.py tests/test_extension_e2e.py

# 4. Lancer le backend local souverain en arrière-plan sur le port 8000
Start-Process python -ArgumentList "-m uvicorn backend.api:app --host 127.0.0.1 --port 8000"

# 5. Ouvrir la page de gestion des extensions dans Microsoft Edge (ou Chrome)
Start-Process msedge "edge://extensions"

# 6. Ouvrir l'environnement bancaire cible avec le panneau jury activé
Start-Process msedge "https://safinum.cm/hackathon-test?jury=1"
```

### Chargement de l'Extension dans le Navigateur (30 secondes)
1. Dans la page `edge://extensions` (ou `chrome://extensions`), activez le curseur **Mode développeur** (en bas à gauche sous Edge, en haut à droite sous Chrome).
2. Cliquez sur le bouton **Charger les composants décompressés** (*Load unpacked*).
3. Sélectionnez le sous-dossier : `C:\Users\FLEX ZONE\Models_Langues\extension`.
4. L'extension *SAFINUM Accessibility — Couche Linguistique Nationale* est immédiatement active.

### Scripts d'Automatisation & Packaging v2
Pour simplifier l'évaluation, trois scripts prêts à l'emploi sont mis à disposition :

* **`powershell -ExecutionPolicy Bypass -File scripts/lancer_demo.ps1`** :
  Démarre le backend souverain FastAPI (port 8000), attend que `/health` réponde, et ouvre automatiquement Microsoft Edge avec l'extension préchargée via un profil temporaire isolé sur `https://safinum.cm/hackathon-test?jury=1` (avec repli local automatique sur `tests/mock_bank.html` si le réseau distant est indisponible).

* **`powershell -ExecutionPolicy Bypass -File scripts/run_all_checks.ps1`** :
  Exécute séquentiellement l'intégralité des 5 suites de tests de validation (backend unitaire & sécurité v2, intégrité jury & maquette Playwright, accessibilité WCAG Shadow DOM, performances & latence, régression jury live avec skip propre si réseau indisponible) et affiche un tableau récapitulatif détaillé.

* **`python scripts/package_release.py`** :
  Génère les archives officielles de distribution dans `dist/` :
  - `dist/extension_linguafin_v2.zip` : extension décompressable avec `manifest.json` à la racine (prête pour les stores ou le chargement navigateur).
  - `dist/linguafin_v2_source.zip` : code source complet avec exclusions strictes (modèles lourds, `.env`, `.git`, `__pycache__`), scan anti-secrets (0 token hf_/sk-/api_key), contrôle de taille et décompression test en sandbox.

---

## 2. Parcours de Démonstration Reproductible

1. **Activation du widget** : Rendez-vous sur `https://safinum.cm/hackathon-test?jury=1`. Un widget flottant encapsulé en Shadow DOM apparaît en bas à droite : `🇨🇲 Langue : Duálá`.
2. **Transparence IA permanente** : Le volet affiche le bandeau `« ⚠️ Traductions générées par IA, non validées par un locuteur natif. »`.
3. **Bascule linguistique** : Sélectionnez **Duálá** ou **Ɓàsàa**, ou revenez instantanément au **Français** sans recharger la page.
4. **Contrôle d'intégrité financière** :
   - **Étape 1 (Solde)** : Le solde disponible `250 000 FCFA` et le compte `CM 001 2345 6789 01` sont intacts.
   - **Étape 2 (Frais)** : Saisissez `25000` ; les frais `0 FCFA` et le total `25 000 FCFA` restent stricts et non altérés.
   - **Étape 3 (Bénéficiaire)** : Le nom `Jean-Paul Mbarga` et le téléphone `+237 6 99 12 34 56` sont préservés.
   - **Étape 4 (Récapitulatif)** : La référence `SAF-2026-*` et les montants sont strictement conservés ; affichage bilingue parallèle sans substitution (`Texte source [Proposition]`).
   - **Étape 5 (Confirmation)** : Le reçu de transfert confirme l'opération.
5. **Validation par le Panneau Jury** : Avec `?jury=1`, le contrôle d'intégrité du jury enregistre **100 % Intègre (0 compromis sur les 9 soumissions du parcours)** en mode hors-ligne nominal (catalogue embarqué) comme sur la page native et en mode connecté, grâce à la neutralisation des faux différentiels d'espace insécable (`\u202F`) et à l'interdiction de crochets bilingues sur les montants purs.
6. **Mode hors ligne (sans réseau)** : Coupez la connexion Internet ou arrêtez le backend : l'extension bascule automatiquement sur `offline_catalog.json` sans interruption de service.

---

## 3. Résultats Mesurés & Métriques Réelles

| Métrique | Valeur Réelle Mesurée | Statut / Méthode |
|---|---|---|
| **Validation par locuteur natif** | **0 / 84 chaînes (0,0 %)** | Aucune validation humaine acquise à date (84 entrées CSV / 83 chaînes sources uniques dans `offline_catalog.json`) |
| **Recoupement lexical Duálá (`dua`)** | **0 / 84 attesté (0,0 %)** | `scripts/crosscheck_lexiques.py` (colonne traduction Mélac) |
| **Recoupement lexical Ɓàsàa (`bas`)** | **4 / 84 attesté (4,8 %)**, 58 partiels (69,0 %) | `scripts/crosscheck_lexiques.py` sur 994 mots réels |
| **Recoupement lexical combiné** | **4 / 168 attesté (2,4 %)**, 58 partiels (34,5 %) | `catalogue/crosscheck_rapport.csv` |
| **Tests unitaires & adversariaux** | **83 / 83 tests réussis (0 échec)** | 77 tests backend + 6 tests racine (`unittest discover`) |
| **Tests d'intégrité jury (`normalizeValue`)** | **8 / 8 vérifications conformes** | `tests/test_jury_integrity.py` |
| **Temps d'exécution regex (anti-ReDoS)** | **< 0,01 ms** sur chaîne piège | Benchmark `time.time()` |
| **Empreinte de l'extension client** | **121 590 octets (118,74 Ko)** (zéro dépendance externe) | Somme exacte des 4 fichiers du dossier `extension/` (`background.js`, `content.js`, `manifest.json`, `offline_catalog.json`) |
| **Temps de bascule hors ligne** | **Instantané** (mémoire cache) | Mesuré via mock bank Playwright |
| **Premier rendu traduit (offline / online)** | **79 ms** (offline) / **77 ms** (online) | Médiane 12 runs — [`docs/mesures_performance.md`](docs/mesures_performance.md) |
| **Latence `/translate/batch` (local)** | **16 ms** (médiane), **25 ms** (P95) | 200 appels batch — [`docs/mesures_performance.md`](docs/mesures_performance.md) |
| **Temps de retour langue source** | **0,8 ms** (médiane sur 15 itérations) | `performance.now()` — [`docs/mesures_performance.md`](docs/mesures_performance.md) |
| **Consommation mémoire sur smartphone bas de gamme** | **Non mesuré** | Environnement de banc d'essai PC (Win 11) |
| **Taux de rétention usagers ruraux en conditions réelles** | **Non mesuré** | Expérimentation terrain post-challenge requise |

---

## 4. Documentation des Livrables

* **Livrable 1 — Description de la solution** : [`docs/description_solution.md`](docs/description_solution.md)
* **Livrable 2 — Démo reproductible & README** : [`README.md`](README.md)
* **Livrable 3 — Script vidéo chronométré (≤ 3 min)** : [`docs/script_video.md`](docs/script_video.md)
* **Livrable 4 — Note technique d'architecture** : [`docs/note_technique.md`](docs/note_technique.md)
* **Livrable 5 — Langues et validation linguistique** : [`docs/langue_et_validation.md`](docs/langue_et_validation.md)
* **Registre des composants tiers & modèles d'IA** : [`THIRD_PARTY.md`](THIRD_PARTY.md)
* **Rapport de vérification croisée lexicale** : [`catalogue/crosscheck_rapport.csv`](catalogue/crosscheck_rapport.csv)
* **Rapport d'audit hostile & Red Team** : [`docs/03_audit.md`](docs/03_audit.md)
