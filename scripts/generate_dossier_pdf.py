# -*- coding: utf-8 -*-
"""
Script de génération du dossier de soumission officiel PDF : dist/dossier_soumission.pdf
Conforme aux spécifications du Hackathon SAFINUM 2026 :
- Page de garde : prototype LinguaFin Cameroun, équipe Triomphe Digital, Douala.
- Ordre strict : docs/description_solution.md, docs/note_technique.md, docs/langue_et_validation.md, THIRD_PARTY.md, Section Captures.
- 5 captures docs/screens/final/ réduites à 1200 px en JPEG.
- Table des matières cliquable.
- Impression via Playwright page.pdf.
- Vérification taille (< 8 Mo), nombre de pages et extraction texte page 1.
"""

import os
import sys
import re
import base64
import html
from io import BytesIO
from PIL import Image
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST_DIR = os.path.join(REPO_ROOT, "dist")
PDF_PATH = os.path.join(DIST_DIR, "dossier_soumission.pdf")
HTML_TEMP_PATH = os.path.join(DIST_DIR, "dossier_soumission.html")


def resize_image_to_jpeg_base64(img_path: str, max_width: int = 1200, quality: int = 85) -> str:
    """Ouvre une image PNG, la redimensionne à max_width px en conservant le ratio, et l'encode en JPEG base64."""
    with Image.open(img_path) as im:
        im = im.convert("RGB")
        w, h = im.size
        if w > max_width:
            new_h = int(h * (max_width / w))
            im = im.resize((max_width, new_h), Image.Resampling.LANCZOS)
        buf = BytesIO()
        im.save(buf, format="JPEG", quality=quality, optimize=True)
        encoded = base64.b64encode(buf.getvalue()).decode("ascii")
        return f"data:image/jpeg;base64,{encoded}"


def slugify(text: str) -> str:
    """Génère un identifiant d'ancre HTML propre à partir d'un titre."""
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[-\s]+", "-", text).strip("-")


def parse_markdown_to_html(md_text: str, heading_offset: int = 0) -> str:
    """Convertit un texte Markdown en HTML sémantique propre."""
    lines = md_text.split("\n")
    html_out = []
    in_code_block = False
    code_lang = ""
    code_lines = []
    in_table = False
    table_lines = []
    in_ul = False
    in_ol = False
    in_blockquote = False
    blockquote_lines = []

    def close_open_blocks():
        nonlocal in_ul, in_ol, in_blockquote, blockquote_lines
        res = []
        if in_ul:
            res.append("</ul>")
            in_ul = False
        if in_ol:
            res.append("</ol>")
            in_ol = False
        if in_blockquote:
            bq_content = "<br>".join(blockquote_lines)
            res.append(f"<blockquote>{bq_content}</blockquote>")
            in_blockquote = False
            blockquote_lines = []
        return res

    def format_inline(txt: str) -> str:
        txt = html.escape(txt)
        txt = re.sub(r"`([^`]+)`", r"<code>\1</code>", txt)
        txt = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", txt)
        txt = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", txt)
        txt = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', txt)
        return txt

    def render_table(t_lines: list) -> str:
        if not t_lines:
            return ""
        table_html = ['<div class="table-container"><table>']
        header_cells = [c.strip() for c in t_lines[0].split("|")[1:-1]]
        table_html.append("<thead><tr>")
        for c in header_cells:
            table_html.append(f"<th>{format_inline(c)}</th>")
        table_html.append("</tr></thead>")
        table_html.append("<tbody>")
        for row in t_lines[2:]:
            if not row.strip() or "|" not in row:
                continue
            cells = [c.strip() for c in row.split("|")[1:-1]]
            table_html.append("<tr>")
            for c in cells:
                table_html.append(f"<td>{format_inline(c)}</td>")
            table_html.append("</tr>")
        table_html.append("</tbody></table></div>")
        return "\n".join(table_html)

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("```"):
            if in_code_block:
                in_code_block = False
                escaped_code = html.escape("\n".join(code_lines))
                html_out.append(f'<pre><code class="language-{code_lang}">{escaped_code}</code></pre>')
                code_lines = []
                code_lang = ""
            else:
                html_out.extend(close_open_blocks())
                in_code_block = True
                code_lang = stripped[3:].strip()
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        if stripped.startswith("|") and stripped.endswith("|"):
            html_out.extend(close_open_blocks())
            in_table = True
            table_lines.append(stripped)
            continue
        elif in_table:
            html_out.append(render_table(table_lines))
            table_lines = []
            in_table = False

        if not stripped:
            html_out.extend(close_open_blocks())
            continue

        if stripped in ("---", "___", "***"):
            html_out.extend(close_open_blocks())
            html_out.append("<hr>")
            continue

        if stripped.startswith(">"):
            if in_ul:
                html_out.append("</ul>")
                in_ul = False
            if in_ol:
                html_out.append("</ol>")
                in_ol = False
            in_blockquote = True
            bq_text = stripped.lstrip("> ").strip()
            blockquote_lines.append(format_inline(bq_text))
            continue
        elif in_blockquote:
            html_out.extend(close_open_blocks())

        m_head = re.match(r"^(#{1,4})\s+(.+)$", stripped)
        if m_head:
            html_out.extend(close_open_blocks())
            level = len(m_head.group(1)) + heading_offset
            level = min(level, 6)
            title_text = m_head.group(2).strip()
            slug = slugify(title_text)
            formatted_title = format_inline(title_text)
            html_out.append(f'<h{level} id="{slug}">{formatted_title}</h{level}>')
            continue

        m_ul = re.match(r"^[-*]\s+(.+)$", stripped)
        if m_ul:
            if in_ol:
                html_out.append("</ol>")
                in_ol = False
            if not in_ul:
                html_out.append("<ul>")
                in_ul = True
            html_out.append(f"<li>{format_inline(m_ul.group(1))}</li>")
            continue

        m_ol = re.match(r"^\d+\.\s+(.+)$", stripped)
        if m_ol:
            if in_ul:
                html_out.append("</ul>")
                in_ul = False
            if not in_ol:
                html_out.append("<ol>")
                in_ol = True
            html_out.append(f"<li>{format_inline(m_ol.group(1))}</li>")
            continue

        html_out.extend(close_open_blocks())
        html_out.append(f"<p>{format_inline(stripped)}</p>")

    if in_code_block:
        html_out.append(f'<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>')
    if in_table:
        html_out.append(render_table(table_lines))
    html_out.extend(close_open_blocks())

    return "\n".join(html_out)


def build_full_html() -> str:
    with open(os.path.join(REPO_ROOT, "docs", "description_solution.md"), "r", encoding="utf-8") as f:
        desc_md = f.read()

    with open(os.path.join(REPO_ROOT, "docs", "note_technique.md"), "r", encoding="utf-8") as f:
        note_md = f.read()

    with open(os.path.join(REPO_ROOT, "docs", "langue_et_validation.md"), "r", encoding="utf-8") as f:
        lang_md = f.read()

    with open(os.path.join(REPO_ROOT, "THIRD_PARTY.md"), "r", encoding="utf-8") as f:
        third_md = f.read()

    desc_html = parse_markdown_to_html(desc_md)
    note_html = parse_markdown_to_html(note_md)
    lang_html = parse_markdown_to_html(lang_md)
    third_html = parse_markdown_to_html(third_md)

    screens = [
        (
            "passB_01_solde_dua.png",
            "Étape 1 — Tableau de bord & Consultation du solde en Duálá (250 000 FCFA intact, widget Shadow DOM actif)",
            "docs/screens/final/passB_01_solde_dua.png"
        ),
        (
            "passB_02_frais_dua.png",
            "Étape 2 — Calcul et transparence des frais de transfert en Duálá (25 000 FCFA et 0 FCFA intacts)",
            "docs/screens/final/passB_02_frais_dua.png"
        ),
        (
            "passB_07_securite_dua.png",
            "Étape 7 — Alerte de sécurité bancaire en Duálá et retour instantané au texte source",
            "docs/screens/final/passB_07_securite_dua.png"
        ),
        (
            "passB_09_injected_1_security_amount.png",
            "Contenu Inédit — Injection d'une alerte avec montant (75 000 FCFA préservé au franc près, repli sécurisé)",
            "docs/screens/final/passB_09_injected_1_security_amount.png"
        ),
        ]

    captures_html = []
    for fname, caption, rel_path in screens:
        abs_path = os.path.join(REPO_ROOT, rel_path)
        if os.path.exists(abs_path):
            img_b64 = resize_image_to_jpeg_base64(abs_path, max_width=1200, quality=85)
            captures_html.append(f"""
            <div class="capture-card">
                <div class="capture-header"><strong>{html.escape(fname)}</strong> — {html.escape(caption)}</div>
                <img src="{img_b64}" alt="{html.escape(caption)}" class="capture-img">
            </div>
            """)
        else:
            captures_html.append(f"<p class='error'>Capture introuvable : {html.escape(rel_path)}</p>")

    captures_block = "".join(captures_html)

    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>LinguaFin Cameroun — Dossier de Soumission SAFINUM 2026</title>
    <style>
        @page {{
            size: A4;
            margin: 18mm 15mm 20mm 15mm;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            font-size: 10pt;
            line-height: 1.55;
            color: #1e293b;
            background-color: #ffffff;
            margin: 0;
            padding: 0;
        }}

        .page-break {{
            page-break-after: always;
            break-after: page;
        }}

        /* PAGE DE GARDE */
        .cover-page {{
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-height: 920px;
            box-sizing: border-box;
            padding: 30px 20px;
        }}

        .cover-header {{
            border-bottom: 3px solid #0284c7;
            padding-bottom: 20px;
        }}

        .cover-badge {{
            display: inline-block;
            background: #e0f2fe;
            color: #0369a1;
            font-weight: 700;
            font-size: 10pt;
            padding: 6px 14px;
            border-radius: 20px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 15px;
        }}

        .cover-title {{
            font-size: 32pt;
            font-weight: 800;
            color: #0f172a;
            margin: 0 0 10px 0;
            line-height: 1.15;
        }}

        .cover-subtitle {{
            font-size: 14pt;
            color: #475569;
            margin: 0 0 10px 0;
            font-weight: 500;
        }}

        .cover-event {{
            font-size: 11pt;
            font-weight: 600;
            color: #0284c7;
        }}

        .cover-body {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-left: 6px solid #0284c7;
            border-radius: 8px;
            padding: 25px 30px;
            margin: 25px 0;
        }}

        .cover-info-group {{
            margin-bottom: 16px;
        }}

        .cover-info-label {{
            font-size: 9pt;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #64748b;
            font-weight: 700;
            margin-bottom: 4px;
        }}

        .cover-info-val {{
            font-size: 12pt;
            font-weight: 700;
            color: #0f172a;
        }}

        .cover-team-list {{
            list-style: none;
            padding: 0;
            margin: 8px 0 0 0;
        }}

        .cover-team-list li {{
            font-size: 10.5pt;
            color: #334155;
            padding: 4px 0;
        }}

        .cover-team-list li::before {{
            content: "• ";
            color: #0284c7;
            font-weight: bold;
        }}

        .cover-footer {{
            border-top: 1px solid #e2e8f0;
            padding-top: 15px;
            display: flex;
            justify-content: space-between;
            color: #64748b;
            font-size: 9pt;
        }}

        /* TABLE DES MATIÈRES */
        .toc-container {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 20px 25px;
            margin-bottom: 25px;
        }}

        .toc-title {{
            font-size: 16pt;
            font-weight: 800;
            color: #0f172a;
            margin-top: 0;
            margin-bottom: 12px;
            border-bottom: 2px solid #0284c7;
            padding-bottom: 6px;
        }}

        .toc-list {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}

        .toc-item {{
            margin: 8px 0;
        }}

        .toc-link {{
            display: flex;
            justify-content: space-between;
            text-decoration: none;
            color: #0369a1;
            font-weight: 600;
            font-size: 10.5pt;
            border-bottom: 1px dotted #cbd5e1;
            padding-bottom: 3px;
        }}

        /* TYPOGRAPHIE ET TITRES */
        h1 {{
            font-size: 19pt;
            color: #0f172a;
            margin-top: 25px;
            margin-bottom: 12px;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 5px;
            page-break-after: avoid;
        }}

        h2 {{
            font-size: 14pt;
            color: #0369a1;
            margin-top: 20px;
            margin-bottom: 8px;
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 4px;
            page-break-after: avoid;
        }}

        h3 {{
            font-size: 11.5pt;
            color: #1e293b;
            margin-top: 16px;
            margin-bottom: 6px;
            page-break-after: avoid;
        }}

        h4 {{
            font-size: 10.5pt;
            color: #334155;
            margin-top: 12px;
            margin-bottom: 4px;
            page-break-after: avoid;
        }}

        p {{
            margin: 0 0 9px 0;
            text-align: justify;
        }}

        /* TABLEAUX */
        .table-container {{
            margin: 12px 0;
            overflow-x: auto;
            page-break-inside: avoid;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 8pt;
        }}

        th, td {{
            border: 1px solid #cbd5e1;
            padding: 5px 7px;
            text-align: left;
            vertical-align: top;
        }}

        th {{
            background-color: #f1f5f9;
            color: #0f172a;
            font-weight: 700;
        }}

        tr:nth-child(even) td {{
            background-color: #f8fafc;
        }}

        blockquote {{
            margin: 10px 0;
            padding: 8px 14px;
            background-color: #f0fdf4;
            border-left: 4px solid #16a34a;
            color: #166534;
            border-radius: 4px;
            font-size: 9pt;
            page-break-inside: avoid;
        }}

        code {{
            font-family: Consolas, 'Courier New', monospace;
            font-size: 8.5pt;
            background: #f1f5f9;
            color: #0f172a;
            padding: 1px 4px;
            border-radius: 3px;
        }}

        pre {{
            background: #0f172a;
            color: #f8fafc;
            padding: 10px 12px;
            border-radius: 6px;
            overflow-x: auto;
            font-family: Consolas, 'Courier New', monospace;
            font-size: 8pt;
            line-height: 1.35;
            margin: 10px 0;
            page-break-inside: avoid;
        }}

        pre code {{
            background: transparent;
            color: inherit;
            padding: 0;
        }}

        ul, ol {{
            margin: 6px 0 10px 18px;
            padding: 0;
        }}

        li {{
            margin-bottom: 3px;
        }}

        hr {{
            border: none;
            border-top: 1px solid #e2e8f0;
            margin: 20px 0;
        }}

        a {{
            color: #0284c7;
            text-decoration: none;
        }}

        .capture-card {{
            margin: 18px 0;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            overflow: hidden;
            background: #f8fafc;
            page-break-inside: avoid;
        }}

        .capture-header {{
            background: #0f172a;
            color: #ffffff;
            padding: 7px 12px;
            font-size: 9pt;
        }}

        .capture-img {{
            width: 100%;
            height: auto;
            display: block;
        }}
    </style>
</head>
<body>

    <!-- 1. PAGE DE GARDE -->
    <div class="cover-page page-break">
        <div class="cover-header">
            <span class="cover-badge">Hackathon SAFINUM 2026 — Dossier Officiel de Soumission</span>
            <h1 class="cover-title">LinguaFin Cameroun</h1>
            <p class="cover-subtitle">Couche d'accessibilité linguistique non-intrusive pour services financiers numériques</p>
            <div class="cover-event">Défis d'inclusion financière, souveraineté linguistique & intégrité bancaire</div>
        </div>

        <div class="cover-body">
            <div class="cover-info-group">
                <div class="cover-info-label">Prototype</div>
                <div class="cover-info-val">LinguaFin Cameroun</div>
            </div>

            <div class="cover-info-group">
                <div class="cover-info-label">Équipe candidate</div>
                <div class="cover-info-val">Triomphe Digital (Douala, Cameroun)</div>
            </div>

            <div class="cover-info-group">
                <div class="cover-info-label">Responsable du projet</div>
                <div class="cover-info-val">MBENBE BOGMIS PIERRE ALEXANDRE</div>
            </div>

            <div class="cover-info-group">
                <div class="cover-info-label">Membres de l'équipe</div>
                <ul class="cover-team-list">
                    <li><strong>MBENBE BOGMIS PIERRE ALEXANDRE</strong> (Responsable)</li>
                    <li><strong>GRÂCE NZONNOU NJAMPA</strong></li>
                    <li><strong>NTAMACK RENE PASCAL</strong></li>
                    <li><strong>TOWA TCHAPTCHIE EMMANUEL FILS</strong></li>
                </ul>
            </div>

            <div class="cover-info-group">
                <div class="cover-info-label">Environnement de Démonstration & Évaluation</div>
                <div style="font-size: 9.5pt; color: #334155; margin-top: 4px;">
                    Site cible : <code>https://safinum.cm/hackathon-test</code> &nbsp;|&nbsp; 
                    Extension Manifest V3 (Shadow DOM) &nbsp;|&nbsp; 
                    Mode 100% Hors-ligne souverain
                </div>
            </div>
        </div>

        <div class="cover-footer">
            <div>Douala, Cameroun — Samedi 14 novembre 2026</div>
            <div>Dossier de soumission — SAFINUM Innovate Challenge</div>
        </div>
    </div>

    <!-- 2. TABLE DES MATIÈRES CLIQUABLE -->
    <div class="page-break">
        <div class="toc-container">
            <h2 class="toc-title">Table des Matières</h2>
            <ul class="toc-list">
                <li class="toc-item">
                    <a class="toc-link" href="#sec-description">
                        <span><strong>1.</strong> Description de la Solution</span>
                        <span>Section 1</span>
                    </a>
                </li>
                <li class="toc-item">
                    <a class="toc-link" href="#sec-technique">
                        <span><strong>2.</strong> Note Technique d'Intégration & Architecture</span>
                        <span>Section 2</span>
                    </a>
                </li>
                <li class="toc-item">
                    <a class="toc-link" href="#sec-langue">
                        <span><strong>3.</strong> Langues Supportées et Protocole de Validation Linguistique</span>
                        <span>Section 3</span>
                    </a>
                </li>
                <li class="toc-item">
                    <a class="toc-link" href="#sec-thirdparty">
                        <span><strong>4.</strong> Déclaration des Dépendances, Modèles d'IA et Jeux de Données</span>
                        <span>Section 4</span>
                    </a>
                </li>
                <li class="toc-item">
                    <a class="toc-link" href="#sec-captures">
                        <span><strong>5.</strong> Captures d'Écran et Preuves du Parcours Réel</span>
                        <span>Section 5</span>
                    </a>
                </li>
            </ul>
        </div>

        <!-- 3. DESCRIPTION DE LA SOLUTION -->
        <div id="sec-description">
            {desc_html}
        </div>
    </div>

    <!-- 4. NOTE TECHNIQUE -->
    <div class="page-break" id="sec-technique">
        {note_html}
    </div>

    <!-- 5. LANGUES ET PROTOCOLE DE VALIDATION -->
    <div class="page-break" id="sec-langue">
        {lang_html}
    </div>

    <!-- 6. THIRD_PARTY.MD -->
    <div class="page-break" id="sec-thirdparty">
        {third_html}
    </div>

    <!-- 7. SECTION CAPTURES D'ÉCRAN RÉELLES -->
    <div class="page-break" id="sec-captures">
        <h1>Captures d'Écran et Preuves du Parcours Réel</h1>
        <p>Les captures ci-dessous proviennent de l'exécution certifiée sous Microsoft Edge (profil vierge) sur l'environnement officiel <code>https://safinum.cm/hackathon-test</code> et son volet d'évaluation jury <code>?jury=1</code>. Elles attestent du fonctionnement réel du parcours complet (Solde, Frais, Sécurité, Contenu inédit et Panneau jury).</p>
        {captures_block}
    </div>

</body>
</html>
"""

    with open(HTML_TEMP_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"HTML généré : {HTML_TEMP_PATH} ({os.path.getsize(HTML_TEMP_PATH):,} octets)")
    return HTML_TEMP_PATH


def convert_html_to_pdf_with_playwright(html_path: str):
    print("\n--- Impression du PDF avec Playwright (page.pdf) ---")
    os.makedirs(DIST_DIR, exist_ok=True)
    if os.path.exists(PDF_PATH):
        os.remove(PDF_PATH)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page()
        file_url = f"file:///{os.path.abspath(html_path).replace(os.sep, '/')}"
        page.goto(file_url, wait_until="networkidle")
        page.wait_for_timeout(1000)

        page.pdf(
            path=PDF_PATH,
            format="A4",
            print_background=True,
            margin={
                "top": "15mm",
                "bottom": "15mm",
                "left": "15mm",
                "right": "15mm"
            },
            display_header_footer=True,
            header_template="<div></div>",
            footer_template="""
            <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 8pt; width: 100%; padding: 0 15mm; display: flex; justify-content: space-between; color: #64748b;">
                <span>LinguaFin Cameroun — Équipe Triomphe Digital (Douala)</span>
                <span>Page <span class="pageNumber"></span> sur <span class="totalPages"></span></span>
            </div>
            """
        )
        browser.close()

    pdf_size = os.path.getsize(PDF_PATH)
    pdf_size_mb = pdf_size / (1024 * 1024)
    print(f"PDF généré avec succès : {PDF_PATH}")
    print(f"Taille du PDF : {pdf_size:,} octets ({pdf_size_mb:.2f} Mo)")
    return PDF_PATH, pdf_size_mb


def verify_pdf():
    print("\n--- Vérification d'intégrité du fichier PDF ---")
    import fitz

    doc = fitz.open(PDF_PATH)
    num_pages = len(doc)
    size_mb = os.path.getsize(PDF_PATH) / (1024 * 1024)

    print(f"Nombre total de pages : {num_pages}")
    print(f"Taille finale : {size_mb:.2f} Mo (Seuil requis : < 8.00 Mo -> {'CONFORME (PASS)' if size_mb < 8.0 else 'NON CONFORME (FAIL)'})")

    page1_text = doc[0].get_text()
    print("\n--- Extrait du texte extrait de la Page 1 (Page de garde) ---")
    for line in page1_text.strip().split("\n"):
        print(" ", line)

    required_keywords = [
        "LinguaFin",
        "Triomphe Digital",
        "Douala",
        "MBENBE BOGMIS PIERRE ALEXANDRE",
        "GRÂCE NZONNOU NJAMPA",
        "NTAMACK RENE PASCAL",
        "TOWA TCHAPTCHIE EMMANUEL FILS"
    ]

    all_found = True
    print("\n--- Vérification des mentions requises sur la page de garde ---")
    for kw in required_keywords:
        found = kw.lower() in page1_text.lower()
        print(f"  Vérification mot-clé '{kw}' : {'TROUVÉ' if found else 'MANQUANT'}")
        if not found:
            all_found = False

    full_text = "".join(p.get_text() for p in doc)
    native_phrase = "0/84" in full_text and "locuteur natif" in full_text
    fulfulde_phrase = "Fulfulde" in full_text and ("écarté" in full_text or "désactivé" in full_text)

    print(f"\nMention '0/84 validées par un locuteur natif' présente : {'OUI' if native_phrase else 'NON'}")
    print(f"Mention 'moteur Fulfulde écarté / désactivé' présente : {'OUI' if fulfulde_phrase else 'NON'}")

    return num_pages, size_mb, all_found and native_phrase and fulfulde_phrase


def main():
    html_path = build_full_html()
    pdf_path, size_mb = convert_html_to_pdf_with_playwright(html_path)
    num_pages, size_mb, success = verify_pdf()
    print(f"\nBilan global de génération : {'SUCCÈS' if success else 'ÉCHEC'}")


if __name__ == "__main__":
    main()
