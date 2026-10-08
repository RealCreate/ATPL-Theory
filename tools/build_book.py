"""Build data/book-<code>.json from the Markdown study text in book/<code>/chNN.md.

Each chapter file starts with '## <Label> · <Title>'. Learning-objective tags are
inline code spans such as `050.01.02.03.04` or ranges `050.01.02.03.04–07`.
Run:  python3 tools/build_book.py 050
"""
import json
import re
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
TAG = re.compile(r"`(\d{3}(?:\.\d\d){4})(?:–(\d\d))?`")
CALLOUTS = [("Exam trap", "trap"), ("Worked example", "worked"), ("Key numbers", "keys")]


def expand(base, end):
    if not end:
        return [base]
    head, start = base[:-2], int(base[-2:])
    return [f"{head}{i:02d}" for i in range(start, int(end) + 1)]


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]


def tags_html(m):
    refs = expand(m.group(1), m.group(2))
    label = m.group(1)[4:] + (f"–{m.group(2)}" if m.group(2) else "")
    return (f'<a class="lo-tag" href="#/lo/{refs[0]}" data-refs="{" ".join(refs)}" '
            f'title="Learning objective{"s" if len(refs) > 1 else ""} {m.group(1)}'
            f'{"–" + m.group(2) if m.group(2) else ""}">{label}</a>')


def build_chapter(path, n):
    md = path.read_text(encoding="utf-8")
    first, _, body = md.partition("\n")
    label, _, title = first.lstrip("# ").partition(" · ")
    refs = []
    for m in TAG.finditer(body):
        for r in expand(m.group(1), m.group(2)):
            if r not in refs:
                refs.append(r)
    body = TAG.sub(tags_html, body)
    html = markdown.markdown(body, extensions=["tables", "sane_lists"])

    # Section headings get ids; collect them for the contents list.
    sections = []

    def head(m):
        text = re.sub(r"<[^>]+>", "", m.group(1))
        sid = f"c{n}-" + slug(text)
        cls = ' class="check"' if text.lower().startswith("check yourself") else ""
        sections.append({"id": sid, "title": text})
        return f'<h3 id="{sid}"{cls}>{m.group(1)}</h3>'

    html = re.sub(r"<h3>(.*?)</h3>", head, html)

    # Images → figures with captions.
    html = re.sub(r'<p><img alt="([^"]*)" src="([^"]+)" ?/?></p>',
                  r'<figure class="dia"><img src="\2" alt="\1" loading="lazy" decoding="async"><figcaption>\1</figcaption></figure>',
                  html)

    # Tables scroll horizontally on small screens.
    html = html.replace("<table>", '<div class="tbl"><table>').replace("</table>", "</table></div>")

    # Callouts by their opening bold label.
    def callout(m):
        inner = m.group(1)
        lead = re.search(r"<strong>([^<]+)</strong>", inner)
        kind = "note"
        if lead:
            for word, cls in CALLOUTS:
                if lead.group(1).startswith(word):
                    kind = cls
                    break
        return f'<aside class="callout {kind}">{inner}</aside>'

    html = re.sub(r"<blockquote>(.*?)</blockquote>", callout, html, flags=re.S)

    # Paragraphs holding only tags sit flush right as a quiet footer line.
    html = re.sub(r'<p>((?:<a class="lo-tag"[^>]*>[^<]*</a>\s*)+)</p>', r'<p class="tags">\1</p>', html)
    return {"n": n, "label": label.strip(), "title": title.strip(), "refs": refs,
            "sections": sections, "html": html}


def main(code):
    src = ROOT / "book" / code
    chapters = [build_chapter(p, i + 1) for i, p in enumerate(sorted(src.glob("ch*.md")))]
    out = ROOT / "data" / f"book-{code}.json"
    out.write_text(json.dumps({"code": code, "chapters": chapters}, ensure_ascii=False, separators=(",", ":")),
                   encoding="utf-8")
    subj = json.loads((ROOT / "data" / f"{code}.json").read_text(encoding="utf-8"))
    all_refs = [l["ref"] for c in subj["chapters"] for s in c["subs"] for t in s["topics"] for l in t["los"]]
    tagged = {r for c in chapters for r in c["refs"]}
    missing = [r for r in all_refs if r not in tagged]
    unknown = sorted(tagged - set(all_refs))
    print(f"{out.name}: {len(chapters)} chapters, {len(tagged)}/{len(all_refs)} objectives tagged, "
          f"{out.stat().st_size // 1024} KB")
    if missing or unknown:
        print("missing:", missing, "unknown:", unknown)
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "050")
