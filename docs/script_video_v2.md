# Script Vidéo de Démonstration v2 (≤ 3 Minutes / 180 s) — SAFINUM 2026

> **Challenge** : SAFINUM Innovate Challenge 2026 — Finale  
> **Livrable 3 (Version actualisée v2)** : Démonstration intégrale chronométrée (180 secondes maximum)  
> **Cible réelle** : `https://safinum.cm/hackathon-test?jury=1` & `tests/mock_bank.html`  
> **Environnement de démonstration** : Microsoft Edge, script `scripts/lancer_demo.ps1`, API locale FastAPI

---

## 1. Déroulé Chronométré Séquence par Séquence

```
[00:00] ─── Introduction & Principe Non-Intrusif ─── [00:20]
[00:20] ─── Parcours Source FR (Solde, Frais, Destinataire) ─── [00:50]
[00:50] ─── Récapitulatif, Reçu & Zéro Altération ─── [01:15]
[01:15] ─── Parcours Source Anglaise (Bilinguisme EN→FR) ─── [01:40]
[01:40] ─── Contenus Inédits & Alertes de Sécurité Sanctuarisées ─── [02:15]
[02:15] ─── Panneau Jury, Hors-Ligne & Transparence Native ─── [03:00]
```

---

### Séquence 1 : Introduction & Architecture Non-Intrusive (00:00 – 00:20 / 20 s)
* **Visuel** : Vue globale de la page `https://safinum.cm/hackathon-test` en français. Le script `scripts/lancer_demo.ps1` a lancé l'environnement.
* **Voix off** :  
  *« L'inclusion financière au Cameroun se heurte à la barrière de la langue. Voici SAFINUM Accessibility v2 : une surcouche souveraine en extension Manifest V3 et API locale, capable d'adapter l'interface en Duálá et en Ɓàsàa sans modifier une seule ligne de code de l'application bancaire hôte. »*

---

### Séquence 2 : Parcours Bancaire Source Française — Solde, Frais & Bénéficiaire (00:20 – 00:50 / 30 s)
* **Visuel** : Clic sur le widget flottant Shadow DOM en bas à droite (`🇨🇲 Langue : Duálá`). Le tableau de bord passe en Duálá : *« Solde disponible »* devient *« Moni mi titi »*. Le solde `250 000 FCFA` et le compte `CM 001 2345 6789 01` restent rigoureusement intacts. Saisie de `25000` à l'étape des frais : le champ de saisie est sanctuarisé. À l'étape 3, saisie du bénéficiaire `Jean-Paul Mbarga` et du téléphone `+237 6 99 12 34 56`.
* **Voix off** :  
  *« L'usager active le Duálá dans le widget encapsulé en Shadow DOM. Les termes financiers sont traduits instantanément, tandis que le montant de 250 000 FCFA et les identifiants bancaires sont protégés par masquage de jetons déterministe. Les frais à 0 FCFA et les coordonnées du bénéficiaire restent strictement inviolés. »*

---

### Séquence 3 : Récapitulatif & Reçu de Transfert (00:50 – 01:15 / 25 s)
* **Visuel** : Écran 4 (Récapitulatif) montrant la référence `SAF-2026-GOUNQP` et le total `25 000 FCFA`. Clic sur *« Kakisane tomba »* (Confirmer le transfert). Affichage de l'écran 5 (Reçu de confirmation).
* **Voix off** :  
  *« À l'étape du récapitulatif, la référence de transaction et les totaux sont vérifiés par notre garde-fou d'intégrité avant tout affichage. L'usager valide son opération en toute clarté et reçoit son reçu de confirmation en langue nationale. »*

---

### Séquence 4 : Prise en Charge des Interfaces en Anglais (01:15 – 01:40 / 25 s)
* **Visuel** : Bascule du site cible en langue source anglaise (`Available Balance`, `Transfer Fee`, `Beneficiary`). Le widget SAFINUM détecte la source EN via `data/en_to_fr_index.json`. L'interface bascule en Ɓàsàa (`Mɔni i yé`, `Mût a kɔs mɔni`).
* **Voix off** :  
  *« Qu'en est-il d'un service bancaire rédigé en anglais ? Grâce à notre index de correspondance bilingue, l'extension normalise les segments anglophones vers les équivalents nationaux tout en appliquant les mêmes règles d'intégrité. Zéro compromis, quelle que soit la langue de départ. »*

---

### Séquence 5 : Contenus Inédits & Alertes de Sécurité Sanctuarisées (01:40 – 02:15 / 35 s)
* **Visuel** : Injection de deux contenus via le simulateur ou le panneau jury :
  1. *Alerte de sécurité avec montant* : `Alerte de sécurité : tentative de débit suspect de 75 000 FCFA sur votre compte.` -> Affichage en français avec le badge d'avertissement : `[avertissement affiché en français : traduction non validée]`. Le montant `75 000 FCFA` est strictement sans crochets.
  2. *Contenu inédit standard* : Phrase non répertoriée avec termes financiers connus -> Affichage bilingue parallèle avec espace avant le badge : `[contenu inédit : termes annotés, phrase non traduite]`.
* **Voix off** :  
  *« Sur un contenu inédit, notre pipeline annote les concepts connus sans inventer de phrase. Et sur une alerte de sécurité critique, notre règle ANNOTATE_SECURITY_ALERTS refuse tout risque de contresens : le texte est maintenu en français avec un badge explicite, et le montant de 75 000 FCFA ne comporte aucun crochet parasite. »*

---

### Séquence 6 : Panneau Jury, Mode Hors-Ligne & Transparence Native (02:15 – 03:00 / 45 s)
* **Visuel** : Zoom sur le panneau d'évaluation jury `?jury=1`. L'onglet des soumissions affiche **100 % Intègre (0 compromis)** sur l'intégralité du parcours. Arrêt volontaire de la connexion réseau ou du serveur backend : l'extension bascule instantanément sur le catalogue embarqué (`offline_catalog.json`). Présentation du volet du widget avec le bandeau d'avertissement et du kit de validation (`catalogue/kit_validation/GUIDE_VALIDATEUR.md`).
* **Voix off** :  
  *« Le panneau jury officiel atteste du résultat : 100 % des soumissions sont marquées intègres, zéro compromis. En cas de coupure réseau, le catalogue embarqué prend le relais sans rupture de service.*  
  *Enfin, nous faisons le choix d'une transparence absolue : à ce jour, 0 chaîne n'a encore été validée par un locuteur natif. Toutes nos propositions portent la mention 'brouillon IA', et notre kit de validation humaine est d'ores et déjà prêt pour certifier chaque mot avec les communautés avant tout déploiement en production. SAFINUM Accessibility : la technologie au service de l'inclusion, avec rigueur et intégrité. »*

---

## 2. Synthèse des Commandes Exécutables pour la Démonstration

Toutes les étapes de ce script vidéo sont reproductibles avec les outils du dépôt :

```powershell
# 1. Lancement automatique de l'environnement de démo (FastAPI + Edge + Extension)
powershell -ExecutionPolicy Bypass -File scripts/lancer_demo.ps1

# 2. Exécution de toutes les suites de contrôle (187 tests, 0 échec)
powershell -ExecutionPolicy Bypass -File scripts/run_all_checks.ps1

# 3. Production des archives de distribution certifiées
python scripts/package_release.py
```
