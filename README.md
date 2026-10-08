# ATPL Theory

EASA ATPL(A) theory, organised by the official learning objectives (TK Syllabus v6, ECQB 2026).

- 13 subjects, every ATPL(A) learning objective
- 050 Meteorology has a full study text written to read like a book (10 chapters plus a formula sheet and glossary), with every learning objective tagged in small print, and the same theory per objective with exam diagrams; other subjects show the syllabus as a study checklist
- Tick objectives as studied (saved on the device), search all objectives, works offline once loaded
- Add to the iPad/iPhone home screen for a full-screen app

Static site, no build step: `index.html`, `app.css`, `app.js`, data in `data/`, diagrams in `img/`.

The study text lives in `book/050/chNN.md`. After editing it, rebuild its data with `python3 tools/build_book.py 050` (needs the `markdown` package); the script fails if any learning objective is left untagged.
