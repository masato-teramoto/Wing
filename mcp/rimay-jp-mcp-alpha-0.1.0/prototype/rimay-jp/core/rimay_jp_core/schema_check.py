"""canonical-requirement.schema.json による構造検証（validate_coreのSchema層）。"""
import json
from functools import lru_cache

from jsonschema import Draft202012Validator

from .lexicon import ROOT


@lru_cache(maxsize=1)
def _validator() -> Draft202012Validator:
    with open(ROOT / "canonical" / "canonical-requirement.schema.json", encoding="utf-8") as f:
        return Draft202012Validator(json.load(f))


def validate_schema(canonical: dict) -> list[str]:
    """Schema違反のリスト（空なら適合）。"""
    return [f"{'/'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}"
            for e in _validator().iter_errors(canonical)]
