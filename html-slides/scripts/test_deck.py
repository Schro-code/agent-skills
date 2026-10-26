"""Tests for deck.py. Run: python3 -m unittest discover -s scripts -p 'test_*.py'"""

from __future__ import annotations

import base64
import contextlib
import io
import tempfile
import unittest
from pathlib import Path

import deck

SKILL = Path(__file__).resolve().parent.parent
SAMPLE = SKILL / "examples" / "sample-slides.html"
PNG_1PX = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
)


def run(*argv: str) -> tuple[int, str]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        code = deck.main(list(argv))
    return code, out.getvalue()


class BuildTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.out = self.tmp / "deck.html"

    def fragment(self, text: str) -> str:
        path = self.tmp / "slides.html"
        path.write_text(text, encoding="utf-8")
        return str(path)

    def build(self, slides: str, *extra: str) -> tuple[int, str]:
        return run("build", "--slides", slides, "--out", str(self.out), "--title", "Demo", *extra)

    def test_sample_builds_and_passes_check(self) -> None:
        code, output = self.build(str(SAMPLE))
        self.assertEqual(code, 0, output)
        self.assertIn("6 slide(s)", output)
        document = self.out.read_text(encoding="utf-8")
        for placeholder in deck.PLACEHOLDERS:
            self.assertNotIn(placeholder, document)
        self.assertEqual(run("check", str(self.out))[0], 0)

    def test_title_is_escaped(self) -> None:
        code, output = run("build", "--slides", str(SAMPLE), "--out", str(self.out), "--title", "<b>A & B</b>")
        self.assertEqual(code, 0, output)
        self.assertIn("<title>&lt;b&gt;A &amp; B&lt;/b&gt;</title>", self.out.read_text(encoding="utf-8"))

    def test_refuses_to_overwrite_without_force(self) -> None:
        self.out.write_text("keep me", encoding="utf-8")
        code, output = self.build(str(SAMPLE))
        self.assertEqual(code, 2)
        self.assertIn("already exists", output)
        self.assertEqual(self.out.read_text(encoding="utf-8"), "keep me")
        self.assertEqual(self.build(str(SAMPLE), "--force")[0], 0)

    def test_single_logo_is_used_on_both_backgrounds(self) -> None:
        logo = self.tmp / "logo.png"
        logo.write_bytes(PNG_1PX)
        code, output = self.build(str(SAMPLE), "--logo-light", str(logo))
        self.assertEqual(code, 0, output)
        self.assertEqual(self.out.read_text(encoding="utf-8").count("data:image/png;base64,"), 2)

    def test_rejects_non_image_logo(self) -> None:
        fake = self.tmp / "logo.png"
        fake.write_text("not an image", encoding="utf-8")
        code, output = self.build(str(SAMPLE), "--logo-light", str(fake))
        self.assertEqual(code, 2)
        self.assertIn("must be PNG", output)

    def test_rejects_invalid_lang(self) -> None:
        self.assertEqual(self.build(str(SAMPLE), "--lang", 'en" onload="x')[0], 2)

    def test_unsafe_fragments_are_rejected_and_not_written(self) -> None:
        unsafe = {
            "script": '<section class="slide"><script>alert(1)</script></section>',
            "handler": '<section class="slide"><p onclick="alert(1)">x</p></section>',
            "js link": '<section class="slide"><a href="java\tscript:alert(1)">x</a></section>',
            "external img": '<section class="slide"><img src="https://example.com/x.png" alt=""></section>',
            "iframe": '<section class="slide"><iframe></iframe></section>',
            "refresh": '<section class="slide"><meta http-equiv="refresh" content="0"></section>',
            "style url": '<section class="slide" style="background:url(https://example.com/x)"></section>',
            "no slides": "<p>just text</p>",
        }
        for name, html in unsafe.items():
            with self.subTest(name):
                code, output = self.build(self.fragment(html))
                self.assertEqual(code, 1, output)
                self.assertFalse(self.out.exists(), "an unsafe deck must not be written")

    def test_allowed_links_pass(self) -> None:
        html = (
            '<section class="slide"><a href="https://example.com">a</a>'
            '<a href="mailto:someone@example.com">b</a><a href="#s2">c</a>'
            '<a href="notes/page.html">d</a></section>'
        )
        code, output = self.build(self.fragment(html))
        self.assertEqual(code, 0, output)

    def test_dense_slide_warns_but_builds(self) -> None:
        items = "".join(f"<li>Point {i}</li>" for i in range(8))
        code, output = self.build(self.fragment(f'<section class="slide"><ul class="bullets">{items}</ul></section>'))
        self.assertEqual(code, 0, output)
        self.assertIn("8 list items", output)


class CheckTest(unittest.TestCase):
    def test_tampered_csp_fails(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        out = tmp / "deck.html"
        run("build", "--slides", str(SAMPLE), "--out", str(out), "--title", "Demo")
        out.write_text(out.read_text(encoding="utf-8").replace("default-src 'none'", "default-src *"), encoding="utf-8")
        code, output = run("check", str(out))
        self.assertEqual(code, 1)
        self.assertIn("Content-Security-Policy", output)


class CatalogTest(unittest.TestCase):
    def test_lists_every_template(self) -> None:
        code, output = run("catalog", "--list")
        self.assertEqual(code, 0)
        template = deck.read_template()
        self.assertEqual(output.count("## "), template.count('<template id="tpl-'))
        self.assertIn("(tpl-cover)", output)


if __name__ == "__main__":
    unittest.main()
