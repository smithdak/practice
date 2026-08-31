#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover - environment diagnostic
    raise SystemExit("PyYAML is required: install it before running this validator") from exc


DEFAULT_ROOT = Path(__file__).resolve().parents[2]
SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
PLACEHOLDER_RE = re.compile(r"\b(TODO|TBD|PLACEHOLDER|LOREM IPSUM)\b", re.IGNORECASE)
CAPABILITIES = {"learn", "use", "automate", "build", "transform"}
MATURITIES = {"experimental", "tested", "stable"}
ENVIRONMENTS = {"agent-skills-compatible", "codex-repository"}
TOOLS = {"filesystem-read", "filesystem-write", "git", "python3", "shell"}
DISTRIBUTIONS = {"public-candidate", "repository-only", "retired"}
REQUIRED_CASE_KINDS = {
    "activation.direct",
    "activation.indirect",
    "activation.negative",
    "behavior.incomplete-input",
    "behavior.unsafe-input",
    "behavior.output-shape",
    "behavior.verification",
    "behavior.source-adherence",
    "maintenance.source-drift",
}
REQUIRED_ENTRY_FIELDS = {
    "id",
    "version",
    "path",
    "use_case",
    "intended_users",
    "capability_tags",
    "sources",
    "maturity",
    "supported_environments",
    "required_tools",
    "maintainer",
    "last_reviewed",
    "distribution",
    "eval",
}


def load_yaml(path: Path, errors: list[str]) -> dict:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"Cannot parse {path}: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"Expected a mapping in {path}")
        return {}
    return value


def safe_path(root: Path, relative: object, label: str, errors: list[str]) -> Path | None:
    if not isinstance(relative, str) or not relative:
        errors.append(f"{label} must be a non-empty repository-relative path")
        return None
    if Path(relative).is_absolute():
        errors.append(f"{label} must be repository-relative: {relative}")
        return None
    path = (root / relative).resolve()
    try:
        path.relative_to(root)
    except ValueError:
        errors.append(f"{label} escapes the repository: {relative}")
        return None
    return path


def string_set(
    value: object,
    label: str,
    errors: list[str],
    *,
    allow_empty: bool = False,
) -> set[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        errors.append(f"{label} must be a list of non-empty strings")
        return set()
    if not allow_empty and not value:
        errors.append(f"{label} must not be empty")
    if len(value) != len(set(value)):
        errors.append(f"{label} contains duplicates")
    return set(value)


def markdown_frontmatter(path: Path, errors: list[str]) -> dict:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"Cannot read {path}: {exc}")
        return {}
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        errors.append(f"Missing YAML frontmatter in {path}")
        return {}
    raw = text[4:].split("\n---\n", 1)[0]
    try:
        value = yaml.safe_load(raw)
    except Exception as exc:
        errors.append(f"Cannot parse frontmatter in {path}: {exc}")
        return {}
    return value if isinstance(value, dict) else {}


def validate_eval(
    root: Path,
    entry: dict,
    source_paths: list[str],
    errors: list[str],
) -> None:
    eval_path = safe_path(root, entry.get("eval"), f"{entry.get('id')} eval", errors)
    if eval_path is None:
        return
    if not eval_path.is_file():
        errors.append(f"Missing eval file for {entry.get('id')}: {entry.get('eval')}")
        return
    spec = load_yaml(eval_path, errors)
    if spec.get("schema_version") != 1:
        errors.append(f"{eval_path} must use schema_version 1")
    if spec.get("skill_id") != entry.get("id"):
        errors.append(f"{eval_path} skill_id does not match catalog")
    if str(spec.get("skill_version")) != str(entry.get("version")):
        errors.append(f"{eval_path} skill_version does not match catalog")
    eval_sources = string_set(spec.get("source_paths"), f"{eval_path} source_paths", errors)
    if eval_sources != set(source_paths):
        errors.append(f"{eval_path} source_paths do not match catalog sources")

    execution = spec.get("execution", {})
    if not isinstance(execution, dict):
        errors.append(f"{eval_path} execution must be a mapping")
        execution = {}
    minimum_families = execution.get("minimum_model_families")
    if not isinstance(minimum_families, int) or minimum_families < 2:
        errors.append(f"{eval_path} must require at least two model families")
    if execution.get("when_unavailable") != "record-limitation-and-do-not-count-as-pass":
        errors.append(f"{eval_path} must define the unavailable-family policy")

    cases = spec.get("cases", [])
    if not isinstance(cases, list):
        errors.append(f"{eval_path} cases must be a list")
        return
    seen: set[str] = set()
    kinds: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            errors.append(f"{eval_path} contains a non-mapping case")
            continue
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id:
            errors.append(f"{eval_path} contains a case without an id")
        elif case_id in seen:
            errors.append(f"{eval_path} contains duplicate case id {case_id}")
        else:
            seen.add(case_id)
        kind = case.get("kind")
        if isinstance(kind, str):
            kinds.add(kind)
            if kind not in REQUIRED_CASE_KINDS:
                errors.append(f"{eval_path} case {case_id} has unknown kind {kind}")
        else:
            errors.append(f"{eval_path} case {case_id} needs a kind")
        if not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
            errors.append(f"{eval_path} case {case_id} needs a prompt")
        for field in ("expected", "forbidden"):
            value = case.get(field)
            if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
                errors.append(f"{eval_path} case {case_id} needs a non-empty {field} list")
    missing = sorted(REQUIRED_CASE_KINDS - kinds)
    if missing:
        errors.append(f"{eval_path} missing required case kinds: {', '.join(missing)}")


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    catalog_path = root / "skills" / "catalog.yaml"
    if not catalog_path.is_file():
        return ["Missing skills/catalog.yaml"]
    catalog = load_yaml(catalog_path, errors)
    if catalog.get("schema_version") != 1:
        errors.append("skills/catalog.yaml must use schema_version 1")
    metadata = catalog.get("catalog")
    if not isinstance(metadata, dict):
        errors.append("skills/catalog.yaml catalog must be a mapping")
        metadata = {}
    vocabulary_checks = {
        "capability_vocabulary": CAPABILITIES,
        "maturity_vocabulary": MATURITIES,
        "environment_vocabulary": ENVIRONMENTS,
        "tool_vocabulary": TOOLS,
    }
    for field, expected in vocabulary_checks.items():
        actual = string_set(metadata.get(field), f"catalog.{field}", errors)
        if actual != expected:
            errors.append(f"catalog.{field} does not match the validator vocabulary")
    entries = catalog.get("skills", [])
    if not isinstance(entries, list):
        return errors + ["skills/catalog.yaml skills must be a list"]

    runtime_root = root / ".agents" / "skills"
    if not runtime_root.is_dir():
        return errors + ["Missing .agents/skills runtime directory"]
    runtime_ids = {path.name for path in runtime_root.iterdir() if path.is_dir() and (path / "SKILL.md").is_file()}
    catalog_ids: set[str] = set()

    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("Catalog contains a non-mapping skill entry")
            continue
        missing_fields = sorted(REQUIRED_ENTRY_FIELDS - set(entry))
        if missing_fields:
            errors.append(f"Catalog entry {entry.get('id')} missing: {', '.join(missing_fields)}")
        skill_id = entry.get("id")
        if not isinstance(skill_id, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", skill_id):
            errors.append(f"Invalid skill id: {skill_id}")
            continue
        if skill_id in catalog_ids:
            errors.append(f"Duplicate catalog skill id: {skill_id}")
        catalog_ids.add(skill_id)
        version = str(entry.get("version", ""))
        if not SEMVER_RE.fullmatch(version):
            errors.append(f"{skill_id} version is not semantic x.y.z: {version}")
        if entry.get("maturity") not in MATURITIES:
            errors.append(f"{skill_id} has invalid maturity {entry.get('maturity')}")
        for field in ("use_case", "maintainer", "last_reviewed"):
            if entry.get(field) is None or not str(entry.get(field)).strip():
                errors.append(f"{skill_id} needs a non-empty {field}")
        if entry.get("distribution") not in DISTRIBUTIONS:
            errors.append(f"{skill_id} has invalid distribution {entry.get('distribution')}")
        string_set(entry.get("intended_users"), f"{skill_id} intended_users", errors)
        capabilities = string_set(entry.get("capability_tags"), f"{skill_id} capability_tags", errors)
        if not capabilities or not capabilities <= CAPABILITIES:
            errors.append(f"{skill_id} has invalid capability tags")
        environments = string_set(
            entry.get("supported_environments"),
            f"{skill_id} supported_environments",
            errors,
        )
        if not environments or not environments <= ENVIRONMENTS:
            errors.append(f"{skill_id} has invalid supported environments")
        tools = string_set(
            entry.get("required_tools"),
            f"{skill_id} required_tools",
            errors,
            allow_empty=True,
        )
        if not tools <= TOOLS:
            errors.append(f"{skill_id} has invalid required tools")

        skill_path = safe_path(root, entry.get("path"), f"{skill_id} path", errors)
        expected_relative = f".agents/skills/{skill_id}"
        if entry.get("path") != expected_relative:
            errors.append(f"{skill_id} path must be {expected_relative}")
        if skill_path is None or not (skill_path / "SKILL.md").is_file():
            errors.append(f"{skill_id} is missing SKILL.md")
        else:
            skill_file = skill_path / "SKILL.md"
            metadata = markdown_frontmatter(skill_file, errors)
            if metadata.get("name") != skill_id:
                errors.append(f"{skill_file} name does not match catalog id")
            description = metadata.get("description")
            if not isinstance(description, str) or not description.strip():
                errors.append(f"{skill_file} needs a description")
            text = skill_file.read_text(encoding="utf-8")
            if PLACEHOLDER_RE.search(text):
                errors.append(f"Unfinished scaffold placeholder in {skill_file}")

        source_paths: list[str] = []
        sources = entry.get("sources", [])
        if not isinstance(sources, list) or not sources:
            errors.append(f"{skill_id} needs at least one canonical source")
            sources = []
        for source in sources:
            if not isinstance(source, dict):
                errors.append(f"{skill_id} has a non-mapping source")
                continue
            relative = source.get("path")
            source_path = safe_path(root, relative, f"{skill_id} source", errors)
            if isinstance(relative, str):
                source_paths.append(relative)
            if source_path is None or not source_path.is_file():
                errors.append(f"{skill_id} source does not exist: {relative}")
                continue
            if "version" in source:
                metadata = markdown_frontmatter(source_path, errors)
                if str(metadata.get("version")) != str(source.get("version")):
                    errors.append(f"{skill_id} recorded source version is stale for {relative}")
        if len(source_paths) != len(set(source_paths)):
            errors.append(f"{skill_id} contains duplicate source paths")
        validate_eval(root, entry, source_paths, errors)

    if runtime_ids != catalog_ids:
        missing = sorted(catalog_ids - runtime_ids)
        extra = sorted(runtime_ids - catalog_ids)
        if missing:
            errors.append(f"Cataloged skills missing from runtime: {', '.join(missing)}")
        if extra:
            errors.append(f"Runtime skills missing from catalog: {', '.join(extra)}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the Practice skill catalog and eval definitions")
    parser.add_argument("--root", default=str(DEFAULT_ROOT))
    args = parser.parse_args()
    root = Path(args.root).resolve()
    errors = validate(root)
    if errors:
        print("Practice skill validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)
    count = len(load_yaml(root / "skills" / "catalog.yaml", []).get("skills", []))
    print(f"Practice skill validation passed for {count} skills.")


if __name__ == "__main__":
    main()
