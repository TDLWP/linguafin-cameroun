# Mesure et Audit de l'Accessibilité Numérique du Widget SAFINUM (WCAG 2.1 AA)

> **Document de référence** : Mesures réelles avant et après mise en conformité de la couche d'accessibilité linguistique (Shadow DOM).  
> **Outils d'audit** : `axe-playwright-python 0.1.8`, `axe-core`, Microsoft Edge (Chromium) sous Windows 11, suites de tests Playwright.  
> **Date de mesure** : 16 novembre 2026.  
> **Environnements testés** : `tests/mock_bank.html` (local) et `https://safinum.cm/hackathon-test` (plateforme cible).

---

## 1. Méthodologie et Périmètre d'Évaluation

L'évaluation porte sur le widget d'accessibilité linguistique SAFINUM injecté dans un **Shadow DOM ouvert** afin d'assurer son isolation vis-à-vis des feuilles de styles du site hôte.

Conformément aux règles du projet et au standard international **WCAG 2.1 niveau AA**, les critères suivants ont été audités :
1. **Dimensions des zones cliquables (Target Size)** : Seuil minimal recommandé de 44 × 44 px (WCAG 2.5.5 / 2.5.8).
2. **Contraste des couleurs** : Ratio minimal de **4,5:1** pour le texte normal et **3:1** pour les composants d'interface (WCAG 1.4.3 / 1.4.11).
3. **Navigation clavier complète & Piège de focus (Focus Trap)** : Navigation séquentielle (Tab, Maj+Tab), raccourcis (Entrée, Espace, Échap) et cycle fermé dans le dialogue.
4. **Indicateurs de focus visuels** : Visibilité contrastée du focus sur tous les composants interactifs.
5. **Rôles et libellés sémantiques ARIA** : Structuration en région (`role="region"`), dialogue (`role="dialog"`), interrupteurs et libellés accessibles.
6. **Annonces dynamiques `aria-live` non répétitives** : Transmission vocale des changements d'état sans pollution sonore ni répétition intempestive.
7. **Affichage sur écran étroit (360 px de large)** : Absence totale de défilement horizontal ou de troncature (WCAG 1.4.10 Reflow).
8. **Adaptation au zoom écran 200 %** : Lisibilité et accessibilité intégrale des contrôles dans un viewport vertical réduit (WCAG 1.4.4).
9. **Respect des préférences utilisateur (Reduced Motion)** : Suppression des animations et transitions lorsque `prefers-reduced-motion: reduce` est actif (WCAG 2.3.3).

---

## 2. Relevé des Violations et Mesures Réelles (Avant vs Après)

Les données ci-dessous proviennent des exécutions réelles consignées dans `docs/raw_accessibility_audit_before.json` et `docs/raw_accessibility_audit_after.json`.

### 2.1 Cibles tactiles et zones cliquables (Target Size >= 44 px)

| Composant | ID / Sélecteur | Avant correction | Statut Avant | Après correction | Statut Après |
|---|---|---|---|---|---|
| **Badge flottant déclencheur** | `#badge` | 151.1 × 44.8 px | ✅ Conforme | **155.1 × 44.8 px** | ✅ Conforme (>= 44 px) |
| **Bouton fermeture** | `#btnClose` | 21.1 × 29.6 px | ❌ **Non conforme** | **44.0 × 44.0 px** | ✅ Conforme (>= 44 px) |
| **Sélecteur de langue** | `#langSelect` | 306.4 × 33.6 px | ❌ **Non conforme** (h < 44 px) | **286.4 × 44.0 px** | ✅ Conforme (h >= 44 px) |
| **Bouton bascule traduction** | `#btnToggleTranslate` | 306.4 × 37.6 px | ❌ **Non conforme** (h < 44 px) | **286.4 × 44.0 px** | ✅ Conforme (h >= 44 px) |
| **Interrupteur bilingue** | `#checkBilingual` (`.switch`) | 38.0 × 22.0 px | ❌ **Non conforme** | **48.0 × 44.0 px** | ✅ Conforme (>= 44 px) |
| **Interrupteur expérimental** | `#checkExperimental` (`.switch`) | 38.0 × 22.0 px | ❌ **Non conforme** | **48.0 × 44.0 px** | ✅ Conforme (>= 44 px) |

*Correction appliquée* : Intégration de `min-width: 44px; min-height: 44px;` sur tous les boutons, sélecteurs et zones tactiles des interrupteurs.

---

### 2.2 Ratios de contraste des couleurs (Seuil WCAG AA >= 4,5:1)

| Composant testé | Texte (FG) | Fond (BG) | Ratio calculé | Seuil exigé | Statut |
|---|---|---|---|---|---|
| **Badge texte sur fond cyan** | `#021226` (rgb 2, 18, 38) | `#00BFFF` (rgb 0, 191, 255) | **8.86:1** | 4.5:1 | ✅ Conforme (AAA) |
| **Bouton fermeture** | `#FFFFFF` (rgb 255, 255, 255) | `#1E293B` (rgb 30, 41, 59) | **14.63:1** | 4.5:1 | ✅ Conforme (AAA) |
| **Libellés de section** | `#CBD5E1` (rgb 203, 213, 225) | `#0A192F` (rgb 10, 25, 47) | **11.86:1** | 4.5:1 | ✅ Conforme (AAA) |
| **Bandeau d'avertissement IA** | `#FEF3C7` (rgb 254, 243, 199) | `#451A03` (rgb 69, 26, 3) | **13.45:1** | 4.5:1 | ✅ Conforme (AAA) |
| **Bouton de bascule actif** | `#021226` (rgb 2, 18, 38) | `#10B981` (rgb 16, 185, 129) | **7.41:1** | 4.5:1 | ✅ Conforme (AAA) |
| **Titre du panneau** | `#00BFFF` (rgb 0, 191, 255) | `#0A192F` (rgb 10, 25, 47) | **8.30:1** | 4.5:1 | ✅ Conforme (AAA) |

*Correction appliquée* : Remplacement des teintes de texte secondaire `#94A3B8` (qui offraient un contraste limite) par `#CBD5E1` (offrant un contraste de 11.86:1 sur le fond sombre `#0A192F`).

---

### 2.3 Navigation clavier complète et Focus Trap

| Fonctionnalité | Avant correction | Après correction | Statut |
|---|---|---|---|
| **Prise de focus initiale** | Reçue sur `#badge` (`tabindex="0"`) | Reçue sur `#badge` (`tabindex="0"`, `aria-haspopup="dialog"`) | ✅ Conforme |
| **Ouverture via `[Entrée]`** | Panneau ouvert, focus sur `langSelect` | Panneau ouvert, focus sur `btnClose` | ✅ Conforme |
| **Fermeture via `[Échap]`** | Panneau fermé, focus sur `badge` | Panneau fermé, focus restauré sur `badge` | ✅ Conforme |
| **Ouverture via `[Espace]`** | Panneau ouvert | Panneau ouvert | ✅ Conforme |
| **Séquence [Tab] (Focus Trap)** | `['btnToggleTranslate', 'checkBilingual', 'checkExperimental', 'badge', None]` *(Fuite hors du widget)* | `['langSelect', 'btnToggleTranslate', 'checkBilingual', 'checkExperimental', 'btnClose', 'langSelect']` *(Boucle fermée stricte)* | ✅ **Piège de focus conforme** |
| **Séquence [Maj+Tab] (Arrière)** | `[None, 'badge', 'checkExperimental']` *(Fuite hors du widget)* | `['btnClose', 'checkExperimental', 'checkBilingual']` *(Cycle arrière fermé)* | ✅ **Cycle arrière conforme** |
| **Focus visible** | Absent sur les interrupteurs switch, faible sur les boutons | Anneau de focus visible contrasté : `outline: 2px solid #00BFFF; outline-offset: 2px;` sur tous les focusables | ✅ Conforme |

---

### 2.4 Affichage mobile responsive (360 px) et Zoom 200 %

| Critère | Mesure Avant | Statut Avant | Mesure Après | Statut Après |
|---|---|---|---|---|
| **Largeur d'écran 360 px** | Largeur panneau : 331.2 px, `right: 18px` (Total 349.2 px), débordement horizontal | ❌ Débordement | Largeur : **320.0 px**, `right: 12px`, `max-width: calc(100vw - 24px)`. Aucun débordement. | ✅ **Parfaitement inscrit sans scrollbar** |
| **Zoom 200 % (Viewport 400 px haut)** | Hauteur panneau : 417 px, `overflow-y` absent | ❌ Contrôles inférieurs rognés | Hauteur bornée à `max-height: calc(100vh - 80px); overflow-y: auto;` | ✅ **Accessible et défilable au clavier** |

---

### 2.5 Préférence de réduction des animations (`prefers-reduced-motion`)

| Configuration | Mesure Avant | Mesure Après |
|---|---|---|
| **`prefers-reduced-motion: reduce`** | `badge.transition = "transform 0.18s, box-shadow 0.18s"` (actif) | `badge.transition = "none 1e-06s"` (désactivé) |
| **Animation ouverture panneau** | `@keyframes popIn 0.2s` (actif) | `animation: none !important;` (désactivé) |

*Correction appliquée* : Ajout de la media query `@media (prefers-reduced-motion: reduce)` désactivant strictement toute animation et transition pour préserver les utilisateurs sujets aux troubles vestibulaires.

---

### 2.6 Annonces dynamiques ARIA-Live non répétitives

| Composant | Avant correction | Après correction |
|---|---|---|
| **Boîte d'intégrité / statistiques** | `aria-live="polite"` sur tout le bloc `.status-box` | Attribut `aria-live` retiré de `.status-box` pour éviter le spam lors des réévaluations DOM |
| **Live Announcer dédié** | Absent | Présent : `<div id="liveAnnouncer" class="sr-only" aria-live="polite" aria-atomic="true"></div>` |
| **Gestion des répétitions** | Aucune mémorisation | Mémorisation de `lastAnnouncedMessage` + debounce 200 ms. Seuls les changements d'état délibérés (choix de langue, bascule de mode) sont annoncés. |

---

## 3. Résultats de l'Analyse Axe-Core Automatisée

### 3.1 Sur `tests/mock_bank.html`
- **Violations sur le widget SAFINUM** : **0 violation**.
- **Violations globales de la page hôte de test** : 2 règles modérées concernant la structure native de la page mock (`page-has-heading-one`, `landmark-one-main`), sans rapport avec le widget d'accessibilité.

### 3.2 Sur le site cible `https://safinum.cm/hackathon-test`
- **Violations sur le widget SAFINUM** : **0 violation bloquante, critique ou sérieuse**.
- **Violations natives du site cible distant** :
  - `label` (critique) : champs de saisie du panneau jury du site distant sans balise label associée.
  - `select-name` (critique) : élément select du panneau jury distant sans libellé accessible.
  - *Rappel de la règle absolue* : Le site cible distant n'est pas modifié (`aucune modification du site cible`). Le widget SAFINUM est strictement autonome et exempt de ces anomalies.

---

## 4. Ce qui n'est pas testé (« Non mesuré »)

Conformément à la règle n°4 de transparence et véracité des métriques :
- **Lecteur d'écran réel sous Windows (NVDA, Narrator)** : **non mesuré** (les tests sont exécutés par moteur automatisé Playwright Chromium/Edge et l'API DOM d'Axe-core ; aucun testeur humain équipé d'un lecteur d'écran physique n'a été déployé).
- **Lecteur d'écran macOS/iOS (VoiceOver)** : **non mesuré**.
- **Afficheur braille dynamique** : **non mesuré**.

---

## 5. Synthèse de Conformité WCAG 2.1 AA

| Règle WCAG | Intitulé | Avant | Après |
|---|---|---|---|
| **1.4.3 (AA)** | Contraste minimal (4,5:1) | ⚠️ Partiel (5.37:1 à la limite) | ✅ **Conforme (7.41:1 à 14.63:1)** |
| **1.4.4 (AA)** | Redimensionnement du texte (200 %) | ❌ Débordement vertical | ✅ **Conforme (`overflow-y: auto`)** |
| **1.4.10 (AA)** | Reflow (360 px mobile) | ❌ Débordement horizontal | ✅ **Conforme (320 px + 12 px marge)** |
| **2.1.1 (A)** | Accessibilité au clavier | ⚠️ Fuite de focus en modal | ✅ **Conforme (Focus Trap complet)** |
| **2.1.2 (A)** | Pas de piège au clavier (sortie Échap) | ✅ Conforme | ✅ **Conforme** |
| **2.3.3 (AAA/Best Practice)** | Animations déclenchées par l'utilisateur | ❌ Actives en reduced-motion | ✅ **Conforme (Désactivées)** |
| **2.4.7 (AA)** | Focus visible | ❌ Absent sur switch | ✅ **Conforme (`outline` cyan 2px)** |
| **2.5.5 / 2.5.8 (AA/AAA)** | Taille des cibles tactiles (44 px) | ❌ 4 éléments < 44 px | ✅ **100 % des cibles >= 44 px** |
| **4.1.2 (A)** | Nom, rôle et valeur (ARIA) | ⚠️ Manque `aria-haspopup` | ✅ **Conforme (`region`, `dialog`, `liveAnnouncer`)** |
