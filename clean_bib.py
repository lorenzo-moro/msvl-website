"""Build the Publications page lists from Articles.bib.

Runs automatically before every render (pre-render in _quarto.yml).
Articles.bib stays exactly as it is in the Overleaf CV (the full CV
bibliography). This script:
  1. splits it by the "% ..." section comments of the CV file;
  2. keeps only what the website shows:
       - Journal papers ............ all
       - Books and Book chapters ... from CHAPTERS_FROM onwards
       - Conference papers ......... from CONFERENCES_FROM onwards
     (posters, reports, theses and lectures are not shown);
  3. cleans entries for the web (no \\underline, no "and and",
     bare DOIs, no "(Peer reviewed)" notes, titles kept as written);
  4. formats each list with Quarto's citation processor into
     _pubs_journal.md, _pubs_chapters.md and _pubs_conferences.md,
     which publications.qmd includes.

To show more or fewer years, change the two numbers below.
"""
import re
import shutil
import subprocess
from pathlib import Path

CHAPTERS_FROM = 2022
CONFERENCES_FROM = 2023

SECTIONS = {  # start of the CV section comment -> list name
    "Journal Papers": "journal",
    "Books and Book chapters": "chapters",
    "Conference Papers": "conferences",
}
MIN_YEAR = {"journal": 0, "chapters": CHAPTERS_FROM, "conferences": CONFERENCES_FROM}


def field_span(text, start):
    """(open, close) indices of the {...} value starting at text[start] == '{'."""
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return start, i
    return start, len(text) - 1


def protect_titles(entry):
    """Wrap titles in an extra pair of braces so capitalisation is kept."""
    res, pos = [], 0
    for m in re.finditer(r"(?<![a-z])(title|booktitle|journal)\s*=\s*\{", entry, flags=re.I):
        o, c = field_span(entry, m.end() - 1)
        inner = entry[o + 1:c]
        if not (inner.startswith("{") and inner.endswith("}")):
            inner = "{" + " ".join(inner.split()) + "}"
        res.append(entry[pos:o + 1] + inner)
        pos = c
    res.append(entry[pos:])
    return "".join(res)


def clean(entry):
    e = re.sub(r"^@conference\s*\{", "@inproceedings{", entry, flags=re.I)
    e = re.sub(r"\\underline\{([^{}]*)\}", r"\1", e)
    e = re.sub(r"\band\s+and\b", "and", e)
    e = re.sub(r"(doi\s*=\s*\{)\s*https?://(dx\.)?doi\.org/", r"\1", e, flags=re.I)
    e = re.sub(r"^\s*doi\s*=\s*\{\s*\}\s*,?\s*$\n?", "", e, flags=re.I | re.M)
    # notes: drop "(Peer reviewed)" / "Invited", drop the note if nothing is left
    e = re.sub(r"\(\s*peer[ -]reviewed\s*\)\s*,?\s*(invited)?", "", e, flags=re.I)
    e = re.sub(r"^\s*note\s*=\s*\{[\s.,]*\}\s*,?\s*$\n?", "", e, flags=re.I | re.M)
    if re.search(r"doi\s*=\s*\{\s*10\.", e, flags=re.I):
        e = re.sub(r"^\s*url\s*=\s*\{[^}]*\}\s*,?\s*$\n?", "", e, flags=re.I | re.M)
    return protect_titles(e)


def year_of(entry):
    m = re.search(r"(?<![a-z])year\s*=\s*[{\"]?\s*(\d{4})", entry, flags=re.I)
    return int(m.group(1)) if m else 0


src = Path("Articles.bib").read_text(encoding="utf-8")
lists = {name: [] for name in MIN_YEAR}
current = None
for line_block in re.split(r"(?m)^(?=%|@)", src):
    if line_block.startswith("%"):
        header = line_block.lstrip("%").strip()
        current = next((n for k, n in SECTIONS.items() if header.startswith(k)), None)
        continue
    if current and line_block.startswith("@") and year_of(line_block) >= MIN_YEAR[current]:
        lists[current].append(clean(line_block))

quarto = shutil.which("quarto") or "quarto"
for name, entries in lists.items():
    bib = Path(f"_web_{name}.bib")
    bib.write_text("\n".join(entries), encoding="utf-8")
    doc = "---\nnocite: |\n  @*\n---\n"
    out = subprocess.run(
        [quarto, "pandoc", "--citeproc", f"--bibliography={bib}",
         "--csl=newest-first.csl", "-f", "markdown", "-t", "markdown-citations",
         "--wrap=none"],
        input=doc, capture_output=True, text=True, encoding="utf-8")
    if out.returncode != 0:
        raise SystemExit(f"Formatting {name} failed:\n{out.stderr}")
    text = out.stdout.replace("{#refs .references", "{.references")
    Path(f"_pubs_{name}.md").write_text(text, encoding="utf-8")
