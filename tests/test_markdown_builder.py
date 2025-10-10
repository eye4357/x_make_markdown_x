"""Tests for the Markdown document builder."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import TYPE_CHECKING, NoReturn

from x_make_markdown_x.x_cls_make_markdown_x import XClsMakeMarkdownX

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch


def test_generate_writes_markdown_and_toc(tmp_path: Path) -> None:
    builder = XClsMakeMarkdownX(wkhtmltopdf_path="")
    builder.add_header("Intro", level=1)
    builder.add_paragraph("Welcome")
    builder.add_header("Details", level=2)
    builder.add_list(["Point A", "Point B"], ordered=True)
    builder.add_toc()

    output_md = tmp_path / "doc.md"
    markdown_text = builder.generate(output_file=str(output_md))

    written = output_md.read_text(encoding="utf-8")
    if written != markdown_text:
        raise AssertionError("generated markdown should match file contents")
    if not markdown_text.startswith("- [1 Intro]"):
        raise AssertionError("TOC should start with Intro header entry")
    if "1.1 Details" not in markdown_text:
        raise AssertionError("Nested header should appear in generated TOC")
    if (tmp_path / "doc.pdf").exists():
        raise AssertionError("PDF should not be created without wkhtmltopdf")


def test_to_html_fallback_when_markdown_missing(monkeypatch: MonkeyPatch) -> None:
    builder = XClsMakeMarkdownX()

    def fake_import(name: str, package: str | None = None) -> NoReturn:  # noqa: ARG001
        raise ModuleNotFoundError("markdown unavailable")

    monkeypatch.setattr(importlib, "import_module", fake_import)

    result = builder.to_html("<b>bold</b>")

    if not result.startswith("<pre>"):
        raise AssertionError("fallback should wrap output in <pre> tag")
    if "&lt;b&gt;bold&lt;/b&gt;" not in result:
        raise AssertionError("fallback should escape HTML content")


def test_to_pdf_requires_existing_wkhtmltopdf(tmp_path: Path) -> None:
    import pytest

    builder = XClsMakeMarkdownX(wkhtmltopdf_path=str(tmp_path / "missing.exe"))

    with pytest.raises(RuntimeError, match="binary not found"):
        builder.to_pdf("<html></html>", str(tmp_path / "out.pdf"))


def test_to_pdf_raises_when_pdfkit_unavailable(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    import pytest

    wkhtmltopdf = tmp_path / "wkhtmltopdf.exe"
    wkhtmltopdf.write_text("binary")
    builder = XClsMakeMarkdownX(wkhtmltopdf_path=str(wkhtmltopdf))

    def fake_import(name: str, package: str | None = None) -> NoReturn:  # noqa: ARG001
        raise ImportError("pdfkit missing")

    monkeypatch.setattr(importlib, "import_module", fake_import)

    with pytest.raises(RuntimeError, match="pdfkit is required"):
        builder.to_pdf("<html></html>", str(tmp_path / "out.pdf"))


def test_to_pdf_invokes_pdfkit_when_available(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    wkhtmltopdf = tmp_path / "wkhtmltopdf.exe"
    wkhtmltopdf.write_text("binary")
    builder = XClsMakeMarkdownX(wkhtmltopdf_path=str(wkhtmltopdf))

    captured: dict[str, object] = {}

    class FakePdfKit:
        def configuration(self, *, wkhtmltopdf: str) -> object:
            captured["wkhtmltopdf"] = wkhtmltopdf
            return {"wkhtmltopdf": wkhtmltopdf}

        def from_string(
            self, html_str: str, out_path: str, *, configuration: object
        ) -> None:
            captured["html"] = html_str
            captured["out_path"] = out_path
            Path(out_path).write_text("PDF", encoding="utf-8")
            captured["config"] = configuration

    def load_pdfkit(
        name: str, package: str | None = None
    ) -> FakePdfKit:
        return FakePdfKit()

    monkeypatch.setattr(importlib, "import_module", load_pdfkit)

    out_pdf = tmp_path / "out.pdf"
    builder.to_pdf("<html><body>hi</body></html>", str(out_pdf))

    if not out_pdf.exists():
        raise AssertionError("PDF output file should be created")
    if out_pdf.read_text(encoding="utf-8") != "PDF":
        raise AssertionError("PDF placeholder content should be written")
    if captured.get("wkhtmltopdf") != str(wkhtmltopdf):
        raise AssertionError("wkhtmltopdf path should be passed to pdfkit")
    html = captured.get("html")
    if not isinstance(html, str) or not html.startswith("<html>"):
        raise AssertionError("HTML content should be forwarded to pdfkit")
    if captured.get("out_path") != str(out_pdf):
        raise AssertionError("Output path should be forwarded to pdfkit")
