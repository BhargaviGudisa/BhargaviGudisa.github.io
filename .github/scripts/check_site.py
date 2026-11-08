#!/usr/bin/env python3
"""Structural checks for the single-file portfolio site.

Nothing here is a style opinion. Each check corresponds to a way the page has
actually broken or could break silently in a browser, where a visitor sees the
damage and you do not.

Run locally with:  python .github/scripts/check_site.py
"""
from __future__ import annotations

import html.parser
import json
import os
import re
import sys

PAGE = "index.html"
VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}

failures: list[str] = []
notes: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)


def ok(msg: str) -> None:
    notes.append(msg)


class TagBalance(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, tuple[int, int]]] = []
        self.errors: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append((tag, self.getpos()))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.errors.append(f"stray </{tag}> at line {self.getpos()[0]}")
            return
        open_tag, pos = self.stack[-1]
        if open_tag != tag:
            self.errors.append(
                f"</{tag}> at line {self.getpos()[0]} closes <{open_tag}> opened at line {pos[0]}"
            )
        else:
            self.stack.pop()


def main() -> int:
    if not os.path.exists(PAGE):
        print(f"{PAGE} not found", file=sys.stderr)
        return 1

    with open(PAGE, encoding="utf-8") as fh:
        src = fh.read()

    # 1. Tag balance. An unclosed section silently swallows the rest of the page.
    parser = TagBalance()
    parser.feed(src)
    for err in parser.errors:
        fail(f"markup: {err}")
    for tag, pos in parser.stack:
        fail(f"markup: <{tag}> opened at line {pos[0]} is never closed")
    if not parser.errors and not parser.stack:
        ok("markup is balanced")

    # 2. JSON-LD. Malformed structured data is ignored without warning, so the
    #    rich result just never appears and nothing tells you why.
    blocks = re.findall(
        r'<script type="application/ld\+json">(.*?)</script>', src, re.S
    )
    if not blocks:
        fail("structured data: no JSON-LD block found")
    for i, block in enumerate(blocks):
        try:
            data = json.loads(block)
            ok(f"JSON-LD block {i} parses (@type={data.get('@type')})")
        except json.JSONDecodeError as exc:
            fail(f"structured data: JSON-LD block {i} is invalid — {exc}")

    # 3. Every aria-controls points at a real element, or the case-study
    #    toggles lie to screen readers.
    targets = sorted(set(re.findall(r'aria-controls="([^"]+)"', src)))
    missing = [t for t in targets if f'id="{t}"' not in src]
    for target in missing:
        fail(f"a11y: aria-controls=\"{target}\" has no matching id")
    if not missing:
        ok(f"all {len(targets)} aria-controls targets resolve")

    # 4. Every label points at a real field.
    labels = sorted(set(re.findall(r'<label for="([^"]+)"', src)))
    orphans = [t for t in labels if f'id="{t}"' not in src]
    for target in orphans:
        fail(f"a11y: <label for=\"{target}\"> has no matching field")
    if not orphans:
        ok(f"all {len(labels)} labels resolve")

    # 5. Duplicate ids break getElementById and anchor links.
    ids = re.findall(r'\sid="([^"]+)"', src)
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    for dupe in dupes:
        fail(f"markup: id \"{dupe}\" is used more than once")
    if not dupes:
        ok(f"{len(set(ids))} unique ids, no duplicates")

    # 6. Local assets referenced by the page must exist in the repository,
    #    otherwise the deploy 404s for a visitor but not for us.
    refs: set[str] = set(re.findall(r'(?:href|src)="\./([^"#?]+)"', src))
    for attr in re.findall(r'srcset="([^"]+)"', src):
        for candidate in attr.split(","):
            part = candidate.strip().split()
            if part:
                refs.add(part[0].lstrip("./"))
    absent = [r for r in sorted(refs) if not os.path.exists(r)]
    for ref in absent:
        fail(f"assets: {ref} is referenced but not in the repository")
    if not absent:
        ok(f"all {len(refs)} local asset references exist")

    # 7. The hiding rule must stay scoped to html.js. Unscoped, a failed CDN
    #    load leaves every .reveal block invisible and the page looks empty.
    if re.search(r"(?<!html\.js )\.reveal\s*\{[^}]*opacity:\s*0", src):
        fail(
            "resilience: a .reveal opacity:0 rule is not scoped to html.js — "
            "if GSAP fails to load the page renders blank"
        )
    else:
        ok(".reveal hiding stays scoped to html.js")

    if "HAS_GSAP" not in src:
        fail("resilience: the HAS_GSAP fallback guard is missing")
    else:
        ok("HAS_GSAP fallback guard present")

    for line in notes:
        print(f"ok    {line}")
    for line in failures:
        print(f"FAIL  {line}", file=sys.stderr)

    print(f"\n{len(notes)} checks passed, {len(failures)} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
