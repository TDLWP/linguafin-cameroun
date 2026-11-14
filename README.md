# SAFINUM 2026 — Couche d'Accessibilité Linguistique pour Services Financiers

> **Challenge** : SAFINUM Innovate Challenge 2026  
> **Date limite de soumission** : Samedi 14 novembre 2026, 23h59 (Cameroun)  
> **Cible de test** : `https://safinum.cm/hackathon-test` (Safinum Pay)  
> **Langue pilote** : Duálá (`dua`) — **Langue secondaire** : Ɓàsàa (`bas`)  
> **Statut linguistique** : **0 / 84 chaînes validées par un locuteur natif** (100 % statut `machine_suggested`).  
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
5. **Validation par le Panneau Jury** : Avec `?jury=1`, la fonction de normalisation du jury affiche **OK (0 compromission)** sur l'intégralité du parcours.
6. **Mode hors ligne (sans réseau)** : Coupez la connexion Internet ou arrêtez le backend : l'extension bascule automatiquement sur `catalogue_offline.json` sans interruption de service.

---

## 3. Résultats Mesurés & Métriques Réelles

| Métrique | Valeur Réelle Mesurée | Statut / Méthode |
|---|---|---|
| **Validation par locuteur natif** | **0 / 84 chaînes (0,0 %)** | Aucune validation humaine acquise à date |
| **Recoupement lexical Duálá (`dua`)** | **0 / 84 attesté (0,0 %)** | `scripts/crosscheck_lexiques.py` (colonne traduction Mélac) |
| **Recoupement lexical Ɓàsàa (`bas`)** | **4 / 84 attesté (4,8 %)**, 58 partiels (69,0 %) | `scripts/crosscheck_lexiques.py` sur 994 mots réels |
| **Recoupement lexical combiné** | **4 / 168 attesté (2,4 %)**, 58 partiels (34,5 %) | `catalogue/crosscheck_rapport.csv` |
| **Tests unitaires & adversariaux** | **80 / 80 tests réussis (0 échec)** | `unittest discover backend/tests` + tests E2E |
| **Tests d'intégrité jury (`normalizeValue`)** | **8 / 8 vérifications conformes** | `tests/test_jury_integrity.py` |
| **Temps d'exécution regex (anti-ReDoS)** | **< 0,01 ms** sur chaîne piège | Benchmark `time.time()` |
| **Empreinte de l'extension client** | **< 80 Ko** (zéro dépendance externe) | Mesuré sur dossier `extension/` |
| **Temps de bascule hors ligne** | **Instantané** (mémoire cache) | Mesuré via mock bank Playwright |
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
