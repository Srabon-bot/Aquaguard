"""
Converts a Markdown file into a paginated PDF, for turning the project's plain-text
manuals (README.md, packages/SETUP_MANUAL.md, hardware/FIREBASE_SETUP.md) into a
portable PDF form -- no LaTeX/pandoc/wkhtmltopdf dependency, just `markdown` (pure
Python, converts .md -> HTML) + `pymupdf`'s `Story` API (handles automatic multi-page
layout from HTML, already a project dependency via the report-generation scripts under
reports/).

Usage:
    python md_to_pdf.py <input.md> <output.pdf> [--title "Document Title"]

Re-run any time a source .md file changes -- this always regenerates from the current
Markdown, never hand-edited after the fact.
"""

import argparse
import sys
from pathlib import Path

import markdown
import pymupdf

CSS = """
@page { margin: 2cm; }
body {
    font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
    font-size: 10.5pt;
    line-height: 1.5;
    color: #1a1a1a;
}
h1 {
    font-size: 20pt;
    color: #0f4c5c;
    border-bottom: 2px solid #0f4c5c;
    padding-bottom: 6px;
    margin-top: 0;
}
h2 {
    font-size: 15pt;
    color: #0f4c5c;
    margin-top: 22px;
    border-bottom: 1px solid #cfd8dc;
    padding-bottom: 3px;
}
h3 { font-size: 12.5pt; color: #12707f; margin-top: 16px; }
p { margin: 6px 0; }
a { color: #0f6fa3; }
code {
    font-family: "Consolas", "Courier New", monospace;
    background: #f0f2f4;
    padding: 1px 4px;
    border-radius: 3px;
    font-size: 9.5pt;
}
pre {
    background: #f0f2f4;
    border: 1px solid #dfe3e6;
    border-radius: 5px;
    padding: 8px 10px;
    font-size: 9pt;
    line-height: 1.4;
    white-space: pre-wrap;
}
/* Deliberately no "pre code { background: none }" override here: PyMuPDF's
   Story CSS engine mis-renders that descendant-selector combination as a
   solid black fill over the text (confirmed by isolated bisection testing,
   not assumed). pre and code already share the same background color, so
   code's own background/padding inside a pre block is redundant but
   harmless -- omitting the override avoids the bug entirely. */
table { border-collapse: collapse; width: 100%; margin: 10px 0; font-size: 9.5pt; }
th, td { border: 1px solid #cfd8dc; padding: 5px 8px; text-align: left; }
th { background: #e8f0f2; }
blockquote {
    border-left: 3px solid #0f4c5c;
    margin: 8px 0;
    padding: 2px 12px;
    color: #45525a;
    background: #f7f9fa;
}
li { margin: 3px 0; }
hr { border: none; border-top: 1px solid #cfd8dc; margin: 18px 0; }
"""


# A handful of Unicode symbols this project's docs use that render as blank/broken
# "tofu" boxes through PyMuPDF's Story engine (no matching glyph in its fallback
# font) -- confirmed by visual inspection of a rendered test page, not assumed.
# Em/en dashes, arrows drawn as "->", and plain bullets all render fine and are
# left alone; only the emoji-range symbols below needed a plain-text stand-in.
SYMBOL_FALLBACKS = {
    "✅": "[done]",       # checkmark button
    "⏳": "[in progress]",  # hourglass
    "▶": ">",             # play/triangle
    # These 4 render as fully blank gaps (not even a tofu box) rather than
    # black boxes -- worse for a manual, since "Click ' Capture acid...'"
    # reads as a typo, not an obviously-missing icon. Dropped entirely
    # (including the space that normally follows them in this project's
    # docs) rather than given a bracketed text stand-in like the 3 above --
    # the button/action text alone is already self-explanatory, so a
    # "[test tube]" tag would just add clutter. Order matters here: the
    # "symbol+space" entries must be replaced before the bare-symbol
    # fallback below, or the bare replacement runs first and leaves a
    # stray double space.
    "🧪 ": "", "🧂 ": "", "💾 ": "", "🗑 ": "",
    "🧪": "", "🧂": "", "💾": "", "🗑": "",
}


def convert(md_path: Path, pdf_path: Path, title: str | None) -> int:
    text = md_path.read_text(encoding="utf-8")
    for symbol, fallback in SYMBOL_FALLBACKS.items():
        text = text.replace(symbol, fallback)
    body_html = markdown.markdown(
        text, extensions=["tables", "fenced_code", "sane_lists", "toc"]
    )
    doc_title = title or md_path.stem.replace("_", " ")
    html = f"<html><head><style>{CSS}</style></head><body>{body_html}</body></html>"

    story = pymupdf.Story(html=html)
    writer = pymupdf.DocumentWriter(str(pdf_path))
    mediabox = pymupdf.paper_rect("a4")
    where = mediabox + (0, 0, 0, 0)  # CSS @page margin handles the inset

    more = 1
    pages = 0
    while more:
        device = writer.begin_page(mediabox)
        more, _filled = story.place(where)
        story.draw(device)
        writer.end_page()
        pages += 1
    writer.close()

    # Stamp document metadata (title shown in PDF viewers/tabs) as a quick
    # second pass -- Story/DocumentWriter don't expose metadata directly.
    with pymupdf.open(str(pdf_path)) as doc:
        doc.set_metadata({"title": doc_title})
        doc.saveIncr()

    return pages


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Source .md file")
    parser.add_argument("output", type=Path, help="Destination .pdf file")
    parser.add_argument("--title", default=None, help="PDF metadata title (default: filename)")
    args = parser.parse_args()

    if not args.input.is_file():
        print(f"Input file not found: {args.input}", file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    pages = convert(args.input, args.output, args.title)
    print(f"Wrote {args.output} ({pages} pages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
