from __future__ import annotations

import asyncio
import json
import math
from pathlib import Path
from typing import Any

import httpx
import pytest

from app.main import app

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "pillar-a"
TOLERANCE = 1e-6

ENDPOINT_BY_FN = {
    "computeCalibration": "/v1/calibration",
    "getPromptDetail": "/v1/calibration/prompt-detail",
    "computeProgress": "/v1/progress",
    "generateRoadmap": "/v1/roadmap/generate",
    "regenerateRoadmap": "/v1/roadmap/regenerate",
}


def _fixture_cases() -> list[tuple[str, Path, str]]:
    cases: list[tuple[str, Path, str]] = []
    for area in ["progress", "roadmap"]:
        for input_path in sorted((FIXTURE_ROOT / area).glob("*.input.json")):
            payload = json.loads(input_path.read_text())
            endpoint = ENDPOINT_BY_FN.get(payload["fn"])
            if endpoint is None:
                continue
            cases.append((f"{area}/{input_path.stem.replace('.input', '')}", input_path, endpoint))
    return cases


async def _post_json(endpoint: str, payload: dict[str, Any]) -> httpx.Response:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.post(endpoint, json=payload)


def _assert_close(actual: Any, expected: Any, path: str = "") -> None:
    if actual is None and expected is None:
        return
    if isinstance(expected, bool):
        assert actual == expected, f"{path}: {actual!r} != {expected!r}"
        return
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        if isinstance(expected, int) and isinstance(actual, int) and not isinstance(
            expected, bool
        ):
            assert actual == expected, f"{path}: {actual!r} != {expected!r}"
            return
        if not math.isclose(float(actual), float(expected), rel_tol=TOLERANCE, abs_tol=TOLERANCE):
            raise AssertionError(f"{path}: {actual!r} != {expected!r} (tol={TOLERANCE})")
        return
    if isinstance(expected, str):
        assert actual == expected, f"{path}: {actual!r} != {expected!r}"
        return
    if isinstance(expected, list):
        assert isinstance(actual, list), f"{path}: expected list, got {type(actual)}"
        assert len(actual) == len(expected), f"{path}: length {len(actual)} != {len(expected)}"
        for i, (a, e) in enumerate(zip(actual, expected, strict=True)):
            _assert_close(a, e, f"{path}[{i}]")
        return
    if isinstance(expected, dict):
        assert isinstance(actual, dict), f"{path}: expected dict, got {type(actual)}"
        assert set(actual.keys()) == set(expected.keys()), (
            f"{path}: keys {sorted(actual.keys())!r} != {sorted(expected.keys())!r}"
        )
        for key in expected:
            _assert_close(actual[key], expected[key], f"{path}.{key}")
        return
    assert actual == expected, f"{path}: {actual!r} != {expected!r}"


@pytest.mark.parametrize(("case_name", "input_path", "endpoint"), _fixture_cases())
def test_v1_endpoint_matches_golden_fixture(case_name: str, input_path: Path, endpoint: str) -> None:
    payload = json.loads(input_path.read_text())
    expected_path = input_path.with_name(input_path.name.replace(".input.json", ".expected.json"))
    expected = json.loads(expected_path.read_text())

    body = dict(payload)
    body.pop("fn")

    response = asyncio.run(_post_json(endpoint, body))

    assert response.status_code == 200, response.text
    _assert_close(response.json(), expected, case_name)
