# Note Technique — Couche d'Accessibilité Linguistique SAFINUM 2026

> **Projet** : SAFINUM Innovate Challenge 2026  
> **Livrable 4** : Architecture, intégration, dépendances et limites  
> **Cible** : `https://safinum.cm/hackathon-test` (Safinum Pay)

---

## 1. Architecture Globale

La solution est conçue selon un modèle en double anneau (Extension Navigateur + Backend Souverain Local), garantissant une accessibilité maximale sans jamais compromettre le système bancaire hôte.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Navigateur Web (Client)                         │
│                                                                        │
│   ┌───────────────────────────┐      ┌─────────────────────────────┐   │
│   │ Site Cible (Safinum Pay)  │      │ Widget Accessibilité        │   │
│   │ • SPA Vue 3 / Inertia.js  │      │ • Encapsulation Shadow DOM  │   │
│   │ • Nœuds textuels natifs   │      │ • Isolation CSS absolue     │   │
│   └─────────────┬─────────────┘      └──────────────┬──────────────┘   │
│                 │                                   │                  │
│                 ▼                                   ▼                  │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │ Content Script MV3 (MutationObserver debouncé + Masquage)      │   │
│   │ • Détection des entités sensibles                              │   │
│   │ • Substitutions par jetons __SAFE_TYPE_N__                     │   │
│   │ • Mode Démo Hors Ligne embarqué (catalogue_offline.json)       │   │
│   └────────────────────────────────┬───────────────────────────────┘   │
└────────────────────────────────────┼───────────────────────────────────┘
                                     │ Requêtes HTTP JSON (asynchrones)
                                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      Backend Local (FastAPI / Python)                  │
│   • /health : Statut du service et des catalogues                      │
│   • /languages : Métadonnées linguistiques (Duala, Bassa'a, etc.)      │
│   • /translate/batch : Pipeline strict masquage -> mémoire -> glossaire│
│   • /feedback : Enregistrement des révisions et validations humaines   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Intégration et Indépendance du Site Cible

1. **Zéro Modification Source** : Aucun script, feuille de style ou balise du site hôte n'est altéré.
2. **Encapsulation Shadow DOM** : L'interface utilisateur du widget (sélecteur de langue, indicateurs d'intégrité, affichage bilingue) réside dans un `ShadowRoot` isolé (`attachShadow({ mode: 'open' })`). Aucune règle Tailwind CSS du site ne peut fuiter vers le widget, et réciproquement.
3. **Surveillance Non-Destructive** : Un `MutationObserver` surveille le conteneur racine `#app` avec un anti-rebond (*debounce*) de 160 ms pour intercepter les transitions de vue déclenchées par Inertia.js sans provoquer de boucle de ré-observation infinie.

---

## 3. Préservation de l'Intégrité Financière (Règle d'Or)

Toute altération de montants, frais, bénéficiaires ou références constituerait un défaut majeur (éliminatoire lors du contrôle `normalizeValue` du jury).  
Le pipeline applique les garde-fous suivants :

1. **Expressions Régulières Déterministes** : Identification systématique des montants en FCFA/XAF/EUR, pourcentages, numéros de téléphone (+237), numéros de compte (format CM) et références d'opération (`SAF-2026-*`).
2. **Substitutions par Jetons Typés** : Les valeurs sensibles sont extraites et remplacées par des balises délimitées (`__SAFE_AMOUNT_0__`, `__SAFE_TEL_1__`, etc.).
3. **Restauration et Contrôle Multi-Ensemble** : Avant toute réinjection dans le DOM, le système compare le sac de jetons en entrée et en sortie ($Tokens_{in} == Tokens_{out}$).
4. **Repli Source Immédiat** : En cas de décalage ou d'échec de désérialisation, le texte original est restauré sans altération.

---

## 4. Dépendances & Empreinte Légère

Conformément aux règles permanentes (`AGENTS.md`) :
- **Extension Navigateur** : Pur JavaScript (Vanilla ES6), **zéro dépendance externe**, zéro bundler complexe. Empreinte totale de l'extension : **< 80 Ko**.
- **Backend Local** :
  - `FastAPI` (0.115+) : Framework API REST haute performance.
  - `Uvicorn` : Serveur ASGI léger.
  - `Pydantic` (v2) : Typage et validation stricte des schémas de données.
  - Aucune dépendance de réseau externe lors du fonctionnement standard.

---

## 5. Limites et Évolutions Futures

1. **Formulaires de saisie utilisateur** : Par conception sécuritaire, les champs `<input>` et `<textarea>` où l'utilisateur saisit des montants ou des téléphones ne sont pas traduits pour éviter d'interférer avec le modèle de données réactif de Vue 3. Seuls les libellés (`<label>`), aides, boutons et avertissements sont traduits.
2. **Synthèse vocale (TTS)** : Pour les populations non lectrices, l'étape suivante consiste à raccorder le lecteur audio aux modèles wav déjà disponibles dans le projet Mélac (`shared/data/duala/audio/` et `shared/data/bassa/audio/`).
