/* Lanceur du jeu de test d'integrite financiere.
   Usage : node run.js <adaptateur> [--strict] [--json sortie.json] [--bilingual] [options de l'adaptateur]
   Un adaptateur exporte  async run(cases, opts) -> tableau de sorties (une par cas).            */
const fs = require('fs'), path = require('path');
const argv = process.argv.slice(2);
if (!argv[0]) { console.log('Usage: node run.js <adapters/xxx.js> [--strict] [--json out.json] [--ext dossier]'); process.exit(2); }
const opt = n => { const i = argv.indexOf(n); return i >= 0 ? argv[i + 1] : null; };
const strict = argv.includes('--strict');
const data = JSON.parse(fs.readFileSync(path.join(__dirname, 'cases.json'), 'utf8'));
const adapter = require(path.resolve(argv[0]));
const nd = s => (String(s).match(/\p{Nd}+/gu) || []).sort();
const count = (s, p) => { let c = 0, i = 0; if (!p) return 0; while ((i = s.indexOf(p, i)) >= 0) { c++; i += p.length; } return c; };
function plain(c, out) {
  const pb = [];
  c.protected.forEach(p => { if (count(out, p) !== count(c.text, p)) pb.push('valeur modifiee/perdue/dupliquee : ' + JSON.stringify(p)); });
  if (nd(out).join('|') !== nd(c.text).join('|')) pb.push('chiffres differents : [' + nd(c.text) + '] -> [' + nd(out) + ']');
  return pb;
}
function judge(c, out) {
  if (typeof out !== 'string') return { s: 'ECHEC', why: ['pas de sortie'] };
  if (c.secret) return out === c.text ? { s: 'OK' } : { s: 'ECHEC', why: ['secret transforme ou envoye : ' + JSON.stringify(out).slice(0, 80)] };
  if (c.pure_values) return out === c.text ? { s: 'OK' } : { s: 'ECHEC', why: ['valeur seule modifiee : ' + JSON.stringify(out).slice(0, 80)] };
  // affichage bilingue « source [proposition] » : la source est conservee, on juge la proposition
  if (out.startsWith(c.text + ' [') && out.endsWith(']')) {
    const prop = out.slice(c.text.length + 2, -1), src = nd(c.text), invented = nd(prop).filter(x => !src.includes(x));
    if (invented.length) return { s: 'ECHEC', why: ['chiffre invente dans la proposition : ' + invented] };
    const miss = plain(c, prop);
    return miss.length ? { s: 'AVERT', why: ['proposition incomplete (source conservee) : ' + miss[0]] } : { s: 'OK' };
  }
  const pb = plain(c, out);
  return pb.length ? { s: 'ECHEC', why: pb } : { s: 'OK' };
}
(async () => {
  const t0 = Date.now();
  const outs = await adapter.run(data.cases, { ext: opt('--ext') });
  const res = data.cases.map((c, i) => Object.assign({ id: c.id, group: c.group }, judge(c, outs[i])));
  let ok = 0, ko = 0, av = 0, pol = 0; const by = {};
  data.cases.forEach((c, i) => {
    const r = res[i]; by[c.group] = by[c.group] || { OK: 0, ECHEC: 0, AVERT: 0 }; by[c.group][r.s]++;
    if (r.s === 'OK') ok++; else if (r.s === 'ECHEC') { ko++; console.log('ECHEC ' + c.id + ' [' + c.group + '] ' + JSON.stringify(c.text).slice(0, 70) + '\n     -> ' + r.why.join(' ; ') + '\n     sortie : ' + JSON.stringify(outs[i]).slice(0, 110)); }
    else { av++; console.log('AVERT ' + c.id + ' [' + c.group + '] ' + r.why[0]); }
    if (strict && c.unknown && !c.secret && !c.pure_values && outs[i] !== c.text) pol++;
  });
  console.log('\nPar groupe :'); Object.keys(by).forEach(g => console.log('  ' + g.padEnd(22) + JSON.stringify(by[g])));
  console.log('\nTotal: ' + ok + ' OK, ' + ko + ' ECHEC(S), ' + av + ' AVERTISSEMENT(S) sur ' + data.cases.length + ' cas' +
    (strict ? ' | politique : ' + pol + ' contenu(s) inconnu(s) modifie(s)' : '') + ' (' + (Date.now() - t0) + ' ms)');
  if (opt('--json')) fs.writeFileSync(opt('--json'), JSON.stringify({ adapter: argv[0], res, outs }, null, 1));
  process.exit(ko ? 1 : 0);
})();
