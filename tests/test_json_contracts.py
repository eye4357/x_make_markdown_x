from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import pytest
from x_make_common_x.json_contracts import validate_payload, validate_schema

from x_make_markdown_x.json_contracts import (
    ERROR_SCHEMA,
    INPUT_SCHEMA,
    OUTPUT_SCHEMA,
)
from x_make_markdown_x.x_cls_make_markdown_x import main_json

if TYPE_CHECKING:
    pass
else:
    pytest = cast("Any", pytest)

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "json_contracts"
REPORTS_DIR = Path(__file__).resolve().parents[1] / "reports"


def _load_fixture(name: str) -> dict[str, object]:
    with (FIXTURE_DIR / f"{name}.json").open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return cast("dict[str, object]", data)


@pytest.fixture(scope="module")
def sample_input() -> dict[str, object]:
    return _load_fixture("input")


@pytest.fixture(scope="module")
def sample_output() -> dict[str, object]:
    return _load_fixture("output")


@pytest.fixture(scope="module")
def sample_error() -> dict[str, object]:
    return _load_fixture("error")


def test_schemas_are_valid() -> None:
    for schema in (INPUT_SCHEMA, OUTPUT_SCHEMA, ERROR_SCHEMA):
        validate_schema(schema)


def test_sample_payloads_match_schema(
    sample_input: dict[str, object],
    sample_output: dict[str, object],
    sample_error: dict[str, object],
) -> None:
    validate_payload(sample_input, INPUT_SCHEMA)
    validate_payload(sample_output, OUTPUT_SCHEMA)
    validate_payload(sample_error, ERROR_SCHEMA)


def test_existing_reports_align_with_schema() -> None:
    if not REPORTS_DIR.exists():
        pytest.skip("no reports directory for markdown tool")
    report_files = sorted(REPORTS_DIR.glob("x_make_markdown_x_run_*.json"))
    if not report_files:
        pytest.skip("no markdown run reports to validate")
    for report_file in report_files:
        with report_file.open("r", encoding="utf-8") as handle:
            payload = cast("dict[str, object]", json.load(handle))
        validate_payload(payload, OUTPUT_SCHEMA)


def test_main_json_executes_happy_path(sample_input: dict[str, object]) -> None:
    result = main_json(sample_input)
    validate_payload(result, OUTPUT_SCHEMA)
    status_value = result.get("status")
    assert isinstance(status_value, str)
    assert status_value == "success"


def test_main_json_returns_error_for_invalid_payload(
    sample_input: dict[str, object],
) -> None:
    invalid = copy.deepcopy(sample_input)
    parameters = invalid.get("parameters")
    if isinstance(parameters, dict):
        parameters.pop("output_markdown", None)
    result = main_json(invalid)
    validate_payload(result, ERROR_SCHEMA)
    status_value = result.get("status")
    assert isinstance(status_value, str)
    assert status_value == "failure"
