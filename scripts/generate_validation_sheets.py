# -*- coding: utf-8 -*-
"""
Script de génération des fiches de validation humaine officielles en PDF et CSV.
SAFINUM Innovate Challenge 2026.

Génère :
- catalogue/kit_validation/fiche_validation_duala.pdf
- catalogue/kit_validation/fiche_validation_bassaa.pdf
- catalogue/kit_validation/fiche_validation_duala.csv
- catalogue/kit_validation/fiche_validation_bassaa.csv

Spécifications strictes :
- Format A4.
- 2 à 4 pages A4 par langue.
- Taille de police minimale absolue >= 9 pt (vérifiée par extraction PyMuPDF/fitz).
- En-tête répété sur chaque page A4 (thead avec display: table-header-group).
- Préservation intégrale des CSV existants.
"""

import os
import sys
import csv
import json
import html
import fitz  # PyMuPDF
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOGUE_DIR = os.path.join(REPO_ROOT, "catalogue")
KIT_DIR = os.path.join(CATALOGUE_DIR, "kit_validation")
TRANSLATIONS_CSV = os.path.join(CATALOGUE_DIR, "translations.csv")

os.makedirs(KIT_DIR, exist_ok=True)


def load_translations(lang_code: str) -> list[dict]:
    """Charge les 84 entrées de traduction pour la langue cible depuis translations.csv."""
    items = []
    with open(TRANSLATIONS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["langue"] == lang_code:
                items.append({
                    "cle": row["cle"],
                    "source": row["source"],
                    "cible": row["cible"],
                    "statut": row["statut"],
                    "commentaire": row["commentaire"]
                })
    return items


def export_csv(items: list[dict], lang_code: str, lang_name: str) -> str:
    """Exporte les items au format CSV pour le kit de validation."""
    csv_filename = f"fiche_validation_{'duala' if lang_code == 'dua' else 'bassaa'}.csv"
    csv_path = os.path.join(KIT_DIR, csv_filename)

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["N°", "Clé / Contexte", "Texte Source (Français)", f"Proposition Traduction ({lang_name})", "Correction du validateur", "Validation (OK / KO)", "Commentaire linguistique"])
        for idx, item in enumerate(items, 1):
            writer.writerow([
                idx,
                item["cle"],
                item["source"],
                item["cible"],
                "",  # à remplir par le validateur
                "",  # OK / KO
                item["commentaire"]
            ])

    print(f"  [CSV] Exporté : {csv_path} ({len(items)} lignes)")
    return csv_path


def build_html(items: list[dict], lang_code: str, lang_name: str) -> str:
    """Construit le document HTML paginé A4 avec en-têtes répétés et styles stricts >= 9pt."""
    rows_html = []
    for idx, item in enumerate(items, 1):
        src_escaped = html.escape(item["source"])
        target_escaped = html.escape(item["cible"])
        key_escaped = html.escape(item["cle"])
        comment_escaped = html.escape(item["commentaire"])

        rows_html.append(f"""
        <tr>
          <td class="col-num">{idx}</td>
          <td class="col-key">{key_escaped}</td>
          <td class="col-src">{src_escaped}</td>
          <td class="col-target"><strong>{target_escaped}</strong></td>
          <td class="col-corr"></td>
          <td class="col-status"></td>
        </tr>
        """)

    table_rows = "\n".join(rows_html)

    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <title>Fiche de Validation Linguistique — {lang_name} ({lang_code})</title>
  <style>
    @page {{
      size: A4 portrait;
      margin: 12mm 10mm 15mm 10mm;
    }}
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      font-size: 9.5pt;
      line-height: 1.35;
      color: #0F172A;
      background: #FFFFFF;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }}

    .document-header {{
      margin-bottom: 10px;
      border-bottom: 2pt solid #0A192F;
      padding-bottom: 8px;
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
    }}
    .doc-title {{
      font-size: 14pt;
      font-weight: 800;
      color: #0A192F;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .doc-meta {{
      font-size: 9.5pt;
      color: #334155;
      font-weight: 600;
      text-align: right;
    }}

    table.validation-table {{
      width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
    }}
    table.validation-table thead {{
      display: table-header-group;
    }}
    table.validation-table tr {{
      page-break-inside: avoid;
    }}
    table.validation-table th {{
      background-color: #0A192F;
      color: #FFFFFF;
      font-size: 9.5pt;
      font-weight: 700;
      padding: 6px 5px;
      text-align: left;
      border: 1px solid #0A192F;
    }}
    table.validation-table td {{
      padding: 5px 5px;
      font-size: 9.5pt;
      border: 1px solid #CBD5E1;
      vertical-align: top;
      word-wrap: break-word;
      overflow-wrap: break-word;
    }}
    table.validation-table tbody tr:nth-child(even) {{
      background-color: #F8FAFC;
    }}

    .col-num {{ width: 5%; text-align: center; font-weight: bold; color: #475569; }}
    .col-key {{ width: 15%; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 9pt; color: #64748b; }}
    .col-src {{ width: 33%; color: #0F172A; }}
    .col-target {{ width: 31%; color: #0369A1; }}
    .col-corr {{ width: 11%; background-color: #FFF; }}
    .col-status {{ width: 5%; text-align: center; }}

    .table-subhead {{
      background: #F1F5F9;
      color: #0A192F;
      font-size: 9.5pt;
      font-weight: 700;
      padding: 5px;
      text-align: left;
      border: 1px solid #CBD5E1;
    }}
  </style>
</head>
<body>

  <div class="document-header">
    <div>
      <div class="doc-title">🇨🇲 Fiche de Validation Linguistique — {lang_name} ({lang_code})</div>
      <div style="font-size: 9.5pt; color: #475569; margin-top: 2px;">
        Projet SAFINUM 2026 — Couche d'accessibilité financière souveraine | Équipe Triomphe Digital
      </div>
    </div>
    <div class="doc-meta">
      <div>Total chaînes : <strong>84</strong></div>
      <div>Statut cible : <strong>human_validated</strong></div>
    </div>
  </div>

  <table class="validation-table">
    <thead>
      <tr>
        <th class="col-num">N°</th>
        <th class="col-key">Clé Contexte</th>
        <th class="col-src">Texte Source (Français)</th>
        <th class="col-target">Proposition Traduction ({lang_name})</th>
        <th class="col-corr">Correction Validateur</th>
        <th class="col-status">OK/KO</th>
      </tr>
    </thead>
    <tbody>
      {table_rows}
    </tbody>
  </table>

</body>
</html>
"""
    return html_content


def generate_pdf_for_language(lang_code: str, lang_name: str) -> tuple[str, str]:
    """Génère le CSV et le PDF pour une langue donnée."""
    items = load_translations(lang_code)
    csv_path = export_csv(items, lang_code, lang_name)

    html_content = build_html(items, lang_code, lang_name)
    temp_html_path = os.path.join(KIT_DIR, f"temp_{lang_code}.html")
    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    pdf_filename = f"fiche_validation_{'duala' if lang_code == 'dua' else 'bassaa'}.pdf"
    pdf_path = os.path.join(KIT_DIR, pdf_filename)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page()
        page.goto(f"file:///{os.path.abspath(temp_html_path).replace(os.sep, '/')}", wait_until="networkidle")

        footer_html = f"""
        <div style="font-family: system-ui, sans-serif; font-size: 9pt; width: 100%; padding: 0 10mm; display: flex; justify-content: space-between; color: #64748B;">
          <span>SAFINUM 2026 — Fiche de Validation Linguistique ({lang_name})</span>
          <span>Page <span class="pageNumber"></span> / <span class="totalPages"></span></span>
        </div>
        """

        page.pdf(
            path=pdf_path,
            format="A4",
            print_background=True,
            margin={
                "top": "12mm",
                "bottom": "14mm",
                "left": "10mm",
                "right": "10mm"
            },
            display_header_footer=True,
            header_template="<div></div>",
            footer_template=footer_html
        )
        browser.close()

    if os.path.exists(temp_html_path):
        os.remove(temp_html_path)

    print(f"  [PDF] Généré : {pdf_path}")
    return pdf_path, csv_path


def verify_pdf_constraints(pdf_path: str, lang_name: str) -> tuple[int, float]:
    """
    Vérifie rigoureusement par extraction fitz (PyMuPDF) :
    1. Que le nombre de pages est strictement compris entre 2 et 4 pages A4.
    2. Que la taille minimale de police extraite est >= 9.0 pt.
    """
    doc = fitz.open(pdf_path)
    num_pages = len(doc)
    print(f"\n[VÉRIFICATION FITZ] Fiche {lang_name} ({os.path.basename(pdf_path)}) :")
    print(f"  - Nombre de pages : {num_pages} (Seuil requis : 2 à 4 pages)")
    assert 2 <= num_pages <= 4, f"Nombre de pages {num_pages} hors de l'intervalle requis [2, 4] pour {lang_name} !"

    min_font_size = 999.0
    total_spans = 0

    for page_idx, page in enumerate(doc, 1):
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" in b:
                for line in b["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if text:
                            size = float(span["size"])
                            min_font_size = min(min_font_size, size)
                            total_spans += 1

    print(f"  - Nombre total d'éléments textuels analysés : {total_spans}")
    print(f"  - Taille de police minimale absolue extraite : {min_font_size:.2f} pt (Seuil requis : >= 9.00 pt)")
    assert min_font_size >= 9.0, f"Taille de police {min_font_size:.2f} pt inférieure au seuil strict de 9.0 pt pour {lang_name} !"

    print(f"  --> VALIDATION CONFORME À 100% (Pages: {num_pages}, Police min: {min_font_size:.2f} pt)")
    return num_pages, min_font_size


def main():
    print("=" * 70)
    print(" GÉNÉRATION ET VÉRIFICATION DES FICHES DE VALIDATION LINGUISTIQUE")
    print("=" * 70)

    # 1. Duálá
    print("\n--- 1. Traitement Duálá (dua) ---")
    pdf_dua, csv_dua = generate_pdf_for_language("dua", "Duálá")
    pages_dua, font_dua = verify_pdf_constraints(pdf_dua, "Duálá")

    # 2. Ɓàsàa
    print("\n--- 2. Traitement Ɓàsàa (bas) ---")
    pdf_bas, csv_bas = generate_pdf_for_language("bas", "Ɓàsàa")
    pages_bas, font_bas = verify_pdf_constraints(pdf_bas, "Ɓàsàa")

    print("\n" + "=" * 70)
    print(" BILAN OFFICIEL DU KIT DE VALIDATION")
    print("=" * 70)
    print(f"  Duálá  : {pages_dua} pages A4 | Police minimale : {font_dua:.2f} pt | Conforme [2-4 pages, >=9pt]")
    print(f"  Ɓàsàa  : {pages_bas} pages A4 | Police minimale : {font_bas:.2f} pt | Conforme [2-4 pages, >=9pt]")
    print(f"  CSV conservés et exportés dans {KIT_DIR}")


if __name__ == "__main__":
    main()
