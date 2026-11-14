# Audit Technique et Cartographie de l'Environnement de Test SAFINUM 2026

> **Cible** : `https://safinum.cm/hackathon-test`  
> **Date de l'audit** : 13 novembre 2026  
> **Méthode** : Navigation réelle sans modification via navigateur automatisé (Chromium/Edge headless), capture intégrale des flux réseau, analyse du bundle Vue 3 / Inertia.js décompilé et extraction directe des nœuds DOM textuels.  
> **Intégrité** : Aucune donnée modifiée sur le site cible, aucune sécurité contournée.

---

## 1. Parcours Utilisateur Disponible & Captures d'Écran

L'environnement de test simule un parcours bancaire complet de **Mobile Money / Banque en ligne** nommé **Safinum Pay**. Le parcours est structuré en **5 étapes séquentielles** avec gestion d'alertes de sécurité, validation stricte et panneau d'évaluation (Jury).

Toutes les captures d'écran pleine page ont été enregistrées dans [`docs/screens/`](file:///C:/Users/FLEX%20ZONE/Models_Langues/docs/screens/) :

| Étape | Rôle fonctionnel | Capture FR | Capture EN |
|---|---|---|---|
| **Étape 1 : Solde / Tableau de bord** | Consultation du solde disponible, numéro de compte, historique des 4 dernières transactions | [`01_dashboard_fr.png`](file:///C:/Users/FLEX%20ZONE/Models_Langues/docs/screens/01_dashboard_fr.png) | [`01_dashboard_en.png`](file:///C:/Users/FLEX%20ZONE/Models_Langues/docs/screens/01_dashboard_en.png) |
| **Étape 2 : Frais de transfert** | Choix du type d'opération (Safinum, Mobile Money, Autre banque), saisie du montant, calcul instantané des frais et solde restant | [`02_frais_fr.png`](file:///C:/Users/FLEX%20ZONE/Models_Langues/docs/screens/02_frais_fr.png) | [`02_frais_en.png`](file:///C:/Users/FLEX%20ZONE/Models_Langues/docs/screens/02_frais_en.png) |
| **Étape 3 : Bénéficiaire** | Saisie destinataire (nom, téléphone, motif, note) + avertissement de sécurité sur nouveau bénéficiaire + case de vérification obligatoire | [`03_beneficiaire_fr.png`](file:///C:/Users/FLEX%20ZONE/Models_Langues/docs/screens/03_beneficiaire_fr.png) | [`03_beneficiaire_en.png`](file:///C:/Users/FLEX%20ZONE/Models_Langues/docs/screens/03_beneficiaire_en.png) |
| **Étape 4 : Récapitulatif** | Tableau récapitulatif complet (montant, frais, total débité, bénéficiaire, téléphone, référence, type d'opération) + case d'engagement | [`04_recapitulatif_fr.png`](file:///C:/Users/FLEX%20ZONE/Models_Langues/docs/screens/04_recapitulatif_fr.png) | [`04_recapitulatif_en.png`](file:///C:/Users/FLEX%20ZONE/Models_Langues/docs/screens/04_recapitulatif_en.png) |
| **Étape 5 : Reçu / Confirmation** | Notification de succès, référence définitive générée (`SAF-2026-XXXXXX`), détails de transaction, bouton nouveau transfert | [`05_recu_fr.png`](file:///C:/Users/FLEX%20ZONE/Models_Langues/docs/screens/05_recu_fr.png) | [`05_recu_en.png`](file:///C:/Users/FLEX%20ZONE/Models_Langues/docs/screens/05_recu_en.png) |
| **Alertes d'Erreur & Sécurité** | Bannières d'alerte contextuelles (Solde insuffisant, Alerte sécurité nouveau tiers, Erreur réseau) | [`06_erreur_solde_insuffisant.png`](file:///C:/Users/FLEX%20ZONE/Models_Langues/docs/screens/06_erreur_solde_insuffisant.png)<br>[`06_alerte_securite.png`](file:///C:/Users/FLEX%20ZONE/Models_Langues/docs/screens/06_alerte_securite.png)<br>[`06_erreur_reseau.png`](file:///C:/Users/FLEX%20ZONE/Models_Langues/docs/screens/06_erreur_reseau.png) | — |
| **Panneau Jury (`?jury=1`)** | Outil d'évaluation interne Safinum : injection de contenu inédit, simulation d'alertes, calcul de couverture et détection d'intégrité compromise | [`07_jury_panel.png`](file:///C:/Users/FLEX%20ZONE/Models_Langues/docs/screens/07_jury_panel.png) | — |

---

## 2. Structure Technique du DOM

- **Architecture applicative** : **Single Page Application (SPA)** propulsée par **Inertia.js v2** avec **Vue 3** (Composition API, `script setup`, compilée avec Vite). Le backend serveur est Laravel.
- **Point de montage DOM** : `<div id="app" data-page="..."></div>`. Le HTML initial servi par le serveur contient les métadonnées JSON dans l'attribut `data-page`, puis le bundle JavaScript (`app-AI8e1_sa.js` + `HackathonTest-Dzv3A9Ti.js`) monte l'interface dynamiquement dans `#app`.
- **Pages multiples vs SPA** : Il s'agit d'une SPA stricte pour le simulateur. La transition entre les étapes 1, 2, 3, 4 et 5 s'opère par mutation d'état réactif (`state.step`) sans rechargement de page (`window.location` ne change pas).
- **Rendu du texte** : 100 % du texte est présent sous forme de **nœuds textuels natifs du DOM** (`Node.TEXT_NODE`). **Aucun texte n'est rendu dans un `<canvas>` ni encapsulé dans des images bitmap**.
- **Icônes** : Icônes vectorielles SVG injectées via la bibliothèque `lucide-vue-next` (icônes décoratives, sans texte intérieur altérable).
- **Shadow DOM sur le site cible** : **Aucun Shadow DOM** n'est employé par le site cible.
- **iframes** : **Aucune iframe** dans la page de test.
- **Dynamisme et réactivité** :
  - Les montants, frais et totaux sont recalculés à la volée lors de la frappe dans l'input `amount` ou du changement du `select` d'opération.
  - Le basculement de langue (FR <-> EN) s'opère instantanément par mise à jour de la variable réactive `state.lang`, modifiant tous les libellés sans rafraîchissement réseau.
  - Du contenu imprévu peut être injecté à l'exécution dans le conteneur `#injected-{id}` via le panneau jury.

---

## 3. Liste Exhaustive des Écrans, Chaînes Visibles & Rendu des Entités Financières

### Règle d'or de détection des données financières (Critique)

Dans le code source de test (`HackathonTest-Dzv3A9Ti.js`), le module de vérification du Jury utilise une fonction de normalisation stricte :
```javascript
function normalizeValue(val) {
  return String(val ?? "").normalize("NFKC")
    .replace(/fcfa/gi, "")
    .replace(/[\s\u00A0\u202F,.'’]+/g, "")
    .trim().toLowerCase();
}
```
Si une extension modifie ne serait-ce qu'un chiffre, une virgule d'un montant, le nom d'un bénéficiaire ou le code d'une référence, le jury enregistre un écart (`diff`) et classe la soumission comme **`compromised`** (défaut majeur).

---

### Écran 1 : Solde / Tableau de bord (Step 1)

#### Chaînes visibles (FR / EN) :
- `Safinum Pay` / `Safinum Pay` (Marque)
- `Banque en ligne` / `Online banking`
- `Environnement de test — données fictives, aucune transaction réelle.` / `Test environment — fictional data, no real transaction.`
- `Protocole de test` / `Test protocol`
- `Retour au hackathon` / `Back to hackathon`
- `Solde` / `Balance`
- `Frais` / `Fees`
- `Bénéficiaire` / `Beneficiary`
- `Récapitulatif` / `Summary`
- `Confirmation` / `Confirmation`
- `Votre compte` / `Your account`
- `Bonjour, Amina` / `Hello, Amina`
- `Consultez votre solde et lancez un transfert en toute sécurité.` / `Check your balance and start a secure transfer.`
- `Solde disponible` / `Available balance`
- `Numéro de compte` / `Account number`
- `Compte courant` / `Current account`
- `Effectuer un transfert` / `Make a transfer`
- `Consulter les frais` / `View fees`
- `Transactions récentes` / `Recent transactions`
- `Paiement marchand` / `Merchant payment`
- `Salaire reçu` / `Salary received`
- `Transfert reçu` / `Transfer received`
- `Facture électricité` / `Electricity bill`
- Dates de transactions : `05 nov. 2026` (`Nov 5, 2026`), `04 nov. 2026` (`Nov 4, 2026`), `02 nov. 2026` (`Nov 2, 2026`), `31 oct. 2026` (`Oct 31, 2026`)
- Bloc latéral sécurité : `Sécurité` / `Security`, `Vérifiez toujours le nom et le numéro du bénéficiaire avant de confirmer un transfert.` / `Always verify the beneficiary name and number before confirming a transfer.`, `Connexion sécurisée` / `Secure connection`
- Pied de page : `Safinum Pay — environnement de démonstration. Ne saisissez aucune donnée personnelle réelle.` / `Safinum Pay — demonstration environment. Do not enter real personal data.`

#### Rendu des entités sensibles :
- **Solde principal** :
  - Balise : `<p ref="balanceTextRef" class="mt-2 text-3xl font-extrabold">250 000 FCFA</p>`
  - Formatage : `Intl.NumberFormat("fr-FR")` avec espace insécable (`\u202F` ou espace classique) + suffixe ` FCFA`.
- **Numéro de compte** :
  - Balise : `<span>Numéro de compte : CM 001 2345 6789 01</span>`
  - Format : `CM` suivi de 14 chiffres groupés en `3 4 4 2`.
- **Montants des transactions récentes** :
  - Balise : `<p class="text-sm font-bold text-slate-700 dark:text-white/70">-12 500 FCFA</p>` et `<p class="text-sm font-bold text-emerald-500">+180 000 FCFA</p>`

---

### Écran 2 : Frais de transfert (Step 2)

#### Chaînes visibles (FR / EN) :
- `Frais de transfert` / `Transfer fees`
- `Choisissez le type de transfert et le montant. Les frais sont calculés automatiquement.` / `Choose the transfer type and amount. Fees are calculated automatically.`
- `Type d'opération` / `Operation type`
- `Compte Safinum` / `Safinum account` — note : `Transfert instantané et gratuit` / `Instant, free transfer`
- `Mobile Money` / `Mobile Money` — note : `Frais de 1,5 % (min. 100 FCFA, max. 2 500 FCFA)` / `1.5% fee (min. 100 FCFA, max. 2,500 FCFA)`
- `Autre banque` / `Other bank` — note : `Frais de 2 % (min. 200 FCFA, max. 5 000 FCFA)` / `2% fee (min. 200 FCFA, max. 5,000 FCFA)`
- `Montant à envoyer` / `Amount to send`
- `Frais` / `Fee`
- `Gratuit` / `Free` (badge affiché si frais = 0)
- `Total à débiter` / `Total to debit`
- `Solde après opération` / `Balance after transfer`
- `Retour` / `Back`
- `Continuer` / `Continue`

#### Rendu des entités sensibles :
- **Champ de saisie montant** :
  - Balise : `<input ref="amountInputRef" type="number" min="0" step="500" class="w-full ... text-lg font-bold" />`
  - Suffixe visuel en span absolu : `<span class="absolute right-4 top-1/2 ...">FCFA</span>`
- **Frais affichés** :
  - Balise : `<span ref="feeTextRef" class="font-bold">0 FCFA</span>` (ou montant calculé selon règles)
- **Total à débiter** :
  - Balise : `<span ref="totalTextRef" class="text-lg font-extrabold">25 000 FCFA</span>`
- **Solde après opération** :
  - Balise : `<span>225 000 FCFA</span>`

---

### Écran 3 : Bénéficiaire (Step 3)

#### Chaînes visibles (FR / EN) :
- `Bénéficiaire` / `Beneficiary`
- `Renseignez les informations du destinataire. Vérifiez toujours le numéro avant de valider.` / `Enter the recipient details. Always verify the number before confirming.`
- Bannière d'avertissement : `Ce bénéficiaire n'a jamais été utilisé sur ce compte. Vérifiez le numéro avant de continuer.` / `This beneficiary has never been used on this account. Verify the number before continuing.`
- `Nom du bénéficiaire` / `Beneficiary name`
- `Numéro de téléphone` / `Phone number`
- `Motif du transfert` / `Transfer reason`
- `Paiement de services` / `Payment for services` (valeur par défaut)
- `Note (optionnel)` / `Note (optional)`
- Case à cocher de sécurité : `J'ai vérifié le nom et le numéro du bénéficiaire.` / `I have verified the beneficiary name and phone number.`
- `Retour` / `Back`
- `Continuer` / `Continue`

#### Rendu des entités sensibles :
- **Nom du bénéficiaire** : `<input ref="beneficiaryInputRef" type="text" value="Jean-Paul Mbarga" />`
- **Téléphone du bénéficiaire** : `<input ref="phoneInputRef" type="tel" value="+237 6 99 12 34 56" />`
- **Case à cocher** : `<input ref="verifiedInputRef" type="checkbox" />`

---

### Écran 4 : Récapitulatif & Validation (Step 4)

#### Chaînes visibles (FR / EN) :
- `Récapitulatif` / `Summary`
- `Vérifiez les informations avant de confirmer le transfert.` / `Check the details before confirming the transfer.`
- `Montant` / `Amount`
- `Frais` / `Fee`
- `Total débité` / `Total debited`
- `Bénéficiaire` / `Beneficiary`
- `Téléphone` / `Phone`
- `Référence` / `Reference`
- `Opération` / `Operation`
- Case à cocher finale : `Je confirme que les informations ci-dessus sont correctes.` / `I confirm the information above is correct.`
- Boutons : `Modifier` / `Edit`, `Confirmer le transfert` / `Confirm transfer`

#### Rendu des entités sensibles :
- Structure : Définition en liste de description `<dl class="divide-y ...">`
- `Montant` : `<dd ref="summaryAmountRef" class="text-sm font-bold">25 000 FCFA</dd>`
- `Frais` : `<dd ref="summaryFeeRef" class="text-sm font-bold">0 FCFA</dd>`
- `Total débité` : `<dd ref="summaryTotalRef" class="text-base font-extrabold text-[#00BFFF]">25 000 FCFA</dd>`
- `Bénéficiaire` : `<dd ref="summaryBeneficiaryRef" class="text-sm font-bold">Jean-Paul Mbarga</dd>`
- `Téléphone` : `<dd ref="summaryPhoneRef" class="text-sm font-bold">+237 6 99 12 34 56</dd>`
- `Référence` : `<dd ref="summaryReferenceRef" class="font-mono text-sm font-bold">SAF-2026-X7Y8Z9</dd>`
- `Opération` : `<dd class="text-sm font-bold">Compte Safinum</dd>`

---

### Écran 5 : Reçu / Confirmation finale (Step 5)

#### Chaînes visibles (FR / EN) :
- `Transfert effectué` / `Transfer completed`
- `Votre transfert a été envoyé avec succès.` / `Your transfer has been sent successfully.`
- `Référence` / `Reference`
- `Montant` / `Amount`
- `Frais` / `Fee`
- `Total débité` / `Total debited`
- `Bénéficiaire` / `Beneficiary`
- `Statut` / `Status`
- `Succès` / `Success`
- Bouton : `Nouveau transfert` / `New transfer`

#### Rendu des entités sensibles :
- Rendu identique en `<dl>` reprenant les références ref : `receiptReferenceRef`, `receiptAmountRef`, `receiptFeeRef`, `receiptTotalRef`, `receiptBeneficiaryRef`.

---

### Alertes & Messages d'Erreur (Simulables via Panneau Jury)

- `AMOUNT_001` : `Le montant doit être supérieur à zéro.` / `The amount must be greater than zero.`
- `AMOUNT_002` : `Solde insuffisant pour effectuer ce transfert.` / `Insufficient balance for this transfer.`
- `BENEFICIARY_001` : `Veuillez renseigner le nom et le numéro du bénéficiaire.` / `Please provide the beneficiary name and phone number.`
- `SECURITY_001` : `Alerte de sécurité : vérifiez le numéro du bénéficiaire avant de continuer.` / `Security warning: verify the beneficiary phone number before continuing.`
- `SECURITY_002` : `Alerte de sécurité : ce bénéficiaire n'a jamais été utilisé sur ce compte.` / `Security warning: this beneficiary has never been used on this account.`
- `NETWORK_001` : `Erreur réseau : le service est temporairement indisponible. Réessayez.` / `Network error: the service is temporarily unavailable. Please try again.`
- `CONFIRM_001` : `Vous devez confirmer les informations avant de valider le transfert.` / `You must confirm the details before validating the transfer.`
- En-têtes d'alertes : `Une erreur est survenue` / `An error occurred` (icône triangle rouge), `Alerte de sécurité` / `Security warning` (icône bouclier ambre), bouton `Fermer` / `Dismiss`.
- Conteneur dynamique : `#injected-{id}` portant le titre `Message important` / `Important message`.

---

## 4. Contraintes pour une Extension Navigateur Manifest V3

1. **Content-Security-Policy (CSP)** :
   - L'en-tête HTTP `Content-Security-Policy` n'est **pas défini** par le serveur sur cette page.
   - Aucune balise `<meta http-equiv="Content-Security-Policy">` n'est présente dans le `<head>`.
   - **Conséquence pour MV3** : Les scripts injectés via Content Scripts s'exécutent dans leur propre *Isolated World*. Ils n'ont pas de restriction CSP bloquante pour communiquer avec l'API locale FastAPI (`fetch('http://localhost:8000/...')`), sous réserve de déclarer `http://localhost:*` ou `http://127.0.0.1:*` dans les permissions de l'extension.

2. **Permissions Host dans `manifest.json`** :
   ```json
   "host_permissions": [
     "https://safinum.cm/hackathon-test*",
     "http://localhost:8000/*",
     "http://127.0.0.1:8000/*"
   ]
   ```

3. **Injection du Widget d'Accessibilité (Shadow DOM obligatoire)** :
   - Le site utilise Tailwind CSS v3 avec des styles globaux et des variables de couleur sombres/claires (`.dark`).
   - Pour garantir une **étanchéité totale** sans altérer le style du site ni subir ses règles CSS, le widget flottant de l'extension doit obligatoirement être encapsulé dans un **Shadow DOM fermé** (`attachShadow({ mode: 'closed' })` ou `'open'`).

4. **Observation des mutations du DOM (`MutationObserver`)** :
   - Comme l'application est une SPA Vue 3, le changement d'étape détruit et recrée des pans entiers de l'arbre DOM dans `#app`.
   - Un `MutationObserver` doit surveiller `#app` (`childList: true, subtree: true, characterData: true`) avec un anti-rebond (*debounce*) d'environ 150-250 ms pour appliquer les traductions instantanément dès l'apparition d'un nouvel écran ou d'une alerte dynamique, **sans boucle infinie**.

5. **Détection et Masquage par Jetons (Intégrité Financière)** :
   - Avant de soumettre une chaîne de caractères à la traduction (en local ou en cache), tout motif correspondant à :
     - Montants et devises (`\d+([\s\u00A0\u202F]\d{3})*\s*(FCFA|XAF)` ou `\d+`)
     - Numéros de téléphone (`\+237[\s\d]+` ou `6[5-9]\d{7}`)
     - Numéros de compte (`CM\s*\d{3}\s*\d{4}\s*\d{4}\s*\d{2}`)
     - Références (`SAF-2026-[A-Z0-9]+`)
     - Noms propres de bénéficiaires (`Jean-Paul Mbarga`, `Amina Ngo Bell`)
   - **Doit être remplacé par un jeton inviolable** (ex: `__NUM_0__`, `__BENEF_0__`, `__REF_0__`), puis réinjecté à l'identique après traduction avec vérification systématique de non-altération.

---

## 5. Synthèse des Données Structurées Extraites

Toutes les 79 chaînes uniques relevées dans le parcours ont été structurées et enregistrées dans :
[`data/test_env_strings.json`](file:///C:/Users/FLEX%20ZONE/Models_Langues/data/test_env_strings.json)

Chaque entrée comprend :
- Le texte source FR (clé principale)
- La traduction officielle EN
- Le contexte d'apparition et l'écran cible
- La règle d'intégrité financière (`translatable`, `financial_date_protected`, `financial_condition_masked`, `security_warning_critical`, `security_condition_critical`, `financial_validation_error`, etc.)

Cet audit fournit la base exhaustive et vérifiée pour alimenter le catalogue hors ligne et le moteur de masquage de l'extension.
