"""Markdown document builder with optional PDF generation.

Features (redrabbit):
- Headers with hierarchical numbering and TOC entries
- Paragraphs, tables, images, lists
- Optional PDF export using wkhtmltopdf via pdfkit
"""

from __future__ import annotations

import importlib
import logging as _logging
import os as _os
import sys as _sys
from contextlib import suppress
from pathlib import Path
from typing import Protocol, TypeVar, cast

from x_make_common_x.exporters import (
    CommandRunner,
    ExportResult,
    export_html_to_pdf,
    export_markdown_to_pdf,
)

_LOGGER = _logging.getLogger("x_make")


_T = TypeVar("_T")


class BaseMake:
    @classmethod
    def get_env(cls, name: str, default: _T | None = None) -> str | _T | None:
        value = _os.environ.get(name)
        if value is None:
            return default
        return value

    @classmethod
    def get_env_bool(cls, name: str, *, default: bool = False) -> bool:
        v = cls.get_env(name)
        if v is None:
            return default
        return str(v).lower() in ("1", "true", "yes")


def _info(*args: object) -> None:
    msg = " ".join(str(a) for a in args)
    with suppress(Exception):
        _LOGGER.info("%s", msg)
    if not _emit_print(msg):
        with suppress(Exception):
            _sys.stdout.write(msg + "\n")


def _emit_print(msg: str) -> bool:
    try:
        print(msg)
    except (OSError, RuntimeError):
        return False
    return True


def _ctx_is_verbose(ctx: object | None) -> bool:
    """Return True if the context exposes a truthy `verbose` attribute."""
    attr = cast("object", getattr(ctx, "verbose", False))
    if isinstance(attr, bool):
        return attr
    return bool(attr)


# red rabbit 2025_0902_0944


class MarkdownModule(Protocol):
    def markdown(self, text: str) -> str: ...


class XClsMakeMarkdownX(BaseMake):
    """A simple markdown builder with an optional PDF export step."""

    # Environment variable to override wkhtmltopdf path
    WKHTMLTOPDF_ENV_VAR: str = "X_WKHTMLTOPDF_PATH"
    # Default Windows install path (used if present and env var not set)
    DEFAULT_WKHTMLTOPDF_PATH: str = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    HEADER_MAX_LEVEL: int = 6

    def __init__(
        self,
        wkhtmltopdf_path: str | None = None,
        ctx: object | None = None,
        *,
        runner: CommandRunner | None = None,
    ) -> None:
        """Accept optional ctx for future orchestrator integration.

        Backwards compatible: callers that don't pass ctx behave as before.
        If ctx has a truthy `verbose` attribute this class will emit small
        informational messages to stdout to help debugging in orchestrated runs.
        """
        self._ctx = ctx
        self.elements: list[str] = []
        self.toc: list[str] = []
        self.section_counter: list[int] = []
        self._runner: CommandRunner | None = runner
        self._last_export_result: ExportResult | None = None
        resolved_path: str | None
        if wkhtmltopdf_path is None:
            env_value = self.get_env(self.WKHTMLTOPDF_ENV_VAR)
            env_candidate = Path(env_value) if isinstance(env_value, str) else None
            default_candidate = Path(self.DEFAULT_WKHTMLTOPDF_PATH)
            if env_candidate and env_candidate.is_file():
                resolved_path = str(env_candidate)
            elif default_candidate.is_file():
                resolved_path = str(default_candidate)
            else:
                resolved_path = None
        else:
            resolved_path = wkhtmltopdf_path
        self.wkhtmltopdf_path: str | None = resolved_path

    def add_header(self, text: str, level: int = 1) -> None:
        """Add a header with hierarchical numbering and TOC update."""
        if level > self.HEADER_MAX_LEVEL:
            message = f"Header level cannot exceed {self.HEADER_MAX_LEVEL}."
            raise ValueError(message)

        # Update section counter
        while len(self.section_counter) < level:
            self.section_counter.append(0)
        self.section_counter = self.section_counter[:level]
        self.section_counter[-1] += 1

        # Generate section index
        section_index = ".".join(map(str, self.section_counter))
        header_text = f"{section_index} {text}"

        # Add header to elements and TOC
        self.elements.append(f"{'#' * level} {header_text}\n")
        self.toc.append(
            f"{'  ' * (level - 1)}- [{header_text}]"
            f"(#{header_text.lower().replace(' ', '-').replace('.', '')})"
        )

    def add_paragraph(self, text: str) -> None:
        """Add a paragraph to the markdown document."""
        self.elements.append(f"{text}\n\n")

    def add_table(self, headers: list[str], rows: list[list[str]]) -> None:
        """Add a table to the markdown document."""
        header_row = " | ".join(headers)
        separator_row = " | ".join(["---"] * len(headers))
        data_rows = "\n".join([" | ".join(row) for row in rows])
        self.elements.append(f"{header_row}\n{separator_row}\n{data_rows}\n\n")

    def add_image(self, alt_text: str, url: str) -> None:
        """Add an image to the markdown document."""
        self.elements.append(f"![{alt_text}]({url})\n\n")

    def add_list(self, items: list[str], *, ordered: bool = False) -> None:
        """Add a list to the markdown document."""
        if ordered:
            self.elements.extend([f"{i + 1}. {item}" for i, item in enumerate(items)])
        else:
            self.elements.extend([f"- {item}" for item in items])
        self.elements.append("\n")

    def add_toc(self) -> None:
        """Add a table of contents (TOC) to the top of the document."""
        self.elements = ["\n".join(self.toc) + "\n\n", *self.elements]

    def to_html(self, text: str) -> str:
        """Convert markdown text to HTML using python-markdown."""
        try:
            markdown_module = cast(
                "MarkdownModule",
                importlib.import_module("markdown"),
            )
            return markdown_module.markdown(text or "")
        except (ModuleNotFoundError, AttributeError, TypeError, ValueError):
            # Minimal fallback: return plain text wrapped in <pre> to preserve content
            escaped = (text or "").replace("<", "&lt;").replace(">", "&gt;")
            return f"<pre>{escaped}</pre>"

    def to_pdf(self, html_str: str, out_path: str) -> None:
        """Render HTML to PDF using the shared exporter pipeline."""
        if not self.wkhtmltopdf_path:
            message = (
                f"wkhtmltopdf not found (set {self.WKHTMLTOPDF_ENV_VAR}"
                " or install at default path)"
            )
            raise RuntimeError(message)
        pdf_path = Path(out_path)
        export_dir = pdf_path.parent
        result: ExportResult = export_html_to_pdf(
            html_str,
            output_dir=export_dir,
            stem=pdf_path.stem,
            wkhtmltopdf_path=self.wkhtmltopdf_path,
            runner=self._runner,
            keep_html=False,
        )
        self._last_export_result = result
        if not result.succeeded:
            detail = result.detail or "wkhtmltopdf execution failed"
            raise RuntimeError(detail)

    def generate(self, output_file: str = "example.md") -> str:
        """Generate markdown and save it to a file; optionally render a PDF."""
        markdown_content = "".join(self.elements)
        output_path = Path(output_file)
        output_path.write_text(markdown_content, encoding="utf-8")

        if _ctx_is_verbose(self._ctx):
            _info(f"[markdown] wrote markdown to {output_file}")

        # Convert to PDF if wkhtmltopdf_path is configured
        if self.wkhtmltopdf_path:
            result = export_markdown_to_pdf(
                markdown_content,
                output_dir=output_path.parent,
                stem=output_path.stem,
                wkhtmltopdf_path=self.wkhtmltopdf_path,
                runner=self._runner,
                keep_html=False,
            )
            self._last_export_result = result
            if not result.succeeded:
                detail = result.detail or "Failed to render markdown to PDF"
                raise RuntimeError(detail)
        else:
            self._last_export_result = None

        return markdown_content

    def get_last_export_result(self) -> ExportResult | None:
        return self._last_export_result


if __name__ == "__main__":
    # Rich example: Alice in Wonderland sampler -> Markdown + PDF beside this file
    base_dir = Path(__file__).resolve().parent
    out_dir = base_dir / "out_docs"
    out_dir.mkdir(parents=True, exist_ok=True)

    class _Ctx:
        verbose = True

    maker = XClsMakeMarkdownX(ctx=_Ctx())

    maker.add_header("Alice's Adventures in Wonderland", 1)
    maker.add_paragraph("Public-domain sampler inspired by Lewis Carroll (1865).")

    maker.add_header("Down the Rabbit-Hole", 2)
    maker.add_paragraph(
        "Alice was beginning to get very tired of sitting by her sister on the bank, "
        "and of having nothing to do: once or twice she had peeped into the book her "
        "sister was reading, but it had no pictures or conversations in it..."
    )

    maker.add_list(
        [
            "Sees a White Rabbit with a pocket watch",
            "Follows it down the rabbit-hole",
            "Finds a hall with many locked doors",
        ],
        ordered=True,
    )

    maker.add_header("A Curious Bottle", 2)
    maker.add_paragraph(
        "On a little table she found a bottle, on it was a paper label, "
        'with the words "DRINK ME" beautifully printed on it.'
    )

    maker.add_table(
        ["Item", "Effect"],
        [
            ["Cake (EAT ME)", "Grows tall"],
            ["Fan", "Shrinks"],
            ["Key", "Opens small door"],
        ],
    )

    maker.add_image(
        "Alice meets the White Rabbit (Tenniel, public domain)",
        "https://upload.wikimedia.org/wikipedia/commons/6/6f/Alice_par_John_Tenniel_02.png",
    )

    maker.add_header("Conclusion", 2)
    maker.add_paragraph(
        "This document demonstrates headers with numbering and TOC, "
        "lists, tables, and images."
    )

    # Insert TOC at the top after all headers were added
    maker.add_toc()

    output_md = out_dir / "alice_in_wonderland.md"
    maker.generate(output_file=str(output_md))

    if not maker.wkhtmltopdf_path:
        _info(
            "[markdown] PDF not generated: set "
            f"{XClsMakeMarkdownX.WKHTMLTOPDF_ENV_VAR} to wkhtmltopdf.exe"
        )


x_cls_make_markdown_x = XClsMakeMarkdownX
