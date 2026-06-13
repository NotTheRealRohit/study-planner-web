from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from research_comparison.params import PARAMS_VERSION_HASH

GENERATOR_VERSION = "0.1.0"


@dataclass(frozen=True)
class Manifest:
    seed: int
    generator_version: str
    params_version_hash: str
    archetype_mix: dict[str, int]
    n_learners: int


def build_manifest(seed: int, archetype_mix: dict[str, int], n_learners: int) -> Manifest:
    return Manifest(seed, GENERATOR_VERSION, PARAMS_VERSION_HASH, archetype_mix, n_learners)


def stamp(result: dict[str, Any], manifest: Manifest) -> dict[str, Any]:
    """Attach provenance to any result dict written to disk."""
    return {**result, "_provenance": asdict(manifest)}
