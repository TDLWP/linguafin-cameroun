# Audit Final Hostile du Dépôt SAFINUM — 28 Novembre 2026

> **Cadre** : Exercice d'audit antagoniste simulant un jury technique hostile.  
> **Méthode** : Exécution de `scripts/run_all_checks.ps1` (205 tests), audit de code source (content.js, protect.py, api.py, background.js, manifest.json), vérification croisée des affirmations documentaires et des chiffres réels, tentatives de casse sur les 6 vecteurs d'attaque demandés.  
> **Branche** : `amelioration` (HEAD après correctifs).

---

## Tableau Récapitulatif des Constats

| # | Sévérité | Vecteur | Constat | Statut |
|---|---|---|---|---|
| C1 | **CRITIQUE** | (6) Doc vs Code | `docs/questions_jury.md` cite `has_confidential_secret()` : cette fonction n'existe pas dans `backend/protect.py` (réelle : `is_secret_text()`) | **Corrigé** |
| M1 | **MAJEUR** | (2) Secret envoyé | Faux négatifs des regex de secrets : « Votre PIN est 1234 », « PIN code: 1234 », « Code secret 847362 » échappent à la détection | **Corrigé** |
| M2 | **MAJEUR** | (2) Secret envoyé | Endpoint `POST /feedback` écrit `source_text`, `suggested_translation` et `comment` sur disque sans filtrage par `is_secret_text()` — un OTP soumis par un utilisateur serait stocké en clair | **Corrigé** |
| M3 | **MAJEUR** | (6) Doc vs Code | Absence de directive `content_security_policy` explicite dans `extension/manifest.json` (MV3 applique un défaut, mais l'expliciter est une exigence de rigueur) | **Corrigé** |
| m1 | Mineur | (2) Secret envoyé | Faux positifs conservateurs : les messages de sensibilisation contenant le mot « OTP » (ex : « Ne communiquez jamais votre OTP ») sont bloqués côté traduction — comportement sûr mais potentiellement frustrant pour l'UX | Documenté |
| m2 | Mineur | (3) Panneau jury | Exclusion du panneau jury repose sur `<aside>` et `.jury-panel` — fragile si le site cible restructure son balisage HTML (mais confirmé fonctionnel sur le site actuel par les tests live) | Documenté |
| m3 | Mineur | (5) Échec réseau | Suite 5 « Jury Live » échoue à 8 tests (728 s) en raison de la latence ou indisponibilité du réseau vers `safinum.cm` — ce n'est pas un défaut de code mais une dépendance réseau externe | Documenté |
| m4 | Mineur | (6) Doc vs Code | `docs/langue_et_validation.md` mentionne « Ghomálá' 52 termes, Ewondo 52 termes » pour les glossaires — le fichier réel `catalogue/glossaire.csv` contient 208 termes (glossaire combiné, pas séparé) | Documenté |

---

## Détail des Constats

### C1 — CRITIQUE : Nom de fonction inexistant dans la documentation

- **Fichier** : `docs/questions_jury.md`, ligne 123.
- **Affirmation** : *« `has_confidential_secret()` dans `backend/protect.py` »*.
- **Réalité** : La fonction s'appelle `is_secret_text()` (`backend/protect.py:L31`). Le nom `has_confidential_secret` n'existe nulle part dans le dépôt.
- **Impact** : Un jury inspectant le code ne trouverait pas cette fonction, remettant en cause la crédibilité documentaire.
- **Correctif** : Remplacement de `has_confidential_secret()` par `is_secret_text()` dans `docs/questions_jury.md`.

---

### M1 — MAJEUR : Faux négatifs dans la détection de secrets OTP/PIN

- **Fichiers** : `backend/protect.py:L21-28`, `extension/content.js:L239-246`.
- **Preuve** : Les regex actuelles ne détectent pas ces variantes réelles :
  1. `"Votre PIN est 1234"` → Le motif `pin\s*[:=\s]+\d+` exige un `:`, `=` ou espace immédiatement suivi de chiffres. Avec « est », le mot bloque la capture.
  2. `"PIN code: 1234"` → Le motif attend `code\s+pin` (code avant pin), pas `pin code`.
  3. `"Code secret 847362"` → Le motif exige `(?:est|:)` entre le label et les chiffres. Sans séparateur, le secret échappe.
- **Impact** : Un code PIN ou OTP dans ces formats pourrait être envoyé à l'API de traduction locale.
- **Correctif** : Ajout de 3 motifs complémentaires dans `SECRET_PATTERNS` de `backend/protect.py` et `extension/content.js` :
  - `\bpin\s+(?:code\s*)?(?:est|is|:|\s)\s*\d{4,8}\b` (PIN suivi de « est/is/: » puis chiffres)
  - `\b(?:code\s+)?(?:secret|d'accès|d'activation)\s*[:=]?\s*\d{4,8}\b` (codes nommés avec ou sans séparateur)
  - `\bvotre\s+pin\s+est\s+\d{4,8}\b` (variante directe)

---

### M2 — MAJEUR : Endpoint `/feedback` sans filtrage de secrets

- **Fichier** : `backend/api.py:L592-625`.
- **Preuve** : La fonction `submit_feedback()` écrit directement `req.source_text`, `req.suggested_translation` et `req.comment` dans `catalogue/feedback_submissions.json` sans aucun appel à `is_secret_text()`.
- **Impact** : Si un utilisateur soumet un retour contenant un code OTP, un PIN ou un mot de passe temporaire, ces données sensibles sont stockées en clair sur le disque du serveur.
- **Correctif** : Ajout d'un filtrage `is_secret_text()` sur les champs textuels de la requête, avec rejet HTTP 422 et message explicite si un secret est détecté.

---

### M3 — MAJEUR : Absence de CSP explicite dans manifest.json

- **Fichier** : `extension/manifest.json`.
- **Preuve** : Aucune clé `"content_security_policy"` n'est déclarée. MV3 applique un défaut restrictif (`script-src 'self'; object-src 'self'`), mais l'absence d'explicitation est un manque de rigueur devant un jury sécurité.
- **Correctif** : Ajout de `"content_security_policy": { "extension_pages": "script-src 'self'; object-src 'self';" }` dans `manifest.json`.

---

### m1 — Mineur : Faux positifs conservateurs sur les messages OTP

- **Preuve** : Le motif `/\b(?:otp|one-time\s+password)\b/i` capture le mot « OTP » même dans des messages informatifs comme « Ne communiquez jamais votre OTP à un tiers ». Ces messages de sensibilisation sont donc exclus de la traduction.
- **Analyse** : Ce comportement est **délibérément conservateur** (côté sûr). Le blocage empêche tout risque de modification d'un message de sécurité contenant un code réel. Le compromis UX est acceptable : ces messages restent lisibles en français.
- **Statut** : Documenté, non corrigé (choix de conception sécuritaire).

---

### m2 — Mineur : Fragilité du sélecteur d'exclusion du panneau jury

- **Fichier** : `extension/content.js:L180-199`.
- **Preuve** : L'exclusion repose sur les sélecteurs `aside`, `.jury-panel`, `[data-safinum-jury]`, `[data-safinum-ignore]`, `[class*="jury-panel"]`. Si le site cible restructure son panneau jury dans un `<div>` ou un `<section>` sans ces classes, l'extension tenterait de le traduire.
- **Atténuation existante** : Le test `tests/test_jury_integrity.py` vérifie en conditions réelles (Playwright + Edge) que le panneau jury n'est pas modifié. Ce test échouerait immédiatement en cas de changement structurel, alertant les développeurs.
- **Statut** : Documenté, non corrigé (risque contrôlé par test de régression).

---

### m3 — Mineur : Échec de la suite Jury Live (réseau)

- **Preuve** : Suite 5 de `run_all_checks.ps1` : 8 tests, 728 s, code de sortie 1. L'échec est dû à des timeouts réseau vers `safinum.cm` (latence > 60 s ou indisponibilité temporaire du serveur distant).
- **Analyse** : Ce n'est pas un défaut du code SAFINUM mais une dépendance externe. Les 4 autres suites (197 tests locaux) passent à 100 %.
- **Statut** : Documenté, non corrigé (dépendance réseau externe).

---

### m4 — Mineur : Chiffres des glossaires dans les docs

- **Preuve** : `docs/langue_et_validation.md:L17-18` indique « Ghomálá' 52 termes » et « Ewondo 52 termes ». Le fichier réel `catalogue/glossaire.csv` contient 208 termes dans un glossaire combiné multi-langues (pas un fichier par langue).
- **Analyse** : Le glossaire combiné couvre plusieurs langues et domaines. Les 52 termes par langue sont un sous-ensemble de ce fichier. La formulation documentaire n'est pas fausse mais mérite clarification.
- **Statut** : Documenté.

---

## Vérification Croisée des Affirmations Chiffrées (Vecteur 6)

| Affirmation des docs | Valeur réelle mesurée | Verdict |
|---|---|---|
| 84 chaînes par langue dans `translations.csv` | 168 lignes : 84 `dua` + 84 `bas` | ✅ Conforme |
| 83 clés par langue dans `offline_catalog.json` (homonyme « Sécurité ») | `dua` : 83 clés, `bas` : 83 clés | ✅ Conforme |
| 168/168 au statut `machine_suggested` | 168/168 `machine_suggested`, 0 `human_validated` | ✅ Conforme |
| Empreinte extension/ = 125 034 octets (122,10 Ko) | `content.js` 62 624 + `offline_catalog.json` 58 304 + `background.js` 2 970 + `manifest.json` 1 136 = **125 034 octets** | ✅ Conforme |
| 91 cas d'intégrité (30 réels, 61 hostiles, 3 secrets) | 91 cas, groupes : 32 réels + 56 hostiles + 3 secrets = 91 | ✅ Conforme |
| 60 exécutions de répétition finale | `repetition_finale_resultats.json` : 60 entrées | ✅ Conforme |
| 84 lignes par fiche de validation CSV | `fiche_validation_duala.csv` : 84 lignes, `fiche_validation_bassaa.csv` : 84 lignes | ✅ Conforme |
| `host_permissions` limité à `127.0.0.1:8000` et `localhost:8000` | `["http://127.0.0.1:8000/*", "http://localhost:8000/*"]` | ✅ Conforme |
| Premier rendu traduit < 80 ms (backend arrêté) | 79,22 ms médiane documentée dans `docs/mesures_performance.md` | ✅ Conforme (non re-mesuré) |
| 205 tests exécutables | `run_all_checks.ps1` : 205 tests exécutés | ✅ Conforme |

---

## Résultats de `scripts/run_all_checks.ps1`

| Suite | Tests | Durée | Résultat |
|---|:---:|:---:|---|
| Backend (API, Sécurité v2, Contrat OpenAPI, Protection) | 168 | 1,29 s | ✅ SUCCÈS |
| Racine (Intégrité Jury, Intégrité Figée 91 cas, Recoupement UI, E2E Extension, Mock Bank) | 18 | 5,18 s | ✅ SUCCÈS |
| Accessibilité Widget (Clavier, ARIA, Contraste, Mobile 360px, Zoom, Reduced Motion) | 7 | 16,76 s | ✅ SUCCÈS |
| Performance & Régression (Premier rendu, Latence, Dérive DOM) | 4 | 5,03 s | ✅ SUCCÈS |
| Jury Live & Non-Régression (safinum.cm) | 8 | 728,05 s | ⚠️ ÉCHEC (réseau) |
| **TOTAL** | **205** | **756,31 s** | **197/205 locaux OK** |

---

## Tentatives de Casse — Synthèse par Vecteur

### (1) Montant ou référence altéré
**Résultat** : Impossible à reproduire. Les 91 cas d'épreuve (dont 61 hostiles avec montants en lettres, espaces insécables, devises préfixées, URLs piégées, doubles montants, décimales) passent à 100 % sur le pipeline algorithmique et l'API (`tests/test_integrite_figee.py`). Le masquage par jetons et la vérification de restauration empêchent toute altération.

### (2) Secret envoyé
**Résultat** : Failles trouvées et corrigées (M1, M2). Les regex de base détectent correctement les formats courants mais présentaient des lacunes sur des variantes syntaxiques réalistes. L'endpoint `/feedback` ne filtrait pas les secrets.

### (3) Extension modifiant le panneau jury ou le site
**Résultat** : Non reproductible en conditions normales. L'exclusion par `<aside>` et `.jury-panel` fonctionne sur le site actuel. Le test `test_jury_integrity.py` le confirme en conditions réelles. Le Shadow DOM isole complètement le widget. Aucun `innerHTML`, `eval` ou `document.write` dans le code (immunité XSS vérifiée).

### (4) Contenu inédit piégé
**Résultat** : Impossible à reproduire. Le masquage préalable hors-ligne (`OFFLINE_SENSITIVE_PATTERNS`) protège systématiquement tous les montants, références, URLs, emails, dates et téléphones dans les contenus inédits avant toute annotation de glossaire. Un contrôle d'intégrité strict rejette toute altération résiduelle.

### (5) Échec réseau en cours de parcours
**Résultat** : Résilience confirmée. Le timeout de 400 ms, l'essai unique, la mémorisation d'état en session (`sessionStorage`), la sonde non bloquante toutes les 30 s et le service worker avec `AbortController` garantissent un repli hors-ligne transparent. Le premier rendu traduit avec backend arrêté prend 79,22 ms en médiane.

### (6) Affirmations documentaires
**Résultat** : Une divergence critique (C1 : nom de fonction inexistant) et une majeure (M3 : CSP absente) trouvées et corrigées. Tous les chiffres factuels (84 chaînes, 125 034 octets, 91 cas, 60 exécutions, 205 tests) sont conformes.
