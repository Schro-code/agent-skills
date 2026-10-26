#!/usr/bin/env python3
"""Build and validate self-contained HTML slide decks from assets/template.html.

Commands:
  catalog                 list the slide types defined in the template
  build                   assemble a deck from a slides fragment
  check                   validate an existing deck

Standard library only; works with Python 3.8+.
"""

from __future__ import annotations

import argparse
import base64
import html
import os
import re
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "template.html"

PLACEHOLDERS = ("{{TITLE}}", "{{LANG}}", "{{SLIDES}}", "__LOGO_ON_LIGHT__", "__LOGO_ON_DARK__")
MAX_LOGO_BYTES = 1024 * 1024
MAX_BULLETS = 6
LANG_RE = re.compile(r"^[A-Za-z]{2,3}(-[A-Za-z0-9]{2,8})*$")
SCHEME_RE = re.compile(r"^([a-z][a-z0-9+.\-]*):")
ALLOWED_SCHEMES = {"http", "https", "mailto"}
FORBIDDEN_TAGS = {"iframe", "object", "embed", "link", "base", "form", "frame", "frameset", "applet"}
CSP_RE = re.compile(r'<meta http-equiv="Content-Security-Policy" content="([^"]+)">')
TEMPLATE_RE = re.compile(
    r'<template id="(tpl-[\w-]+)" data-label="([^"]*)" data-use="([^"]*)">\s*(.*?)\s*</template>',
    re.S,
)


class DeckError(Exception):
    pass


def read_template() -> str:
    return TEMPLATE.read_text(encoding="utf-8")


def expected_csp(template: str) -> str:
    match = CSP_RE.search(template)
    if not match:
        raise DeckError(f"template has no CSP meta tag: {TEMPLATE}")
    return match.group(1)


# --- catalog -----------------------------------------------------------------

def cmd_catalog(args: argparse.Namespace) -> int:
    template = read_template()
    for tpl_id, label, use, markup in TEMPLATE_RE.findall(template):
        print(f"## {label} ({tpl_id})")
        print(f"Use: {html.unescape(use)}")
        if not args.list:
            print()
            print(markup)
        print()
    return 0


# --- logos -------------------------------------------------------------------

def logo_data_uri(path: Path) -> str:
    if not path.is_file():
        raise DeckError(f"logo not found: {path}")
    data = path.read_bytes()
    if len(data) > MAX_LOGO_BYTES:
        raise DeckError(f"logo larger than {MAX_LOGO_BYTES // 1024} KB: {path}")
    mime = sniff_image(data)
    if mime is None:
        raise DeckError(f"logo must be PNG, JPEG, WebP or SVG: {path}")
    return f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"


def sniff_image(data: bytes) -> str | None:
    # Content decides the type, not the file extension.
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    try:
        text = data.decode("utf-8-sig").lstrip().lower()
    except UnicodeDecodeError:
        return None
    head = text[:2048]
    if (head.startswith("<svg") or (head.startswith("<?xml") and "<svg" in head)) and "<script" not in text:
        return "image/svg+xml"
    return None


# --- check -------------------------------------------------------------------

class DeckInspector(HTMLParser):
    """Collects the facts the safety checks need in a single pass."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.template_depth = 0
        self.slides = 0
        self.scripts = 0
        self.styles = 0
        self.bullets_in_slide = 0
        self.in_style = False
        self.style_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {name.lower(): (value or "") for name, value in attrs}
        line = self.getpos()[0]

        if tag == "template":
            self.template_depth += 1
        if tag == "script":
            self.scripts += 1
        if tag == "style":
            self.styles += 1
            self.in_style = True
        if tag in FORBIDDEN_TAGS:
            self.errors.append(f"line {line}: <{tag}> is not allowed")
        if tag == "meta":
            self.check_meta(attributes, line)

        for name, value in attributes.items():
            if name.startswith("on"):
                self.errors.append(f"line {line}: inline event handler '{name}' is not allowed")
            if name == "src" and not value.strip().lower().startswith("data:image/"):
                self.errors.append(f"line {line}: external resource src='{value[:60]}'")
            if name == "href":
                self.check_href(tag, value, line)
            if name == "style" and re.search(r"url\(\s*['\"]?(?!data:)", value, re.I):
                self.errors.append(f"line {line}: style url() must use a data: URI")

        if self.template_depth == 0:
            if tag == "section" and "slide" in attributes.get("class", "").split():
                self.close_slide()
                self.slides += 1
                self.bullets_in_slide = 0
            if tag == "li":
                self.bullets_in_slide += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "template":
            self.template_depth = max(0, self.template_depth - 1)
        if tag == "style":
            self.in_style = False
        if tag == "main":
            self.close_slide()

    def handle_data(self, data: str) -> None:
        if self.in_style:
            self.style_text.append(data)

    def close_slide(self) -> None:
        if self.slides and self.bullets_in_slide > MAX_BULLETS:
            self.warnings.append(
                f"slide {self.slides}: {self.bullets_in_slide} list items; consider splitting it"
            )
        self.bullets_in_slide = 0

    def check_meta(self, attributes: dict[str, str], line: int) -> None:
        http_equiv = attributes.get("http-equiv", "").lower()
        if "charset" in attributes or attributes.get("name") == "viewport":
            return
        if http_equiv == "content-security-policy":
            return
        self.errors.append(f"line {line}: unexpected <meta> {attributes}")

    def check_href(self, tag: str, value: str, line: int) -> None:
        if tag != "a":
            self.errors.append(f"line {line}: href on <{tag}> is not allowed")
            return
        # Browsers ignore whitespace and control characters inside a scheme ("java\tscript:").
        normalized = re.sub(r"[\x00-\x20]+", "", value).lower()
        match = SCHEME_RE.match(normalized)
        if match and match.group(1) not in ALLOWED_SCHEMES:
            self.errors.append(f"line {line}: link scheme '{match.group(1)}:' is not allowed")


def inspect(document: str, csp: str) -> tuple[list[str], list[str], int]:
    errors: list[str] = []
    for placeholder in PLACEHOLDERS:
        if placeholder in document:
            errors.append(f"unfilled placeholder {placeholder}")
    found = CSP_RE.findall(document)
    if found != [csp]:
        errors.append("Content-Security-Policy is missing, duplicated or changed")

    inspector = DeckInspector()
    inspector.feed(document)
    inspector.close()
    errors.extend(inspector.errors)
    if inspector.slides == 0:
        errors.append("no slides found inside the deck")
    if inspector.scripts != 1:
        errors.append(f"expected exactly 1 <script> (the template's), found {inspector.scripts}")
    if inspector.styles != 1:
        errors.append(f"expected exactly 1 <style> (the template's), found {inspector.styles}")
    if re.search(r"url\(\s*['\"]?(?!data:)", "".join(inspector.style_text), re.I):
        errors.append("stylesheet url() must use a data: URI")
    return errors, inspector.warnings, inspector.slides


def report(errors: list[str], warnings: list[str], slides: int, path: str) -> int:
    for warning in warnings:
        print(f"WARN  {warning}")
    for error in errors:
        print(f"ERROR {error}")
    if errors:
        print(f"FAIL  {path}: {len(errors)} error(s)")
        return 1
    print(f"OK    {path}: {slides} slide(s)")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    path = Path(args.deck)
    if not path.is_file():
        raise DeckError(f"deck not found: {path}")
    errors, warnings, slides = inspect(path.read_text(encoding="utf-8"), expected_csp(read_template()))
    return report(errors, warnings, slides, str(path))


# --- build -------------------------------------------------------------------

def write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False, suffix=".tmp") as tmp:
        tmp.write(text)
    os.replace(tmp.name, path)


def cmd_build(args: argparse.Namespace) -> int:
    out = Path(args.out)
    if out.exists() and not args.force:
        raise DeckError(f"{out} already exists; pass --force only after the user confirms overwriting it")
    if not LANG_RE.match(args.lang):
        raise DeckError(f"invalid language tag: {args.lang!r}")

    fragment_path = Path(args.slides)
    if not fragment_path.is_file():
        raise DeckError(f"slides fragment not found: {fragment_path}")
    fragment = fragment_path.read_text(encoding="utf-8").strip()

    # One logo is reused on both backgrounds; no logo leaves both slots empty.
    light = logo_data_uri(Path(args.logo_light)) if args.logo_light else ""
    dark = logo_data_uri(Path(args.logo_dark)) if args.logo_dark else ""
    light, dark = light or dark, dark or light

    template = read_template()
    for placeholder in PLACEHOLDERS:
        if template.count(placeholder) != 1:
            raise DeckError(f"template must contain {placeholder} exactly once")

    document = (
        template.replace("{{TITLE}}", html.escape(args.title, quote=True))
        .replace("{{LANG}}", args.lang)
        .replace("__LOGO_ON_LIGHT__", light)
        .replace("__LOGO_ON_DARK__", dark)
        # Slides go in last so text inside them is never treated as a placeholder.
        .replace("{{SLIDES}}", fragment)
    )

    errors, warnings, slides = inspect(document, expected_csp(template))
    if errors:
        return report(errors, warnings, slides, f"{out} (not written)")
    write_atomic(out, document)
    return report(errors, warnings, slides, str(out))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    catalog = sub.add_parser("catalog", help="list slide types from the template")
    catalog.add_argument("--list", action="store_true", help="names and usage only, without markup")
    catalog.set_defaults(func=cmd_catalog)

    build = sub.add_parser("build", help="assemble a deck from a slides fragment")
    build.add_argument("--slides", required=True, help="HTML fragment with the <section class=\"slide\"> elements")
    build.add_argument("--out", required=True, help="output .html path")
    build.add_argument("--title", required=True, help="deck title (escaped automatically)")
    build.add_argument("--lang", default="en", help="BCP 47 language tag, e.g. en, es, pt-BR")
    build.add_argument("--logo-light", help="logo shown on light slides (PNG, JPEG, WebP or SVG)")
    build.add_argument("--logo-dark", help="logo shown on dark/accent slides")
    build.add_argument("--force", action="store_true", help="overwrite an existing output file")
    build.set_defaults(func=cmd_build)

    check = sub.add_parser("check", help="validate an existing deck")
    check.add_argument("deck", help="deck .html path")
    check.set_defaults(func=cmd_check)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except DeckError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
