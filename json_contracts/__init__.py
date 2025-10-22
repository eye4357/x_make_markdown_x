"""JSON contracts for x_make_markdown_x."""

from __future__ import annotations

import sys as _sys
from typing import TYPE_CHECKING

_JSON_VALUE_TYPES: list[str] = [
    "object",
    "array",
    "string",
    "number",
    "boolean",
    "null",
]

_HEADER_BLOCK: dict[str, object] = {
    "type": "object",
    "properties": {
        "kind": {"const": "header"},
        "text": {"type": "string", "minLength": 1},
        "level": {"type": "integer", "minimum": 1, "maximum": 6},
    },
    "required": ["kind", "text", "level"],
    "additionalProperties": False,
}

_PARAGRAPH_BLOCK: dict[str, object] = {
    "type": "object",
    "properties": {
        "kind": {"const": "paragraph"},
        "text": {"type": "string"},
    },
    "required": ["kind", "text"],
    "additionalProperties": False,
}

_TABLE_BLOCK: dict[str, object] = {
    "type": "object",
    "properties": {
        "kind": {"const": "table"},
        "headers": {
            "type": "array",
            "items": {"type": "string", "minLength": 1},
            "minItems": 1,
        },
        "rows": {
            "type": "array",
            "items": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 1,
            },
        },
    },
    "required": ["kind", "headers", "rows"],
    "additionalProperties": False,
}

_IMAGE_BLOCK: dict[str, object] = {
    "type": "object",
    "properties": {
        "kind": {"const": "image"},
        "alt_text": {"type": "string", "minLength": 1},
        "url": {"type": "string", "format": "uri"},
    },
    "required": ["kind", "alt_text", "url"],
    "additionalProperties": False,
}

_LIST_BLOCK: dict[str, object] = {
    "type": "object",
    "properties": {
        "kind": {"const": "list"},
        "items": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1,
        },
        "ordered": {"type": "boolean"},
    },
    "required": ["kind", "items"],
    "additionalProperties": False,
}

_RAW_BLOCK: dict[str, object] = {
    "type": "object",
    "properties": {
        "kind": {"const": "raw"},
        "text": {"type": "string"},
    },
    "required": ["kind", "text"],
    "additionalProperties": False,
}

_BLOCK_SCHEMA: dict[str, object] = {
    "oneOf": [
        _HEADER_BLOCK,
        _PARAGRAPH_BLOCK,
        _TABLE_BLOCK,
        _IMAGE_BLOCK,
        _LIST_BLOCK,
        _RAW_BLOCK,
    ]
}

_DOCUMENT_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "title": {"type": ["string", "null"], "minLength": 1},
        "subtitle": {"type": ["string", "null"], "minLength": 1},
        "generated_at": {"type": ["string", "null"], "format": "date-time"},
        "include_toc": {"type": "boolean"},
        "blocks": {
            "type": "array",
            "items": _BLOCK_SCHEMA,
            "minItems": 1,
        },
    },
    "required": ["blocks"],
    "additionalProperties": False,
}

_PDF_METADATA_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "exporter": {"type": "string", "minLength": 1},
        "succeeded": {"type": "boolean"},
        "output_path": {"type": ["string", "null"], "minLength": 1},
        "command": {
            "type": "array",
            "items": {"type": "string"},
        },
        "stdout": {"type": "string"},
        "stderr": {"type": "string"},
        "inputs": {
            "type": "object",
            "additionalProperties": {"type": "string"},
        },
        "binary_path": {"type": ["string", "null"], "minLength": 1},
        "detail": {"type": ["string", "null"]},
    },
    "required": [
        "exporter",
        "succeeded",
        "output_path",
        "command",
        "stdout",
        "stderr",
        "inputs",
        "binary_path",
    ],
    "additionalProperties": False,
}

_MARKDOWN_ARTIFACT_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "path": {"type": "string", "minLength": 1},
        "bytes": {"type": "integer", "minimum": 0},
        "pdf": _PDF_METADATA_SCHEMA,
    },
    "required": ["path", "bytes"],
    "additionalProperties": True,
}

INPUT_SCHEMA: dict[str, object] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "x_make_markdown_x input",
    "type": "object",
    "properties": {
        "command": {"const": "x_make_markdown_x"},
        "parameters": {
            "type": "object",
            "properties": {
                "output_markdown": {"type": "string", "minLength": 1},
                "wkhtmltopdf_path": {"type": ["string", "null"], "minLength": 1},
                "export_pdf": {"type": "boolean"},
                "document": _DOCUMENT_SCHEMA,
                "metadata": {
                    "type": "object",
                    "additionalProperties": {"type": _JSON_VALUE_TYPES},
                },
            },
            "required": ["output_markdown", "document"],
            "additionalProperties": False,
        },
    },
    "required": ["command", "parameters"],
    "additionalProperties": False,
}

OUTPUT_SCHEMA: dict[str, object] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "x_make_markdown_x output",
    "type": "object",
    "properties": {
        "status": {"const": "success"},
        "schema_version": {"const": "x_make_markdown_x.run/1.0"},
        "generated_at": {"type": "string", "format": "date-time"},
        "markdown": _MARKDOWN_ARTIFACT_SCHEMA,
        "summary": {
            "type": "object",
            "additionalProperties": {"type": _JSON_VALUE_TYPES},
        },
        "messages": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": ["status", "schema_version", "generated_at", "markdown"],
    "additionalProperties": False,
}

ERROR_SCHEMA: dict[str, object] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "x_make_markdown_x error",
    "type": "object",
    "properties": {
        "status": {"const": "failure"},
        "message": {"type": "string", "minLength": 1},
        "details": {
            "type": "object",
            "additionalProperties": {"type": _JSON_VALUE_TYPES},
        },
    },
    "required": ["status", "message"],
    "additionalProperties": True,
}

# Preserve legacy import path "json_contracts" for downstream tooling.
if not TYPE_CHECKING:
    _sys.modules.setdefault("json_contracts", _sys.modules[__name__])

__all__ = ["ERROR_SCHEMA", "INPUT_SCHEMA", "OUTPUT_SCHEMA"]
