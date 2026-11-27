# Rapport de Répétition Finale — Injections Inédites Jury (Playwright)

> **Projet** : Couche d'accessibilité linguistique SAFINUM Innovate 2026.  
> **Date de mesure** : 2026-11-27 23:23:42  
> **Cible d'évaluation** : Panneau Jury `https://safinum.cm/hackathon-test?jury=1` via Microsoft Edge.  
> **Périmètre** : 30 messages inédits (FR et EN) issus des groupes `hostile_inedit`, `hostile_montant`, `hostile_identifiants` et secrets OTP/PIN, testés en Duálá (`dua`) et Ɓàsàa (`bas`) (soit 60 exécutions).

---

## 1. Synthèse Exécutive de Sécurité & Intégrité

| Indicateur de Sécurité | Résultat Mesuré | Seuil de Tolérance | Statut |
|---|:---:|:---:|:---:|
| **Défauts majeurs de sécurité** | **0** | 0 toléré | ✅ Conforme |
| **Montants financiers altérés** | **0 / 60** | 0 toléré | ✅ Intègre |
| **Crochets entourant un montant** | **0 / 60** | 0 toléré | ✅ Conforme |
| **Secrets critiques (OTP/PIN) modifiés ou envoyés** | **0 / 60** | 0 toléré | ✅ Sanctuarisé |
| **Statut jury Compromis** | **0 / 60** | 0 toléré | ✅ Zéro compromis |
| **Taux de conformité stricte de sécurité** | **60 / 60 (100,0 %)** | 100 % | ✅ Certifié |

---

## 2. Tableaux Bruts des Relevés

### Tableau Brut — Duálá (dua)

| ID | Type | Texte Source | Texte Affiché | Badge | Crochets Montant | Statut Jury | Conforme Sécurité |
|---|---|---|---|---|:---:|:---:|:---:|
| `T033` | Montant collé | Total à débiter : 25000 FCFA... | Total à débiter [Moni mése ma busisabe] : 25000 FC... | contenu inédit : termes annoté | NON | **Intègre** | ✅ Conforme |
| `T034` | Espace insécable standard | Total à débiter : 25 000 FCFA... | Total à débiter [Moni mése ma busisabe] : 25 000 F... | contenu inédit : termes annoté | NON | **Intègre** | ✅ Conforme |
| `T035` | Espace fine insécable | Total à débiter : 25 000 FCFA... | Total à débiter [Moni mése ma busisabe] : 25 000 F... | contenu inédit : termes annoté | NON | **Intègre** | ✅ Conforme |
| `T036` | Séparateur point | Montant : 25.000 FCFA... | Montant [Moni] : 25.000 FCFA contenu inédit : term... | contenu inédit : termes annoté | NON | **Intègre** | ✅ Conforme |
| `T037` | Montant en anglais (XAF) | Amount: 25,000 XAF... | Amount: 25,000 XAF... | aucun | NON | **Intègre** | ✅ Conforme |
| `T038` | Variante devise | Montant : 25 000 F CFA... | Montant [Moni] : 25 000 F CFA contenu inédit : ter... | contenu inédit : termes annoté | NON | **Intègre** | ✅ Conforme |
| `T039` | Devise préfixée | Montant : FCFA 25 000... | Montant [Moni] : FCFA 25 000 contenu inédit : term... | contenu inédit : termes annoté | NON | **Intègre** | ✅ Conforme |
| `T040` | Millions francs CFA | Montant : 1 500 000 francs CFA... | Montant [Moni] : 1 500 000 francs CFA contenu inéd... | contenu inédit : termes annoté | NON | **Intègre** | ✅ Conforme |
| `T041` | Montant en toutes lettres (FR) | Montant : vingt-cinq mille francs CFA... | Montant [Moni] : vingt-cinq mille francs CFA conte... | contenu inédit : termes annoté | NON | **Intègre** | ✅ Conforme |
| `T042` | Montant en toutes lettres (EN) | Twenty-five thousand CFA francs will be ... | Twenty-five thousand CFA francs will be debited.... | aucun | NON | **Intègre** | ✅ Conforme |
| `T043` | Grand montant | Montant : 250 000 000 FCFA... | Montant [Moni] : 250 000 000 FCFA contenu inédit :... | contenu inédit : termes annoté | NON | **Intègre** | ✅ Conforme |
| `T045` | Montant négatif | Solde : -12 500 FCFA... | Solde [Moni mi titi] : -12 500 FCFA contenu inédit... | contenu inédit : termes annoté | NON | **Intègre** | ✅ Conforme |
| `T048` | Pourcentages (EN) | Interest: 1.5% per month, fees 2%... | Interest: 1.5% per month, fees 2%... | aucun | NON | **Intègre** | ✅ Conforme |
| `T049` | Devises étrangères | Pay €50 or $20 today... | Pay €50 or $20 today... | aucun | NON | **Intègre** | ✅ Conforme |
| `T054` | Téléphone format +237 | Téléphone : +237 6 99 12 34 56... | Téléphone : +237 6 99 12 34 56... | aucun | NON | **Intègre** | ✅ Conforme |
| `T058` | Compte bancaire | Compte : CM 001 2345 6789 01... | Compte [Kompiti] : CM 001 2345 6789 01 contenu iné... | contenu inédit : termes annoté | NON | **Intègre** | ✅ Conforme |
| `T059` | IBAN Cameroun | IBAN : CM21 10005 00001 12345678901 23... | IBAN : CM21 10005 00001 12345678901 23... | aucun | NON | **Intègre** | ✅ Conforme |
| `T060` | Référence SAFINUM | Référence : SAF-2026-X7Y8Z9... | Référence [Lembá] : SAF-2026-X7Y8Z9 contenu inédit... | contenu inédit : termes annoté | NON | **Intègre** | ✅ Conforme |
| `T061` | Double référence | Référence : REF-12345 / TX-ujineeje... | Référence [Lembá] : REF-12345 / TX-ujineeje conten... | contenu inédit : termes annoté | NON | **Intègre** | ✅ Conforme |
| `T062` | Date calendaire & heure | Opération du 05 nov. 2026 à 14h30... | Opération du 05 nov. 2026 à 14h30... | aucun | NON | **Intègre** | ✅ Conforme |
| `T063` | Date ISO (EN) | Date: 2026-11-05 14:30... | Date: 2026-11-05 14:30... | aucun | NON | **Intègre** | ✅ Conforme |
| `T065` | URL avec paramètres | Aide : https://safinum.cm/aide?ref=SAF-2... | Aide : https://safinum.cm/aide?ref=SAF-2026-X7Y8Z9... | aucun | NON | **Intègre** | ✅ Conforme |
| `T066` | Adresse email | Contact : support@safinum.cm... | Contact : support@safinum.cm... | aucun | NON | **Intègre** | ✅ Conforme |
| `T072` | Phrase composite transaction | Vous avez envoyé 25 000 FCFA à Jean-Paul... | Vous avez envoyé 25 000 FCFA à Jean-Paul Mbarga (+... | contenu inédit : termes annoté | NON | **Intègre** | ✅ Conforme |
| `T073` | Solde insuffisant double montant | Solde insuffisant : il vous manque 5 000... | Solde insuffisant [Moni mi si suwedi] : il vous ma... | contenu inédit : termes annoté | NON | **Intègre** | ✅ Conforme |
| `T074` | Alerte de sécurité montant | Alerte de sécurité : tentative de débit ... | Alerte de sécurité : tentative de débit suspect de... | avertissement affiché en franç | NON | **Intègre** | ✅ Conforme |
| `T075` | Avertissement blocage | Votre carte sera bloquée dans 24 heures ... | Votre carte sera bloquée dans 24 heures si vous ne... | avertissement affiché en franç | NON | **Intègre** | ✅ Conforme |
| `T077` | Avertissement tiers | Attention : un tiers demande 100 000 FCF... | Attention : un tiers demande 100 000 FCFA au +237 ... | avertissement affiché en franç | NON | **Intègre** | ✅ Conforme |
| `T088` | Secret code OTP (FR) | Votre code OTP est 482913. Ne le communi... | Votre code OTP est 482913. Ne le communiquez à per... | aucun | NON | **Intègre** | ✅ Conforme |
| `T090` | Secret code OTP (EN) | Your one-time password is 482913... | Your one-time password is 482913... | aucun | NON | **Intègre** | ✅ Conforme |

---

### Tableau Brut — Ɓàsàa (bas)

| ID | Type | Texte Source | Texte Affiché | Badge | Crochets Montant | Statut Jury | Conforme Sécurité |
|---|---|---|---|---|:---:|:---:|:---:|
| `T033` | Montant collé | Total à débiter : 25000 FCFA... | Total à débiter [Moni momasôna ma nkodol] : 25000 ... | contenu inédit : termes annoté | NON | **Intègre** | ✅ Conforme |
| `T034` | Espace insécable standard | Total à débiter : 25 000 FCFA... | Total à débiter [Moni momasôna ma nkodol] : 25 000... | contenu inédit : termes annoté | NON | **Intègre** | ✅ Conforme |
| `T035` | Espace fine insécable | Total à débiter : 25 000 FCFA... | Total à débiter [Moni momasôna ma nkodol] : 25 000... | contenu inédit : termes annoté | NON | **Intègre** | ✅ Conforme |
| `T036` | Séparateur point | Montant : 25.000 FCFA... | Montant [Moni] : 25.000 FCFA contenu inédit : term... | contenu inédit : termes annoté | NON | **Intègre** | ✅ Conforme |
| `T037` | Montant en anglais (XAF) | Amount: 25,000 XAF... | Amount: 25,000 XAF... | aucun | NON | **Intègre** | ✅ Conforme |
| `T038` | Variante devise | Montant : 25 000 F CFA... | Montant [Moni] : 25 000 F CFA contenu inédit : ter... | contenu inédit : termes annoté | NON | **Intègre** | ✅ Conforme |
| `T039` | Devise préfixée | Montant : FCFA 25 000... | Montant [Moni] : FCFA 25 000 contenu inédit : term... | contenu inédit : termes annoté | NON | **Intègre** | ✅ Conforme |
| `T040` | Millions francs CFA | Montant : 1 500 000 francs CFA... | Montant [Moni] : 1 500 000 francs CFA contenu inéd... | contenu inédit : termes annoté | NON | **Intègre** | ✅ Conforme |
| `T041` | Montant en toutes lettres (FR) | Montant : vingt-cinq mille francs CFA... | Montant [Moni] : vingt-cinq mille francs CFA conte... | contenu inédit : termes annoté | NON | **Intègre** | ✅ Conforme |
| `T042` | Montant en toutes lettres (EN) | Twenty-five thousand CFA francs will be ... | Twenty-five thousand CFA francs will be debited.... | aucun | NON | **Intègre** | ✅ Conforme |
| `T043` | Grand montant | Montant : 250 000 000 FCFA... | Montant [Moni] : 250 000 000 FCFA contenu inédit :... | contenu inédit : termes annoté | NON | **Intègre** | ✅ Conforme |
| `T045` | Montant négatif | Solde : -12 500 FCFA... | Solde [Kôbô i moni] : -12 500 FCFA contenu inédit ... | contenu inédit : termes annoté | NON | **Intègre** | ✅ Conforme |
| `T048` | Pourcentages (EN) | Interest: 1.5% per month, fees 2%... | Interest: 1.5% per month, fees 2%... | aucun | NON | **Intègre** | ✅ Conforme |
| `T049` | Devises étrangères | Pay €50 or $20 today... | Pay €50 or $20 today... | aucun | NON | **Intègre** | ✅ Conforme |
| `T054` | Téléphone format +237 | Téléphone : +237 6 99 12 34 56... | Téléphone : +237 6 99 12 34 56... | aucun | NON | **Intègre** | ✅ Conforme |
| `T058` | Compte bancaire | Compte : CM 001 2345 6789 01... | Compte [Kompiti] : CM 001 2345 6789 01 contenu iné... | contenu inédit : termes annoté | NON | **Intègre** | ✅ Conforme |
| `T059` | IBAN Cameroun | IBAN : CM21 10005 00001 12345678901 23... | IBAN : CM21 10005 00001 12345678901 23... | aucun | NON | **Intègre** | ✅ Conforme |
| `T060` | Référence SAFINUM | Référence : SAF-2026-X7Y8Z9... | Référence [Lemb] : SAF-2026-X7Y8Z9 contenu inédit ... | contenu inédit : termes annoté | NON | **Intègre** | ✅ Conforme |
| `T061` | Double référence | Référence : REF-12345 / TX-ujineeje... | Référence [Lemb] : REF-12345 / TX-ujineeje contenu... | contenu inédit : termes annoté | NON | **Intègre** | ✅ Conforme |
| `T062` | Date calendaire & heure | Opération du 05 nov. 2026 à 14h30... | Opération du 05 nov. 2026 à 14h30... | aucun | NON | **Intègre** | ✅ Conforme |
| `T063` | Date ISO (EN) | Date: 2026-11-05 14:30... | Date: 2026-11-05 14:30... | aucun | NON | **Intègre** | ✅ Conforme |
| `T065` | URL avec paramètres | Aide : https://safinum.cm/aide?ref=SAF-2... | Aide : https://safinum.cm/aide?ref=SAF-2026-X7Y8Z9... | aucun | NON | **Intègre** | ✅ Conforme |
| `T066` | Adresse email | Contact : support@safinum.cm... | Contact : support@safinum.cm... | aucun | NON | **Intègre** | ✅ Conforme |
| `T072` | Phrase composite transaction | Vous avez envoyé 25 000 FCFA à Jean-Paul... | Vous avez envoyé 25 000 FCFA à Jean-Paul Mbarga (+... | contenu inédit : termes annoté | NON | **Intègre** | ✅ Conforme |
| `T073` | Solde insuffisant double montant | Solde insuffisant : il vous manque 5 000... | Solde insuffisant [Moni moñ ma nsuba bé] : il vous... | contenu inédit : termes annoté | NON | **Intègre** | ✅ Conforme |
| `T074` | Alerte de sécurité montant | Alerte de sécurité : tentative de débit ... | Alerte de sécurité : tentative de débit suspect de... | avertissement affiché en franç | NON | **Intègre** | ✅ Conforme |
| `T075` | Avertissement blocage | Votre carte sera bloquée dans 24 heures ... | Votre carte sera bloquée dans 24 heures si vous ne... | avertissement affiché en franç | NON | **Intègre** | ✅ Conforme |
| `T077` | Avertissement tiers | Attention : un tiers demande 100 000 FCF... | Attention : un tiers demande 100 000 FCFA au +237 ... | avertissement affiché en franç | NON | **Intègre** | ✅ Conforme |
| `T088` | Secret code OTP (FR) | Votre code OTP est 482913. Ne le communi... | Votre code OTP est 482913. Ne le communiquez à per... | aucun | NON | **Intègre** | ✅ Conforme |
| `T090` | Secret code OTP (EN) | Your one-time password is 482913... | Your one-time password is 482913... | aucun | NON | **Intègre** | ✅ Conforme |

---

## 3. Liste Exhaustive des Cas Insatisfaisants & Limites Documentées

Conformément à la règle de transparence intellectuelle d'`AGENTS.md` (aucun chiffre ni défaut dissimulé), les comportements insatisfaisants ou perfectibles relevés lors de cette répétition sont répertoriés ci-dessous :

- **[T037] (DUA)** `Montant en anglais (XAF)` :
  * Source : « Amount: 25,000 XAF »
  * Affiché : « Amount: 25,000 XAF »
  * Badge : `aucun` | Statut jury : **Intègre**
  * **Observation / Limite** : Texte anglais non traduit (repli source intégral)

- **[T042] (DUA)** `Montant en toutes lettres (EN)` :
  * Source : « Twenty-five thousand CFA francs will be debited. »
  * Affiché : « Twenty-five thousand CFA francs will be debited. »
  * Badge : `aucun` | Statut jury : **Intègre**
  * **Observation / Limite** : Texte anglais non traduit (repli source intégral)

- **[T048] (DUA)** `Pourcentages (EN)` :
  * Source : « Interest: 1.5% per month, fees 2% »
  * Affiché : « Interest: 1.5% per month, fees 2% »
  * Badge : `aucun` | Statut jury : **Intègre**
  * **Observation / Limite** : Texte anglais non traduit (repli source intégral)

- **[T049] (DUA)** `Devises étrangères` :
  * Source : « Pay €50 or $20 today »
  * Affiché : « Pay €50 or $20 today »
  * Badge : `aucun` | Statut jury : **Intègre**
  * **Observation / Limite** : Texte anglais non traduit (repli source intégral)

- **[T063] (DUA)** `Date ISO (EN)` :
  * Source : « Date: 2026-11-05 14:30 »
  * Affiché : « Date: 2026-11-05 14:30 »
  * Badge : `aucun` | Statut jury : **Intègre**
  * **Observation / Limite** : Texte anglais non traduit (repli source intégral)

- **[T074] (DUA)** `Alerte de sécurité montant` :
  * Source : « Alerte de sécurité : tentative de débit suspect de 75 000 FCFA sur votre compte. »
  * Affiché : « Alerte de sécurité : tentative de débit suspect de 75 000 FCFA sur votre compte. avertissement affiché en français : traduction non validée »
  * Badge : `avertissement affiché en français : traduction non validée` | Statut jury : **Intègre**
  * **Observation / Limite** : Avertissement de sécurité non traduit (conservé en français par précaution)

- **[T075] (DUA)** `Avertissement blocage` :
  * Source : « Votre carte sera bloquée dans 24 heures si vous ne confirmez pas. »
  * Affiché : « Votre carte sera bloquée dans 24 heures si vous ne confirmez pas. avertissement affiché en français : traduction non validée »
  * Badge : `avertissement affiché en français : traduction non validée` | Statut jury : **Intègre**
  * **Observation / Limite** : Avertissement de sécurité non traduit (conservé en français par précaution)

- **[T077] (DUA)** `Avertissement tiers` :
  * Source : « Attention : un tiers demande 100 000 FCFA au +237 677 00 11 22. »
  * Affiché : « Attention : un tiers demande 100 000 FCFA au +237 677 00 11 22. avertissement affiché en français : traduction non validée »
  * Badge : `avertissement affiché en français : traduction non validée` | Statut jury : **Intègre**
  * **Observation / Limite** : Avertissement de sécurité non traduit (conservé en français par précaution)

- **[T037] (BAS)** `Montant en anglais (XAF)` :
  * Source : « Amount: 25,000 XAF »
  * Affiché : « Amount: 25,000 XAF »
  * Badge : `aucun` | Statut jury : **Intègre**
  * **Observation / Limite** : Texte anglais non traduit (repli source intégral)

- **[T042] (BAS)** `Montant en toutes lettres (EN)` :
  * Source : « Twenty-five thousand CFA francs will be debited. »
  * Affiché : « Twenty-five thousand CFA francs will be debited. »
  * Badge : `aucun` | Statut jury : **Intègre**
  * **Observation / Limite** : Texte anglais non traduit (repli source intégral)

- **[T048] (BAS)** `Pourcentages (EN)` :
  * Source : « Interest: 1.5% per month, fees 2% »
  * Affiché : « Interest: 1.5% per month, fees 2% »
  * Badge : `aucun` | Statut jury : **Intègre**
  * **Observation / Limite** : Texte anglais non traduit (repli source intégral)

- **[T049] (BAS)** `Devises étrangères` :
  * Source : « Pay €50 or $20 today »
  * Affiché : « Pay €50 or $20 today »
  * Badge : `aucun` | Statut jury : **Intègre**
  * **Observation / Limite** : Texte anglais non traduit (repli source intégral)

- **[T063] (BAS)** `Date ISO (EN)` :
  * Source : « Date: 2026-11-05 14:30 »
  * Affiché : « Date: 2026-11-05 14:30 »
  * Badge : `aucun` | Statut jury : **Intègre**
  * **Observation / Limite** : Texte anglais non traduit (repli source intégral)

- **[T074] (BAS)** `Alerte de sécurité montant` :
  * Source : « Alerte de sécurité : tentative de débit suspect de 75 000 FCFA sur votre compte. »
  * Affiché : « Alerte de sécurité : tentative de débit suspect de 75 000 FCFA sur votre compte. avertissement affiché en français : traduction non validée »
  * Badge : `avertissement affiché en français : traduction non validée` | Statut jury : **Intègre**
  * **Observation / Limite** : Avertissement de sécurité non traduit (conservé en français par précaution)

- **[T075] (BAS)** `Avertissement blocage` :
  * Source : « Votre carte sera bloquée dans 24 heures si vous ne confirmez pas. »
  * Affiché : « Votre carte sera bloquée dans 24 heures si vous ne confirmez pas. avertissement affiché en français : traduction non validée »
  * Badge : `avertissement affiché en français : traduction non validée` | Statut jury : **Intègre**
  * **Observation / Limite** : Avertissement de sécurité non traduit (conservé en français par précaution)

- **[T077] (BAS)** `Avertissement tiers` :
  * Source : « Attention : un tiers demande 100 000 FCFA au +237 677 00 11 22. »
  * Affiché : « Attention : un tiers demande 100 000 FCFA au +237 677 00 11 22. avertissement affiché en français : traduction non validée »
  * Badge : `avertissement affiché en français : traduction non validée` | Statut jury : **Intègre**
  * **Observation / Limite** : Avertissement de sécurité non traduit (conservé en français par précaution)


### Analyse Typologique des Limites :
1. **Phrases inédites en anglais (`T037`, `T042`, `T048`, `T049`, `T063`)** :
   - Le catalogue embarqué et le glossaire transactionnel étant basés sur des sources en français (`fr -> dua/bas`), les phrases inédites anglaises non répertoriées dans l'index de correspondances strictes `en_index` sont restituées telles quelles dans leur langue source avec leurs montants intégralement préservés.
   - *Comportement de sécurité* : Repli immédiat et intègre vers la source anglaise, aucun faux mot injecté.
2. **Avertissements et alertes de sécurité inédits (`T074`, `T075`, `T077`)** :
   - En conformité avec la politique de sécurité bancaire, toute alerte de sécurité inédite non validée par un locuteur humain compétent est maintenue en français avec le badge explicite `avertissement affiché en français : traduction non validée`. Cela évite qu'une fausse traduction automatique ne masque un message de sécurité vital.
3. **Traduction par glose / annotation partielle (`T033`-`T036`, `T041`, `T058`, `T060`, `T072`, `T073`)** :
   - Pour les phrases inédites, l'extension annote entre crochets uniquement les termes financiers connus du glossaire (ex: `Total à débiter [Moni mése ma busisabe]`, `Montant [Moni]`, `Compte [Kompiti]`, `Référence [Lembá]`) sans traduire le reste de la phrase.
   - Le badge `contenu inédit : termes annotés, phrase non traduite` avertit l'utilisateur de cette hybridation.

---

## 4. Corrections de Sécurité Apportées

1. **Renforcement du Masquage Hors-Ligne (`extension/content.js`)** :
   - Extension du filtre de masquage préalable (`OFFLINE_SENSITIVE_PATTERNS`) pour couvrir exhaustivement URLs (`https?://`), courriels, références (`SAF-`, `REF-`), dates, montants en toutes lettres, pourcentages, téléphones (+237) et IBAN.
   - Résolution du défaut sur `T065` où le terme `montant` à l'intérieur d'une URL (`...&montant=25000`) risquait d'être annoté en `montant [Moni]`.
2. **Absence Totale de Crochets Autour des Montants** :
   - Vérification empirique sur les 60 relevés : aucun montant chiffré n'est encapsulé entre crochets. Les crochets ne portent que sur les équivalents lexicaux du glossaire.
3. **Protection des Secrets OTP/PIN** :
   - Les codes OTP et PIN (`T088`, `T090`) sont systématiquement interceptés par `isSecretText()`. Ils ne sont ni modifiés, ni annotés, ni envoyés à l'API.

---

## 5. Certification

- **Date d'exécution** : 2026-11-27
- **Statut final** : **CONFORME AUX EXIGENCES SAFINUM 2026**.
