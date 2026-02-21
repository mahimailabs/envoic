from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum, StrEnum
from pathlib import Path
from typing import Any, Literal, TypedDict, cast, overload


class EnvType(StrEnum):
    VENV = "venv"
    CONDA = "conda"
    DOTENV_DIR = "dotenv_dir"
    UNKNOWN = "unknown"


class SafetyLevel(StrEnum):
    ALWAYS_SAFE = "always_safe"
    USUALLY_SAFE = "usually_safe"
    CAREFUL = "careful"


class ArtifactCategory(StrEnum):
    BYTECODE_CACHE = "bytecode_cache"
    TOOL_CACHE = "tool_cache"
    TEST_ENV = "test_env"
    BUILD_ARTIFACT = "build_artifact"
    COVERAGE_NOTEBOOK = "coverage_notebook"


@dataclass(slots=True)
class EnvInfo:
    path: Path
    env_type: EnvType
    python_version: str | None = None
    size_bytes: int | None = None
    created: datetime | None = None
    modified: datetime | None = None
    package_count: int | None = None
    is_stale: bool = False
    has_pyvenv_cfg: bool = False
    signals: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ScanResult:
    scan_path: Path
    scan_depth: int
    duration_seconds: float
    environments: list[EnvInfo]
    total_size_bytes: int
    hostname: str
    timestamp: datetime
    artifacts: list[ArtifactInfo] = field(default_factory=list)
    artifact_summary: list[ArtifactSummary] = field(default_factory=list)


@dataclass(slots=True)
class ArtifactInfo:
    path: Path
    category: ArtifactCategory
    safety: SafetyLevel
    size_bytes: int | None = None
    pattern_matched: str = ""


@dataclass(slots=True)
class ArtifactSummary:
    """Rolled-up summary per pattern/category."""

    category: ArtifactCategory
    safety: SafetyLevel
    count: int
    total_size_bytes: int
    items: list[ArtifactInfo]
    pattern: str = ""


EnvTypeValue = Literal["venv", "conda", "dotenv_dir", "unknown"]
SafetyLevelValue = Literal["always_safe", "usually_safe", "careful"]
ArtifactCategoryValue = Literal[
    "bytecode_cache",
    "tool_cache",
    "test_env",
    "build_artifact",
    "coverage_notebook",
]


class EnvInfoDict(TypedDict):
    path: str
    env_type: EnvTypeValue
    python_version: str | None
    size_bytes: int | None
    created: str | None
    modified: str | None
    package_count: int | None
    is_stale: bool
    has_pyvenv_cfg: bool
    signals: list[str]


class ArtifactInfoDict(TypedDict):
    path: str
    category: ArtifactCategoryValue
    safety: SafetyLevelValue
    size_bytes: int | None
    pattern_matched: str


class ArtifactSummaryDict(TypedDict):
    category: ArtifactCategoryValue
    safety: SafetyLevelValue
    count: int
    total_size_bytes: int
    items: list[ArtifactInfoDict]
    pattern: str


class ScanResultDict(TypedDict):
    scan_path: str
    scan_depth: int
    duration_seconds: float
    environments: list[EnvInfoDict]
    total_size_bytes: int
    hostname: str
    timestamp: str
    artifacts: list[ArtifactInfoDict]
    artifact_summary: list[ArtifactSummaryDict]


def _serialize_value(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, list):
        return [_serialize_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize_value(inner) for key, inner in value.items()}
    return value


def _to_serializable_dict(
    data: ScanResult | EnvInfo | ArtifactInfo | ArtifactSummary,
) -> dict[str, Any]:
    return cast(dict[str, Any], _serialize_value(asdict(data)))


@overload
def to_serializable_dict(data: EnvInfo) -> EnvInfoDict: ...


@overload
def to_serializable_dict(data: ScanResult) -> ScanResultDict: ...


@overload
def to_serializable_dict(data: ArtifactInfo) -> ArtifactInfoDict: ...


@overload
def to_serializable_dict(data: ArtifactSummary) -> ArtifactSummaryDict: ...


def to_serializable_dict(
    data: EnvInfo | ScanResult | ArtifactInfo | ArtifactSummary,
) -> EnvInfoDict | ScanResultDict | ArtifactInfoDict | ArtifactSummaryDict:
    serialized = _to_serializable_dict(data)
    return cast(
        EnvInfoDict | ScanResultDict | ArtifactInfoDict | ArtifactSummaryDict,
        serialized,
    )
