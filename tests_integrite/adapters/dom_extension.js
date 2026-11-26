/* Adaptateur generique : charge les content scripts d'une extension MV3 dans jsdom (page https://safinum.cm/hackathon-test),
   insere un <p> par cas dans #app, attend le traitement et relit le texte affiche.
   Usage : node run.js adapters/dom_extension.js --ext <dossier de l'extension>  (necessite jsdom : NODE_PATH=.../node_modules) */
const fs = require('fs'), path = require('path');
const { JSDOM } = require('jsdom');
const sleep = ms => new Promise(r => setTimeout(r, ms));
exports.run = async (cases, opts) => {
  const ext = path.resolve(opts.ext || '.');
  const manifest = JSON.parse(fs.readFileSync(path.join(ext, 'manifest.json'), 'utf8').replace(/^\uFEFF/, ''));
  const scripts = [].concat(...manifest.content_scripts.map(c => c.js || []));
  const dom = new JSDOM('<!doctype html><html><body><div id="app"></div></body></html>', { url: 'https://safinum.cm/hackathon-test', runScripts: 'outside-only', pretendToBeVisual: true });
  const w = dom.window; const app = w.document.getElementById('app');
  const els = cases.map(c => { const p = w.document.createElement('p'); p.setAttribute('data-id', c.id); p.textContent = c.text; app.appendChild(p); return p; });
  const store = {};
  const area = { get: (k, cb) => { const r = {}; (Array.isArray(k) ? k : [k]).forEach(x => { if (store[x] !== undefined) r[x] = store[x]; }); cb && cb(r); return Promise.resolve(r); }, set: (o, cb) => { Object.assign(store, o); cb && cb(); return Promise.resolve(); } };
  w.chrome = { runtime: { getURL: p => 'file://' + path.join(ext, p), sendMessage: () => {}, onMessage: { addListener() {} }, id: 'test' }, storage: { local: area, sync: area } };
  w.fetch = async url => {
    if (String(url).startsWith('file://')) { const f = String(url).slice(7); const t = fs.readFileSync(f, 'utf8'); return { ok: true, status: 200, json: async () => JSON.parse(t), text: async () => t }; }
    throw new Error('reseau bloque pour le test : ' + url);
  };
  w.eval('self = window;');
  scripts.forEach(s => w.eval(fs.readFileSync(path.join(ext, s), 'utf8')));
  await sleep(2500);
  let changed = els.some((e, i) => e.textContent !== cases[i].text);
  if (!changed) {                                   // essaie d'activer la traduction via le widget (Shadow DOM ouvert)
    const host = w.document.querySelector('[id*="safinum"]');
    const sr = host && host.shadowRoot;
    if (sr) { const b = [...sr.querySelectorAll('button')].find(x => /traduit|translate|activer/i.test(x.textContent)); if (b) { b.click(); await sleep(2500); } }
  }
  const outs = els.map(e => e.textContent);
  dom.window.close();
  return outs;
};
