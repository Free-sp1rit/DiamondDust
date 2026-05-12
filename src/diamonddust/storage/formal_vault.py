"""Read-only formal vault safety checks."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
from pathlib import Path, PurePosixPath
from types import MappingProxyType
from typing import Mapping

from diamonddust.application.patch_review import (
    PatchReviewError,
    inspect_patch_diff,
    validate_patch_review_safety,
)
from diamonddust.domain import KnowledgePatch, PatchOperationType
from diamonddust.storage.candidate_markdown import render_candidate_markdown


FORMAL_VAULT_DIRS = (
    "00-inbox",
    "10-sources",
    "20-questions",
    "30-evidence",
    "40-concepts",
    "50-synthesis",
    "60-maps",
    "70-publications",
    "80-assets",
    "90-archive",
)


class FormalVaultConflictType(StrEnum):
    TARGET_PATH_EXISTS = "target_path_exists"
    UNIT_ID_EXISTS = "unit_id_exists"
    DUPLICATE_PATCH_TARGET_PATH = "duplicate_patch_target_path"
    DUPLICATE_PATCH_UNIT_ID = "duplicate_patch_unit_id"


class FormalVaultConflictError(ValueError):
    """Raised when a formal vault conflict check cannot be performed safely."""


class FormalVaultApplyPlanError(ValueError):
    """Raised when a formal vault dry-run apply plan cannot be created safely."""


@dataclass(frozen=True)
class FormalVaultConflict:
    conflict_type: FormalVaultConflictType
    operation_index: int
    message: str
    unit_id: str | None = None
    target_path: str | None = None
    existing_path: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.conflict_type, FormalVaultConflictType):
            raise FormalVaultConflictError(
                "conflict_type must be a FormalVaultConflictType"
            )
        _require_positive_int("operation_index", self.operation_index)
        _require_non_empty("message", self.message)
        _require_optional_str("unit_id", self.unit_id)
        _require_optional_str("target_path", self.target_path)
        _require_optional_str("existing_path", self.existing_path)


@dataclass(frozen=True)
class FormalVaultConflictReport:
    patch_id: str
    vault_root: str
    conflicts: tuple[FormalVaultConflict, ...]
    checked_target_paths: tuple[str, ...]
    checked_unit_ids: tuple[str, ...]
    existing_unit_paths: Mapping[str, str]

    def __post_init__(self) -> None:
        _require_non_empty("patch_id", self.patch_id)
        _require_non_empty("vault_root", self.vault_root)
        _require_tuple("conflicts", self.conflicts, FormalVaultConflict)
        _require_str_tuple("checked_target_paths", self.checked_target_paths)
        _require_str_tuple("checked_unit_ids", self.checked_unit_ids)
        _require_str_mapping("existing_unit_paths", self.existing_unit_paths)

    @property
    def formal_write_safe(self) -> bool:
        return not self.conflicts


@dataclass(frozen=True)
class FormalVaultApplyPlanFile:
    operation_index: int
    unit_id: str
    target_path: str
    content: str
    content_hash: str
    rollback_step: str

    def __post_init__(self) -> None:
        _require_positive_int("operation_index", self.operation_index)
        _require_non_empty("unit_id", self.unit_id)
        _require_non_empty("target_path", self.target_path)
        _require_non_empty("content", self.content)
        _require_non_empty("content_hash", self.content_hash)
        _require_non_empty("rollback_step", self.rollback_step)


@dataclass(frozen=True)
class FormalVaultApplyPlan:
    patch_id: str
    vault_root: str
    files: tuple[FormalVaultApplyPlanFile, ...]
    rollback_steps: tuple[str, ...]
    conflict_report: FormalVaultConflictReport
    formal_write_performed: bool
    requires_user_review: bool

    def __post_init__(self) -> None:
        _require_non_empty("patch_id", self.patch_id)
        _require_non_empty("vault_root", self.vault_root)
        _require_tuple("files", self.files, FormalVaultApplyPlanFile)
        _require_str_tuple("rollback_steps", self.rollback_steps)
        if not isinstance(self.conflict_report, FormalVaultConflictReport):
            raise FormalVaultApplyPlanError(
                "conflict_report must be a FormalVaultConflictReport"
            )
        if self.conflict_report.patch_id != self.patch_id:
            raise FormalVaultApplyPlanError("conflict_report patch_id must match plan patch_id")
        if self.formal_write_performed is not False:
            raise FormalVaultApplyPlanError("formal apply plans must not perform writes")
        if self.requires_user_review is not True:
            raise FormalVaultApplyPlanError("formal apply plans require user review")

    @property
    def file_count(self) -> int:
        return len(self.files)


def check_formal_vault_conflicts(
    patch: KnowledgePatch,
    *,
    vault_root: str | Path,
) -> FormalVaultConflictReport:
    """Check whether a patch can be handed to future formal apply without collisions."""

    try:
        validate_patch_review_safety(patch)
    except PatchReviewError as exc:
        raise FormalVaultConflictError("patch is not safe for formal preflight") from exc

    root = Path(vault_root)
    root_resolved = root.resolve()
    existing_unit_paths = _scan_existing_unit_paths(root)
    conflicts: list[FormalVaultConflict] = []
    checked_target_paths: list[str] = []
    checked_unit_ids: list[str] = []
    seen_target_paths: dict[str, int] = {}
    seen_unit_ids: dict[str, int] = {}

    for operation_index, operation in enumerate(patch.operations, start=1):
        if operation.operation_type != PatchOperationType.CREATE_NOTE:
            continue
        if operation.unit is None or operation.target_path is None:
            raise FormalVaultConflictError("create_note operation is missing unit or target_path")

        target_path = operation.target_path
        unit_id = operation.unit.id
        checked_target_paths.append(target_path)
        checked_unit_ids.append(unit_id)

        if target_path in seen_target_paths:
            conflicts.append(
                FormalVaultConflict(
                    conflict_type=FormalVaultConflictType.DUPLICATE_PATCH_TARGET_PATH,
                    operation_index=operation_index,
                    target_path=target_path,
                    message=(
                        f"target path duplicates operation "
                        f"{seen_target_paths[target_path]}"
                    ),
                )
            )
        else:
            seen_target_paths[target_path] = operation_index

        if unit_id in seen_unit_ids:
            conflicts.append(
                FormalVaultConflict(
                    conflict_type=FormalVaultConflictType.DUPLICATE_PATCH_UNIT_ID,
                    operation_index=operation_index,
                    unit_id=unit_id,
                    target_path=target_path,
                    message=f"unit id duplicates operation {seen_unit_ids[unit_id]}",
                )
            )
        else:
            seen_unit_ids[unit_id] = operation_index

        existing_target = _safe_vault_path(root_resolved, target_path)
        if existing_target.exists():
            conflicts.append(
                FormalVaultConflict(
                    conflict_type=FormalVaultConflictType.TARGET_PATH_EXISTS,
                    operation_index=operation_index,
                    unit_id=unit_id,
                    target_path=target_path,
                    existing_path=target_path,
                    message="target path already exists in formal vault",
                )
            )

        existing_unit_path = existing_unit_paths.get(unit_id)
        if existing_unit_path is not None:
            conflicts.append(
                FormalVaultConflict(
                    conflict_type=FormalVaultConflictType.UNIT_ID_EXISTS,
                    operation_index=operation_index,
                    unit_id=unit_id,
                    target_path=target_path,
                    existing_path=existing_unit_path,
                    message="unit id already exists in formal vault",
                )
            )

    return FormalVaultConflictReport(
        patch_id=patch.patch_id,
        vault_root=root.as_posix(),
        conflicts=tuple(conflicts),
        checked_target_paths=tuple(checked_target_paths),
        checked_unit_ids=tuple(checked_unit_ids),
        existing_unit_paths=MappingProxyType(dict(existing_unit_paths)),
    )


def plan_formal_vault_apply(
    patch: KnowledgePatch,
    *,
    vault_root: str | Path,
    conflict_report: FormalVaultConflictReport | None = None,
) -> FormalVaultApplyPlan:
    """Create a dry-run formal apply plan without writing vault files."""

    report = conflict_report or check_formal_vault_conflicts(patch, vault_root=vault_root)
    if report.patch_id != patch.patch_id:
        raise FormalVaultApplyPlanError("conflict report patch_id does not match patch")
    if not report.formal_write_safe:
        raise FormalVaultApplyPlanError("cannot plan formal apply with unresolved conflicts")

    candidate_export = render_candidate_markdown(patch)
    target_paths = tuple(file.target_path for file in candidate_export.files)
    if target_paths != report.checked_target_paths:
        raise FormalVaultApplyPlanError("conflict report target paths do not match patch")

    operation_indices = _create_note_operation_indices(patch)
    rollback_by_target = _rollback_steps_by_target(patch)
    planned_unit_ids = frozenset(file.unit_id for file in candidate_export.files)
    _require_plannable_relation_operations(patch, planned_unit_ids)

    files: list[FormalVaultApplyPlanFile] = []
    for file in candidate_export.files:
        content = _formal_note_content(file.content)
        files.append(
            FormalVaultApplyPlanFile(
                operation_index=operation_indices[file.target_path],
                unit_id=file.unit_id,
                target_path=file.target_path,
                content=content,
                content_hash=_content_hash(content),
                rollback_step=rollback_by_target[file.target_path],
            )
        )
    diff = inspect_patch_diff(patch)
    return FormalVaultApplyPlan(
        patch_id=patch.patch_id,
        vault_root=Path(vault_root).as_posix(),
        files=tuple(files),
        rollback_steps=diff.rollback_steps,
        conflict_report=report,
        formal_write_performed=False,
        requires_user_review=patch.requires_user_review,
    )


def _scan_existing_unit_paths(root: Path) -> dict[str, str]:
    unit_paths: dict[str, str] = {}
    for formal_dir in FORMAL_VAULT_DIRS:
        directory = root / formal_dir
        if not directory.exists():
            continue
        for path in directory.rglob("*.md"):
            if not path.is_file():
                continue
            unit_id = _frontmatter_id(path)
            if unit_id and unit_id not in unit_paths:
                unit_paths[unit_id] = path.relative_to(root).as_posix()
    return unit_paths


def _create_note_operation_indices(patch: KnowledgePatch) -> dict[str, int]:
    indices: dict[str, int] = {}
    for index, operation in enumerate(patch.operations, start=1):
        if operation.operation_type != PatchOperationType.CREATE_NOTE:
            continue
        if operation.target_path is None:
            raise FormalVaultApplyPlanError("create_note operation is missing target_path")
        indices[operation.target_path] = index
    return indices


def _rollback_steps_by_target(patch: KnowledgePatch) -> dict[str, str]:
    diff = inspect_patch_diff(patch)
    rollback_steps: dict[str, str] = {}
    for line, rollback_step in zip(diff.lines, diff.rollback_steps, strict=True):
        if line.operation_type == PatchOperationType.CREATE_NOTE and line.target_path:
            rollback_steps[line.target_path] = rollback_step
    return rollback_steps


def _require_plannable_relation_operations(
    patch: KnowledgePatch,
    planned_unit_ids: frozenset[str],
) -> None:
    for operation in patch.operations:
        if operation.operation_type != PatchOperationType.ADD_RELATION:
            continue
        if operation.relation is None:
            raise FormalVaultApplyPlanError("add_relation operation is missing relation")
        if operation.relation.source_id not in planned_unit_ids:
            raise FormalVaultApplyPlanError(
                "relation updates for existing formal notes cannot be planned yet"
            )


def _formal_note_content(candidate_content: str) -> str:
    lines = candidate_content.splitlines()
    if not lines or lines[0].strip() != "---":
        raise FormalVaultApplyPlanError("candidate note content must have frontmatter")
    try:
        frontmatter_end = next(
            index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---"
        )
    except StopIteration as exc:
        raise FormalVaultApplyPlanError("candidate note frontmatter is not closed") from exc

    frontmatter: list[str] = []
    skipping_candidate_block = False
    for line in lines[1:frontmatter_end]:
        stripped = line.strip()
        if skipping_candidate_block:
            if line.startswith((" ", "\t")) or not stripped:
                continue
            skipping_candidate_block = False
        if stripped.startswith("artifact_type:"):
            continue
        if stripped.startswith("artifact_schema_version:"):
            continue
        if stripped == "candidate:":
            skipping_candidate_block = True
            continue
        frontmatter.append(line)

    formal_lines = ["---", *frontmatter, "---", *lines[frontmatter_end + 1 :]]
    return "\n".join(formal_lines).rstrip() + "\n"


def _content_hash(content: str) -> str:
    return "sha256:" + sha256(content.encode("utf-8")).hexdigest()


def _frontmatter_id(path: Path) -> str | None:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise FormalVaultConflictError(f"cannot read formal note: {path}") from exc

    if not lines or lines[0].strip() != "---":
        return None

    for line in lines[1:]:
        stripped = line.strip()
        if stripped == "---":
            return None
        key, separator, value = stripped.partition(":")
        if separator == ":" and key.strip() == "id":
            return _strip_quotes(value.strip()) or None
    return None


def _safe_vault_path(root_resolved: Path, relative_path: str) -> Path:
    _validate_relative_path(relative_path)
    output_path = (root_resolved / PurePosixPath(relative_path)).resolve()
    if output_path != root_resolved and root_resolved not in output_path.parents:
        raise FormalVaultConflictError("target path must stay inside vault root")
    return output_path


def _validate_relative_path(relative_path: str) -> None:
    _require_non_empty("target_path", relative_path)
    pure_path = PurePosixPath(relative_path)
    if pure_path.is_absolute():
        raise FormalVaultConflictError("target_path must be relative")
    if ".." in pure_path.parts or any(part == "" for part in pure_path.parts):
        raise FormalVaultConflictError("target_path must not contain traversal")


def _strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _require_non_empty(name: str, value: str | None) -> None:
    if not isinstance(value, str) or not value.strip():
        raise FormalVaultConflictError(f"{name} must be a non-empty string")


def _require_optional_str(name: str, value: str | None) -> None:
    if value is not None:
        _require_non_empty(name, value)


def _require_positive_int(name: str, value: object) -> None:
    if not isinstance(value, int) or value < 1:
        raise FormalVaultConflictError(f"{name} must be a positive integer")


def _require_tuple(name: str, value: object, item_type: type) -> None:
    if not isinstance(value, tuple):
        raise FormalVaultConflictError(f"{name} must be a tuple")
    if not all(isinstance(item, item_type) for item in value):
        raise FormalVaultConflictError(f"{name} must contain only {item_type.__name__}")


def _require_str_tuple(name: str, value: object) -> None:
    if not isinstance(value, tuple):
        raise FormalVaultConflictError(f"{name} must be a tuple")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise FormalVaultConflictError(f"{name} must contain non-empty strings")


def _require_str_mapping(name: str, value: object) -> None:
    if not isinstance(value, Mapping):
        raise FormalVaultConflictError(f"{name} must be a mapping")
    if not all(
        isinstance(key, str)
        and key.strip()
        and isinstance(item, str)
        and item.strip()
        for key, item in value.items()
    ):
        raise FormalVaultConflictError(f"{name} must map non-empty strings")
