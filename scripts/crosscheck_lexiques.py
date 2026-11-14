import sys; sys.stdout.reconfigure(encoding='utf-8')
# -*- coding: utf-8 -*-
"""
Script de vérification croisée (cross-check) des traductions proposées
par rapport aux lexiques réels du projet Mélac :
- shared/data/duala/lexique_duala.json (colonne traduction uniquement)
- shared/data/bassa/lexique_bassa.json (colonne traduction uniquement)
- shared/data/bassa/lexique_manuel_bassa.json (colonne traduction uniquement)

Règles strictes :
- Colonne traduction uniquement, ne jamais en fabriquer.
- Statut par terme :
  * « attesté » : 100% des mots trouvés dans le lexique
  * « partiellement attesté » : au moins un mot trouvé et au moins un mot non trouvé
  * « non attesté » : 0 mot trouvé dans le lexique
- Ne modifie aucune traduction.
- Produit catalogue/crosscheck_rapport.csv.
"""

import os
import re
import csv
import json
import unicodedata
from collections import defaultdict


def normalize_token(text: str) -> str:
    """Normalise une chaîne en minuscules Unicode NFC."""
    if not text:
        return ""
    return unicodedata.normalize("NFC", str(text).strip().lower())


def extract_words(text: str) -> list:
    """
    Extrait la liste des mots significatifs (lettres étendues camerounaises et apostrophes internes),
    en ignorant les chiffres purs et la ponctuation périphérique.
    """
    if not text:
        return []
    norm = normalize_token(text)
    # Lettres AGCL camerounaises et latin étendu
    raw_tokens = re.findall(r"[\w\u00C0-\u024F\u1E00-\u1EFF]+", norm, re.UNICODE)
    # Exclure les nombres purs (ex: 25000, 100, 2)
    words = [t for t in raw_tokens if not t.isdigit() and len(t) >= 1]
    return words


def load_lexique_words(filepath: str) -> set:
    """
    Charge le vocabulaire attesté depuis un fichier lexique JSON.
    RÈGLE ABSOLUE : colonne 'traduction' UNIQUEMENT, ne jamais en fabriquer.
    """
    words = set()
    if not os.path.exists(filepath):
        print(f"[ATTENTION] Fichier lexique introuvable : {filepath}")
        return words

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    for entry in data:
        # COLONNE TRADUCTION UNIQUEMENT
        trad = entry.get("traduction")
        if trad and isinstance(trad, str) and trad.strip():
            tokens = extract_words(trad)
            words.update(tokens)

    return words


def run_crosscheck():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    trans_csv_path = os.path.join(base_dir, "catalogue", "translations.csv")
    rapport_csv_path = os.path.join(base_dir, "catalogue", "crosscheck_rapport.csv")

    dua_lex_path = os.path.join(base_dir, "shared", "data", "duala", "lexique_duala.json")
    bas_lex_path1 = os.path.join(base_dir, "shared", "data", "bassa", "lexique_bassa.json")
    bas_lex_path2 = os.path.join(base_dir, "shared", "data", "bassa", "lexique_manuel_bassa.json")

    # 1. Chargement des lexiques réels (colonne traduction uniquement)
    dua_lexicon = load_lexique_words(dua_lex_path)

    bas_lexicon = set()
    bas_lexicon.update(load_lexique_words(bas_lex_path1))
    bas_lexicon.update(load_lexique_words(bas_lex_path2))

    print("=" * 70)
    print("VÉRIFICATION CROISÉE DES TRADUCTIONS SAFINUM VS LEXIQUES RÉELS MÉLAC")
    print("=" * 70)
    print(f"Lexique Duálá ('traduction' uniquement) : {len(dua_lexicon)} mots uniques réels")
    print(f"Lexique Ɓàsàa ('traduction' uniquement)  : {len(bas_lexicon)} mots uniques réels")
    print("-" * 70)

    # 2. Analyse des traductions de catalogue/translations.csv
    rows_by_lang = defaultdict(list)

    with open(trans_csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            lang = row.get("langue", "").strip().lower()
            if lang in ("dua", "bas"):
                rows_by_lang[lang].append(row)

    report_rows = []
    stats = {
        "dua": {"atteste": 0, "partiel": 0, "non_atteste": 0, "total": 0, "words_total": 0, "words_found": 0},
        "bas": {"atteste": 0, "partiel": 0, "non_atteste": 0, "total": 0, "words_total": 0, "words_found": 0}
    }

    # 2.1 Première passe : calcul des statistiques globales par langue
    interm_results = []
    for lang in ("dua", "bas"):
        lexicon = dua_lexicon if lang == "dua" else bas_lexicon

        for row in rows_by_lang[lang]:
            term_id = row.get("cle", "").strip()
            source_fr = row.get("source", "").strip()
            target_prop = row.get("cible", "").strip()

            words = extract_words(target_prop)
            found = [w for w in words if w in lexicon]
            not_found = [w for w in words if w not in lexicon]

            if len(words) == 0:
                statut = "non attesté"
            elif len(not_found) == 0:
                statut = "attesté"
            elif len(found) > 0:
                statut = "partiellement attesté"
            else:
                statut = "non attesté"

            stats[lang]["total"] += 1
            stats[lang]["words_total"] += len(words)
            stats[lang]["words_found"] += len(found)

            if statut == "attesté":
                stats[lang]["atteste"] += 1
            elif statut == "partiellement attesté":
                stats[lang]["partiel"] += 1
            else:
                stats[lang]["non_atteste"] += 1

            interm_results.append({
                "id": term_id,
                "langue": lang,
                "source": source_fr,
                "traduction": target_prop,
                "mots_trouves": " ".join(found),
                "mots_non_trouves": " ".join(not_found),
                "statut": statut
            })

    # Calcul des pourcentages par langue
    pct_str = {}
    for lang in ("dua", "bas"):
        tot = stats[lang]["total"]
        if tot > 0:
            p_att = (stats[lang]["atteste"] / tot) * 100
            p_part = (stats[lang]["partiel"] / tot) * 100
            p_non = (stats[lang]["non_atteste"] / tot) * 100
            pct_str[lang] = f"{lang.upper()}: {p_att:.1f}% attesté, {p_part:.1f}% partiellement attesté, {p_non:.1f}% non attesté"
        else:
            pct_str[lang] = f"{lang.upper()}: N/A"

    # Construction des lignes finales avec la colonne pourcentage_global_langue
    for r in interm_results:
        lang = r["langue"]
        report_rows.append({
            "id": r["id"],
            "langue": r["langue"],
            "source": r["source"],
            "traduction": r["traduction"],
            "mots_trouves": r["mots_trouves"],
            "mots_non_trouves": r["mots_non_trouves"],
            "statut": r["statut"],
            "pourcentage_global_langue": pct_str[lang]
        })

    # 3. Écriture du fichier catalogue/crosscheck_rapport.csv
    fieldnames = [
        "id",
        "langue",
        "source",
        "traduction",
        "mots_trouves",
        "mots_non_trouves",
        "statut",
        "pourcentage_global_langue"
    ]

    with open(rapport_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in report_rows:
            writer.writerow(r)

        # Ajout des lignes de synthèse en fin de rapport
        tot_all = stats["dua"]["total"] + stats["bas"]["total"]
        att_all = stats["dua"]["atteste"] + stats["bas"]["atteste"]
        part_all = stats["dua"]["partiel"] + stats["bas"]["partiel"]
        non_all = stats["dua"]["non_atteste"] + stats["bas"]["non_atteste"]

        writer.writerow({
            "id": "# SYNTHESE_DUA",
            "langue": "dua",
            "source": f"Total {stats['dua']['total']} termes",
            "traduction": f"Attesté: {stats['dua']['atteste']} ({stats['dua']['atteste']/stats['dua']['total']*100:.1f}%) | Partiel: {stats['dua']['partiel']} ({stats['dua']['partiel']/stats['dua']['total']*100:.1f}%) | Non attesté: {stats['dua']['non_atteste']} ({stats['dua']['non_atteste']/stats['dua']['total']*100:.1f}%)",
            "mots_trouves": f"Mots trouvés: {stats['dua']['words_found']}/{stats['dua']['words_total']}",
            "mots_non_trouves": f"Mots non trouvés: {stats['dua']['words_total'] - stats['dua']['words_found']}/{stats['dua']['words_total']}",
            "statut": "SYNTHÈSE DUÁLÁ",
            "pourcentage_global_langue": pct_str["dua"]
        })
        writer.writerow({
            "id": "# SYNTHESE_BAS",
            "langue": "bas",
            "source": f"Total {stats['bas']['total']} termes",
            "traduction": f"Attesté: {stats['bas']['atteste']} ({stats['bas']['atteste']/stats['bas']['total']*100:.1f}%) | Partiel: {stats['bas']['partiel']} ({stats['bas']['partiel']/stats['bas']['total']*100:.1f}%) | Non attesté: {stats['bas']['non_atteste']} ({stats['bas']['non_atteste']/stats['bas']['total']*100:.1f}%)",
            "mots_trouves": f"Mots trouvés: {stats['bas']['words_found']}/{stats['bas']['words_total']}",
            "mots_non_trouves": f"Mots non trouvés: {stats['bas']['words_total'] - stats['bas']['words_found']}/{stats['bas']['words_total']}",
            "statut": "SYNTHÈSE ƁÀSÀA",
            "pourcentage_global_langue": pct_str["bas"]
        })
        writer.writerow({
            "id": "# SYNTHESE_GLOBALE",
            "langue": "dua+bas",
            "source": f"Total {tot_all} termes",
            "traduction": f"Attesté: {att_all} ({att_all/tot_all*100:.1f}%) | Partiel: {part_all} ({part_all/tot_all*100:.1f}%) | Non attesté: {non_all} ({non_all/tot_all*100:.1f}%)",
            "mots_trouves": f"Mots trouvés: {stats['dua']['words_found'] + stats['bas']['words_found']}/{stats['dua']['words_total'] + stats['bas']['words_total']}",
            "mots_non_trouves": f"Mots non trouvés: {(stats['dua']['words_total'] + stats['bas']['words_total']) - (stats['dua']['words_found'] + stats['bas']['words_found'])}/{stats['dua']['words_total'] + stats['bas']['words_total']}",
            "statut": "SYNTHÈSE GLOBALE",
            "pourcentage_global_langue": f"GLOBAL: {att_all/tot_all*100:.1f}% attesté, {part_all/tot_all*100:.1f}% partiellement attesté, {non_all/tot_all*100:.1f}% non attesté"
        })

    print(f"[SUCCÈS] Rapport généré : {rapport_csv_path} ({len(report_rows)} lignes + 3 lignes de synthèse)")
    print("-" * 70)

    # 4. Affichage des 3 pourcentages réels
    dua_tot = stats["dua"]["total"]
    bas_tot = stats["bas"]["total"]

    dua_pct_att = (stats["dua"]["atteste"] / dua_tot) * 100
    dua_pct_part = (stats["dua"]["partiel"] / dua_tot) * 100
    dua_pct_non = (stats["dua"]["non_atteste"] / dua_tot) * 100

    bas_pct_att = (stats["bas"]["atteste"] / bas_tot) * 100
    bas_pct_part = (stats["bas"]["partiel"] / bas_tot) * 100
    bas_pct_non = (stats["bas"]["non_atteste"] / bas_tot) * 100

    glob_pct_att = (att_all / tot_all) * 100
    glob_pct_part = (part_all / tot_all) * 100
    glob_pct_non = (non_all / tot_all) * 100

    print("RÉSULTATS RÉELS DU CROSS-CHECK (AUCUNE INVENTION) :")
    print(f"1. DUÁLÁ (dua - {dua_tot} entrées) :")
    print(f"   - Attesté (100% mots trouvés)           : {stats['dua']['atteste']} / {dua_tot} = {dua_pct_att:.1f}%")
    print(f"   - Partiellement attesté (≥1 mot trouvé)  : {stats['dua']['partiel']} / {dua_tot} = {dua_pct_part:.1f}%")
    print(f"   - Non attesté (0 mot trouvé)            : {stats['dua']['non_atteste']} / {dua_tot} = {dua_pct_non:.1f}%")
    print()
    print(f"2. ƁÀSÀA (bas - {bas_tot} entrées) :")
    print(f"   - Attesté (100% mots trouvés)           : {stats['bas']['atteste']} / {bas_tot} = {bas_pct_att:.1f}%")
    print(f"   - Partiellement attesté (≥1 mot trouvé)  : {stats['bas']['partiel']} / {bas_tot} = {bas_pct_part:.1f}%")
    print(f"   - Non attesté (0 mot trouvé)            : {stats['bas']['non_atteste']} / {bas_tot} = {bas_pct_non:.1f}%")
    print()
    print(f"3. GLOBAL COMBINÉ (dua + bas - {tot_all} entrées) :")
    print(f"   - Attesté (100% mots trouvés)           : {att_all} / {tot_all} = {glob_pct_att:.1f}%")
    print(f"   - Partiellement attesté (≥1 mot trouvé)  : {part_all} / {tot_all} = {glob_pct_part:.1f}%")
    print(f"   - Non attesté (0 mot trouvé)            : {non_all} / {tot_all} = {glob_pct_non:.1f}%")
    print("=" * 70)


if __name__ == "__main__":
    run_crosscheck()
