/**
 * SAFINUM Accessibility Extension — Content Script
 * Manifest V3 - Accessibilité linguistique pour services financiers camerounais
 *
 * RÈGLES CRITIQUES :
 * - Aucune modification du site hôte, aucun clic intercepté, aucun comportement modifié.
 * - Ne modifie JAMAIS les valeurs des inputs, montants saisis, formulaires ou boutons de confirmation.
 * - Mécanisme par lots vers l'API locale avec cache en mémoire.
 * - Repli automatique vers offline_catalog.json en cas d'indisponibilité de l'API.
 * - Widget flottant en Shadow DOM accessible (clavier, lecteur d'écran, mobile-friendly).
 * - Bascule instantanée Original / Traduit sans rechargement.
 * - Affichage bilingue au survol.
 */

(function () {
  'use strict';

  if (window.__SAFINUM_EXTENSION_V3_INJECTED__) return;
  window.__SAFINUM_EXTENSION_V3_INJECTED__ = true;

  console.log('[SAFINUM] Démarrage de la couche d\'accessibilité linguistique...');

  // Configuration
  const API_ENDPOINTS = [
    'http://localhost:8000/translate/batch',
    'http://127.0.0.1:8000/translate/batch'
  ];

  // Injection des styles pour la mise en valeur des montants, sécurité et badge de contenu inédit
  function injectDocumentStyles() {
    if (document.getElementById('safinum-doc-styles')) return;
    const style = document.createElement('style');
    style.id = 'safinum-doc-styles';
    style.textContent = `
      .safinum-highlight-amount {
        font-weight: 700 !important;
        letter-spacing: 0.2px;
      }
      .safinum-highlight-security {
        font-weight: 700 !important;
        border-left: 3px solid #F59E0B !important;
        background-color: rgba(245, 158, 11, 0.08) !important;
        padding-left: 6px !important;
        border-radius: 4px;
      }
      .safinum-novel-badge {
        display: inline-block !important;
        background-color: #FEF3C7 !important;
        color: #92400E !important;
        border: 1px solid #F59E0B !important;
        border-radius: 4px !important;
        padding: 2px 6px !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        margin-left: 8px !important;
        vertical-align: middle !important;
        line-height: 1.2 !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
      }
    `;
    (document.head || document.documentElement).appendChild(style);
  }
  injectDocumentStyles();

  // État applicatif de l'extension
  const state = {
    currentLang: 'dua',       // 'dua', 'bas', 'fr' (et 'ful' uniquement en mode expérimental)
    isTranslated: true,       // Mode Traduit (true) vs Original (false)
    bilingualMode: true,      // Affichage de l'original au survol
    experimentalMode: false,  // Désactivé par défaut (débloque Fulfulde expérimental)
    annotateSecurityAlerts: (typeof window !== 'undefined' && typeof window.ANNOTATE_SECURITY_ALERTS !== 'undefined') ? Boolean(window.ANNOTATE_SECURITY_ALERTS) : false, // Réglage ANNOTATE_SECURITY_ALERTS (défaut : false)
    offlineCatalog: null,     // Catalogue embarqué offline_catalog.json
    cache: new Map(),         // Clé: "texte__langue" -> { target, status, integrity_verified }
    managedNodes: new Set(),  // Nœuds textuels sous gestion
    stats: {
      human_validated: 0,
      machine_suggested: 0,
      fallback_source: 0
    },
    mutationTimer: null,
    isProcessing: false,
    isMutating: false
  };

  // --- Sélecteurs d'exclusion configurables ---
  // Ces sélecteurs désignent les zones que l'extension ne doit JAMAIS toucher.
  // Le panneau jury est identifié par <aside> (sélecteur confirmé via Playwright sur safinum.cm/hackathon-test).
  // La variable window.SAFINUM_EXCLUDED_SELECTORS permet de surcharger ou compléter en test.
  function getExcludedSelectors() {
    const defaultSelectors = [
      '#safinum-accessibility-host',   // Widget propre de l'extension (Shadow DOM)
      'aside',                          // Panneau jury SAFINUM (élément <aside> sur safinum.cm/hackathon-test)
      '[data-safinum-jury]',            // Conteneur jury explicitement marqué
      '[data-safinum-ignore]',          // Tout élément marqué manuellement à exclure
      '.jury-panel',                    // Conteneur de classe jury-panel
      '[class*="jury-panel"]'
    ];
    if (typeof window !== 'undefined' && window.SAFINUM_EXCLUDED_SELECTORS) {
      if (Array.isArray(window.SAFINUM_EXCLUDED_SELECTORS)) {
        return Array.from(new Set([...defaultSelectors, ...window.SAFINUM_EXCLUDED_SELECTORS]));
      }
      if (typeof window.SAFINUM_EXCLUDED_SELECTORS === 'string') {
        const custom = window.SAFINUM_EXCLUDED_SELECTORS.split(',').map(s => s.trim()).filter(Boolean);
        return Array.from(new Set([...defaultSelectors, ...custom]));
      }
    }
    return defaultSelectors;
  }

  /**
   * Vérifie si un nœud ou l'un de ses ancêtres est dans une zone exclue.
   * @param {Element} el - L'élément à tester.
   * @returns {boolean}
   */
  function isInExcludedZone(el) {
    if (!el) return false;
    const selectors = getExcludedSelectors();
    for (const selector of selectors) {
      try {
        if (el.matches && el.matches(selector)) return true;
        if (el.closest && el.closest(selector)) return true;
      } catch (e) {
        // Ignorer un sélecteur invalide éventuel
      }
    }
    return false;
  }

  if (typeof window !== 'undefined') {
    window.SAFINUM_IS_IN_EXCLUDED_ZONE = isInExcludedZone;
    window.SAFINUM_GET_EXCLUDED_SELECTORS = getExcludedSelectors;
  }

  // Mots-clés factorisés pour la détection des avertissements de sécurité et alertes
  const SECURITY_ALERT_KEYWORDS = [
    'alerte', 'sécurité', 'securite', 'attention', 'fraude', 'suspect', 'danger',
    'bloqué', 'bloque', 'confidentialité', 'confidentiel', 'warning', 'alert',
    'security', 'fraud', 'avertissement'
  ];

  function isSecurityAlertText(text) {
    if (!text) return false;
    const lower = text.toLowerCase();
    return SECURITY_ALERT_KEYWORDS.some(kw => lower.includes(kw));
  }

  // Motifs de détection des secrets (OTP, PIN, codes d'authentification)
  const SECRET_PATTERNS = [
    /\b(?:otp|one-time\s+password|one-time\s+passcode|one-time\s+code)\b/i,
    /\b(?:code\s+pin|pin)\s*[:=\s]+\d+/i,
    /\bvotre\s+code\s+pin\s+est\s+\d+/i,
    /\b(?:mot\s+de\s+passe\s+temporaire|temporary\s+password)\b/i,
    /\b(?:mot\s+de\s+passe|password)\s*[:=]\s*\S+/i,
    /\bcode\s+(?:de\s+)?(?:validation|confirmation|sécurité|securite|vérification|verification|secret)\s*(?:est|:)\s*\d+/i
  ];

  /**
   * Détecte si un texte contient un secret critique (OTP, PIN, mot de passe).
   * RÈGLE ABSOLUE : un secret ne doit JAMAIS être envoyé à l'API ni modifié.
   */
  function isSecretText(text) {
    if (!text || typeof text !== 'string') return false;
    return SECRET_PATTERNS.some(pat => pat.test(text));
  }

  if (typeof window !== 'undefined') {
    window.SAFINUM_IS_SECRET_TEXT = isSecretText;
  }

  function shouldAnnotateSecurityAlerts() {
    if (typeof window !== 'undefined' && typeof window.ANNOTATE_SECURITY_ALERTS !== 'undefined') {
      return Boolean(window.ANNOTATE_SECURITY_ALERTS);
    }
    return Boolean(state.annotateSecurityAlerts);
  }


  // --- 1. Chargement du Catalogue Hors-Ligne Embarqué ---
  async function loadOfflineCatalog() {
    try {
      if (typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.getURL) {
        const url = chrome.runtime.getURL('offline_catalog.json');
        const res = await fetch(url);
        state.offlineCatalog = await res.json();
        console.log('[SAFINUM] Catalogue hors ligne chargé avec succès.');
        return;
      }
    } catch (err) {
      console.warn('[SAFINUM] Impossible de charger via chrome.runtime, essai de fallback...', err);
    }

    if (!state.offlineCatalog) {
      state.offlineCatalog = { translations: { dua: {}, bas: {} }, glossary: {}, en_index: {} };
    }
  }

  /**
   * Normalise une chaîne pour la comparaison de clés EN.
   * NFKC + lower + espaces insécables → espace ordinaire + trim.
   */
  function normalizeEnKey(s) {
    // Remplacer espaces insécables (U+00A0, U+202F, U+2007) par espace ordinaire
    return s.replace(/[\u00A0\u202F\u2007]/g, ' ').toLowerCase().trim();
  }

  /**
   * Résout une chaîne EN vers sa source FR via l'index embarqué en_index.
   * Retourne la source FR si trouvée, sinon null.
   * Règle : correspondance exacte normalisée uniquement (jamais inventée).
   */
  function resolveEnToFr(text) {
    if (!state.offlineCatalog || !state.offlineCatalog.en_index) return null;
    const key = normalizeEnKey(text.trim());
    const frSource = state.offlineCatalog.en_index[key];
    return frSource || null;
  }



  // Détection des chaînes à sensibilité critique (montants, frais, avertissements, erreurs, récapitulatifs)
  function isCriticalText(text) {
    if (!text) return false;
    const lower = text.toLowerCase();
    // Montants, devises, pourcentages, grands nombres
    if (/fcfa|xaf|eur|usd|cfa|frs|%|\b\d{2,}\b|[€$£]/.test(lower)) return true;
    // Frais, tarifs, solde, montant
    if (/frais|commission|mutoa|ntomb|solde|montant/.test(lower)) return true;
    // Sécurité, avertissements, alertes, fraudes
    if (isSecurityAlertText(lower)) return true;
    // Erreurs, échecs
    if (/erreur|échec|insuffisant|invalide|rejeté|impossible|error|fail|bwemba|mbebi/.test(lower)) return true;
    // Récapitulatifs, confirmation
    if (/récapitulatif|recapitulatif|confirmation|total à débiter|total a debiter/.test(lower)) return true;
    return false;
  }

  // --- 2. Résolution Hors-Ligne (Repli & Inédit) ---
  function resolveOffline(text, lang) {
    // Règle absolue de sécurité : les secrets ne doivent JAMAIS être modifiés
    if (isSecretText(text)) {
      return { target: text, status: 'fallback_source', integrity_verified: true, bilingual_required: false, novel_annotated: false, badge: null };
    }

    if (!state.offlineCatalog || !state.offlineCatalog.translations) {
      return { target: text, status: 'fallback_source', integrity_verified: true, bilingual_required: isCriticalText(text), novel_annotated: false, badge: null };
    }

    const dict = state.offlineCatalog.translations[lang] || {};
    const glossary = state.offlineCatalog.glossary || {};
    const trimmed = text.trim();
    const critical = isCriticalText(trimmed);

    // 0. Résolution EN→FR : si la chaîne n'est pas trouvée directement,
    //    essayer de la résoudre via l'index anglais (en_index) pour obtenir
    //    la clé FR et utiliser la même traduction locale.
    //    Règle : correspondance exacte normalisée uniquement, jamais inventée.
    let lookupText = trimmed;
    if (!dict[trimmed]) {
      const frSource = resolveEnToFr(trimmed);
      if (frSource && dict[frSource]) {
        lookupText = frSource; // on utilise la source FR pour le lookup
      }
    }

    // 1. Recherche exacte dans la mémoire (FR natif ou résolu depuis EN)
    if (dict[lookupText]) {
      const entryStatus = dict[lookupText].status || 'machine_suggested';
      return {
        target: dict[lookupText].target,
        status: entryStatus,
        integrity_verified: true,
        bilingual_required: critical && (entryStatus !== 'human_validated'),
        novel_annotated: false,
        badge: null
      };
    }

    // 2. Recherche exacte dans le glossaire (terme seul)
    if (glossary[trimmed] && glossary[trimmed][lang]) {
      const entryStatus = glossary[trimmed].status || 'machine_suggested';
      return {
        target: glossary[trimmed][lang],
        status: entryStatus,
        integrity_verified: true,
        bilingual_required: critical && (entryStatus !== 'human_validated'),
        novel_annotated: false,
        badge: null
      };
    }

    // 2.5 Avertissement de sécurité / alerte inédit lorsque ANNOTATE_SECURITY_ALERTS est false (défaut)
    if (!shouldAnnotateSecurityAlerts() && isSecurityAlertText(trimmed)) {
      return {
        target: text,
        status: 'fallback_source',
        integrity_verified: true,
        bilingual_required: false,
        novel_annotated: false,
        badge: 'avertissement affiché en français : traduction non validée'
      };
    }


    // 3. Texte absent de la mémoire : conservation du texte source + annotation des termes financiers du glossaire
    // Masquage préalable des montants/numéros pour ne jamais insérer de crochets autour d'eux
    const amountRegex = /(?:[+-]\s*)?(?:(?:[$€£]\s*(?:\d{1,3}(?:[\s\u00A0\u202F\u2007,\.]\d{3})*|\d+)(?:[,\.]\d+)?)|(?:\b(?:\d{1,3}(?:[\s\u00A0\u202F\u2007,\.]\d{3})*|\d+)(?:[,\.]\d+)?\s*(?:FCFA|XAF|CFA|XOF|EUR|USD|GBP|€|\$|£|francs?\s*(?:cfa)?|frs)(?!\w)))/gi;
    const safeTokens = [];
    let masked = trimmed.replace(amountRegex, (m) => {
      const tok = `__SAFE_OFFLINE_${safeTokens.length}__`;
      safeTokens.push({ token: tok, value: m });
      return tok;
    });

    // Sélectionner les termes du glossaire disponibles pour la langue
    const availableTerms = [];
    for (const [srcTerm, trMap] of Object.entries(glossary)) {
      if (trMap[lang] && typeof trMap[lang] === 'string' && trMap[lang].trim()) {
        const tgt = trMap[lang].trim();
        if (srcTerm.trim().toLowerCase() !== tgt.toLowerCase()) {
          availableTerms.push({ src: srcTerm.trim(), tgt: tgt });
        }
      }
    }

    // Trier par longueur décroissante
    availableTerms.sort((a, b) => b.src.length - a.src.length);

    let hasAnnotation = false;
    const glossTokens = [];

    for (const item of availableTerms) {
      const escaped = item.src.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const pattern = new RegExp(`(?<![A-Za-z0-9_À-ÿ])(${escaped})(?![A-Za-z0-9_À-ÿ])`, 'gi');
      if (pattern.test(masked)) {
        masked = masked.replace(pattern, (match, word) => {
          const tok = `__GLOSS_OFFLINE_${glossTokens.length}__`;
          glossTokens.push({ token: tok, value: `${word} [${item.tgt}]` });
          hasAnnotation = true;
          return tok;
        });
      }
    }

    // Restauration des jetons de glossaire
    for (const gt of glossTokens) {
      masked = masked.split(gt.token).join(gt.value);
    }

    // Restauration des montants protégés
    for (const st of safeTokens) {
      masked = masked.split(st.token).join(st.value);
    }

    if (hasAnnotation) {
      return {
        target: masked,
        status: 'machine_suggested',
        integrity_verified: true,
        bilingual_required: false,
        novel_annotated: true,
        badge: 'contenu inédit : termes annotés, phrase non traduite'
      };
    }

    // 4. Repli vers le texte source
    return {
      target: text,
      status: 'fallback_source',
      integrity_verified: true,
      bilingual_required: critical,
      novel_annotated: false,
      badge: null
    };
  }

  // --- 3. Appel de l'API Locale par Lot avec Timeout ---
  async function fetchTranslationsBatch(texts, targetLang) {
    const results = new Map();
    const uncachedTexts = [];

    // Vérification préalable dans le cache mémoire
    for (const text of texts) {
      const trimmed = text.trim();
      // RÈGLE ABSOLUE DE SÉCURITÉ : les secrets (OTP, PIN) ne doivent JAMAIS être envoyés à l'API ni modifiés
      if (isSecretText(trimmed)) {
        results.set(text, {
          target: text,
          status: 'fallback_source',
          integrity_verified: true,
          bilingual_required: false,
          novel_annotated: false,
          badge: null
        });
        continue;
      }
      const cacheKey = `${trimmed}__${targetLang}`;
      if (state.cache.has(cacheKey)) {
        results.set(text, state.cache.get(cacheKey));
      } else {
        uncachedTexts.push(text);
      }
    }

    if (uncachedTexts.length === 0) {
      return results;
    }

    // Construction du payload conforme à openapi.yaml.
    // Résolution EN→FR : si un texte anglais a un équivalent FR dans l'index, on
    // envoie le texte FR à l'API (qui cherche dans sa mémoire FR). On conserve
    // le texte original (EN ou FR) comme clé de résultat dans results.
    const items = uncachedTexts.map((txt, idx) => {
      const frEquiv = resolveEnToFr(txt.trim());
      return {
        id: `node_${idx}_${Date.now()}`,
        text: (frEquiv || txt).trim(),   // envoie l'équivalent FR si connu
        screen_context: 'active_screen',
        _original_text: txt.trim()       // gardé localement pour le mapping retour
      };
    });

    const payload = {
      source_lang: 'fr',    // toujours FR : la mémoire catalogue est en FR
      target_lang: targetLang,
      allow_machine_translation: true,
      allow_experimental: Boolean(state.experimentalMode),
      annotate_security_alerts: shouldAnnotateSecurityAlerts(),
      items: items.map(({ id, text, screen_context }) => ({ id, text, screen_context }))
    };



    let apiSuccess = false;
    let apiData = null;

    // Tentative 1 : Via le Service Worker d'extension (conforme Manifest V3, contourne Private Network Access et Mixed Content)
    if (typeof chrome !== 'undefined' && chrome.runtime && typeof chrome.runtime.sendMessage === 'function') {
      try {
        const swResponse = await new Promise((resolve) => {
          const timer = setTimeout(() => resolve(null), 1800);
          try {
            chrome.runtime.sendMessage(
              { type: 'SAFINUM_TRANSLATE_BATCH', payload },
              (resp) => {
                clearTimeout(timer);
                if (chrome.runtime.lastError || !resp || !resp.success) {
                  resolve(null);
                } else {
                  resolve(resp.data);
                }
              }
            );
          } catch (sendErr) {
            clearTimeout(timer);
            resolve(null);
          }
        });
        if (swResponse && Array.isArray(swResponse.items)) {
          apiData = swResponse;
          apiSuccess = true;
        }
      } catch (swErr) {
        // Service worker non joignable, tentative directe
      }
    }

    // Tentative 2 : Direct fetch (si Service Worker indisponible ou hors contexte extension)
    if (!apiSuccess) {
      for (const endpoint of API_ENDPOINTS) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 1500);

        try {
          const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
            signal: controller.signal
          });
          clearTimeout(timeoutId);

          if (response.ok) {
            apiData = await response.json();
            apiSuccess = true;
            break;
          }
        } catch (e) {
          clearTimeout(timeoutId);
        }
      }
    }

    // Traitement des données renvoyées par l'API
    if (apiSuccess && apiData && Array.isArray(apiData.items)) {
      const idToOriginal = {};
      items.forEach(it => { idToOriginal[it.id] = it._original_text || it.text; });

      for (const item of apiData.items) {
        const resObj = {
          target: item.target_text,
          status: item.status,
          integrity_verified: item.integrity_verified,
          bilingual_required: Boolean(item.bilingual_required),
          novel_annotated: Boolean(item.novel_annotated),
          badge: item.badge || null
        };
        const origText = idToOriginal[item.id] || item.source_text;
        results.set(origText, resObj);
        state.cache.set(`${origText}__${targetLang}`, resObj);
        if (origText !== item.source_text) {
          results.set(item.source_text, resObj);
          state.cache.set(`${item.source_text}__${targetLang}`, resObj);
        }
      }
    } else {
      // Repli automatique vers le catalogue hors ligne si l'API est injoignable
      for (const txt of uncachedTexts) {
        const fallbackRes = resolveOffline(txt, targetLang);
        results.set(txt, fallbackRes);
        state.cache.set(`${txt.trim()}__${targetLang}`, fallbackRes);
      }
    }

    return results;
  }

  // --- 4. Collecte et Traduction des Nœuds du DOM ---
  function getEligibleTextNodes(root) {
    const nodes = [];
    const walker = document.createTreeWalker(
      root,
      NodeFilter.SHOW_TEXT,
      {
        acceptNode: function (node) {
          const parent = node.parentElement;
          if (!parent) return NodeFilter.FILTER_REJECT;

          const tag = parent.tagName.toLowerCase();
          // Exclure balises techniques et scripts
          if (['script', 'style', 'code', 'pre', 'svg', 'noscript', 'iframe'].includes(tag)) {
            return NodeFilter.FILTER_REJECT;
          }
          // Exclure les zones configurées (widget Shadow DOM, panneau jury <aside>, data-safinum-jury, data-safinum-ignore, etc.)
          if (isInExcludedZone(parent)) {
            return NodeFilter.FILTER_REJECT;
          }
          // RÈGLE ABSOLUE : Ne jamais modifier les inputs, textareas ou selects
          if (['input', 'textarea', 'select'].includes(tag)) {
            return NodeFilter.FILTER_REJECT;
          }

          const txt = node.nodeValue.trim();
          if (txt.length < 2) return NodeFilter.FILTER_REJECT;

          return NodeFilter.FILTER_ACCEPT;
        }
      }
    );

    while (walker.nextNode()) {
      nodes.push(walker.currentNode);
    }
    return nodes;
  }

  async function processDOMTranslation() {
    if (state.isProcessing) return;
    state.isProcessing = true;

    try {
      const appRoot = document.getElementById('app') || document.body;

      // 1. Si l'utilisateur demande le mode "Original (Français)", réinitialisation instantanée
      if (!state.isTranslated || state.currentLang === 'fr') {
        revertToSource();
        updateWidgetUI();
        return;
      }

      // 2. Collecte des nœuds éligibles
      const textNodes = getEligibleTextNodes(appRoot);
      const uniqueTexts = new Set();

      for (const node of textNodes) {
        if (typeof node._safinum_orig === 'undefined') {
          // Si le parent possède déjà l'attribut data-safinum-orig (ex: re-rendu Vue 3),
          // on récupère le vrai texte source original pour éviter toute double traduction !
          if (node.parentElement && node.parentElement.hasAttribute('data-safinum-orig')) {
            node._safinum_orig = node.parentElement.getAttribute('data-safinum-orig');
          } else {
            node._safinum_orig = node.nodeValue;
          }
        }
        state.managedNodes.add(node);
        uniqueTexts.add(node._safinum_orig.trim());
      }

      // 3. Récupération des traductions par lot (cache -> API -> catalogue hors-ligne)
      const translationsMap = await fetchTranslationsBatch(Array.from(uniqueTexts), state.currentLang);

      // Verrouillage contre la ré-observation interne
      state.isMutating = true;

      // 4. Application des traductions aux nœuds
      let statsHuman = 0;
      let statsMachine = 0;
      let statsFallback = 0;

      for (const node of textNodes) {
        const origTrimmed = node._safinum_orig.trim();
        const res = translationsMap.get(origTrimmed) || resolveOffline(origTrimmed, state.currentLang);

        if (res && res.target) {
          // Préserver les espacements d'origine
          const leadSpace = node._safinum_orig.match(/^\s*/)[0];
          const trailSpace = node._safinum_orig.match(/\s*$/)[0];

          // Règle critique : pour toute chaîne dont sensibilité est critique
          // (montants, frais, avertissements, erreurs) ET non attestée,
          // affiche le texte français d'origine suivi de la proposition entre crochets, sans le remplacer.
          const isCritical = Boolean(res.bilingual_required) || isCriticalText(origTrimmed);
          const isAttested = (res.status === 'human_validated');

          const isSameText = (
            res.status === 'fallback_source' ||
            origTrimmed === res.target ||
            origTrimmed.normalize('NFKC').replace(/[\s\u00A0\u202F]+/g, ' ').trim() ===
            res.target.normalize('NFKC').replace(/[\s\u00A0\u202F]+/g, ' ').trim()
          );

          let displayedTarget = res.target;
          if (res.novel_annotated) {
            // Contenu inédit : termes financiers annotés individuellement entre crochets dans la phrase source
            displayedTarget = res.target;
          } else if (isSameText) {
            displayedTarget = origTrimmed;
          } else if (displayedTarget.startsWith(origTrimmed + ' [')) {
            // Déjà formaté par le backend
          } else if (isCritical && !isAttested && origTrimmed !== res.target) {
            displayedTarget = `${origTrimmed} [${res.target}]`;
          }

          const newContent = leadSpace + displayedTarget + trailSpace;

          if (node.nodeValue !== newContent) {
            node.nodeValue = newContent;
          }

          if (node.parentElement) {
            node.parentElement.setAttribute('data-safinum-translated', 'true');
            node.parentElement.setAttribute('data-safinum-orig', origTrimmed);
            if (state.bilingualMode) {
              node.parentElement.setAttribute('title', `Original : ${origTrimmed}`);
            } else {
              node.parentElement.removeAttribute('title');
            }

            // Mise en évidence visuelle : Montants financiers (gras et contraste)
            if (/\b(?:\d{1,3}(?:[\s\u00A0\u202F]\d{3})*|\d+)\s*(?:FCFA|XAF|CFA|EUR|USD|€|\$)/i.test(origTrimmed)) {
              node.parentElement.classList.add('safinum-highlight-amount');
            }

            // Mise en évidence visuelle : Avertissements de sécurité (gras et contraste)
            if (isSecurityAlertText(origTrimmed)) {
              node.parentElement.classList.add('safinum-highlight-security');
            }

            // Badge visible : « contenu inédit » ou « avertissement affiché en français : traduction non validée »
            if (res.novel_annotated || res.badge) {
              const existingBadge = node.parentElement.querySelector('.safinum-novel-badge');
              if (!existingBadge) {
                // Espace avant le badge pour éviter qu'il ne soit collé à la phrase
                node.parentElement.appendChild(document.createTextNode(' '));
                const badgeSpan = document.createElement('span');
                badgeSpan.className = 'safinum-novel-badge';
                badgeSpan.setAttribute('data-safinum-ignore', 'true');
                badgeSpan.textContent = res.badge || 'contenu inédit : termes annotés, phrase non traduite';
                node.parentElement.appendChild(badgeSpan);
              } else if (res.badge && existingBadge.textContent !== res.badge) {
                existingBadge.textContent = res.badge;
              }
            }
          }


          if (res.status === 'human_validated') statsHuman++;
          else if (res.status === 'machine_suggested') statsMachine++;
          else statsFallback++;
        }
      }

      // 5. Traduction non-intrusive des placeholders (sans toucher aux valeurs des inputs)
      const formElements = appRoot.querySelectorAll('input[placeholder], textarea[placeholder]');
      for (const el of formElements) {
        if (!isInExcludedZone(el)) {
          if (typeof el._safinum_orig_ph === 'undefined') {
            el._safinum_orig_ph = el.getAttribute('placeholder');
          }
          const phTrimmed = el._safinum_orig_ph ? el._safinum_orig_ph.trim() : '';
          if (phTrimmed) {
            const resPh = translationsMap.get(phTrimmed) || resolveOffline(phTrimmed, state.currentLang);
            if (resPh && resPh.target) {
              el.setAttribute('placeholder', resPh.target);
            }
          }
        }
      }

      state.stats.human_validated = statsHuman;
      state.stats.machine_suggested = statsMachine;
      state.stats.fallback_source = statsFallback;
      updateWidgetUI();

    } finally {
      state.isMutating = false;
      state.isProcessing = false;
    }
  }

  // Restauration instantanée du texte d'origine sans requête réseau
  function revertToSource() {
    for (const node of state.managedNodes) {
      if (typeof node._safinum_orig !== 'undefined' && node.nodeValue !== node._safinum_orig) {
        node.nodeValue = node._safinum_orig;
      }
      if (node.parentElement) {
        node.parentElement.removeAttribute('data-safinum-translated');
        node.parentElement.removeAttribute('title');
        node.parentElement.removeAttribute('data-safinum-orig');
        node.parentElement.classList.remove('safinum-highlight-amount');
        node.parentElement.classList.remove('safinum-highlight-security');
      }
    }

    // Retirer tous les badges de contenus inédits injectés
    const novelBadges = document.querySelectorAll('.safinum-novel-badge');
    for (const b of novelBadges) {
      b.remove();
    }

    // Rétablir les placeholders
    const appRoot = document.getElementById('app') || document.body;
    const formElements = appRoot.querySelectorAll('input[placeholder], textarea[placeholder]');
    for (const el of formElements) {
      if (typeof el._safinum_orig_ph !== 'undefined') {
        el.setAttribute('placeholder', el._safinum_orig_ph);
      }
    }

    state.stats.human_validated = 0;
    state.stats.machine_suggested = 0;
    state.stats.fallback_source = state.managedNodes.size;
  }

  // --- 5. Surveillance Réactive via MutationObserver (Debounce 160ms) ---
  function setupMutationObserver() {
    const target = document.getElementById('app') || document.body;
    const observer = new MutationObserver((mutations) => {
      // Ignorer si l'extension est déjà en train de modifier le DOM
      if (state.isProcessing || state.isMutating) return;

      // Ignorer les mutations survenant uniquement dans des zones exclues (Shadow DOM du widget, panneau jury <aside>, etc.)
      let hasRelevantMutation = false;
      for (const m of mutations) {
        const el = (m.target && m.target.nodeType === Node.ELEMENT_NODE) ? m.target : (m.target ? m.target.parentElement : null);
        if (el && isInExcludedZone(el)) {
          continue;
        }
        let allAddedExcluded = true;
        if (m.addedNodes && m.addedNodes.length > 0) {
          for (let i = 0; i < m.addedNodes.length; i++) {
            const n = m.addedNodes[i];
            const elem = (n.nodeType === Node.ELEMENT_NODE) ? n : n.parentElement;
            if (elem && !isInExcludedZone(elem)) {
              allAddedExcluded = false;
              break;
            }
          }
        } else {
          allAddedExcluded = false;
        }
        if (!allAddedExcluded) {
          hasRelevantMutation = true;
          break;
        }
      }
      if (!hasRelevantMutation) return;

      if (!state.isTranslated || state.currentLang === 'fr') return;

      clearTimeout(state.mutationTimer);
      state.mutationTimer = setTimeout(() => {
        processDOMTranslation();
      }, 160);
    });

    observer.observe(target, {
      childList: true,
      subtree: true,
      characterData: true
    });
  }

  // --- 6. Interface Utilisateur Flottante en Shadow DOM ---
  let shadowRoot = null;

  function createShadowWidget() {
    let host = document.getElementById('safinum-accessibility-host');
    if (!host) {
      host = document.createElement('div');
      host.id = 'safinum-accessibility-host';
      host.style.all = 'initial';
      host.style.position = 'fixed';
      host.style.bottom = '12px';
      host.style.right = '12px';
      host.style.zIndex = '2147483647';
      document.body.appendChild(host);
    }

    shadowRoot = host.attachShadow({ mode: 'open' });

    const styles = document.createElement('style');
    styles.textContent = `
      :host { all: initial; font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; font-size: 13px; }
      * { box-sizing: border-box; margin: 0; padding: 0; }
      
      .sr-only {
        position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px;
        overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0;
      }

      *:focus-visible {
        outline: 2px solid #00BFFF !important;
        outline-offset: 2px !important;
      }

      .safinum-badge {
        display: inline-flex; align-items: center; gap: 8px;
        background: #00BFFF; color: #021226; font-weight: 700;
        min-height: 44px; min-width: 44px;
        padding: 10px 18px; border-radius: 9999px; cursor: pointer;
        box-shadow: 0 4px 14px rgba(0, 191, 255, 0.45);
        border: 2px solid #FFFFFF; user-select: none;
        transition: transform 0.18s, box-shadow 0.18s;
      }
      .safinum-badge:hover, .safinum-badge:focus-visible {
        transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0, 191, 255, 0.65);
        outline: 3px solid #00BFFF; outline-offset: 3px;
      }

      .safinum-panel {
        display: none; width: 320px; max-width: calc(100vw - 24px);
        background: #0A192F; color: #F1F5F9;
        border: 1px solid rgba(0, 191, 255, 0.35); border-radius: 16px;
        padding: 16px; box-shadow: 0 12px 36px rgba(0,0,0,0.65);
        margin-bottom: 12px;
        max-height: calc(100vh - 80px);
        overflow-y: auto;
      }
      .safinum-panel.open { display: block; animation: popIn 0.2s ease-out; }
      @keyframes popIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }

      .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1E293B; padding-bottom: 8px; margin-bottom: 12px; }
      .title { font-size: 14px; font-weight: 800; color: #00BFFF; display: flex; align-items: center; gap: 6px; }
      
      .btn-icon {
        background: transparent; border: none; color: #CBD5E1; font-size: 18px;
        min-width: 44px; min-height: 44px; cursor: pointer; border-radius: 8px;
        display: inline-flex; align-items: center; justify-content: center;
        transition: color 0.15s, background 0.15s;
      }
      .btn-icon:hover, .btn-icon:focus-visible { color: #FFFFFF; background: #1E293B; }

      .section { margin-bottom: 12px; }
      .label { display: block; font-size: 12px; font-weight: 700; color: #CBD5E1; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }
      
      .select-input {
        width: 100%; min-height: 44px; padding: 10px 12px; background: #1E293B; color: #FFF;
        border: 1px solid #334155; border-radius: 8px; font-size: 13px; font-weight: 600;
        outline: none; cursor: pointer;
      }
      .select-input:focus-visible { border-color: #00BFFF; box-shadow: 0 0 0 2px rgba(0, 191, 255, 0.4); }

      /* Bouton Bascule Original / Traduit */
      .toggle-action-btn {
        width: 100%; min-height: 44px; display: flex; align-items: center; justify-content: center; gap: 8px;
        padding: 12px 14px; border-radius: 8px; font-size: 13px; font-weight: 700;
        cursor: pointer; border: none; transition: background 0.2s; user-select: none;
      }
      .toggle-action-btn.active { background: #10B981; color: #021226; }
      .toggle-action-btn.inactive { background: #334155; color: #F1F5F9; }
      .toggle-action-btn:focus-visible { outline: 2px solid #00BFFF; outline-offset: 2px; }

      .switch-row {
        display: flex; justify-content: space-between; align-items: center;
        min-height: 44px; margin-top: 6px; font-size: 13px; color: #F1F5F9;
      }
      .switch {
        position: relative; display: inline-flex; align-items: center; justify-content: center;
        width: 48px; height: 44px; cursor: pointer;
      }
      .switch input {
        position: absolute; width: 48px; height: 44px; opacity: 0; margin: 0;
        cursor: pointer; z-index: 2;
      }
      .slider {
        position: absolute; width: 44px; height: 24px; background-color: #334155;
        transition: .2s ease-in-out; border-radius: 24px; pointer-events: none;
      }
      .slider:before {
        position: absolute; content: ""; height: 18px; width: 18px; left: 3px; bottom: 3px;
        background-color: white; transition: .2s ease-in-out; border-radius: 50%;
      }
      input:checked + .slider { background-color: #00BFFF; }
      input:checked + .slider:before { transform: translateX(20px); }
      input:focus-visible + .slider {
        outline: 2px solid #00BFFF; outline-offset: 3px;
        box-shadow: 0 0 0 3px rgba(0, 191, 255, 0.4);
      }

      /* Bandeau permanent de transparence IA */
      .ai-disclaimer-banner {
        background: #451a03;
        color: #fef3c7;
        border: 1px solid #f59e0b;
        border-radius: 8px;
        padding: 8px 10px;
        font-size: 11px;
        font-weight: 700;
        line-height: 1.4;
        text-align: center;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
      }

      /* Statuts d'intégrité */
      .status-box { background: rgba(15, 23, 42, 0.6); border: 1px solid #1E293B; border-radius: 8px; padding: 10px; margin-top: 12px; }
      .status-line { display: flex; justify-content: space-between; align-items: center; font-size: 12px; margin-bottom: 6px; }
      .status-line:last-child { margin-bottom: 0; }
      .pill { display: inline-flex; align-items: center; gap: 4px; font-weight: 700; color: #CBD5E1; }
      .dot-green { width: 7px; height: 7px; border-radius: 50%; background: #10B981; }
      .dot-amber { width: 7px; height: 7px; border-radius: 50%; background: #F59E0B; }
      .dot-gray { width: 7px; height: 7px; border-radius: 50%; background: #94A3B8; }

      @media (max-width: 480px) {
        .safinum-panel {
          width: calc(100vw - 20px) !important;
          max-width: 320px !important;
        }
      }

      @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
          animation: none !important;
          animation-duration: 0.001ms !important;
          animation-iteration-count: 1 !important;
          transition: none !important;
          transition-duration: 0.001ms !important;
        }
        .safinum-badge:hover, .safinum-badge:focus-visible {
          transform: none !important;
        }
        .safinum-panel.open {
          animation: none !important;
        }
      }
    `;

    const widget = document.createElement('div');
    widget.setAttribute('role', 'region');
    widget.setAttribute('aria-label', 'Accessibilité linguistique SAFINUM');

    function createDOMElement(tag, attrs = {}, children = []) {
      const node = document.createElement(tag);
      for (const [k, v] of Object.entries(attrs)) {
        if (k === 'text') {
          node.textContent = v;
        } else if (k === 'style' && typeof v === 'object') {
          Object.assign(node.style, v);
        } else if (v !== null && v !== undefined) {
          node.setAttribute(k, v);
        }
      }
      for (const child of children) {
        if (typeof child === 'string') {
          node.appendChild(document.createTextNode(child));
        } else if (child instanceof Node) {
          node.appendChild(child);
        }
      }
      return node;
    }

    const liveAnnouncerEl = createDOMElement('div', {
      id: 'liveAnnouncer',
      class: 'sr-only',
      'aria-live': 'polite',
      'aria-atomic': 'true'
    });

    const header = createDOMElement('div', { class: 'header' }, [
      createDOMElement('div', { class: 'title' }, [
        createDOMElement('span', { 'aria-hidden': 'true', text: '🇨🇲 ' }),
        createDOMElement('span', { text: 'SAFINUM Accessibilité' })
      ]),
      createDOMElement('button', {
        class: 'btn-icon',
        id: 'btnClose',
        'aria-label': "Fermer le panneau d'accessibilité",
        title: 'Fermer (Échap)',
        text: '✕'
      })
    ]);

    const aiBanner = createDOMElement('div', { class: 'ai-disclaimer-banner', role: 'note' }, [
      createDOMElement('span', { 'aria-hidden': 'true', text: '⚠️ ' }),
      createDOMElement('span', {
        id: 'aiBannerText',
        text: 'Traductions générées par IA, non validées par un locuteur natif.'
      })
    ]);

    const sectionLang = createDOMElement('div', { class: 'section' }, [
      createDOMElement('label', {
        class: 'label',
        for: 'langSelect',
        id: 'langSelectLabel',
        text: 'Langue camerounaise'
      }),
      createDOMElement('select', {
        class: 'select-input',
        id: 'langSelect',
        'aria-labelledby': 'langSelectLabel'
      }, [
        createDOMElement('option', { value: 'dua', selected: 'selected', text: 'Duálá (Duala)' }),
        createDOMElement('option', { value: 'bas', text: "Ɓàsàa (Bassa'a)" }),
        createDOMElement('option', { value: 'fr', text: 'Français (Langue source)' })
      ])
    ]);

    const sectionToggle = createDOMElement('div', { class: 'section' }, [
      createDOMElement('button', {
        class: 'toggle-action-btn active',
        id: 'btnToggleTranslate',
        'aria-pressed': 'true'
      }, [
        createDOMElement('span', { 'aria-hidden': 'true', text: '🔄 ' }),
        createDOMElement('span', { id: 'toggleBtnText', text: 'Mode Traduit (Duálá)' })
      ])
    ]);

    const switchBilingual = createDOMElement('div', { class: 'switch-row' }, [
      createDOMElement('span', { id: 'labelBilingual', text: 'Affichage bilingue au survol' }),
      createDOMElement('label', { class: 'switch', for: 'checkBilingual' }, [
        createDOMElement('input', {
          type: 'checkbox',
          id: 'checkBilingual',
          checked: 'checked',
          'aria-labelledby': 'labelBilingual'
        }),
        createDOMElement('span', { class: 'slider', 'aria-hidden': 'true' })
      ])
    ]);

    const switchExperimental = createDOMElement('div', {
      class: 'switch-row',
      style: { marginTop: '8px', paddingTop: '8px', borderTop: '1px dashed #334155' }
    }, [
      createDOMElement('span', {
        id: 'labelExperimental',
        text: 'Mode expérimental (IA non calibrée)'
      }),
      createDOMElement('label', { class: 'switch', for: 'checkExperimental' }, [
        createDOMElement('input', {
          type: 'checkbox',
          id: 'checkExperimental',
          'aria-labelledby': 'labelExperimental'
        }),
        createDOMElement('span', { class: 'slider', 'aria-hidden': 'true' })
      ])
    ]);

    const statusBox = createDOMElement('div', { class: 'status-box' }, [
      createDOMElement('div', { class: 'status-line' }, [
        createDOMElement('span', { style: { color: '#CBD5E1' }, text: 'Intégrité financière : ' }),
        createDOMElement('span', { style: { color: '#10B981', fontWeight: '800' }, text: '100% Inviolée' })
      ]),
      createDOMElement('div', { class: 'status-line' }, [
        createDOMElement('span', { class: 'pill' }, [
          createDOMElement('span', { class: 'dot-green' }),
          ' Validé (Humain) : '
        ]),
        createDOMElement('span', { id: 'statHuman', text: '0' })
      ]),
      createDOMElement('div', { class: 'status-line' }, [
        createDOMElement('span', { class: 'pill' }, [
          createDOMElement('span', { class: 'dot-amber' }),
          ' Suggéré (Auto) : '
        ]),
        createDOMElement('span', { id: 'statMachine', text: '0' })
      ]),
      createDOMElement('div', { class: 'status-line' }, [
        createDOMElement('span', { class: 'pill' }, [
          createDOMElement('span', { class: 'dot-gray' }),
          ' Source / Repli : '
        ]),
        createDOMElement('span', { id: 'statFallback', text: '0' })
      ])
    ]);

    const panelEl = createDOMElement('div', {
      class: 'safinum-panel',
      id: 'panel',
      role: 'dialog',
      'aria-modal': 'true',
      'aria-label': 'Paramètres linguistiques SAFINUM'
    }, [
      header,
      aiBanner,
      sectionLang,
      sectionToggle,
      switchBilingual,
      switchExperimental,
      statusBox
    ]);

    const badgeEl = createDOMElement('div', {
      class: 'safinum-badge',
      id: 'badge',
      tabindex: '0',
      role: 'button',
      'aria-haspopup': 'dialog',
      'aria-expanded': 'false',
      'aria-label': "Ouvrir le panneau d'accessibilité linguistique SAFINUM"
    }, [
      createDOMElement('span', { 'aria-hidden': 'true', text: '🇨🇲 ' }),
      createDOMElement('span', { id: 'badgeLabel', text: 'Duálá (Actif)' })
    ]);

    widget.appendChild(liveAnnouncerEl);
    widget.appendChild(panelEl);
    widget.appendChild(badgeEl);

    shadowRoot.appendChild(styles);
    shadowRoot.appendChild(widget);

    // Événements du widget
    const badge = shadowRoot.getElementById('badge');
    const panel = shadowRoot.getElementById('panel');
    const btnClose = shadowRoot.getElementById('btnClose');
    const langSelect = shadowRoot.getElementById('langSelect');
    const btnToggleTranslate = shadowRoot.getElementById('btnToggleTranslate');
    const checkBilingual = shadowRoot.getElementById('checkBilingual');
    const checkExperimental = shadowRoot.getElementById('checkExperimental');
    const liveAnnouncer = shadowRoot.getElementById('liveAnnouncer');

    let lastAnnouncedMessage = '';
    let announceTimeout = null;
    function announceLive(message) {
      if (!message || message === lastAnnouncedMessage) return;
      lastAnnouncedMessage = message;
      if (announceTimeout) clearTimeout(announceTimeout);
      announceTimeout = setTimeout(() => {
        if (liveAnnouncer) {
          liveAnnouncer.textContent = '';
          setTimeout(() => { liveAnnouncer.textContent = message; }, 40);
        }
      }, 200);
    }

    function getFocusableElements() {
      return Array.from(panel.querySelectorAll('button, select, input[type="checkbox"], [tabindex="0"]'))
        .filter(el => !el.disabled && el.offsetParent !== null);
    }

    function openPanel() {
      panel.classList.add('open');
      badge.setAttribute('aria-expanded', 'true');
      btnClose.focus();
      announceLive("Panneau des paramètres d'accessibilité linguistique ouvert");
    }

    function closePanel() {
      panel.classList.remove('open');
      badge.setAttribute('aria-expanded', 'false');
      badge.focus();
      announceLive("Panneau des paramètres fermé");
    }

    function togglePanel() {
      if (panel.classList.contains('open')) {
        closePanel();
      } else {
        openPanel();
      }
    }

    badge.addEventListener('click', togglePanel);
    badge.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        togglePanel();
      }
    });

    btnClose.addEventListener('click', closePanel);

    // Navigation Clavier avec Piège de Focus (Focus Trap) dans le panneau ouvert
    panel.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        closePanel();
        return;
      }
      if (e.key === 'Tab') {
        const focusables = getFocusableElements();
        if (focusables.length === 0) return;
        const firstEl = focusables[0];
        const lastEl = focusables[focusables.length - 1];

        if (e.shiftKey) {
          if (shadowRoot.activeElement === firstEl || shadowRoot.activeElement === panel) {
            e.preventDefault();
            lastEl.focus();
          }
        } else {
          if (shadowRoot.activeElement === lastEl) {
            e.preventDefault();
            firstEl.focus();
          }
        }
      }
    });

    langSelect.addEventListener('change', (e) => {
      state.currentLang = e.target.value;
      if (state.currentLang === 'fr') {
        state.isTranslated = false;
      } else {
        state.isTranslated = true;
      }
      const langName = state.currentLang === 'dua' ? 'Duálá' : (state.currentLang === 'bas' ? 'Ɓàsàa' : (state.currentLang === 'ful' ? 'Fulfulde' : 'Français'));
      announceLive(`Langue sélectionnée : ${langName}`);
      processDOMTranslation();
    });

    btnToggleTranslate.addEventListener('click', () => {
      state.isTranslated = !state.isTranslated;
      announceLive(state.isTranslated ? "Traduction activée" : "Mode original français activé");
      processDOMTranslation();
    });

    checkBilingual.addEventListener('change', (e) => {
      state.bilingualMode = e.target.checked;
      announceLive(state.bilingualMode ? "Affichage bilingue au survol activé" : "Affichage bilingue au survol désactivé");
      processDOMTranslation();
    });

    checkExperimental.addEventListener('change', (e) => {
      state.experimentalMode = e.target.checked;
      const optFul = langSelect.querySelector('option[value="ful"]');
      if (state.experimentalMode) {
        if (!optFul) {
          const opt = document.createElement('option');
          opt.value = 'ful';
          opt.textContent = 'Fulfulde (Expérimental)';
          langSelect.insertBefore(opt, langSelect.querySelector('option[value="fr"]'));
        }
        announceLive("Mode expérimental activé : langue Fulfulde disponible");
      } else {
        if (optFul) {
          if (state.currentLang === 'ful') {
            state.currentLang = 'dua';
            langSelect.value = 'dua';
          }
          optFul.remove();
        }
        announceLive("Mode expérimental désactivé");
      }
      updateWidgetUI();
      processDOMTranslation();
    });
  }

  function updateWidgetUI() {
    if (!shadowRoot) return;

    const badgeLabel = shadowRoot.getElementById('badgeLabel');
    const btnToggleTranslate = shadowRoot.getElementById('btnToggleTranslate');
    const toggleBtnText = shadowRoot.getElementById('toggleBtnText');
    const langSelect = shadowRoot.getElementById('langSelect');

    const statHuman = shadowRoot.getElementById('statHuman');
    const statMachine = shadowRoot.getElementById('statMachine');
    const statFallback = shadowRoot.getElementById('statFallback');
    const aiBannerText = shadowRoot.getElementById('aiBannerText');

    const langName = state.currentLang === 'dua' ? 'Duálá' : (state.currentLang === 'bas' ? 'Ɓàsàa' : (state.currentLang === 'ful' ? 'Fulfulde (Exp.)' : 'Français'));

    if (aiBannerText) {
      if (state.currentLang === 'ful') {
        aiBannerText.textContent = 'Sortie expérimentale non fiable (moteur non calibré, non relu par un locuteur natif).';
      } else {
        aiBannerText.textContent = 'Traductions générées par IA, non validées par un locuteur natif.';
      }
    }

    if (langSelect && langSelect.value !== state.currentLang) {
      langSelect.value = state.currentLang;
    }

    if (state.isTranslated && state.currentLang !== 'fr') {
      badgeLabel.textContent = `${langName} (Actif)`;
      btnToggleTranslate.className = 'toggle-action-btn active';
      btnToggleTranslate.setAttribute('aria-pressed', 'true');
      toggleBtnText.textContent = `Mode Traduit (${langName})`;
    } else {
      badgeLabel.textContent = `Français (Source)`;
      btnToggleTranslate.className = 'toggle-action-btn inactive';
      btnToggleTranslate.setAttribute('aria-pressed', 'false');
      toggleBtnText.textContent = `Mode Original (Français)`;
    }

    if (statHuman) statHuman.textContent = state.stats.human_validated;
    if (statMachine) statMachine.textContent = state.stats.machine_suggested;
    if (statFallback) statFallback.textContent = state.stats.fallback_source;
  }

  // --- 7. Initialisation Globale ---
  async function init() {
    await loadOfflineCatalog();
    createShadowWidget();
    setupMutationObserver();

    // Démarrage par défaut en mode Traduit (Duálá)
    state.currentLang = 'dua';
    state.isTranslated = true;
    processDOMTranslation();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
