# -*- coding: utf-8 -*-
"""
scripts/importer_validation.py — Importation rigoureuse des fiches de validation linguistique.

REGLES STRICTES D'INTEGRITE :
1. Une ligne ne passe en 'human_validated' QUE SI :
     - Le code validateur est explicitement renseigne (non vide) [via --validateur].
     - L'avis est OK (ou equivalent).
     - La date de validation est presente (non vide) [via --date].
     - La ligne n'a PAS de correction proposee.
2. Toute autre ligne reste 'machine_suggested'.
3. DOUTE passe en 'rejected'.
4. Une correction proposee passe en 'draft' (jamais 'human_validated').
5. Le script ne valide JAMAIS quoi que ce soit par defaut.
6. La correspondance se fait par (cle, langue) -- jamais par source seule.
7. Une ligne non retrouvee dans le catalogue est signalee, jamais creee.
"""

import os
import sys
import csv
import json
import re
import unicodedata
import argparse
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CATALOG_CSV = os.path.join(REPO_ROOT, "catalogue", "translations.csv")
DEFAULT_REPORT_PATH = os.path.join(REPO_ROOT, "catalogue", "kit_validation", "rapport_import_validation.md")
DEFAULT_OFFLINE_JSON = os.path.join(REPO_ROOT, "catalogue", "translations_offline.json")
DEFAULT_EXT_OFFLINE_JSON = os.path.join(REPO_ROOT, "extension", "offline_catalog.json")

LANGUES_VALIDES = {"dua", "bas"}

LANGUE_ALIASES = {
    "dua": "dua",
    "duala": "dua",
    "douala": "dua",
    "bas": "bas",
    "bassa": "bas",
    "bassaa": "bas",
}


def normalize_col_name(raw: str) -> str:
    """
    Normalise un nom de colonne CSV brut pour la reconnaissance robuste des en-tetes.
    Methode : NFKD decomposition, suppression accents, lowercase, ponctuation->espace.
    """
    n = unicodedata.normalize("NFKD", raw)
    n = "".join(c for c in n if not unicodedata.combining(c))
    # Remplacer les implosives Bh/bh (Basaa) par b
    n = n.replace("\u0181", "B").replace("\u0253", "b")
    n = n.strip().lower()
    clean = re.sub(r"[^a-z0-9]+", " ", n).strip()

    if clean in ("n", "no", "num", "numero", ""):
        return "num"
    if any(k in clean for k in ("cle", "contexte", "key",)):
        return "cle"
    if "id" == clean:
        return "cle"
    if "source" in clean or "francais" in clean:
        return "source"
    if any(k in clean for k in ("proposition", "traduction", "cible", "duala", "basaa", "basa")):
        return "proposition"
    if "correction" in clean:
        return "correction"
    if any(k in clean for k in ("ok ko", "okko", "validation", "avis", "decision")):
        return "avis"
    if any(k in clean for k in ("commentaire", "notes", "remarque")):
        return "commentaire"
    if any(k in clean for k in ("validateur", "code validateur")):
        return "validateur_code"
    if "date" in clean:
        return "date"
    if any(k in clean for k in ("langue", "lang")):
        return "langue"
    return clean


def normalize_langue(raw: str) -> Optional[str]:
    """Normalise le code langue. Retourne None si inconnu."""
    key = raw.strip().lower().replace("'", "").replace("a", "a")
    return LANGUE_ALIASES.get(key)


def load_input_csv(input_path: str) -> List[Dict[str, str]]:
    """Lit le CSV de validation et normalise les cles des dictionnaires."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Fichier de validation introuvable : {input_path}")

    rows = []
    for enc in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            rows = []
            with open(input_path, "r", encoding=enc) as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if not header:
                    return []
                norm_headers = [normalize_col_name(h) for h in header]
                for line_num, raw_row in enumerate(reader, start=2):
                    if not raw_row or not any(field.strip() for field in raw_row):
                        continue
                    entry = {}
                    for col_idx, col_name in enumerate(norm_headers):
                        val = raw_row[col_idx].strip() if col_idx < len(raw_row) else ""
                        entry[col_name] = val
                    entry["_line_num"] = str(line_num)
                    rows.append(entry)
            break
        except UnicodeDecodeError:
            rows = []
            continue
    return rows


def build_catalog_index(catalog_rows: List[Dict[str, str]]) -> Dict[Tuple[str, str], int]:
    """Construit l'index (cle, langue) -> indice."""
    index: Dict[Tuple[str, str], int] = {}
    for idx, row in enumerate(catalog_rows):
        cle = row.get("cle", "").strip()
        lang = row.get("langue", "").strip().lower()
        if cle and lang:
            index[(cle.lower(), lang)] = idx
    return index


def process_validation_import(
    input_rows: List[Dict[str, str]],
    catalog_path: str = DEFAULT_CATALOG_CSV,
    dry_run: bool = False,
    target_lang: str = "",
    val_code: str = "",
    val_date: str = "",
) -> Tuple[Dict[str, Any], List[Dict[str, str]]]:
    """
    Applique les regles strictes de transition d'etat sur le catalogue.
    Correspondance par (cle, langue). Jamais de creation de nouvelle entree.
    """
    with open(catalog_path, "r", encoding="utf-8") as f:
        catalog_reader = csv.DictReader(f)
        catalog_header = list(catalog_reader.fieldnames or [])
        catalog_rows = list(catalog_reader)

    catalog_index = build_catalog_index(catalog_rows)

    stats: Dict[str, Any] = {
        "total_input_rows": len(input_rows),
        "promoted_human_validated": [],
        "marked_rejected": [],
        "marked_revision_draft": [],
        "retained_machine_suggested": [],
        "errors": [],
    }

    modified_indices: set = set()

    for item in input_rows:
        line_num = item.get("_line_num", "?")

        # Cle du segment
        cle = item.get("cle", "").strip()
        if not cle:
            stats["errors"].append({
                "line": line_num, "cle": "(vide)", "langue": target_lang,
                "reason": "Cle manquante dans la ligne d'entree",
            })
            continue

        # Langue effective
        lang = target_lang.strip().lower() if target_lang else item.get("langue", "").strip().lower()
        if not lang:
            stats["errors"].append({
                "line": line_num, "cle": cle, "langue": "(inconnue)",
                "reason": "Langue non definie (utilisez --langue dua|bas)",
            })
            continue

        lang_norm = normalize_langue(lang)
        if lang_norm is None:
            stats["errors"].append({
                "line": line_num, "cle": cle, "langue": lang,
                "reason": f"Code langue non reconnu : '{lang}'",
            })
            continue
        lang = lang_norm

        # Recherche dans le catalogue par (cle, langue)
        cat_idx = catalog_index.get((cle.lower(), lang))
        if cat_idx is None:
            stats["errors"].append({
                "line": line_num, "cle": cle, "langue": lang,
                "reason": f"Cle '{cle}' introuvable dans translations.csv pour '{lang}'",
            })
            continue

        cat_row = catalog_rows[cat_idx]

        # Validateur et date effectifs
        effective_val_code = val_code or item.get("validateur_code", "").strip()
        effective_val_date = val_date or item.get("date", "").strip()

        avis_raw = item.get("avis", "").strip()
        avis = avis_raw.upper()
        corr = item.get("correction", "").strip()
        comm = item.get("commentaire", "").strip()
        old_status = cat_row.get("statut", "machine_suggested")

        # Regle A : Correction proposee -> draft (JAMAIS human_validated)
        if corr:
            cat_row["statut"] = "draft"
            cat_row["cible"] = corr
            if effective_val_code:
                cat_row["validateur_code"] = effective_val_code
            if effective_val_date:
                cat_row["date"] = effective_val_date
            cat_row["commentaire"] = (
                cat_row.get("commentaire", "")
                + f" [Proposition revisee par {effective_val_code or 'validateur'}: {corr}]"
            ).strip()
            modified_indices.add(cat_idx)
            stats["marked_revision_draft"].append({
                "line": line_num, "cle": cle, "langue": lang,
                "cible_originale": old_status, "correction": corr,
                "validateur_code": effective_val_code or "(non precise)",
                "date": effective_val_date or "(non precisee)",
                "action": f"Passe en draft avec proposition corrigee: '{corr}'",
            })
            continue

        # Regle B : DOUTE -> rejected
        if "DOUTE" in avis or avis in ("DOUBT", "INCERTAIN", "SUSPECT"):
            cat_row["statut"] = "rejected"
            if effective_val_code:
                cat_row["validateur_code"] = effective_val_code
            if effective_val_date:
                cat_row["date"] = effective_val_date
            cat_row["commentaire"] = (
                cat_row.get("commentaire", "")
                + f" [Rejet preventif: validateur {effective_val_code or '?'} signale DOUTE]"
            ).strip()
            modified_indices.add(cat_idx)
            stats["marked_rejected"].append({
                "line": line_num, "cle": cle, "langue": lang,
                "cible": cat_row.get("cible", ""),
                "validateur_code": effective_val_code or "(non precise)",
                "date": effective_val_date or "(non precisee)",
                "reason": "Validateur signale DOUTE -> rejected",
            })
            continue

        # Regle C : KO sans correction -> rejected
        if avis in ("KO", "A_CORRIGER", "A CORRIGER", "CORRECTION", "CORRIGER", "REVISION"):
            cat_row["statut"] = "rejected"
            if effective_val_code:
                cat_row["validateur_code"] = effective_val_code
            if effective_val_date:
                cat_row["date"] = effective_val_date
            cat_row["commentaire"] = (
                cat_row.get("commentaire", "")
                + f" [Rejete par {effective_val_code or 'validateur'} sans correction]"
            ).strip()
            modified_indices.add(cat_idx)
            stats["marked_revision_draft"].append({
                "line": line_num, "cle": cle, "langue": lang,
                "cible_originale": old_status, "correction": "",
                "validateur_code": effective_val_code or "(non precise)",
                "date": effective_val_date or "(non precisee)",
                "action": "Passe en rejected (KO sans texte de remplacement)",
            })
            continue

        # Regle D : human_validated -- CONDITION STRICTE
        is_ok = avis in ("OK", "VALIDE", "VAL", "OUI", "APPROUVE", "APPROUV\u00c9", "VALID\u00c9")
        if is_ok and effective_val_code.strip() and effective_val_date.strip():
            cat_row["statut"] = "human_validated"
            cat_row["validateur_code"] = effective_val_code
            cat_row["date"] = effective_val_date
            if comm:
                cat_row["commentaire"] = comm
            modified_indices.add(cat_idx)
            stats["promoted_human_validated"].append({
                "line": line_num, "cle": cle, "langue": lang,
                "cible": cat_row["cible"],
                "validateur_code": effective_val_code,
                "date": effective_val_date,
                "statut": "human_validated",
            })
            continue

        # Regle E : Tout le reste -> machine_suggested (garde-fou)
        reasons = []
        if not is_ok:
            reasons.append(
                f"avis non reconnu ou absent ('{avis_raw}')" if avis_raw else "aucun avis formule"
            )
        if not effective_val_code.strip():
            reasons.append("code validateur absent")
        if not effective_val_date.strip():
            reasons.append("date de validation absente")

        if old_status != "human_validated":
            cat_row["statut"] = "machine_suggested"
        cat_row["validateur_code"] = ""
        stats["retained_machine_suggested"].append({
            "line": line_num, "cle": cle, "langue": lang,
            "current_status": cat_row["statut"],
            "reason": ", ".join(reasons) if reasons else "conditions de promotion non remplies",
        })

    stats["total_modified"] = len(modified_indices)

    if not dry_run and stats["total_modified"] > 0:
        with open(catalog_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=catalog_header)
            writer.writeheader()
            writer.writerows(catalog_rows)

    return stats, catalog_rows


def generate_markdown_report(
    stats: Dict[str, Any],
    input_file: str,
    catalog_path: str,
    dry_run: bool,
    target_lang: str = "",
    val_code: str = "",
    val_date: str = "",
) -> str:
    """Genere un rapport Markdown sur les operations d'importation."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mode_str = "SIMULATION (DRY-RUN)" if dry_run else "APPLICATION REELLE"
    lines = [
        "# Rapport d'Importation de Validation Linguistique -- SAFINUM 2026",
        "",
        f"- **Date** : `{now_str}`",
        f"- **Mode** : `{mode_str}`",
        f"- **Fichier source** : `{input_file}`",
        f"- **Catalogue** : `{catalog_path}`",
        f"- **Langue** : `{target_lang or '(non precisee)'}`",
        f"- **Validateur** : `{val_code or '(non precise)'}`",
        f"- **Date validation** : `{val_date or '(non precisee)'}`",
        "",
        "---",
        "",
        "## 1. Synthese",
        "",
        "| Metrique | Nombre |",
        "|---|:---:|",
        f"| Lignes analysees | `{stats['total_input_rows']}` |",
        f"| Promus human_validated | `{len(stats['promoted_human_validated'])}` |",
        f"| Rejetes (rejected) | `{len(stats['marked_rejected'])}` |",
        f"| En revision (draft) | `{len(stats['marked_revision_draft'])}` |",
        f"| Conserves machine_suggested | `{len(stats['retained_machine_suggested'])}` |",
        f"| Erreurs correspondance | `{len(stats['errors'])}` |",
        f"| Modifications effectives | `{stats.get('total_modified', 0)}` |",
        "",
    ]
    if stats["promoted_human_validated"]:
        lines.append("## 2. Promus human_validated")
        lines.append("")
        for p in stats["promoted_human_validated"]:
            lines.append(f"- cle `{p['cle']}` langue `{p['langue']}` validateur `{p['validateur_code']}` date `{p['date']}`")
        lines.append("")
    if stats["errors"]:
        lines.append("## Erreurs (cles introuvables)")
        lines.append("")
        for e in stats["errors"]:
            lines.append(f"- ligne {e['line']} cle `{e['cle']}` : {e['reason']}")
        lines.append("")
    return "\n".join(lines)


def sync_offline_catalogs(catalog_rows: List[Dict[str, str]]):
    """Synchronise les catalogues hors-ligne."""
    glossary = {}
    if os.path.exists(DEFAULT_OFFLINE_JSON):
        try:
            with open(DEFAULT_OFFLINE_JSON, "r", encoding="utf-8") as f:
                glossary = json.load(f).get("glossary", {})
        except Exception:
            pass
    offline_data = {
        "version": "1.0.0",
        "translations": {"dua": {}, "bas": {}},
        "glossary": glossary,
    }
    for r in catalog_rows:
        lang = r.get("langue", "").strip().lower()
        if lang in offline_data["translations"]:
            offline_data["translations"][lang][r.get("source", "").strip()] = {
                "target": r.get("cible", "").strip(),
                "status": r.get("statut", "machine_suggested"),
                "key": r.get("cle", ""),
            }
    with open(DEFAULT_OFFLINE_JSON, "w", encoding="utf-8") as f:
        json.dump(offline_data, f, ensure_ascii=False, indent=2)
    with open(DEFAULT_EXT_OFFLINE_JSON, "w", encoding="utf-8") as f:
        json.dump(offline_data, f, ensure_ascii=False, indent=2)
    print("  [SYNC] Catalogues hors-ligne synchronises.")


def main():
    parser = argparse.ArgumentParser(
        description="Importateur strict de fiches de validation linguistique SAFINUM 2026"
    )
    parser.add_argument("--input", "-i", required=True, help="Chemin du CSV de validation rempli")
    parser.add_argument("--catalog", "-c", default=DEFAULT_CATALOG_CSV, help="Chemin de translations.csv")
    parser.add_argument("--report", "-r", default=DEFAULT_REPORT_PATH, help="Chemin du rapport Markdown")
    parser.add_argument("--dry-run", action="store_true", help="Simulation sans ecriture")
    parser.add_argument(
        "--langue", "-l", required=True, choices=["dua", "bas"],
        help="Code langue : 'dua' (Duala) ou 'bas' (Bassa'a) -- obligatoire",
    )
    parser.add_argument("--validateur", "-v", default="", help="Code validateur (s'applique a toute la fiche)")
    parser.add_argument("--date", "-d", default="", help="Date AAAA-MM-JJ (s'applique a toute la fiche)")
    args = parser.parse_args()

    print("\n=== IMPORTATION DE VALIDATION LINGUISTIQUE ===")
    print(f"  Fichier    : {args.input}")
    print(f"  Catalogue  : {args.catalog}")
    print(f"  Langue     : {args.langue}")
    print(f"  Validateur : {args.validateur or '(non precise)'}")
    print(f"  Date       : {args.date or '(non precisee)'}")
    print(f"  Dry-run    : {args.dry_run}")

    input_rows = load_input_csv(args.input)
    print(f"  Lignes lues : {len(input_rows)}")

    stats, updated_catalog = process_validation_import(
        input_rows=input_rows,
        catalog_path=args.catalog,
        dry_run=args.dry_run,
        target_lang=args.langue,
        val_code=args.validateur,
        val_date=args.date,
    )

    report = generate_markdown_report(
        stats, args.input, args.catalog, args.dry_run,
        target_lang=args.langue, val_code=args.validateur, val_date=args.date,
    )
    os.makedirs(os.path.dirname(args.report), exist_ok=True)
    with open(args.report, "w", encoding="utf-8") as f:
        f.write(report)

    print("\n--- RESULTATS ---")
    print(f"  human_validated : {len(stats['promoted_human_validated'])}")
    print(f"  rejected        : {len(stats['marked_rejected'])}")
    print(f"  draft           : {len(stats['marked_revision_draft'])}")
    print(f"  machine_sugg.   : {len(stats['retained_machine_suggested'])}")
    print(f"  erreurs         : {len(stats['errors'])}")
    print(f"  modifications   : {stats.get('total_modified', 0)}")
    print(f"  rapport         : {args.report}")

    if not args.dry_run and stats.get("total_modified", 0) > 0:
        sync_offline_catalogs(updated_catalog)

    print("\n[OPERATION TERMINEE]")


if __name__ == "__main__":
    main()
