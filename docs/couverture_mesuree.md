# Couverture de traduction mesurée — SAFINUM 2026

- **Date de mesure** : `2026-11-16 17:23:31`
- **Methode** : Playwright Edge, profil vierge — collecte sur textes FR natifs
- **URL cible** : `https://safinum.cm/hackathon-test`
- **Langues analysees** : Duálá (`dua`) et Ɓàsàa (`bas`)
- **Regles** : aucun catalogue modifie ; valeur « non mesuré » si navigation impossible

> [!NOTE]
> **Memoire** = chaine FR collectee trouvee dans `catalogue/translations.csv` (source exacte ou partielle).
> **Glossaire** = chaine FR non dans la memoire mais contenant au moins un terme de `catalogue/glossaire.csv`.
> **Non couvert** = absente des deux. Ces chaines ne peuvent pas etre traduites par l'extension.

---

## 1. Couverture par écran — Interface FR (textes source natifs du site)

| Écran | Visibles | dua Mém. | dua Glos. | dua NC | dua% | bas Mém. | bas Glos. | bas NC | bas% |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Tableau de bord (Solde) | 37 | 31 | 0 | 6 | 83% | 31 | 0 | 6 | 83% |
| Consultation des frais | 32 | 30 | 0 | 2 | 93% | 30 | 0 | 2 | 93% |
| Beneficiaire | 28 | 26 | 0 | 2 | 92% | 26 | 0 | 2 | 92% |
| Recapitulatif | 30 | 27 | 0 | 3 | 90% | 27 | 0 | 3 | 90% |
| Recu | 28 | 25 | 0 | 3 | 89% | 25 | 0 | 3 | 89% |
| Alertes / Erreurs | 57 | 37 | 0 | 20 | 64% | 37 | 0 | 20 | 64% |
| **TOTAL (tous écrans, dédup.)** | **91** | **70** | **0** | **21** | **76%** | **70** | **0** | **21** | **76%** |

---

## 2. Chaines non couvertes par écran — Duálá (`dua`)

### Tableau de bord (Solde)

- `Amina Ngo Bell`
- `-12 500 FCFA`
- `+180 000 FCFA`
- `+50 000 FCFA`
- `-7 500 FCFA`
- `CM 001 2345 6789 01`

### Consultation des frais

- `Amina Ngo Bell`
- `CM 001 2345 6789 01`

### Beneficiaire

- `Amina Ngo Bell`
- `CM 001 2345 6789 01`

### Recapitulatif

- `Amina Ngo Bell`
- `Jean-Paul Mbarga`
- `CM 001 2345 6789 01`

### Recu

- `Amina Ngo Bell`
- `Jean-Paul Mbarga`
- `CM 001 2345 6789 01`

### Alertes / Erreurs

- `Amina Ngo Bell`
- `-12 500 FCFA`
- `+180 000 FCFA`
- `+50 000 FCFA`
- `-7 500 FCFA`
- `CM 001 2345 6789 01`
- `Panneau jury`
- `Outil interne Safinum — non fourni aux équipes`
- `Contrôle`
- `Soumissions`
- `Couverture`
- `Injecter du contenu inédit`
- `Texte affiché dans la page après chargement. L'extension doit le traduire sans hook dédié.`
- `Français`
- `English`
- `Injecter`
- `Aucun contenu injecté.`
- `Appliquer`
- `Vérifier l'étape maintenant`
- `Réinitialiser le test`

---

## 3. Chaines non couvertes par écran — Ɓàsàa (`bas`)

### Tableau de bord (Solde)

- `Amina Ngo Bell`
- `-12 500 FCFA`
- `+180 000 FCFA`
- `+50 000 FCFA`
- `-7 500 FCFA`
- `CM 001 2345 6789 01`

### Consultation des frais

- `Amina Ngo Bell`
- `CM 001 2345 6789 01`

### Beneficiaire

- `Amina Ngo Bell`
- `CM 001 2345 6789 01`

### Recapitulatif

- `Amina Ngo Bell`
- `Jean-Paul Mbarga`
- `CM 001 2345 6789 01`

### Recu

- `Amina Ngo Bell`
- `Jean-Paul Mbarga`
- `CM 001 2345 6789 01`

### Alertes / Erreurs

- `Amina Ngo Bell`
- `-12 500 FCFA`
- `+180 000 FCFA`
- `+50 000 FCFA`
- `-7 500 FCFA`
- `CM 001 2345 6789 01`
- `Panneau jury`
- `Outil interne Safinum — non fourni aux équipes`
- `Contrôle`
- `Soumissions`
- `Couverture`
- `Injecter du contenu inédit`
- `Texte affiché dans la page après chargement. L'extension doit le traduire sans hook dédié.`
- `Français`
- `English`
- `Injecter`
- `Aucun contenu injecté.`
- `Appliquer`
- `Vérifier l'étape maintenant`
- `Réinitialiser le test`

---

## 4. Interface EN (anglais) — Comportement observé

| Écran | Visibles EN | dua Mém. | dua NC | bas Mém. | bas NC |
|---|:---:|:---:|:---:|:---:|:---:|
| Tableau de bord (Solde) | 37 | 31 | 6 | 31 | 6 |
| Consultation des frais | 32 | 30 | 2 | 30 | 2 |
| Beneficiaire | 28 | 26 | 2 | 26 | 2 |
| Recapitulatif | 30 | 27 | 3 | 27 | 3 |
| Recu | 28 | 25 | 3 | 25 | 3 |
| Alertes / Erreurs | 57 | 37 | 20 | 37 | 20 |

> [!IMPORTANT]
> Le catalogue est indexé sur le **français**. Si le site bascule en anglais,
> les sources changent de forme et la couverture chute mécaniquement.
> Les données financières (montants, références) restent protégées indépendamment.

> Note : Bouton EN détecté et actif.

---

## 5. Notes méthodologiques

1. **Collecte sans extension** : navigation en FR natif pour obtenir les textes source réels du site.
2. **Exclusions automatiques** : montants, références (`SAF-XXXX-YYYY`), numéros de téléphone,
   dates, chiffres isolés, chaînes < 3 caractères.
3. **Correspondance mémoire** : comparaison insensible à la casse avec `catalogue/translations.csv`
   (correspondance exacte ou partielle — la source catalogue doit être contenue dans la chaîne).
4. **Correspondance glossaire** : présence d'au moins un terme du glossaire (≥ 4 car.) dans la chaîne.
5. **Non couvert** : absent de la mémoire ET sans terme du glossaire.
   Ces chaînes nécessiteraient l'ajout d'entrées dans le catalogue pour être traduites.
6. **Aucune modification** de catalogue effectuée.

---

*Rapport généré le 2026-11-16 17:23:31 par `scripts/mesurer_couverture.py` — branche `amelioration`.*