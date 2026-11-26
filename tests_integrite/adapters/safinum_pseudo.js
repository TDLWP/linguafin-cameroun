/* Adaptateur : couche Safinum (core.js) avec une « pseudo-traduction » appliquee a TOUT texte (pire cas pour le garde-fou). */
const C = require('../../../core.js');
function pseudo(tpl) {
  const map = { a: '\u00e0', e: '\u00e9', i: '\u00ec', o: '\u00f4', u: '\u00f9', y: '\u0177', A: '\u00c0', E: '\u00c9', I: '\u00cc', O: '\u00d4', U: '\u00d9' };
  return '\u00ab ' + tpl.split(/(\u27e6\d+\u27e7|\{x\})/).map(p => /^(\u27e6\d+\u27e7|\{x\})$/.test(p) ? p : p.replace(/[aeiouyAEIOU]/g, c => map[c])).join('') + ' \u00bb';
}
function tr(text) {
  if (C.isSecret && C.isSecret(text)) return text;
  const core = C.normalizeText(text);
  if (!/\p{L}/u.test(core.replace(/\d+/g, ''))) return text;
  const p = C.protect(text);
  if (!/\p{L}/u.test(p.key.replace(/\u27e6\d+\u27e7/g, ''))) return text;
  const tpl = pseudo(p.key), v = C.verify(p.tokens, tpl);
  if (!v.ok) return text;
  const out = C.restore(tpl, p.tokens);
  if (!C.finalCheck(p.tokens, out)) return text;
  return (/^\s*/.exec(text)[0]) + out + (/\s*$/.exec(text)[0]);
}
exports.run = async cases => cases.map(c => { const t = Date.now(); const o = tr(c.text); if (Date.now() - t > 100) console.log('LENT ' + c.id + ' ' + (Date.now() - t) + ' ms'); return o; });
