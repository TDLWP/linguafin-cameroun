# Guide du Validateur Linguistique — SAFINUM 2026

> **Projet** : SAFINUM 2026 — Couche d'accessibilité linguistique pour services financiers numériques  
> **Langues cibles** : Duálá (`dua`) & Ɓàsàa (`bas`)  
> **Document** : Guide d'accompagnement pour la relecture humaine

---

## 1. Pourquoi votre aide est essentielle ?

Au Cameroun, de nombreux usagers ont des difficultés à utiliser les applications bancaires rédigées uniquement en français ou en anglais. Notre objectif est de rendre ces services compréhensibles dans nos langues nationales (Duálá et Ɓàsàa), **sans jamais commettre la moindre erreur sur l'argent** (montants, frais, bénéficiaires).

Les traductions actuellement présentes dans le système ont été générées automatiquement par ordinateur. Elles sont classées au statut `machine_suggested` (brouillon machine). **Seul un locuteur compétent comme vous peut certifier qu'une phrase est naturelle, exacte et compréhensible.**

---

## 2. Comment remplir votre fiche de validation ?

Votre fiche contient **84 courtes expressions** utilisées sur une application de transfert d'argent (environ 15 à 20 minutes de lecture).

Pour chaque ligne, vous disposez de 7 colonnes :

| Colonne | Ce qu'elle contient | Ce que vous devez faire |
|---|---|---|
| **N°** | Numéro d'ordre (1 à 84) | Ne pas modifier. |
| **Clé / Contexte** | Identifiant technique | Ne pas modifier. |
| **Texte Source (Français)** | La phrase d'origine affichée à l'écran | À lire pour comprendre le sens exact. |
| **Proposition Traduction** | La phrase proposée en Duálá ou Ɓàsàa | À évaluer attentivement. |
| **Validation (OK / KO)** | Votre verdict | Écrire **`OK`**, **`KO`** ou **`DOUTE`** (voir règles ci-dessous). |
| **Correction du validateur** | Votre proposition si KO ou imparfait | Écrire la formulation naturelle correcte. |
| **Commentaire linguistique** | Précisions (facultatif) | Noter une remarque de ton, de dialecte ou de nuance. |

---

## 3. Les règles d'or de la relecture

### Règle n° 1 : Ne rien deviner
* Si une proposition vous semble bizarre, bancale ou confuse, **ne cherchez pas à la justifier**.
* Si vous n'êtes pas absolument sûr de la tournure exacte, **ne devinez pas**.

### Règle n° 2 : Utiliser `DOUTE` dès la moindre incertitude
* En matière d'argent, une mauvaise traduction peut induire un usager en erreur (par exemple confondre un débit et un crédit, ou des frais et un montant).
* Si vous hésitez, écrivez simplement **`DOUTE`** dans la colonne *Validation*.
* **Effet de sécurité** : Dans notre système, toute ligne marquée `DOUTE` est immédiatement écartée (`rejected`) et reste affichée en français sécurisé. Le doute protège l'usager !

### Règle n° 3 : Respecter les termes financiers et noms propres
* Les montants en chiffres (ex: `25 000 FCFA`), les numéros de téléphone (`+237 6...`), les références (`SAF-2026...`) et les noms de personnes (`Jean-Paul Mbarga`) ne sont **jamais traduits**.
* Le mot *Safinum Pay* est une marque commerciale : il reste inchangé.

---

## 4. Protection de vos données et consentement

Nous appliquons une charte d'éthique et de transparence stricte :

1. **Aucun nom publié sans accord écrit** : Votre nom de famille et vos coordonnées personnelles ne figureront jamais dans le code source public, ni dans les rapports du concours sans votre consentement explicite.
2. **Attribution par Code Validateur** : Pour assurer la traçabilité scientifique de votre travail tout en préservant votre vie privée, un code anonyme ou pseudonyme vous est attribué (par exemple : `VAL-DUA-01` ou `LOC-BAS-02`). C'est uniquement ce code qui sera consigné dans l'historique technique.
3. **Usage strictement non commercial et d'intérêt général** : Vos relectures et corrections servent exclusivement à améliorer l'accessibilité des services financiers pour les populations camerounaises.
4. **Liberté totale** : Votre participation est bénévole et volontaire. Vous êtes libre de ne relire qu'une partie des lignes ou de vous interrompre à tout moment.

---

## 5. Exemple pratique

| N° | Texte Source (Français) | Proposition Traduction | Validation | Correction du validateur | Commentaire |
|---|---|---|---|---|---|
| 8 | Solde | Moni mi titi | **OK** | *(laisser vide)* | Terme clair et bien compris |
| 9 | Frais | Mutoa | **OK** | *(laisser vide)* | Conforme |
| 13 | Annuler | Kwele ebolo | **KO** | Bwekisa | "Bwekisa" est plus précis pour une action informatique |
| 17 | Paiement en attente | ... | **DOUTE** | *(laisser vide)* | Hésitation entre deux tournures |

*Mba biña ba bwam ! / Mayega ngandak ! (Merci beaucoup pour votre précieuse contribution !)*
