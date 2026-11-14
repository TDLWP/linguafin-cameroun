# Script Vidéo de Démonstration Chronométré (≤ 3 Minutes) — SAFINUM 2026

> **Challenge** : SAFINUM Innovate Challenge 2026  
> **Livrable 3** : Script scénarisé chronométré (3 minutes maximum / 180 secondes)  
> **Cible réelle** : `https://safinum.cm/hackathon-test?jury=1` & `tests/mock_bank.html`  
> **Format vidéo** : 1080p, voix off en français avec sous-titres, capture d'écran dynamique.

---

## 1. Déroulé Chronométré Séquence par Séquence

```
[00:00] ─── Intro ─── [00:20] ─── Écran 1: Solde ─── [00:45] ─── Écran 2: Frais ─── [01:15]
[01:15] ─── Écran 3: Destinataire & Alerte ─── [01:45] ─── Écran 4/5: Récap & Reçu ─── [02:10]
[02:10] ─── Erreur & Inédit ─── [02:35] ─── Panneau Jury & Offline ─── [03:00] Fin
```

---

### Séquence 1 : Introduction & Enjeu d'Accessibilité (00:00 – 00:20 / 20 s)
* **Visuel** : Vue d'ensemble du site `https://safinum.cm/hackathon-test` en français.
* **Voix off** :  
  *"Au Cameroun, des millions de citoyens peinent à utiliser les services financiers numériques car ils sont rédigés uniquement en français et en anglais. Voici SAFINUM Accessibility : une surcouche linguistique souveraine qui rend l'interface compréhensible en langues nationales, sans modifier la moindre ligne de code du site bancaire."*

---

### Séquence 2 : Écran 1 — Solde & Activation du Widget Shadow DOM (00:20 – 00:45 / 25 s)
* **Visuel** : Zoom sur le widget flottant en bas à droite (`🇨🇲 Langue : Duálá`). Clic sur le sélecteur, choix du Duálá. Le tableau de bord passe instantanément en langue nationale. Survol de la souris montrant l'original au survol.
* **Voix off** :  
  *"Grâce à une extension Manifest V3 encapsulée en Shadow DOM, l'utilisateur sélectionne le Duálá d'un simple clic. Immédiatement, 'Solde disponible' devient 'Moni mi titi'. Observez la règle critique : le solde de 250 000 FCFA et le numéro de compte CM restent strictement inviolés et non reformatés."*

---

### Séquence 3 : Écran 2 — Frais de Transfert (00:45 – 01:15 / 30 s)
* **Visuel** : Clic sur `Loma moni` (Effectuer un transfert). Écran des frais. Saisie du montant `25000` dans l'input. Sélection de l'option "Compte Safinum (Gratuit)".
* **Voix off** :  
  *"À l'étape 2, 'Frais de transfert' devient 'Mutoa ma tomba'. L'utilisateur saisit son montant : notre script sanctuarise le champ de saisie sans jamais intercepter la frappe. Les frais calculés de 0 FCFA et le total de 25 000 FCFA s'affichent avec exactitude dans l'interface traduite."*

---

### Séquence 4 : Écran 3 — Préparation de Transfert & Alerte de Sécurité (01:15 – 01:45 / 30 s)
* **Visuel** : Saisie du bénéficiaire `Jean-Paul Mbarga` et du téléphone `+237 6 99 12 34 56`. Zoom sur l'encart d'alerte orange traduit (`Nu nongi a si sengedi no...`). Coche de la case de confirmation.
* **Voix off** :  
  *"À l'étape 3, l'usager renseigne le destinataire. Le nom Jean-Paul Mbarga et le numéro de téléphone restent 100 % intacts. L'avertissement de sécurité critique alertant qu'il s'agit d'un nouveau bénéficiaire est parfaitement traduit, permettant à l'usager de comprendre le risque avant de cocher la case d'engagement."*

---

### Séquence 5 : Écrans 4 & 5 — Récapitulatif et Reçu de Confirmation (01:45 – 02:10 / 25 s)
* **Visuel** : Écran de récapitulatif montrant la référence unique `SAF-2026-GOUNQP`, montant `25 000 FCFA`. Clic sur `Kakisane tomba`. Affichage immédiat du reçu de succès.
* **Voix off** :  
  *"L'écran récapitulatif synthétise les données : la référence d'opération SAF-2026-GOUNQP est protégée par jeton inviolable. L'usager valide : le reçu confirme le transfert réussi avec la mention 'Moni mi lomi na bwam'."*

---

### Séquence 6 : Gestion d'Erreur & Simulation de Contenu Inédit (02:10 – 02:35 / 25 s)
* **Visuel** : Bascule sur `tests/mock_bank.html`. Affichage d'un message d'erreur rouge (`Solde insuffisant`) puis injection dynamique d'une notification inédite contenant un montant :  
  *"Alerte de sécurité : tentative de prélèvement de 45 000 FCFA détectée."*
* **Voix off** :  
  *"Que se passe-t-il face à une erreur ou un contenu inédit ? Les erreurs comme le solde insuffisant sont immédiatement compréhensibles. Sur ce message inédit simulé, notre pipeline protège les 45 000 FCFA et impose un affichage bilingue visible avec le français d'origine pour exclure tout risque de contresens."*

---

### Séquence 7 : Contrôle Panneau Jury & Démonstration Hors Ligne (02:35 – 03:00 / 25 s)
* **Visuel** : Zoom sur le panneau d'audit du jury en haut à droite avec `?jury=1`. Toutes les lignes affichent le statut vert : `OK (0 compromission)`. Coupure volontaire de la connexion réseau (icône mode avion activée) : le widget continue de traduire instantanément grâce au catalogue embarqué.
* **Voix off** :  
  *"Le verdict du panneau jury officiel est formel : 100 % d'intégrité financière respectée, zéro altération. Et si le réseau tombe en pleine transaction ? Le catalogue embarqué prend le relais en mode démo 100 % autonome. SAFINUM Accessibility : l'accessibilité bancaire camerounaise, souveraine et infaillible."*

---

## 2. Plan de Secours en Cas de Panne Réseau (Offline Fallback Contingency Plan)

Si lors de la présentation devant le jury ou pendant le tournage de la vidéo la connexion Internet locale ou l'accès au serveur distant échoue :

| Incident Simulé | Détection Automatique | Action Immédiate du Système | Visuel Présenté au Jury |
|---|---|---|---|
| **Coupure réseau Internet totale (Wi-Fi / 4G)** | L'appel à `safinum.cm` ou à l'API distante échoue. | 1. Utiliser le serveur de secours local : ouvrir `tests/mock_bank.html` dans le navigateur.<br>2. L'extension charge `catalogue_offline.json` embarqué via l'API WebExtensions locale. | Aucune interruption, pas d'écran blanc. Le widget affiche le statut *Mode Hors Ligne (Catalogue Embarqué)*. |
| **Backend FastAPI local éteint ou inaccessible** | Le timeout de 1,5 s de `content.js` expire sur `localhost:8000`. | Bascule automatique sans intervention utilisateur vers le dictionnaire local en mémoire cache. | Les 84 chaînes et 52 termes financiers continuent d'être traduits instantanément en Duálá et Bassa'a. |
| **Tentative de falsification de jeton ou d'injection** | Discordance détectée par `verify_integrity()`. | Restitution immédiate du texte source original (`fallback_source`). | La sécurité financière reste sanctuarisée, évitant tout contresens monétaire. |
