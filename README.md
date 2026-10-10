# ATPL Theory

**Open the app: [realcreate.github.io/ATPL-Theory](https://realcreate.github.io/ATPL-Theory/)**

This link never changes. Every push to `main` is published to the same address, and the app checks for the newest version each time it opens, so the link (or the home-screen icon) always shows the latest update.

## What it is

A free study companion for the EASA ATPL(A) theory exams. Instead of loose notes, everything is organised around the official learning objectives (TK Syllabus v6, ECQB 2026), so you always know exactly what the exam can ask and how much of it you have covered.

It is designed to feel like a native Apple app and works the same on iPad, iPhone and desktop, in light and dark mode.

## What's inside

- **All 13 ATPL(A) subjects, all 4,044 learning objectives**, from 010 Air Law to 090 Communications
- **Study texts that read like a book** for 050 Meteorology, 061 General Navigation and 081 Principles of Flight, with formula sheets, glossaries and illustrated diagrams checked against official sources. Every paragraph is tagged in small print with the learning objectives it covers
- **Theory for every objective** in 050, 061 and 081; the other subjects show the full syllabus as a study checklist
- **Progress tracking**: tick objectives as you study them (saved on your device)
- **Search** across every objective in every subject
- **Works offline** once it has been opened, so you can study on a plane or with no signal

| Code | Subject | Objectives |
|------|---------|-----------:|
| 010 | Air Law | 505 |
| 021 | Airframe & Systems | 509 |
| 022 | Instrumentation | 409 |
| 031 | Mass & Balance | 84 |
| 032 | Performance | 240 |
| 033 | Flight Planning | 118 |
| 040 | Human Performance | 362 |
| 050 | Meteorology | 464 |
| 061 | General Navigation | 117 |
| 062 | Radio Navigation | 322 |
| 070 | Operational Procedures | 346 |
| 081 | Principles of Flight | 489 |
| 090 | Communications | 79 |

## Install on iPad or iPhone

Open the link in Safari, tap **Share → Add to Home Screen**. It then opens full-screen like a normal app and updates itself.

## For development

Static site, no build step: `index.html`, `app.css`, `app.js`, data in `data/`, diagrams in `img/`. Hosted on GitHub Pages from the `main` branch.

The study texts live in `book/<code>/chNN.md`. After editing one, rebuild its data with `python3 tools/build_book.py <code>` (needs the `markdown` package); the script fails if any learning objective is left untagged.
