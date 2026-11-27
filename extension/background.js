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

const LOCAL_API_ENDPOINT = 'http://127.0.0.1:8000/translate/batch';
const LOCAL_HEALTH_ENDPOINT = 'http://127.0.0.1:8000/health';
const TIMEOUT_MS = 400; // Délai maximal strict de 400 ms par tentative (un seul essai)

/**
 * Tente d'envoyer le lot de traduction à l'API locale avec timeout strict de 400 ms.
 * Un seul essai (aucun essai successif sur un second hôte).
 * @param {Object} payload 
 * @returns {Promise<{success: boolean, data?: Object, error?: string}>}
 */
async function translateBatchViaLocalApi(payload) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_MS);

  try {
    const response = await fetch(LOCAL_API_ENDPOINT, {
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
  }

  return { success: false, error: 'Local backend unreachable or timed out (400ms)' };
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
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_MS);
    fetch(LOCAL_HEALTH_ENDPOINT, { method: 'GET', signal: controller.signal })
      .then(r => {
        clearTimeout(timeoutId);
        sendResponse({ success: r.ok, status: r.status });
      })
      .catch(err => {
        clearTimeout(timeoutId);
        sendResponse({ success: false, error: err.message });
      });
    return true;
  }
});

