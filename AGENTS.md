# AGENTS.md — Règles permanentes du projet SAFINUM 2026

> Projet : couche d'accessibilité linguistique pour services financiers numériques (FR/EN -> langues camerounaises).
> Date limite : samedi 14 novembre 2026, 23h59 (heure Cameroun).

---

## 1. Perimetre et architecture

- **Extension navigateur Manifest V3** : content script + MutationObserver + widget en Shadow DOM.
- **API locale FastAPI** (backend traduction).
- **Regle absolue** : aucune modification du site cible (https://safinum.cm/hackathon-test).
- Pas de dependances superflues. Toute bibliotheque tierce doit etre declaree dans `THIRD_PARTY.md`.

---

## 2. Integrite financiere — regle critique

> Toute erreur alterant montant, frais, beneficiaire, condition ou avertissement de securite = **defaut majeur**.

- Montants, devises, frais, nombres, dates, references, numeros de telephone, noms de beneficiaires, codes : **JAMAIS traduits ni reformates**.
- Methode obligatoire : **masquage par jetons** avant traduction, **restauration stricte** apres, **verification** que tous les jetons sont restaures.
- En cas d'echec de restauration -> conserver le **texte source** sans erreur silencieuse.

---

## 3. Donnees personnelles et securite

- **Aucune donnee personnelle ou bancaire collectee** a aucun moment.
- **Aucune cle API dans le code client** (extension navigateur incluse).
- Fichier `.env.example` fourni **sans aucun secret**. Les vraies valeurs ne doivent jamais etre commitees.

---

## 4. Statuts de traduction

| Statut | Signification |
|---|---|
| `draft` | Redigee mais non verifiee |
| `machine_suggested` | Sortie brute d'un moteur automatique |
| `human_validated` | Confirmee par un locuteur competent |
| `rejected` | Rejetee (erreur ou inappropriee) |

**Ne jamais presenter une traduction `machine_suggested` comme authentique.**

---

## 5. Mode demo hors ligne

- Un **catalogue embarque** dans l'extension doit permettre une demonstration complete sans reseau.
- Ce mode doit etre explicitement activable et documente.

---

## 6. Environnement de developpement

- OS : Windows 11, PowerShell en francais.
- RAM : 32 Go. GPU : 4 Go VRAM.
- **Annoncer la taille approximative de tout telechargement** avant de lancer une installation.

---

## 7. Regles agents

- Mettre a jour `SUIVI.md` **a chaque etape** (decision prise, tache terminee, blocage).
- Reponses en **francais**.
- Si une modification du site cible semble necessaire : **s'arreter et signaler**.
- Si une bibliotheque non declaree dans `THIRD_PARTY.md` est requise : **s'arreter, annoncer la taille, attendre validation**.
- Ne jamais commiter de secrets, de donnees personnelles ou de sorties de test contenant des informations financieres reelles.

---

## 8. Criteres de notation (rappel)

| Critere | Points |
|---|---|
| Fonctionnement | 25 |
| Integration et independance | 20 |
| Securite et preservation des infos financieres | 20 |
| Accessibilite / UX | 15 |
| Adaptation a un contenu inedit | 10 |
| Faisabilite / documentation | 10 |

---

## 9. Livrables attendus

1. Description succincte du projet.
2. Prototype fonctionnel ou demo reproductible.
3. Video <= 3 minutes.
4. Note technique (architecture, integration, dependances, limites).
5. Langue(s) supportee(s) + methode de validation linguistique.

---

## 10. Règles de la branche amelioration

1. **Branche et tags** : Avant toute action : `git branch --show-current` doit afficher `amelioration`. Sinon, arrête-toi. Ne touche jamais au tag `v1.0-soumission-14nov` ni à la branche `main`.
2. **Discipline Git** : Aucun commit avec `git add -A` : seulement les fichiers listés. Une tâche = un commit ciblé. À la fin : `git push origin amelioration` ; en cas d'échec réseau, signale-le sans boucler.
3. **Statut linguistique** : Aucune traduction en langue locale ne doit être inventée ni présentée comme validée. Statut `machine_suggested` par défaut ; `human_validated` uniquement via `scripts/importer_validation.py`.
4. **Véracité des métriques** : Tout chiffre rapporté doit venir d'une exécution réelle ; sinon écris « non mesuré ». Montre les sorties brutes des tests.
5. **Dépendances et téléchargements** : Annonce la taille de tout téléchargement avant de l'installer et déclare tout nouveau composant dans `THIRD_PARTY.md`.
6. **Préservation de la version soumise** : Les fichiers de la version soumise ne sont pas réécrits : on ajoute des fichiers, on corrige les défauts, on documente.
7. **Encodage d'affichage** : Python avec `sys.stdout.reconfigure(encoding="utf-8")` pour tout affichage de texte local.
