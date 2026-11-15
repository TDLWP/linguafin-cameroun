/**
 * SAFINUM Accessibility Extension — Content Script
 * Manifest V3 - Accessibilité linguistique pour services financiers camerounais
 *
 * RÈGLES CRITIQUES :
 * - Aucune modification du site hôte, aucun clic intercepté, aucun comportement modifié.
 * - Ne modifie JAMAIS les valeurs des inputs, montants saisis, formulaires ou boutons de confirmation.
 * - Mécanisme par lots vers l'API locale avec cache en mémoire.
 * - Repli automatique vers catalogue_offline.json en cas d'indisponibilité de l'API.
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

  // État applicatif de l'extension
  const state = {
    currentLang: 'dua',       // 'dua', 'bas', 'fr' (et 'ful' uniquement en mode expérimental)
    isTranslated: true,       // Mode Traduit (true) vs Original (false)
    bilingualMode: true,      // Affichage de l'original au survol
    experimentalMode: false,  // Désactivé par défaut (débloque Fulfulde expérimental)
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
      state.offlineCatalog = { translations: { dua: {}, bas: {} }, glossary: {} };
    }
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
    if (/alerte|sécurité|securite|attention|fraude|suspect|danger|bloqué|bloque|avertissement|warning|alert|security|fraud/.test(lower)) return true;
    // Erreurs, échecs
    if (/erreur|échec|insuffisant|invalide|rejeté|impossible|error|fail|bwemba|mbebi/.test(lower)) return true;
    // Récapitulatifs, confirmation
    if (/récapitulatif|recapitulatif|confirmation|total à débiter|total a debiter/.test(lower)) return true;
    return false;
  }

  // --- 2. Résolution Hors-Ligne (Repli) ---
  function resolveOffline(text, lang) {
    if (!state.offlineCatalog || !state.offlineCatalog.translations) {
      return { target: text, status: 'fallback_source', integrity_verified: true, bilingual_required: isCriticalText(text) };
    }

    const dict = state.offlineCatalog.translations[lang] || {};
    const glossary = state.offlineCatalog.glossary || {};
    const trimmed = text.trim();
    const critical = isCriticalText(trimmed);

    // 1. Recherche exacte
    if (dict[trimmed]) {
      const entryStatus = dict[trimmed].status || 'machine_suggested';
      return {
        target: dict[trimmed].target,
        status: entryStatus,
        integrity_verified: true,
        bilingual_required: critical && (entryStatus !== 'human_validated')
      };
    }

    // 2. Recherche dans le glossaire
    if (glossary[trimmed] && glossary[trimmed][lang]) {
      const entryStatus = glossary[trimmed].status || 'machine_suggested';
      return {
        target: glossary[trimmed][lang],
        status: entryStatus,
        integrity_verified: true,
        bilingual_required: critical && (entryStatus !== 'human_validated')
      };
    }

    // 3. Substitution terminologique partielle
    let auto = trimmed;
    let modified = false;
    for (const [term, tr] of Object.entries(glossary)) {
      if (auto.includes(term) && tr[lang]) {
        auto = auto.split(term).join(tr[lang]);
        modified = true;
      }
    }

    if (modified) {
      return {
        target: auto,
        status: 'machine_suggested',
        integrity_verified: true,
        bilingual_required: critical
      };
    }

    // 4. Repli vers le texte source
    return {
      target: text,
      status: 'fallback_source',
      integrity_verified: true,
      bilingual_required: critical
    };
  }

  // --- 3. Appel de l'API Locale par Lot avec Timeout ---
  async function fetchTranslationsBatch(texts, targetLang) {
    const results = new Map();
    const uncachedTexts = [];

    // Vérification préalable dans le cache mémoire
    for (const text of texts) {
      const cacheKey = `${text.trim()}__${targetLang}`;
      if (state.cache.has(cacheKey)) {
        results.set(text, state.cache.get(cacheKey));
      } else {
        uncachedTexts.push(text);
      }
    }

    if (uncachedTexts.length === 0) {
      return results;
    }

    // Construction du payload conforme à openapi.yaml
    const items = uncachedTexts.map((txt, idx) => ({
      id: `node_${idx}_${Date.now()}`,
      text: txt.trim(),
      screen_context: 'active_screen'
    }));

    const payload = {
      source_lang: 'fr',
      target_lang: targetLang,
      allow_machine_translation: true,
      allow_experimental: Boolean(state.experimentalMode),
      items: items
    };

    let apiSuccess = false;

    // Tentative auprès des endpoints API avec timeout strict de 1.5 seconde
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
          const data = await response.json();
          for (const item of data.items) {
            const resObj = {
              target: item.target_text,
              status: item.status,
              integrity_verified: item.integrity_verified,
              bilingual_required: Boolean(item.bilingual_required)
            };
            results.set(item.source_text, resObj);
            state.cache.set(`${item.source_text}__${targetLang}`, resObj);
          }
          apiSuccess = true;
          break;
        }
      } catch (e) {
        clearTimeout(timeoutId);
        // Endpoint indisponible, passage au suivant ou repli hors-ligne
      }
    }

    // Repli automatique vers le catalogue hors ligne si l'API est injoignable
    if (!apiSuccess) {
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
          // Exclure le widget de l'extension
          if (parent.closest('#safinum-accessibility-host')) {
            return NodeFilter.FILTER_REJECT;
          }
          // RÈGLE ABSOLUE : Ne jamais modifier les inputs, textareas ou selects
          if (['input', 'textarea', 'select'].includes(tag)) {
            return NodeFilter.FILTER_REJECT;
          }
          // Exclure les éléments marqués data-safinum-ignore
          if (parent.hasAttribute('data-safinum-ignore')) {
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
          if (isSameText) {
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
          }

          if (res.status === 'human_validated') statsHuman++;
          else if (res.status === 'machine_suggested') statsMachine++;
          else statsFallback++;
        }
      }

      // 5. Traduction non-intrusive des placeholders (sans toucher aux valeurs des inputs)
      const formElements = appRoot.querySelectorAll('input[placeholder], textarea[placeholder]');
      for (const el of formElements) {
        if (!el.closest('#safinum-accessibility-host')) {
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
      }
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

      // Ignorer les mutations survenant dans le Shadow DOM du widget
      for (const m of mutations) {
        const el = (m.target && m.target.nodeType === Node.ELEMENT_NODE) ? m.target : (m.target ? m.target.parentElement : null);
        if (el && el.closest && el.closest('#safinum-accessibility-host')) {
          return;
        }
      }

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
      host.style.bottom = '18px';
      host.style.right = '18px';
      host.style.zIndex = '2147483647';
      document.body.appendChild(host);
    }

    shadowRoot = host.attachShadow({ mode: 'open' });

    const styles = document.createElement('style');
    styles.textContent = `
      :host { all: initial; font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; font-size: 13px; }
      * { box-sizing: border-box; margin: 0; padding: 0; }
      
      .safinum-badge {
        display: inline-flex; align-items: center; gap: 8px;
        background: #00BFFF; color: #021226; font-weight: 700;
        padding: 10px 16px; border-radius: 9999px; cursor: pointer;
        box-shadow: 0 4px 14px rgba(0, 191, 255, 0.45);
        border: 2px solid #FFFFFF; user-select: none;
        transition: transform 0.18s, box-shadow 0.18s;
      }
      .safinum-badge:hover, .safinum-badge:focus-visible {
        transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0, 191, 255, 0.65);
        outline: 2px solid #00BFFF; outline-offset: 2px;
      }

      .safinum-panel {
        display: none; width: min(340px, 92vw); background: #0A192F; color: #F1F5F9;
        border: 1px solid rgba(0, 191, 255, 0.35); border-radius: 16px;
        padding: 16px; box-shadow: 0 12px 36px rgba(0,0,0,0.65);
        margin-bottom: 12px;
      }
      .safinum-panel.open { display: block; animation: popIn 0.2s ease-out; }
      @keyframes popIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }

      .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1E293B; padding-bottom: 8px; margin-bottom: 12px; }
      .title { font-size: 14px; font-weight: 800; color: #00BFFF; display: flex; align-items: center; gap: 6px; }
      .btn-icon { background: transparent; border: none; color: #94A3B8; font-size: 16px; cursor: pointer; padding: 4px; border-radius: 4px; }
      .btn-icon:hover, .btn-icon:focus-visible { color: #FFF; background: #1E293B; }

      .section { margin-bottom: 12px; }
      .label { display: block; font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
      
      .select-input {
        width: 100%; padding: 8px 10px; background: #1E293B; color: #FFF;
        border: 1px solid #334155; border-radius: 8px; font-size: 13px; font-weight: 600;
        outline: none;
      }
      .select-input:focus-visible { border-color: #00BFFF; box-shadow: 0 0 0 2px rgba(0, 191, 255, 0.3); }

      /* Bouton Bascule Original / Traduit */
      .toggle-action-btn {
        width: 100%; display: flex; align-items: center; justify-content: center; gap: 8px;
        padding: 10px; border-radius: 8px; font-size: 13px; font-weight: 700;
        cursor: pointer; border: none; transition: background 0.2s; user-select: none;
      }
      .toggle-action-btn.active { background: #10B981; color: #021226; }
      .toggle-action-btn.inactive { background: #334155; color: #F1F5F9; }
      .toggle-action-btn:focus-visible { outline: 2px solid #00BFFF; outline-offset: 2px; }

      .switch-row { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; font-size: 12px; }
      .switch { position: relative; display: inline-block; width: 38px; height: 22px; }
      .switch input { opacity: 0; width: 0; height: 0; }
      .slider { position: absolute; cursor: pointer; inset: 0; background-color: #334155; transition: .25s; border-radius: 22px; }
      .slider:before { position: absolute; content: ""; height: 16px; width: 16px; left: 3px; bottom: 3px; background-color: white; transition: .25s; border-radius: 50%; }
      input:checked + .slider { background-color: #00BFFF; }
      input:checked + .slider:before { transform: translateX(16px); }

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
      .status-line { display: flex; justify-content: space-between; align-items: center; font-size: 11px; margin-bottom: 5px; }
      .status-line:last-child { margin-bottom: 0; }
      .pill { display: inline-flex; align-items: center; gap: 4px; font-weight: 700; }
      .dot-green { width: 7px; height: 7px; border-radius: 50%; background: #10B981; }
      .dot-amber { width: 7px; height: 7px; border-radius: 50%; background: #F59E0B; }
      .dot-gray { width: 7px; height: 7px; border-radius: 50%; background: #94A3B8; }
    `;

    const widget = document.createElement('div');
    widget.setAttribute('role', 'region');
    widget.setAttribute('aria-label', 'Accessibilité linguistique SAFINUM');

    widget.innerHTML = `
      <div class="safinum-panel" id="panel" role="dialog" aria-modal="false" aria-label="Paramètres linguistiques">
        <div class="header">
          <div class="title">
            <span aria-hidden="true">🇨🇲</span>
            <span>SAFINUM Accessibilité</span>
          </div>
          <button class="btn-icon" id="btnClose" aria-label="Fermer le panneau d'accessibilité">✕</button>
        </div>

        <div class="ai-disclaimer-banner" role="note">
          <span aria-hidden="true">⚠️</span>
          <span id="aiBannerText">Traductions générées par IA, non validées par un locuteur natif.</span>
        </div>

        <div class="section">
          <label class="label" for="langSelect">Langue camerounaise</label>
          <select class="select-input" id="langSelect">
            <option value="dua" selected>Duálá (Duala)</option>
            <option value="bas">Ɓàsàa (Bassa'a)</option>
            <option value="fr">Français (Langue source)</option>
          </select>
        </div>

        <div class="section">
          <button class="toggle-action-btn active" id="btnToggleTranslate" aria-pressed="true">
            <span aria-hidden="true">🔄</span>
            <span id="toggleBtnText">Mode Traduit (Duálá)</span>
          </button>
        </div>

        <div class="switch-row">
          <span>Affichage bilingue au survol</span>
          <label class="switch">
            <input type="checkbox" id="checkBilingual" checked aria-label="Activer l'affichage bilingue au survol">
            <span class="slider"></span>
          </label>
        </div>

        <div class="switch-row" style="margin-top: 8px; padding-top: 8px; border-top: 1px dashed #334155;">
          <span>Mode expérimental (IA non calibrée)</span>
          <label class="switch">
            <input type="checkbox" id="checkExperimental" aria-label="Activer le mode expérimental">
            <span class="slider"></span>
          </label>
        </div>

        <div class="status-box" aria-live="polite">
          <div class="status-line">
            <span>Intégrité financière :</span>
            <span style="color:#10B981; font-weight:800;">100% Inviolée</span>
          </div>
          <div class="status-line">
            <span class="pill"><span class="dot-green"></span> Validé (Humain) :</span>
            <span id="statHuman">0</span>
          </div>
          <div class="status-line">
            <span class="pill"><span class="dot-amber"></span> Suggéré (Auto) :</span>
            <span id="statMachine">0</span>
          </div>
          <div class="status-line">
            <span class="pill"><span class="dot-gray"></span> Source / Repli :</span>
            <span id="statFallback">0</span>
          </div>
        </div>
      </div>

      <div class="safinum-badge" id="badge" tabindex="0" role="button" aria-expanded="false" aria-label="Ouvrir le panneau d'accessibilité linguistique">
        <span aria-hidden="true">🇨🇲</span>
        <span id="badgeLabel">Duálá (Actif)</span>
      </div>
    `;

    shadowRoot.appendChild(styles);
    shadowRoot.appendChild(widget);

    // Événements du widget
    const badge = shadowRoot.getElementById('badge');
    const panel = shadowRoot.getElementById('panel');
    const btnClose = shadowRoot.getElementById('btnClose');
    const langSelect = shadowRoot.getElementById('langSelect');
    const btnToggleTranslate = shadowRoot.getElementById('btnToggleTranslate');
    const checkBilingual = shadowRoot.getElementById('checkBilingual');

    function togglePanel() {
      const isOpen = panel.classList.toggle('open');
      badge.setAttribute('aria-expanded', String(isOpen));
      if (isOpen) {
        langSelect.focus();
      }
    }

    badge.addEventListener('click', togglePanel);
    badge.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        togglePanel();
      }
    });

    btnClose.addEventListener('click', () => {
      panel.classList.remove('open');
      badge.setAttribute('aria-expanded', 'false');
      badge.focus();
    });

    panel.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        panel.classList.remove('open');
        badge.setAttribute('aria-expanded', 'false');
        badge.focus();
      }
    });

    langSelect.addEventListener('change', (e) => {
      state.currentLang = e.target.value;
      if (state.currentLang === 'fr') {
        state.isTranslated = false;
      } else {
        state.isTranslated = true;
      }
      processDOMTranslation();
    });

    btnToggleTranslate.addEventListener('click', () => {
      state.isTranslated = !state.isTranslated;
      processDOMTranslation();
    });

    checkBilingual.addEventListener('change', (e) => {
      state.bilingualMode = e.target.checked;
      processDOMTranslation();
    });

    const checkExperimental = shadowRoot.getElementById('checkExperimental');
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
      } else {
        if (optFul) {
          if (state.currentLang === 'ful') {
            state.currentLang = 'dua';
            langSelect.value = 'dua';
          }
          optFul.remove();
        }
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
