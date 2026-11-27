# -*- coding: utf-8 -*-
"""
scripts/test_integrite_figee.py — Rejoue le jeu de test d'intégrité financière (cases.json)
avec les MÊMES règles d'oracle que run.js sur trois chemins d'exécution :
  (a) Pipeline backend/protect.py : masquage -> pseudo-traduction -> restauration + verify_integrity
  (b) POST /translate/batch : API locale FastAPI en source fr et en
  (c) Chemin hors ligne de extension/content.js via Node si node est disponible
      (annonce la taille avant d'installer jsdom ; sinon indique « non exécuté »)
"""

import os
import sys
import json
import shutil
import subprocess
import re
import unicodedata
from typing import Dict, List, Any, Optional

# Encodage standardisé UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Injection du chemin racine pour imports backend
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.protect import (
    mask_sensitive_data,
    restore_sensitive_data,
    verify_integrity,
    is_secret_text,
    TOKEN_REGEX,
)


# ============================================================================
# RÈGLES DE L'ORACLE (Conformes caractère pour caractère à tests_integrite/run.js)
# ============================================================================

def nd(s: Any) -> List[str]:
    """
    Extrait tous les chiffres décimaux Unicode consécutifs (\\p{Nd}+),
    triés par ordre alphabétique.
    Équivalent JavaScript : (String(s).match(/\\p{Nd}+/gu) || []).sort()
    """
    res = []
    cur = []
    for ch in str(s):
        if unicodedata.category(ch) == 'Nd':
            cur.append(ch)
        elif cur:
            res.append(''.join(cur))
            cur = []
    if cur:
        res.append(''.join(cur))
    res.sort()
    return res


def count(s: str, p: str) -> int:
    """
    Compte les occurrences non chevauchantes de p dans s.
    Équivalent JavaScript : let c = 0, i = 0; while ((i = s.indexOf(p, i)) >= 0) { c++; i += p.length; } return c;
    """
    if not p:
        return 0
    return str(s).count(p)


def plain(c: Dict[str, Any], out: str) -> List[str]:
    """
    Vérification stricte de base :
    - Chaque valeur protégée listée doit apparaître le même nombre de fois.
    - Aucun chiffre Unicode (\\p{Nd}) ne doit être ajouté ni perdu.
    """
    pb = []
    src_text = c['text']
    for p in c.get('protected', []):
        if count(out, p) != count(src_text, p):
            pb.append('valeur modifiee/perdue/dupliquee : ' + json.dumps(p))
    src_nd = nd(src_text)
    out_nd = nd(out)
    if '|'.join(out_nd) != '|'.join(src_nd):
        pb.append(f"chiffres differents : [{', '.join(src_nd)}] -> [{', '.join(out_nd)}]")
    return pb


def judge(c: Dict[str, Any], out: Any) -> Dict[str, Any]:
    """
    Oracle de décision (identique à function judge(c, out) de run.js).
    Retourne {'s': 'OK'|'ECHEC'|'AVERT', 'why': [...]}
    """
    if not isinstance(out, str):
        return {'s': 'ECHEC', 'why': ['pas de sortie']}

    src_text = c['text']

    # 1. Secrets (OTP / PIN) : la sortie doit être strictement identique à l'entrée
    if c.get('secret'):
        return {'s': 'OK'} if out == src_text else {
            's': 'ECHEC',
            'why': ['secret transforme ou envoye : ' + json.dumps(out)[:80]]
        }

    # 2. Valeurs pures (date seule, marque pure) : sortie identique à l'entrée
    if c.get('pure_values'):
        return {'s': 'OK'} if out == src_text else {
            's': 'ECHEC',
            'why': ['valeur seule modifiee : ' + json.dumps(out)[:80]]
        }

    # 3. Affichage bilingue « source [proposition] » : la source est conservée, on juge la proposition
    if out.startswith(src_text + ' [') and out.endswith(']'):
        prop = out[len(src_text) + 2 : -1]
        src_nd = nd(src_text)
        prop_nd = nd(prop)
        invented = [x for x in prop_nd if x not in src_nd]
        if invented:
            return {'s': 'ECHEC', 'why': [f"chiffre invente dans la proposition : {invented}"]}
        miss = plain(c, prop)
        return {'s': 'AVERT', 'why': [f"proposition incomplete (source conservee) : {miss[0]}"]} if miss else {'s': 'OK'}

    # 4. Jugement direct du texte de sortie
    pb = plain(c, out)
    return {'s': 'ECHEC', 'why': pb} if pb else {'s': 'OK'}


# ============================================================================
# PSEUDO-TRADUCTION POUR LE CHEMIN (a)
# ============================================================================

SAFE_AND_ESCAPED_TOKEN_REGEX = re.compile(r"__(?:SAFE|ESCAPED_SAFE)_[A-Za-z0-9_]+__")


def pseudo_translate(masked_text: str) -> str:
    """
    Pseudo-traduction simulant le comportement hostile d'un moteur automatique :
    - Remplace les voyelles par des voyelles accentuées en dehors des jetons.
    - Préserve rigoureusement les jetons __SAFE_*__ et faux jetons échappés sans générer aucun chiffre.
    """
    vowel_map = {
        'a': '\u00e0', 'e': '\u00e9', 'i': '\u00ec', 'o': '\u00f4', 'u': '\u00f9', 'y': '\u0177',
        'A': '\u00c0', 'E': '\u00c9', 'I': '\u00cc', 'O': '\u00d4', 'U': '\u00d9'
    }
    parts = SAFE_AND_ESCAPED_TOKEN_REGEX.split(masked_text)
    tokens = SAFE_AND_ESCAPED_TOKEN_REGEX.findall(masked_text)
    out = []
    for i, p in enumerate(parts):
        # Modification des voyelles uniquement dans le texte hors jetons
        mod = ''.join(vowel_map.get(ch, ch) for ch in p)
        out.append(mod)
        if i < len(tokens):
            out.append(tokens[i])
    return ''.join(out)


# ============================================================================
# EXÉCUTION DES TROIS CHEMINS
# ============================================================================

def run_path_a_protect_pipeline(cases: List[Dict[str, Any]]) -> List[str]:
    """
    Chemin (a) : Pipeline backend/protect.py :
    masquage -> pseudo-traduction -> restauration + verify_integrity.
    """
    outputs = []
    for c in cases:
        text = c['text']

        # Règle absolue : les secrets (OTP/PIN) ne doivent JAMAIS être traduits
        if is_secret_text(text) or c.get('secret'):
            outputs.append(text)
            continue

        # Si le cas est marqué comme valeur pure (date seule, marque pure)
        if c.get('pure_values'):
            outputs.append(text)
            continue

        # Masquage par jetons inviolables
        masked, token_map, ordered = mask_sensitive_data(text)

        # Si après masquage et retrait des jetons il ne reste aucune lettre à traduire
        stripped = TOKEN_REGEX.sub('', masked)
        has_letters = any(unicodedata.category(ch).startswith('L') for ch in stripped)
        if not has_letters:
            outputs.append(text)
            continue

        # Pseudo-traduction
        pseudo = pseudo_translate(masked)

        # Restauration
        restored, is_valid = restore_sensitive_data(pseudo, token_map, text)

        # Contrôle d'intégrité
        if is_valid and verify_integrity(text, restored, token_map):
            outputs.append(restored)
        else:
            outputs.append(text)

    return outputs


def run_path_b_api_batch(cases: List[Dict[str, Any]]) -> List[str]:
    """
    Chemin (b) : POST /translate/batch en source fr et en
    via TestClient FastAPI sur backend.api:app.
    """
    from fastapi.testclient import TestClient
    from backend.api import app

    client = TestClient(app)

    # Séparation selon la langue source déclarée du cas
    cases_fr = [(i, c) for i, c in enumerate(cases) if c.get('lang', 'fr') != 'en']
    cases_en = [(i, c) for i, c in enumerate(cases) if c.get('lang') == 'en']

    results: Dict[int, str] = {}

    # 1. Lot en source française
    if cases_fr:
        payload_fr = {
            "source_lang": "fr",
            "target_lang": "dua",
            "allow_machine_translation": True,
            "items": [{"id": f"idx_{i}", "text": c['text']} for i, c in cases_fr]
        }
        resp_fr = client.post("/translate/batch", json=payload_fr)
        if resp_fr.status_code != 200:
            raise RuntimeError(f"Erreur POST /translate/batch (fr): {resp_fr.status_code} {resp_fr.text}")
        data_fr = resp_fr.json()
        for item_resp in data_fr.get("items", []):
            idx = int(item_resp["id"].replace("idx_", ""))
            results[idx] = item_resp["target_text"]

    # 2. Lot en source anglaise
    if cases_en:
        payload_en = {
            "source_lang": "en",
            "target_lang": "dua",
            "allow_machine_translation": True,
            "items": [{"id": f"idx_{i}", "text": c['text']} for i, c in cases_en]
        }
        resp_en = client.post("/translate/batch", json=payload_en)
        if resp_en.status_code != 200:
            raise RuntimeError(f"Erreur POST /translate/batch (en): {resp_en.status_code} {resp_en.text}")
        data_en = resp_en.json()
        for item_resp in data_en.get("items", []):
            idx = int(item_resp["id"].replace("idx_", ""))
            results[idx] = item_resp["target_text"]

    return [results.get(i, "") for i in range(len(cases))]


def run_path_c_offline_node(cases: List[Dict[str, Any]]) -> Optional[List[str]]:
    """
    Chemin (c) : Chemin hors ligne de extension/content.js via Node si node est disponible.
    Vérifie la présence de jsdom. Si absent, annonce la taille estimée et retourne None (« non exécuté »).
    """
    node_bin = shutil.which("node")
    if not node_bin:
        print("\n[Chemin c] Node.js non trouvé dans le PATH : non exécuté.")
        return None

    # Vérification de jsdom dans l'environnement Node
    check_jsdom = subprocess.run(
        [node_bin, "-e", "try { require('jsdom'); console.log('OK'); } catch(e) { process.exit(1); }"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT
    )
    if check_jsdom.returncode != 0:
        print("\n[Chemin c] extension/content.js hors-ligne via Node/jsdom :")
        print("  -> NON EXÉCUTÉ (bibliothèque 'jsdom' non installée dans node_modules).")
        print("  -> Annonce de taille de téléchargement : jsdom ~6,9 Mo décompressé (archive npm ~3,5 Mo, ~15 à 20 Mo avec ses dépendances transitives).")
        print("  -> Conformément aux règles AGENTS.md (règles 6, 7 et 10.5), aucune installation n'est lancée sans validation explicite.")
        return None

    # Si jsdom est disponible, exécuter l'adaptateur
    adapter_path = os.path.join(PROJECT_ROOT, "tests_integrite", "adapters", "dom_extension.js")
    ext_path = os.path.join(PROJECT_ROOT, "extension")
    run_js_path = os.path.join(PROJECT_ROOT, "tests_integrite", "run.js")
    out_json = os.path.join(PROJECT_ROOT, "tests_integrite", "sortie_c.json")

    cmd = [node_bin, run_js_path, adapter_path, "--ext", ext_path, "--json", out_json]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)
    if os.path.exists(out_json):
        with open(out_json, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("outs")
    print(f"[Chemin c] Échec d'exécution Node jsdom: {proc.stderr}")
    return None


# ============================================================================
# RAPPORT DES RÉSULTATS PAR GROUPE ET BILAN
# ============================================================================

def report_results(path_name: str, cases: List[Dict[str, Any]], outputs: List[str]) -> Dict[str, Any]:
    """
    Rapporte les résultats bruts par groupe (nombre OK / ECHEC / AVERT),
    avec liste exhaustive de chaque ÉCHEC et AVERTISSEMENT.
    """
    print(f"\n================================================================================")
    print(f"RÉSULTATS DU {path_name}")
    print(f"================================================================================")

    res = [judge(c, outputs[i]) for i, c in enumerate(cases)]

    by_group: Dict[str, Dict[str, int]] = {}
    ok_count = 0
    echec_count = 0
    avert_count = 0

    echecs_detail = []
    averts_detail = []

    for i, c in enumerate(cases):
        grp = c['group']
        if grp not in by_group:
            by_group[grp] = {'OK': 0, 'ECHEC': 0, 'AVERT': 0}

        verdict = res[i]['s']
        by_group[grp][verdict] += 1

        if verdict == 'OK':
            ok_count += 1
        elif verdict == 'ECHEC':
            echec_count += 1
            echecs_detail.append((c, res[i]['why'], outputs[i]))
        else:
            avert_count += 1
            averts_detail.append((c, res[i]['why'], outputs[i]))

    # Affichage des ÉCHECS
    if echecs_detail:
        print("\n--- ÉCHECS IDENTIFIÉS ---")
        for c, why, out in echecs_detail:
            print(f"ECHEC {c['id']} [{c['group']}] \"{c['text'][:70]}\"")
            print(f"     -> Raison : {' ; '.join(why)}")
            print(f"     -> Sortie réelle : {json.dumps(out)[:100]}")

    # Affichage des AVERTISSEMENTS
    if averts_detail:
        print("\n--- AVERTISSEMENTS ---")
        for c, why, out in averts_detail:
            print(f"AVERT {c['id']} [{c['group']}] \"{c['text'][:70]}\" -> {why[0]}")

    # Synthèse par groupe
    print("\nBilan par groupe :")
    for grp, counts in sorted(by_group.items()):
        print(f"  {grp.ljust(24)} : {counts['OK']} OK, {counts['ECHEC']} ECHEC, {counts['AVERT']} AVERT")

    print(f"\nTotal {path_name} : {ok_count} OK, {echec_count} ECHEC(S), {avert_count} AVERTISSEMENT(S) sur {len(cases)} cas")

    return {
        "ok": ok_count,
        "echec": echec_count,
        "avert": avert_count,
        "by_group": by_group,
        "echecs": echecs_detail,
        "averts": averts_detail
    }


def main():
    cases_file = os.path.join(PROJECT_ROOT, "tests_integrite", "cases.json")
    if not os.path.exists(cases_file):
        print(f"Erreur : fichier {cases_file} introuvable.")
        sys.exit(1)

    with open(cases_file, "r", encoding="utf-8") as f:
        cases_data = json.load(f)

    cases = cases_data.get("cases", [])
    print(f"Chargement de {len(cases)} cas depuis tests_integrite/cases.json (version {cases_data.get('version')}).")

    # (a) Pipeline backend/protect.py
    outs_a = run_path_a_protect_pipeline(cases)
    res_a = report_results("Chemin (a) [Pipeline protect.py masquage/pseudo-traduction/restauration]", cases, outs_a)

    # (b) POST /translate/batch
    outs_b = run_path_b_api_batch(cases)
    res_b = report_results("Chemin (b) [API POST /translate/batch source fr et en]", cases, outs_b)

    # (c) Chemin hors ligne extension/content.js
    outs_c = run_path_c_offline_node(cases)
    if outs_c is not None:
        report_results("Chemin (c) [extension/content.js hors-ligne via Node]", cases, outs_c)
    else:
        print("\n================================================================================")
        print("RÉSULTATS DU Chemin (c) [extension/content.js hors-ligne via Node]")
        print("================================================================================")
        print("Statut : NON EXÉCUTÉ (jsdom non disponible ; annonce de taille formulée).")

    # Code de retour global : 1 si un échec de sécurité subsiste sur les chemins exécutés
    total_echecs = res_a["echec"] + res_b["echec"]
    if total_echecs > 0:
        print(f"\n[ATTENTION] {total_echecs} ÉCHEC(S) DE SÉCURITÉ DÉTECTÉ(S).")
        sys.exit(1)
    else:
        print(f"\n[SUCCÈS] Tous les chemins exécutés ont 0 ÉCHEC de sécurité !")
        sys.exit(0)


if __name__ == "__main__":
    main()
