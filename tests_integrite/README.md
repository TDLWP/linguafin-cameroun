# Jeu de test d'intégrité financière (figé, v1.0 — 18/11/2026)

## Note d'origine et traçabilité
Ce jeu de données de test figé (version 1.0, 18 novembre 2026) a été conçu pour certifier l'intégrité financière absolue, la confidentialité des secrets et la robustesse face aux injections de données adversariales dans le cadre de la couche d'accessibilité linguistique SAFINUM 2026.
- **Origine des cas** :
  - **30 chaînes réelles** extraites fidèlement du relevé officiel d'audit du 13 novembre 2026 sur le portail de test (marques, noms d'utilisateurs, dates, frais, messages critiques et de sécurité en français et en anglais).
  - **61 cas hostiles** rédigés à la main pour éprouver les cas limites : formats de montants variés, espaces insécables (`\u00A0`, `\u202F`, `\u2007`), espaces de largeur nulle (`\u200B`), chiffres pleine chasse (`\uff10-\uff19`) et arabo-indiens (`\u0660-\u0669`), montants en toutes lettres en français et en anglais, téléphones camerounais et internationaux, comptes bancaires et IBAN, références composites, dates/heures multilingues, URL et adresses e-mail, noms de bénéficiaires intégrant des termes du glossaire, faux jetons injectés (`__SAFE_*__`, `⟦0⟧`), variables de gabarit (`{name}`, `{{amount}}`, `%s`), codes secrets critiques (OTP, PIN, passwords) et test de charge (2 000 chiffres).

## Règles de l'oracle (indépendant du code testé)
1. Chaque valeur listée dans `protected` apparaît le même nombre de fois en sortie qu'en entrée, caractère pour caractère.
2. Aucun chiffre (\p{Nd}) n'est ajouté ni perdu.
3. `secret` (OTP/PIN) : sortie identique à l'entrée (jamais modifié ni transmis). `pure_values` (date seule, marque) : sortie identique.
4. Affichage bilingue « source [proposition] » : la source doit être intacte ; un chiffre inventé dans la proposition = ECHEC ; une valeur manquante = AVERTISSEMENT.
5. `--strict` compte (hors score) les contenus inconnus modifiés : c'est une politique, pas une règle de sécurité.
Les cas `human_check` (négations, conditions) ne sont pas jugés par la machine : à faire relire par un locuteur.

## Lancer
### 1. En Python (Rejeu complet des trois chemins et suite unittest)
```bash
python scripts/test_integrite_figee.py
python -m unittest tests/test_integrite_figee.py
```
Le script teste :
- **Chemin (a)** : Pipeline `backend/protect.py` (masquage -> pseudo-traduction hostile -> restauration + `verify_integrity`).
- **Chemin (b)** : API locale `POST /translate/batch` (sources française et anglaise).
- **Chemin (c)** : Extension hors-ligne via Node/jsdom (si jsdom est installé).

### 2. En JavaScript / Node.js
```bash
node run.js adapters/safinum_pseudo.js                       # couche Safinum, pire cas : tout texte « traduit »
# Note : Pour dom_extension.js, jsdom (~15 à 20 Mo avec dépendances) est requis :
# npm install jsdom
node run.js adapters/dom_extension.js --ext ../extension --json sortie.json
```
La sortie finit par « Total: N OK, M ECHEC(S), W AVERTISSEMENT(S) ».

## Limites
jsdom n'est pas Chrome ; seul le chemin hors ligne est testé (réseau bloqué) ; les noms en texte libre ne sont détectés que par heuristique (après étiquette ou préposition) ; pas de mesure de qualité linguistique ; aucun test des restrictions réseau de Chrome.
