# Architecture Technique & Spécifications — SAFINUM 2026

> **Projet** : Couche d'accessibilité linguistique pour services financiers numériques  
> **Composants** : Extension Navigateur Manifest V3 + API Locale FastAPI + Catalogue Hors-Ligne  
> **Contrainte critique** : Préservation absolue de l'intégrité financière et indépendance totale du site cible.

---

## 1. Vue d'Ensemble & Principes Directeurs

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ Site Cible : https://safinum.cm/hackathon-test (SPA Vue 3 / Inertia)                   │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │ DOM TextNodes (Observation sans altération)
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ Extension Navigateur (Manifest V3)                                                     │
│  ┌───────────────────────┐   ┌──────────────────────────┐   ┌───────────────────────┐  │
│  │   MutationObserver    │──▶│ Pipeline Masquage Jetons │──▶│ Résolution Traduction │  │
│  │ (Debounce 200ms, #app)│   │  Regex & Vérification    │   │ Local Cache / Backend │  │
│  └───────────────────────┘   └─────────────┬────────────┘   └───────────┬───────────┘  │
│                                            │                            │              │
│                                            ▼ Restauration stricte       ▼              │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐  │
│  │ UI Rendu Bilingue & Widget Accessibilité (Shadow DOM isolé, Mode Démo Hors Ligne)│  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │ HTTP JSON (Isolated World)
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ Backend Local FastAPI (http://localhost:8000)                                          │
│  • Catalogue Mémoire & Glossaire (Validation Humaine)                                  │
│  • Moteur Traduction Contenu Inédit (Marqué machine_suggested)                         │
│  • Endpoints : /health, /languages, /translate/batch, /feedback                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

1. **Zéro intrusion** : Aucune modification du code source cible, ni interception intrusive des requêtes applicatives.
2. **Étanchéité visuelle** : Le widget d'accessibilité est isolé dans un **Shadow DOM** (`mode: 'open'`) pour empêcher toute collision CSS avec Tailwind.
3. **Sécurité et intégrité** : Montants, devises, numéros de compte, téléphones, références et noms de tiers sont protégés par jetons inviolables et jamais traduits.

---

## 2. Mécanisme d'Extraction & Injection DOM

### 2.1 Périmètre d'Extraction
- **Nœuds cibles** : `Node.TEXT_NODE` (longueur trimmed > 1, excluant les espaces pures).
- **Attributs cibles** : `placeholder`, `aria-label`, `title`, `alt`.
- **Balises exclues** : `<script>`, `<style>`, `<svg>`, `<code>`, `<pre>`, `<noscript>`, et tout élément portant `data-no-translate` ou le widget de l'extension.

### 2.2 Gestion des Montants Morcelés
Dans Vue 3, un montant et sa devise peuvent être éclatés entre plusieurs balises (ex: `<span>25 000</span> <span>FCFA</span>`).  
- **Règle** : L'extraction analyse les nœuds texte dans leur contexte parent. Si un conteneur inline (`<span>`, `<p>`, `<dd>`) contient un motif monétaire découpé, le nœud parent est marqué comme bloc monétaire atomique (`data-safinum-protected="true"`) et préservé intégralement.

### 2.3 Observation Réactive & Anti-Rebond
- Surveillance via `MutationObserver` sur `#app` (`childList: true, subtree: true, characterData: true`).
- **Debounce** de **180 ms** pour regrouper les mutations lors des transitions d'étapes Inertia.js.
- **Dédoublonnage** : Marquage des nœuds traités via `node._safinum_src = originalText` et attribut `data-safinum-translated="true"` sur le parent direct pour bannir tout cycle infini de ré-observation.

---

## 3. Moteur d'Intégrité Financière (Masquage & Restauration)

### 3.1 Expressions Régulières de Détection des Entités Sensibles

| Entité | Expression Régulière (JavaScript / Python) | Exemple détecté |
|---|---|---|
| **Montant + Devise** | `\b\d{1,3}(?:[\s\u00A0\u202F]\d{3})*(?:[,\.]\d+)?\s*(?:FCFA|XAF|EUR|USD|XOF|\$)\b` | `250 000 FCFA`, `12 500 FCFA` |
| **Pourcentage & Frais** | `\b\d+(?:[,\.]\d+)?\s*%\b` | `1,5 %`, `2 %` |
| **Numéro de Compte** | `\bCM\s*\d{3}\s*\d{4}\s*\d{4}\s*\d{2}\b` | `CM 001 2345 6789 01` |
| **Téléphone Cameroun** | `(?:\+237\s*)?[26]\s*(?:\d\s*){7}\d` | `+237 6 99 12 34 56` |
| **Référence Unique** | `\bSAF-2026-[A-Z0-9]{5,8}\b` | `SAF-2026-X7Y8Z9` |
| **Bénéficiaire / Tiers** | Noms indexés du contexte : `\b(Jean-Paul Mbarga|Amina Ngo Bell|Amina)\b` | `Jean-Paul Mbarga` |
| **Dates Financières** | `\b\d{1,2}\s+(?:janv\.|févr\.|mars|avr\.|mai|juin|juil\.|août|sept\.|oct\.|nov\.|déc\.)\s+\d{4}\b` | `05 nov. 2026` |

### 3.2 Protocole de Masquage et Vérification Strict
1. **Remplacement par Jetons Déterministes** : Les entités sensibles sont substituées par des jetons réservés :  
   `{{__SAFE_NUM_0__}}`, `{{__SAFE_TEL_1__}}`, `{{__SAFE_REF_2__}}`.
2. **Traduction de la structure sémantique uniquement**.
3. **Vérification d'Intégrité (Multi-ensemble)** :  
   Avant réinjection, calcul du multi-ensemble (sac de jetons) :  
   $$\text{Tokens}_{\text{in}} == \text{Tokens}_{\text{out}}$$  
   Si un jeton manque, est dupliqué ou corrompu $\rightarrow$ **Abandon immédiat, retour au texte source non altéré**.
4. **Restauration** : Remplacement des jetons par leurs valeurs brutes exactes (aucun reformatage).

---

## 4. Chaîne de Résolution & Statuts de Traduction

La résolution d'un segment textuel suit un ordonnancement strict en 4 paliers :

```
[Texte Source Masqué]
          │
          ├──▶ 1. Mémoire de Traduction (Cache local / translations.csv)
          │       Statut : human_validated ──▶ Affichage direct
          │
          ├──▶ 2. Glossaire Financier Terminologique (glossaire.csv)
          │       Statut : human_validated ──▶ Substitution contrôlée
          │
          ├──▶ 3. API Traduction Automatique (FastAPI NMT / LLM)
          │       Statut : machine_suggested ──▶ Soumis aux règles spéciales d'affichage
          │
          └──▶ 4. Repli Sécurisé (Source Fallback)
                  Texte original FR/EN conservé si échec réseau, absence ou anomalie jeton.
```

### Règle Spéciale Écrans Critiques (Sécurité & Récapitulatifs)
Pour les alertes de sécurité (`SECURITY_001`, `SECURITY_002`), l'étape 4 (Récapitulatif) et l'étape 5 (Reçu) :  
- **Aucune traduction `machine_suggested` n'est affichée seule**.
- L'affichage bilingue côte-à-côte ou sous-titré avec le texte source original est **obligatoire**.

---

## 5. Expérience Utilisateur (UX) & Accessibilité

- **Widget Flottant (Shadow DOM)** :
  - Sélecteur de langue cible : Duala (`dua`), Bassa'a (`bas`), Ghomala' (`bbj`), Ewondo (`ewo`).
  - Commutateur Mode Hors-Ligne (Démo Jury) / Mode En Ligne (API).
  - Indicateur visuel d'état de traduction :
    - Vert : `human_validated` (validé par locuteur).
    - Ambre : `machine_suggested` (généré automatiquement, vérification recommandée).
- **Affichage Bilingue Sécurisé** :
  - Survol (*hover tooltip*) ou affichage en sous-texte discret (police 80%, opacité 75%) présentant la phrase source pour écarter tout contresens financier.

---

## 6. Schéma des Fichiers Catalogue

### 6.1 `catalogue/translations.csv`
```csv
cle,source,langue,cible,statut,validateur_code,date,commentaire
dash_bal_label,"Solde disponible",dua,"Mbolo ma moni",human_validated,VAL_DUA_01,2026-11-13,"Terme validé"
trans_fee_free,"Gratuit",bas,"Ndutu to yom",human_validated,VAL_BAS_01,2026-11-13,"Frais nuls"
sec_warn_new_benef,"Ce bénéficiaire n'a jamais été utilisé sur ce compte.",bbj,"...",draft,,2026-11-13,""
```

### 6.2 `catalogue/glossaire.csv`
```csv
terme_source,langue,terme_cible,contexte,statut,notes
"Solde",dua,"Molo ma moni","Banque",human_validated,"Montant disponible"
"Frais",bas,"Ntomb","Transfert",human_validated,"Commission"
"Bénéficiaire",bbj,"Mbe fə","Paiement",human_validated,"Destinataire"
```

---

## 7. Plan de Travail Priorisé (< 17 Heures Restantes)

*Échéance : 14 novembre 2026, 23h59 (Cameroun)*

| Étape | Description & Livrable | Durée Estimée | Fin Prévue |
|---|---|---|---|
| **Phase 1** | Spécification API (`openapi.yaml`) et validation de conformité | 1 h 00 | 08h00 |
| **Phase 2** | Catalogues CSV/JSON (79 chaînes complètes en Duala & Bassa'a) | 2 h 30 | 10h30 |
| **Phase 3** | Backend FastAPI (`/health`, `/languages`, `/translate/batch`, `/feedback`) | 2 h 30 | 13h00 |
| **Phase 4** | Extension MV3 (Content Script, Masquage Jetons, Widget Shadow DOM) | 3 h 30 | 16h30 |
| **Phase 5** | Tests E2E sur https://safinum.cm/hackathon-test (Contrôle jury `normalizeValue`) | 2 h 00 | 18h30 |
| **Phase 6** | Note technique finale + Enregistrement vidéo de démo (<= 3 min) | 3 h 00 | 21h30 |
| **Phase 7** | Revue finale, package zip de soumission et livraison | 1 h 30 | 23h00 |
