# -*- coding: utf-8 -*-
"""
scripts/recoupement_references_ui.py — Recoupement des chaînes d'interface SAFINUM
avec les sources de référence communautaires externes :
  - DS-06 : Common Voice Mozilla (format Fluent .ftl, langues dua/bas/en, licence MPL-2.0)
  - DS-30 : MediaWiki Wikimedia (format JSON en.json/dua.json/datetime_*.json, licence GPL-2.0+)

RÈGLES STRICTES :
1. Les données externes sont hors du dépôt et ne doivent JAMAIS y être copiées.
2. Aucune traduction inventée.
3. Correspondance EXACTE (insensible à la casse et à la ponctuation) avec un message anglais
   de référence, puis récupération de la traduction communautaire à clé égale en dua / bas.
4. Génère catalogue/recoupement_ui_resultats.csv et affiche le décompte par langue.
"""

import os
import sys
import json
import csv
import string
import re
import argparse
from typing import Dict, List, Tuple, Any, Optional

# Encodage standardisé UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_EXTERNAL_DIR = r"C:\Users\FLEX ZONE\Desktop\donnees_externes_safinum\DOSSIER_RECHERCHE_DONNEES_SAFINUM\03_DATASETS_TELECHARGES"


def normalize_text_for_match(text: str) -> str:
    """
    Normalisation stricte pour correspondance exacte :
    - Minuscules
    - Suppression balises simples HTML (<...>) ou variables Fluent ({...})
    - Suppression ponctuation et guillemets typographiques
    - Normalisation des espaces consécutifs et insécables
    """
    if not text or not isinstance(text, str):
        return ""
    # Retrait balises HTML
    cleaned = re.sub(r"<[^>]+>", "", text)
    # Retrait variables Fluent { $var }
    cleaned = re.sub(r"\{\s*\$[a-zA-Z0-9_-]+\s*\}", "", cleaned)
    cleaned = cleaned.lower()
    # Remplacer ponctuation et tirets par un espace
    cleaned = "".join(ch if (ch not in string.punctuation and ch not in "—–«»…\"'‘’") else " " for ch in cleaned)
    # Réduire tous les espaces consécutifs et insécables
    cleaned = re.sub(r"[\s\u00a0\u202f\u2007\u200b]+", " ", cleaned)
    return cleaned.strip()


def parse_fluent_ftl(filepath: str) -> Dict[str, str]:
    """
    Parseur déterministe pour fichiers Mozilla Fluent (.ftl).
    Extrait les messages simples {message_id: message_value}.
    """
    messages = {}
    if not os.path.exists(filepath):
        return messages

    current_key = None
    current_val: List[str] = []

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            # Ignorer commentaires (#, ##, ###) et termes globaux (-)
            if stripped.startswith("#") or stripped.startswith("-"):
                continue

            # Nouvelle clé : "identifiant = ..."
            m = re.match(r"^([a-zA-Z0-9_-]+)\s*=\s*(.*)$", line)
            if m:
                if current_key:
                    messages[current_key] = "\n".join(current_val).strip()
                current_key = m.group(1)
                val = m.group(2).strip()
                current_val = [val] if val else []
            elif current_key and (line.startswith(" ") or line.startswith("\t")):
                current_val.append(stripped)
            else:
                if current_key and not stripped:
                    pass

        if current_key:
            messages[current_key] = "\n".join(current_val).strip()

    return messages


def load_common_voice_data(ds06_dir: str) -> Dict[str, Dict[str, List[Dict[str, str]]]]:
    """
    Charge les chaînes Common Voice (.ftl) pour en, dua, bas.
    Retourne index_by_lang: { 'dua': { norm_en: [ {cle, en, local, origine, fichier} ] }, 'bas': ... }
    """
    index: Dict[str, Dict[str, List[Dict[str, str]]]] = {"dua": {}, "bas": {}}
    en_dir = os.path.join(ds06_dir, "en")
    if not os.path.exists(en_dir):
        print(f"[AVERTISSEMENT] Dossier anglais Common Voice introuvable : {en_dir}")
        return index

    for lang in ["dua", "bas"]:
        lang_dir = os.path.join(ds06_dir, lang)
        if not os.path.exists(lang_dir):
            continue

        for root, _, files in os.walk(en_dir):
            for f in files:
                if f.endswith(".ftl"):
                    rel = os.path.relpath(os.path.join(root, f), en_dir)
                    en_path = os.path.join(en_dir, rel)
                    lang_path = os.path.join(lang_dir, rel)

                    en_msgs = parse_fluent_ftl(en_path)
                    lang_msgs = parse_fluent_ftl(lang_path)

                    for k, en_txt in en_msgs.items():
                        if k in lang_msgs and lang_msgs[k]:
                            n_en = normalize_text_for_match(en_txt)
                            if not n_en:
                                continue
                            if n_en not in index[lang]:
                                index[lang][n_en] = []
                            index[lang][n_en].append({
                                "cle": k,
                                "en": en_txt,
                                "local": lang_msgs[k],
                                "origine": "CV",
                                "fichier": rel
                            })

    return index


def load_mediawiki_data(ds30_dir: str) -> Dict[str, Dict[str, List[Dict[str, str]]]]:
    """
    Charge les messages MediaWiki (en.json, dua.json, datetime_bas.json, datetime_dua.json).
    Retourne index_by_lang: { 'dua': { norm_en: [ {cle, en, local, origine, fichier} ] }, 'bas': ... }
    """
    index: Dict[str, Dict[str, List[Dict[str, str]]]] = {"dua": {}, "bas": {}}
    en_json_path = os.path.join(ds30_dir, "en.json")
    if not os.path.exists(en_json_path):
        print(f"[AVERTISSEMENT] Fichier MediaWiki en.json introuvable : {en_json_path}")
        return index

    with open(en_json_path, "r", encoding="utf-8") as f:
        mw_en = json.load(f)

    # 1. Duala (dua.json)
    dua_json_path = os.path.join(ds30_dir, "dua.json")
    if os.path.exists(dua_json_path):
        with open(dua_json_path, "r", encoding="utf-8") as f:
            mw_dua = json.load(f)
        for k, local_txt in mw_dua.items():
            if k.startswith("@") or not isinstance(local_txt, str):
                continue
            if k in mw_en and isinstance(mw_en[k], str):
                en_txt = mw_en[k]
                n_en = normalize_text_for_match(en_txt)
                if not n_en:
                    continue
                if n_en not in index["dua"]:
                    index["dua"][n_en] = []
                index["dua"][n_en].append({
                    "cle": k,
                    "en": en_txt,
                    "local": local_txt,
                    "origine": "MediaWiki",
                    "fichier": "dua.json"
                })

    # 2. Datetime pour Bassa'a et Duala
    for lang, fname in [("bas", "datetime_bas.json"), ("dua", "datetime_dua.json")]:
        dt_path = os.path.join(ds30_dir, fname)
        if os.path.exists(dt_path):
            with open(dt_path, "r", encoding="utf-8") as f:
                dt_data = json.load(f)
            for k, local_txt in dt_data.items():
                if k.startswith("@") or not isinstance(local_txt, str):
                    continue
                if k in mw_en and isinstance(mw_en[k], str):
                    en_txt = mw_en[k]
                    n_en = normalize_text_for_match(en_txt)
                    if not n_en:
                        continue
                    if n_en not in index[lang]:
                        index[lang][n_en] = []
                    index[lang][n_en].append({
                        "cle": k,
                        "en": en_txt,
                        "local": local_txt,
                        "origine": "MediaWiki",
                        "fichier": fname
                    })

    return index


def resolve_external_data_dir(cli_arg: Optional[str] = None) -> str:
    """Détermine le chemin des données externes via CLI, ENV ou valeur par défaut."""
    if cli_arg and os.path.exists(cli_arg):
        return cli_arg

    env_dir = os.environ.get("SAFINUM_EXTERNAL_DATA_DIR") or os.environ.get("DONNEES_EXTERNES_SAFINUM")
    if env_dir and os.path.exists(env_dir):
        return env_dir

    if os.path.exists(DEFAULT_EXTERNAL_DIR):
        return DEFAULT_EXTERNAL_DIR

    raise FileNotFoundError(
        f"Dossier de données externes introuvable.\n"
        f"Veuillez définir la variable d'environnement SAFINUM_EXTERNAL_DATA_DIR "
        f"ou passer l'argument --data-dir <chemin>.\n"
        f"Chemin testé par défaut : {DEFAULT_EXTERNAL_DIR}"
    )


def execute_recoupement(
    external_dir: str,
    translations_csv_path: str,
    test_env_strings_path: str,
    output_csv_path: str
) -> Dict[str, Any]:
    """Exécute le recoupement complet et produit le fichier CSV de résultats."""
    ds06_dir = os.path.join(external_dir, "DS-06_commonvoice_chaines_interface_Fluent")
    ds30_dir = os.path.join(external_dir, "DS-30_mediawiki_interface_duala")

    if not os.path.exists(ds06_dir):
        print(f"[AVERTISSEMENT] Répertoire DS-06 introuvable dans {external_dir}")
    if not os.path.exists(ds30_dir):
        print(f"[AVERTISSEMENT] Répertoire DS-30 introuvable dans {external_dir}")

    print(f"Chargement des références externes depuis : {external_dir}")
    cv_index = load_common_voice_data(ds06_dir)
    mw_index = load_mediawiki_data(ds30_dir)

    # Chargement des chaînes de test anglaises
    with open(test_env_strings_path, "r", encoding="utf-8") as f:
        env_strings = json.load(f)

    # Chargement du catalogue
    with open(translations_csv_path, "r", encoding="utf-8") as f:
        trans_rows = list(csv.DictReader(f))

    results = []
    stats = {
        "dua": {"total": 0, "avec_ref": 0, "identique": 0, "different": 0, "absent": 0},
        "bas": {"total": 0, "avec_ref": 0, "identique": 0, "different": 0, "absent": 0}
    }

    for row in trans_rows:
        cle = row["cle"]
        source_fr = row["source"]
        langue = row["langue"]
        notre_prop = row["cible"]

        # Récupération de l'équivalent anglais
        source_en = env_strings.get(source_fr, {}).get("en")
        if not source_en:
            # Règle : seulement les chaînes qui ont un équivalent anglais dans test_env_strings.json
            continue

        if langue not in stats:
            continue

        stats[langue]["total"] += 1
        n_en = normalize_text_for_match(source_en)

        # Recherche de correspondances exactes dans MediaWiki et Common Voice
        matches = []
        if langue in mw_index and n_en in mw_index[langue]:
            matches.extend(mw_index[langue][n_en])
        if langue in cv_index and n_en in cv_index[langue]:
            matches.extend(cv_index[langue][n_en])

        if matches:
            # Sélection de la référence communautaire la plus concise (terme court d'interface)
            best_match = min(matches, key=lambda m: len(m["local"]))
            ref_comm = best_match["local"]
            origine = best_match["origine"]

            # Accord : identique vs différent
            if normalize_text_for_match(notre_prop) == normalize_text_for_match(ref_comm):
                accord = "identique"
                stats[langue]["identique"] += 1
            else:
                accord = "different"
                stats[langue]["different"] += 1
            stats[langue]["avec_ref"] += 1
        else:
            ref_comm = ""
            origine = ""
            accord = "absent"
            stats[langue]["absent"] += 1

        results.append({
            "cle": cle,
            "langue": langue,
            "source_fr": source_fr,
            "source_en": source_en,
            "source_fr_en": f"{source_fr} / {source_en}",
            "notre_proposition": notre_prop,
            "reference_communautaire": ref_comm,
            "origine": origine,
            "accord": accord
        })

    # Écriture du fichier CSV
    fieldnames = [
        "cle",
        "langue",
        "source_fr",
        "source_en",
        "source_fr_en",
        "notre_proposition",
        "reference_communautaire",
        "origine",
        "accord"
    ]
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    with open(output_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\n[OK] Fichier de résultats généré avec succès : {output_csv_path} ({len(results)} lignes).")
    return {
        "results": results,
        "stats": stats,
        "output_file": output_csv_path
    }


def main():
    parser = argparse.ArgumentParser(
        description="Recoupement des chaînes d'interface avec Common Voice et MediaWiki."
    )
    parser.add_argument(
        "--data-dir", "-d",
        type=str,
        default=None,
        help="Chemin vers le dossier externe 03_DATASETS_TELECHARGES."
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=os.path.join(PROJECT_ROOT, "catalogue", "recoupement_ui_resultats.csv"),
        help="Chemin de sortie du fichier CSV."
    )
    args = parser.parse_args()

    external_dir = resolve_external_data_dir(args.data_dir)
    translations_csv_path = os.path.join(PROJECT_ROOT, "catalogue", "translations.csv")
    test_env_strings_path = os.path.join(PROJECT_ROOT, "data", "test_env_strings.json")

    summary = execute_recoupement(
        external_dir=external_dir,
        translations_csv_path=translations_csv_path,
        test_env_strings_path=test_env_strings_path,
        output_csv_path=args.output
    )

    stats = summary["stats"]
    total_eval = stats["dua"]["total"] + stats["bas"]["total"]
    total_avec_ref = stats["dua"]["avec_ref"] + stats["bas"]["avec_ref"]
    total_identique = stats["dua"]["identique"] + stats["bas"]["identique"]
    total_different = stats["dua"]["different"] + stats["bas"]["different"]
    total_absent = stats["dua"]["absent"] + stats["bas"]["absent"]

    print("\n" + "=" * 70)
    print("        BILAN DU RECOUPEMENT DES RÉFÉRENCES UI COMMUNAUTAIRES        ")
    print("=" * 70)
    print(f"Total des segments évalués (avec source EN) : {total_eval}")
    print(f"Total des segments avec référence trouvée   : {total_avec_ref} ({total_avec_ref/total_eval*100:.1f} %)")
    print(f"  - Identiques                              : {total_identique}")
    print(f"  - Différents                              : {total_different}")
    print(f"  - Absents                                 : {total_absent}")
    print("-" * 70)
    print(f"Détail Duálá (dua) :")
    print(f"  - Évalués        : {stats['dua']['total']}")
    print(f"  - Avec référence : {stats['dua']['avec_ref']} ({stats['dua']['avec_ref']/stats['dua']['total']*100:.1f} %)")
    print(f"  - Accords        : {stats['dua']['identique']} identique, {stats['dua']['different']} différent, {stats['dua']['absent']} absent")
    print("-" * 70)
    print(f"Détail Ɓàsàa (bas) :")
    print(f"  - Évalués        : {stats['bas']['total']}")
    print(f"  - Avec référence : {stats['bas']['avec_ref']} ({stats['bas']['avec_ref']/stats['bas']['total']*100:.1f} %)")
    print(f"  - Accords        : {stats['bas']['identique']} identique, {stats['bas']['different']} différent, {stats['bas']['absent']} absent")
    print("=" * 70 + "\n")

    print("Détail des 8 correspondances trouvées :")
    for r in summary["results"]:
        if r["accord"] != "absent":
            print(f"  - [{r['cle']}] ({r['langue']}) FR: \"{r['source_fr']}\" | EN: \"{r['source_en']}\"")
            print(f"      Notre proposition : \"{r['notre_proposition']}\"")
            print(f"      Réf communautaire : \"{r['reference_communautaire']}\" ({r['origine']}) -> {r['accord']}")


if __name__ == "__main__":
    main()
