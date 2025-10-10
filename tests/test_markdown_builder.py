"""Tests for the Markdown document builder."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

import pytest

from x_cls_make_markdown_x import XClsMakeMarkdownX


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
    assert written == markdown_text
    assert markdown_text.startswith("- [1 Intro]")
    assert "1.1 Details" in markdown_text
    assert not (tmp_path / "doc.pdf").exists()


def test_to_html_fallback_when_markdown_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    builder = XClsMakeMarkdownX()

    def fake_import(name: str, package: str | None = None) -> Any:  # noqa: ARG001
        raise ModuleNotFoundError("markdown unavailable")

    monkeypatch.setattr(importlib, "import_module", fake_import)

    result = builder.to_html("<b>bold</b>")

    assert result.startswith("<pre>")
    assert "&lt;b&gt;bold&lt;/b&gt;" in result


def test_to_pdf_requires_existing_wkhtmltopdf(tmp_path: Path) -> None:
    builder = XClsMakeMarkdownX(wkhtmltopdf_path=str(tmp_path / "missing.exe"))

    with pytest.raises(RuntimeError, match="binary not found"):
        builder.to_pdf("<html></html>", str(tmp_path / "out.pdf"))


def test_to_pdf_raises_when_pdfkit_unavailable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    wkhtmltopdf = tmp_path / "wkhtmltopdf.exe"
    wkhtmltopdf.write_text("binary")
    builder = XClsMakeMarkdownX(wkhtmltopdf_path=str(wkhtmltopdf))

    def fake_import(name: str, package: str | None = None) -> Any:  # noqa: ARG001
        raise ImportError("pdfkit missing")

    monkeypatch.setattr(importlib, "import_module", fake_import)

    with pytest.raises(RuntimeError, match="pdfkit is required"):
        builder.to_pdf("<html></html>", str(tmp_path / "out.pdf"))


def test_to_pdf_invokes_pdfkit_when_available(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    wkhtmltopdf = tmp_path / "wkhtmltopdf.exe"
    wkhtmltopdf.write_text("binary")
    builder = XClsMakeMarkdownX(wkhtmltopdf_path=str(wkhtmltopdf))

    captured: dict[str, Any] = {}

    class FakePdfKit:
        def configuration(self, *, wkhtmltopdf: str) -> object:
            captured["wkhtmltopdf"] = wkhtmltopdf
            return {"wkhtmltopdf": wkhtmltopdf}

        def from_string(self, html_str: str, out_path: str, *, configuration: object) -> None:
            captured["html"] = html_str
            captured["out_path"] = out_path
            Path(out_path).write_text("PDF", encoding="utf-8")
            captured["config"] = configuration

    def load_pdfkit(name: str, package: str | None = None) -> Any:  # noqa: ARG001
        return FakePdfKit()

    monkeypatch.setattr(importlib, "import_module", load_pdfkit)

    out_pdf = tmp_path / "out.pdf"
    builder.to_pdf("<html><body>hi</body></html>", str(out_pdf))

    assert out_pdf.exists()
    assert out_pdf.read_text(encoding="utf-8") == "PDF"
    assert captured["wkhtmltopdf"] == str(wkhtmltopdf)
    assert captured["html"].startswith("<html>")
    assert captured["out_path"] == str(out_pdf)
