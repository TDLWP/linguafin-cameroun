# Rapport de Tests de Bout en Bout — SAFINUM 2026

> **Date d'exécution** : 14 novembre 2026  
> **Cible réelle** : `https://safinum.cm/hackathon-test` (Safinum Pay) & [`tests/mock_bank.html`](file:///C:/Users/FLEX%20ZONE/Models_Langues/tests/mock_bank.html)  
> **Navigateur utilisé** : Microsoft Edge 157 (Chromium) sous Windows 11  
> **Extension** : Manifest V3 avec Widget Shadow DOM et moteur d'intégrité financière

---

## 1. Synthèse Globale des Résultats d'Exécution

| Écran / Scénario | Statut | Captures d'Écran (Avant / Après) | Entités Financières Contrôlées | Retour Source (FR) |
|---|---|---|---|---|
| **Écran 1 : Solde (Tableau de bord)** | **CONFORME** (avec note) | [FR](screens/01_step1_solde_fr.png) / [Dua](screens/01_step1_solde_dua.png) | Solde `250 000 FCFA`, Compte `CM 001 2345 6789 01`, Tx `05 nov. 2026` | ✅ Instantané |
| **Écran 2 : Frais de transfert** | **CONFORME** (avec note) | [FR](screens/02_step2_frais_fr.png) / [Dua](screens/02_step2_frais_dua.png) | Montant saisi `25000`, Frais `0 FCFA`, Total `25 000 FCFA` | ✅ Instantané |
| **Écran 3 : Bénéficiaire & Sécurité** | **PASS** | [FR](screens/03_step3_beneficiaire_fr.png) / [Dua](screens/03_step3_beneficiaire_dua.png) | Bénéficiaire `Jean-Paul Mbarga`, Tél `+237 6 99 12 34 56` | ✅ Instantané |
| **Écran 4 : Récapitulatif** | **CONFORME** (avec note) | [FR](screens/04_step4_recapitulatif_fr.png) / [Dua](screens/04_step4_recapitulatif_dua.png) | Réf `SAF-2026-GOUNQP`, Total `25 000 FCFA`, Destinataire `Jean-Paul Mbarga` | ✅ Instantané |
| **Écran 5 : Reçu / Confirmation** | **CONFORME** (avec note) | [FR](screens/05_step5_recu_fr.png) / [Dua](screens/05_step5_recu_dua.png) | Réf définitive `SAF-2026-GOUNQP`, Statut succès | ✅ Instantané |
| **Alertes & Avertissements de Sécurité** | **PASS** | [FR](screens/06_alerte_securite_fr.png) / [Dua](screens/06_alerte_securite_dua.png) | Alerte `SECURITY_001`, titre et corps traduits | ✅ Bilingue OK |
| **Simulation Contenu Inédit (Mock Bank)** | **PASS** | [Capture](screens/09_mock_bank_novel_content.png) | Montant `45 000 FCFA` inviolé, alerte préservée | ✅ Repli conforme |

---

## 2. Déroulement Détaillé par Écran

### Écran 1 : Solde / Tableau de bord
* **Capture FR** : [`docs/screens/01_step1_solde_fr.png`](screens/01_step1_solde_fr.png)
* **Capture Duálá** : [`docs/screens/01_step1_solde_dua.png`](screens/01_step1_solde_dua.png)
* **Entités vérifiées** :
  * Solde affiché : `250 000 FCFA` présent et non altéré.
  * Numéro de compte : `CM 001 2345 6789 01` strictement intact.
  * Historique : les transactions récentes (`05 nov. 2026`, `-12 500 FCFA`, `+180 000 FCFA`) conservent dates et chiffres d'origine.
* **Libellés traduits** : `Solde disponible` ➔ `Moni mi titi`, `Numéro de compte` ➔ `Nombá ya kompiti`, `Effectuer un transfert` ➔ `Loma moni`.
* **Retour à la langue source** : Clic sur le bouton de bascule du widget Shadow DOM ➔ rétablissement instantané du texte français en mémoire sans rechargement.

### Écran 2 : Frais de transfert
* **Capture FR** : [`docs/screens/02_step2_frais_fr.png`](screens/02_step2_frais_fr.png)
* **Capture Duálá** : [`docs/screens/02_step2_frais_dua.png`](screens/02_step2_frais_dua.png)
* **Entités vérifiées** :
  * Champ montant (`input[type=number]`) : valeur saisie `25000` préservée, aucun reformatage dans l'input.
  * Frais calculés : `0 FCFA` (Compte Safinum).
  * Total à débiter : `25 000 FCFA` (calculé par Vue 3 intact).
  * Solde restant : `225 000 FCFA`.
* **Libellés traduits** : `Frais de transfert` ➔ `Mutoa ma tomba`, `Montant à envoyer` ➔ `Moni ma lomabe`, `Total à débiter` ➔ `Moni mése ma busisabe`.

### Écran 3 : Bénéficiaire & Avertissement de Sécurité
* **Capture FR** : [`docs/screens/03_step3_beneficiaire_fr.png`](screens/03_step3_beneficiaire_fr.png)
* **Capture Duálá** : [`docs/screens/03_step3_beneficiaire_dua.png`](screens/03_step3_beneficiaire_dua.png)
* **Entités vérifiées** :
  * Nom du bénéficiaire : `Jean-Paul Mbarga` préservé dans l'input text.
  * Téléphone : `+237 6 99 12 34 56` préservé dans l'input tel.
* **Avertissement de sécurité** :
  * FR : `Ce bénéficiaire n'a jamais été utilisé sur ce compte. Vérifiez le numéro avant de continuer.`
  * Duálá : `Nu nongi a si sengedi no o yé kompiti. Ombwele nombá oboso na ala oboso.`
  * Case à cocher de vérification : fonctionnelle, non bloquée.

### Écran 4 : Récapitulatif
* **Capture FR** : [`docs/screens/04_step4_recapitulatif_fr.png`](screens/04_step4_recapitulatif_fr.png)
* **Capture Duálá** : [`docs/screens/04_step4_recapitulatif_dua.png`](screens/04_step4_recapitulatif_dua.png)
* **Entités vérifiées** :
  * Référence unique générée : `SAF-2026-GOUNQP` intacte dans la balise `<dd>`.
  * Montant : `25 000 FCFA` intact.
  * Bénéficiaire : `Jean-Paul Mbarga` intact.
  * Téléphone : `+237 6 99 12 34 56` intact.
* **Libellés traduits** : `Récapitulatif` ➔ `Mbondo a tomba`, `Confirmer le transfert` ➔ `Kakisane tomba`.

### Écran 5 : Reçu / Confirmation
* **Capture FR** : [`docs/screens/05_step5_recu_fr.png`](screens/05_step5_recu_fr.png)
* **Capture Duálá** : [`docs/screens/05_step5_recu_dua.png`](screens/05_step5_recu_dua.png)
* **Entités vérifiées** :
  * Référence définitive de confirmation : `SAF-2026-GOUNQP` identique à l'étape 4.
  * Statut : succès de la transaction.
* **Libellés traduits** : `Transfert effectué` ➔ `Moni mi lomi na bwam`, `Votre transfert a été envoyé avec succès.` ➔ `Moni mongó mi lomi bwambwam.`.

### Alertes & Avertissements de Sécurité
* **Capture FR** : [`docs/screens/06_alerte_securite_fr.png`](screens/06_alerte_securite_fr.png)
* **Capture Duálá** : [`docs/screens/06_alerte_securite_dua.png`](screens/06_alerte_securite_dua.png)
* **Résultat** : L'alerte critique `SECURITY_001` est traduite tout en conservant l'encart d'avertissement et la conformité bilingue.

---

## 3. Simulation de Contenu Inédit sur `tests/mock_bank.html`

* **Capture** : [`docs/screens/09_mock_bank_novel_content.png`](screens/09_mock_bank_novel_content.png)
* **Phrase inédite injectée** :
  > *"Alerte de sécurité : une tentative de prélèvement inédite de 45 000 FCFA a été détectée sur votre compte."*
* **Observations constatées** :
  1. **Préservation du montant financier** : La valeur `45 000 FCFA` est **strictement inviolée** dans le texte final.
  2. **Statut et repli sécurisé** : N'ayant pas de correspondance directe pré-validée dans la mémoire, le système active le repli sécurisé (`fallback_source`), conservant la phrase lisible en français sans générer de contresens dangereux.
  3. **Affichage bilingue** : L'attribut `title="Original : Alerte de sécurité..."` est présent sur le conteneur pour consultation au survol.

---

## 4. Liste Exhaustive des Bugs et Anomalies Relevés

*(Conformément à la consigne : liste seulement, aucune correction appliquée).*

### Bug #1 — Discordance d'espace insécable fine Unicode (`\u202F` vs `\x20`)
- **Composant** : Moteur de comparaison et de détection des montants.
- **Symptôme** : Le site Vue 3 utilise `Intl.NumberFormat("fr-FR")` qui sépare les milliers par une espace fine insécable (`\u202F`), ex: `"250\u202F000 FCFA"`. Les comparateurs ou regex attendant une espace ASCII standard (`\x20`) échouent à détecter la chaîne sans appliquer au préalable une normalisation NFKC (`unicodedata.normalize('NFKC', ...)`).
- **Impact** : Faux négatifs lors de tests d'assertion stricts ignorant la normalisation Unicode du jury.
- **Gravité** : **Moyenne** (n'altère pas la valeur visuelle, mais impose `normalizeValue` pour toute vérification automatisée).

### Bug #2 — Délai de bascule hors ligne lors de l'indisponibilité de l'API locale
- **Composant** : `extension/content.js` — fonction `fetchTranslationsBatch`.
- **Symptôme** : Lorsque le serveur FastAPI local est éteint, `content.js` tente successivement de contacter `http://localhost:8000` puis `http://127.0.0.1:8000` avec un timeout de 1,5 s par endpoint. Le basculement vers le catalogue embarqué prend donc ~3 secondes lors du tout premier rendu si l'API est absente.
- **Impact** : Léger retard d'affichage initial de la traduction si l'utilisateur lance la démo sans avoir démarré le backend local.
- **Gravité** : **Mineure**.

### Bug #3 — Délais de montage réactif de Vue 3 vs MutationObserver
- **Composant** : `extension/content.js` — interaction avec la SPA Vue 3 / Inertia.js.
- **Symptôme** : Lors du passage de l'étape 1 à l'étape 2, Vue 3 démonte et recrée les éléments du DOM en plusieurs micro-tâches réactives. Si l'anti-rebond du `MutationObserver` est inférieur à 150 ms, le content script risque de s'exécuter sur un DOM intermédiaire avant que Vue 3 n'ait fini d'injecter les valeurs calculées (`0 FCFA`, `25 000 FCFA`).
- **Impact** : Nécessite un debounce d'au moins 160 ms pour garantir la capture de l'arbre final.
- **Gravité** : **Faible**.

### Bug #4 — Exclusion des mutations internes au Shadow DOM
- **Composant** : `extension/content.js` — écouteur `MutationObserver`.
- **Symptôme** : Lors de la mise à jour des statistiques internes du widget (`statHuman`, `statMachine`), des mutations DOM surviennent dans le document. Si l'observateur ne filtre pas les cibles enfants de `#safinum-accessibility-host`, un risque de cycle de ré-observation superflu peut se produire.
- **Impact** : Consommation CPU évitable lors de mises à jour fréquentes des compteurs.
- **Gravité** : **Faible**.
