# ATPL Theory

EASA ATPL(A) theory, organised by the official learning objectives (TK Syllabus v6, ECQB 2026).

- 13 subjects, every ATPL(A) learning objective
- 050 Meteorology, 061 General Navigation and 081 Principles of Flight have full study texts written to read like a book (with formula sheets, glossaries and sourced diagrams), with every learning objective tagged in small print; 050 and 061 also have theory per objective, other subjects show the syllabus as a study checklist
- Tick objectives as studied (saved on the device), search all objectives, works offline once loaded
- Add to the iPad/iPhone home screen for a full-screen app

Static site, no build step: `index.html`, `app.css`, `app.js`, data in `data/`, diagrams in `img/`.

The study texts live in `book/<code>/chNN.md`. After editing one, rebuild its data with `python3 tools/build_book.py <code>` (needs the `markdown` package); the script fails if any learning objective is left untagged.
