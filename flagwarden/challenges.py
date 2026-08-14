from __future__ import annotations

from pathlib import Path
from typing import Literal
import yaml
from pydantic import BaseModel, Field, field_validator


class Hint(BaseModel):
    cost: int = Field(ge=0)
    text: str = Field(min_length=1, max_length=800)


class SafetySpec(BaseModel):
    scope: Literal["lab_only", "ctf_only", "concept_only"] = "ctf_only"
    notes: str = "Use only in authorized educational environments."


class Debrief(BaseModel):
    concept: str
    why_it_works: str
    remediation: str
    references: list[str] = []


class VerifierConfig(BaseModel):
    type: Literal["exact_hmac", "dynamic_hmac", "quiz_choice"]
    digest: str | None = None
    choices: list[str] = []
    correct_index: int | None = None
    flag_prefix: str = "FLAGWARDEN"

    @field_validator("digest")
    @classmethod
    def validate_digest(cls, value):
        if value is not None and len(value) != 64:
            raise ValueError("HMAC digest must be a 64-character SHA-256 hex string")
        return value


class Challenge(BaseModel):
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]{2,127}$")
    title: str = Field(min_length=3, max_length=160)
    category: str
    difficulty: Literal["easy", "medium", "hard"]
    status: Literal["draft", "review", "published", "deprecated"] = "published"
    version: str = "1.0.0"
    author: str
    reviewer: str | None = None
    learning_objectives: list[str] = Field(min_length=1)
    skills: list[str] = Field(min_length=1)
    points: int = Field(gt=0, le=5000)
    hints: list[Hint] = []
    verifier: VerifierConfig
    safety: SafetySpec = SafetySpec()
    debrief: Debrief

    @field_validator("hints")
    @classmethod
    def hint_costs_reasonable(cls, hints):
        if any(h.cost < 0 for h in hints):
            raise ValueError("Hint costs cannot be negative")
        return hints


class PackMetadata(BaseModel):
    id: str
    name: str
    version: str
    description: str
    author: str


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a YAML mapping")
    return data


def load_challenge(path: Path) -> Challenge:
    return Challenge.model_validate(load_yaml(path))


def validate_pack(pack_dir: str | Path) -> tuple[PackMetadata, list[Challenge]]:
    pack_dir = Path(pack_dir)
    metadata = PackMetadata.model_validate(load_yaml(pack_dir / "pack.yaml"))
    challenges = []
    seen = set()
    for path in sorted((pack_dir / "challenges").glob("*.yaml")):
        challenge = load_challenge(path)
        if challenge.id in seen:
            raise ValueError(f"Duplicate challenge id: {challenge.id}")
        seen.add(challenge.id)
        if challenge.verifier.type == "exact_hmac" and not challenge.verifier.digest:
            raise ValueError(f"{challenge.id}: exact_hmac requires verifier.digest")
        if challenge.verifier.type == "quiz_choice":
            if not challenge.verifier.choices or challenge.verifier.correct_index is None:
                raise ValueError(f"{challenge.id}: quiz_choice requires choices and correct_index")
            if not 0 <= challenge.verifier.correct_index < len(challenge.verifier.choices):
                raise ValueError(f"{challenge.id}: correct_index out of range")
        challenges.append(challenge)
    if not challenges:
        raise ValueError("Challenge pack contains no challenge YAML files")
    return metadata, challenges


def load_all_packs(root: str | Path) -> dict[str, Challenge]:
    result: dict[str, Challenge] = {}
    root = Path(root)
    if not root.exists():
        return result
    for pack in sorted(p for p in root.iterdir() if p.is_dir() and (p / "pack.yaml").exists()):
        _, challenges = validate_pack(pack)
        for challenge in challenges:
            if challenge.status != "published":
                continue
            if challenge.id in result:
                raise ValueError(f"Duplicate challenge id across packs: {challenge.id}")
            result[challenge.id] = challenge
    return result
