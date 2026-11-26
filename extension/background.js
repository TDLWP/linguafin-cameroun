/**
 * SAFINUM Accessibility Extension — Background Service Worker
 * Manifest V3 - Relais réseau sécurisé vers le backend local souverain
 *
 * RÈGLE D'ARCHITECTURE :
 * Ce service worker s'éxécute dans le contexte privilégié de l'extension.
 * Grâce aux \host_permissions\ accordées à l'extension, il effectue les appels
 * vers l'API locale (http://127.0.0.1:8000 et http://localhost:8000) sans être
 * bloqué par les restrictions Private Network Access (PNA) ou Mixed Content
 * imposées aux pages web publiques (comme https://safinum.cm).
 *
 * En cas d'indisponibilité ou de dépassement de délai (timeout 1.5s), il renvoie
 * un échec explicite afin que le content script bascule immédiatement et de
 * façon transparente sur le catalogue embarqué hors-ligne.
 */

'use strict';

const LOCAL_ENDPOINTS = [
  'http://127.0.0.1:8000/translate/batch',
  'http://localhost:8000/translate/batch'
];

/**
 * Tente d'envoyer le lot de traduction à l'API locale avec timeout strict.
 * @param {Object} payload 
 * @returns {Promise<{success: boolean, data?: Object, error?: string}>}
 */
async function translateBatchViaLocalApi(payload) {
  for (const endpoint of LOCAL_ENDPOINTS) {
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
        return { success: true, data };
      }
    } catch (e) {
      clearTimeout(timeoutId);
      // Échec de l'endpoint courant, passage au suivant
    }
  }

  return { success: false, error: 'Local backend unreachable or timed out' };
}

// Écoute des messages runtime émis par le content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message && message.type === 'SAFINUM_TRANSLATE_BATCH') {
    translateBatchViaLocalApi(message.payload)
      .then(res => sendResponse(res))
      .catch(err => sendResponse({ success: false, error: err.message }));
    return true; // Indique une réponse asynchrone
  }

  if (message && message.type === 'SAFINUM_HEALTH_CHECK') {
    sendResponse({ success: true, status: 'active', timestamp: Date.now() });
    return false;
  }
});
