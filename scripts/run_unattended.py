#!/usr/bin/env python3
"""Run one catalogued operation unattended, inside its declared write scope, and record it.

``ops/autonomy/operations.yaml`` declares a ``write_scope`` for every operation:
the only paths a run may create or change. Until this runner existed that scope
was a string in a YAML file that nothing read while an operation was executing.
A runner that simply invoked the catalogued command and trusted it to stay inside
its own bound would be trusting exactly the thing the bound exists to constrain.

This script does three things in order and stops at the first refusal:

1. **Asks the guard.** ``scripts/autonomy_guard.py`` decides whether the
   operation may run at all. Not one of its twenty-seven preconditions is
   reimplemented here; its decision and its message are the runner's. A refusal
   ends the run and is still recorded, because an unrecorded refusal is
   indistinguishable from a run that never happened. The review point the
   guard computed - the promotion's own, or the latest covering renewal's from
   ``ops/autonomy/renewals.yaml`` - is what the entry records as
   ``promotion.review_point``, never the raw promotion field.
2. **Executes inside a bound.** The command runs against a private copy of the
   repository, never against the repository itself. Only files the copy gained or
   changed that match the operation's ``write_scope`` are copied back.
3. **Appends a ledger entry.** Every non-dry run appends exactly one entry
   through ``scripts/ledger.py``, recording the preconditions the guard
   evaluated, the paths read where they are knowable, every path written, the
   reversal derived from the catalog entry, and the outcome.

Nothing here promotes anything. With the records this repository ships - an
engaged kill switch and an empty promotion list - the guard refuses every
catalogued operation, so this runner refuses too, and the only thing it writes is
the refusal.

## The containment mechanism, and what it does not contain

The command is executed with its working directory set to a **staging copy** of
the repository root, made in a private temporary directory. The tree is
snapshotted (path, symlink target, and SHA-256 of each file) immediately after
the copy and again after the command exits. The difference is the set of paths
the command created, changed, or deleted.

A run is applied only when every one of those paths is inside ``write_scope``. If
any created or changed path falls outside the scope, if any path was deleted, if
any changed path is a symlink, or if the command exited non-zero or timed out,
**nothing is copied back**: the staging copy is discarded, the repository is left
exactly as it was, and the run is recorded as ``failed``. Out-of-scope writes are
therefore never applied rather than applied and undone, and the repository is
never in a state a reversal has to repair.

State the limits plainly, because a bound that is described as more than it is
becomes a licence:

- **Only writes into the staging tree are contained.** A command that writes to
  an absolute path, to ``$HOME``, to ``/tmp``, or to any location outside its
  working directory is not stopped, not detected, and not reverted. This is a
  bound on where a run's *results* may land in the repository, not a sandbox. A
  command that could do that is a command this repository should not catalog.
- **No network, process, or resource isolation.** The only resource limit is a
  wall-clock timeout (``COMMAND_TIMEOUT_SECONDS``); a timed-out run is recorded
  as failed and applied not at all.
- **The environment is inherited**, with one change: ``PYTHONDONTWRITEBYTECODE``
  is set, so that importing a module does not create a ``__pycache__`` directory
  inside the tree being compared.
- **``.git``, ``__pycache__``, and ``*.pyc`` are excluded from the comparison.**
  Excluding them cannot weaken containment: nothing under them is ever copied
  back, and the staging copy that holds them is destroyed. Including them would
  make every run of a git-reading operation look like an out-of-scope write,
  because reading a repository refreshes its index.
- **Comparison is by content and existence, not by metadata.** A change to a
  file's mode or timestamp alone is not detected, and neither is a change to an
  empty directory.
- **The staging copy is the whole tree**, including untracked and ignored files
  such as a local ``.env``. It is created with ``mkdtemp`` (mode 0700) and
  removed when the run ends, but on a large repository the copy is the dominant
  cost of a run.
- **Deletions are never applied.** The runner copies back creations and
  modifications only, and treats any deletion anywhere in the tree as a bound
  violation. No catalogued operation deletes anything, the ledger schema requires
  every path in ``paths_written`` to exist for a completed run, and failing
  closed is the right default for the first version of this mechanism.

## Usage

``--private-root PATH`` is an explicit rehearsal/output-routing mode: export
the recorded Git commit instead of the working tree, omit inherited credentials,
and apply outputs and ledger entries under PATH instead of the canonical root.
PATH must be outside that root. It has no Git history and is not a sandbox or
proof that the destination is access-controlled. Never route a live provider's
durable reservation journal through disposable staging. The experimental
context-pack command has no configured live transport.

    python3 scripts/run_unattended.py --operation cadence-snapshot --root .
    python3 scripts/run_unattended.py --operation cadence-snapshot --root . --dry-run

``--dry-run`` writes nothing at all: no operation output, and no ledger entry on
disk. It renders the entry the run would have appended and exits 0. Exit 0 from a
dry run means the simulation finished, never that the operation was permitted -
the rendered entry carries the guard's verdict in its preconditions.

Exit codes: 0 = completed or dry run, 1 = refused or failed, 2 = usage error.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from datetime import date
from fnmatch import fnmatchcase
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

try:
    import yaml
except ImportError as exc:  # pragma: no cover - environment diagnostic
    print(f"run_unattended.py needs PyYAML: {exc}. Fix: python3 -m pip install PyYAML", file=sys.stderr)
    raise SystemExit(2)

import autonomy_guard as guard  # noqa: E402  (sys.path is prepared above)
from ledger import (  # noqa: E402
    LedgerError,
    append_entry,
    default_body,
    next_run_id,
    render_entry,
    split_front_matter,
    validate_entry,
)

DEFAULT_ROOT = SCRIPTS_DIR.parent

CATALOG_PATH = "ops/autonomy/operations.yaml"
PROMOTIONS_PATH = "ops/autonomy/promotions.yaml"
RENEWALS_PATH = "ops/autonomy/renewals.yaml"
LADDER_PATH = "docs/framework/AUTONOMY_LADDER.md"
SCHEMA_REF = "docs/schemas/ACTION_LEDGER_SCHEMA.md"

DEFAULT_LEDGER_DIR = ("ops", "ledger")

# The paths the guard reads to reach its decision. They are what this runner can
# honestly claim to have read; what the operation's own command reads is not
# observable from here and is not recorded.
GUARD_INPUTS = (CATALOG_PATH, PROMOTIONS_PATH, RENEWALS_PATH, LADDER_PATH)

# The promotion keys an entry records, in the ledger schema's order. Every one
# is required by scripts/ledger.py when a promotion is recorded, so a promotion
# missing any of them is recorded as `none` and the guard's refusal says why.
RECORDED_PROMOTION_KEYS = ("level", "signed_by", "signed_on", "review_point")

LEDGER_SCHEMA_VERSION = 1

# The level the run asks for, not the level it was granted. A run that reaches
# this script is asking to act without a person, which is A3 whatever the answer.
CLAIMED_LEVEL = "A3"

TRIGGERS = ("manual", "schedule")
DEFAULT_ACTOR = {"manual": "local-operator", "schedule": "scheduled-workflow"}

KILL_SWITCH_VALUES = ("engaged", "released")
KILL_SWITCH_UNREADABLE = "engaged"

COMMAND_TIMEOUT_SECONDS = 300

# Excluded from the tree comparison only. Nothing under these names is ever
# copied back, and the staging copy that holds them is destroyed with the run.
IGNORED_DIRECTORY_NAMES = frozenset({".git", "__pycache__"})
IGNORED_FILE_SUFFIXES = (".pyc",)

SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{7,40}$")
NUMBERED_RUN_ID_RE = re.compile(r"^(?P<base>[a-z0-9]+(?:-[a-z0-9]+)*)-(?P<number>\d+)$")

OUTPUT_EXCERPT_LINES = 20
DIGEST_CHUNK = 65536


# --- Small helpers ----------------------------------------------------------

def one_line(value) -> str:
    """Collapse a catalog or guard string to a single line of front matter text."""
    return " ".join(str(value).split())


def joined(values) -> str:
    return ", ".join(values)


def is_str_list(value) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) and item.strip() for item in value)


def load_yaml_mapping(path: Path):
    """Return the mapping at ``path``, or ``None`` when it cannot be read as one."""
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return None
    return data if isinstance(data, dict) else None


# --- What the run observed --------------------------------------------------

def read_catalog_entry(root: Path, operation: str) -> tuple[dict | None, str | None]:
    """Return the catalog entry for ``operation``, or ``None`` and why it is unusable.

    The guard has its own, stricter reading of this file. This one exists because
    the runner needs three values before it can bound anything - the command, the
    write scope, and the reversal - and it refuses rather than executes when any
    of them is missing or malformed, whatever the guard concluded.
    """
    record = load_yaml_mapping(root / CATALOG_PATH)
    if record is None:
        return None, f"{CATALOG_PATH} is missing or is not a YAML mapping, so no bound can be read."
    operations = record.get("operations")
    if not isinstance(operations, list):
        return None, f"{CATALOG_PATH}: 'operations' is not a list, so no bound can be read."
    for item in operations:
        if isinstance(item, dict) and str(item.get("id", "")).strip() == operation:
            entry = item
            break
    else:
        return None, f"{CATALOG_PATH} has no entry for '{operation}', so it has no command, scope, or reversal."

    if not is_str_list(entry.get("command")) or len(entry["command"]) < 2:
        return None, (
            f"{CATALOG_PATH}: the entry for '{operation}' has no usable 'command'. The runner "
            "executes an argv list of at least two non-empty strings and never a shell string."
        )
    scope = entry.get("write_scope")
    if not isinstance(scope, list) or not all(isinstance(item, str) and item.strip() for item in scope):
        return None, (
            f"{CATALOG_PATH}: the entry for '{operation}' has no usable 'write_scope'. It must be "
            "a list of repository-relative patterns, or [] when the operation writes nothing."
        )
    reversal = entry.get("reversal")
    if not isinstance(reversal, str) or len(one_line(reversal)) < 8:
        return None, (
            f"{CATALOG_PATH}: the entry for '{operation}' records no usable 'reversal'. A run whose "
            "undo nobody wrote down is refused rather than executed."
        )
    return entry, None


def read_governance_state(root: Path, operation: str) -> tuple[str, object]:
    """Return the kill-switch state and the promotion this run observed.

    Both are recorded in the ledger entry as the run saw them, so a reviewer
    reading the entry later does not have to reconstruct what the records said on
    the day. A record this function cannot read is reported as ``engaged`` and no
    promotion, which is the reading that refuses.
    """
    record = load_yaml_mapping(root / PROMOTIONS_PATH)
    if record is None:
        return KILL_SWITCH_UNREADABLE, "none"

    kill_switch = record.get("kill_switch")
    state = kill_switch if kill_switch in KILL_SWITCH_VALUES else KILL_SWITCH_UNREADABLE

    promotions = record.get("promotions")
    if not isinstance(promotions, list):
        return state, "none"
    for item in promotions:
        if not isinstance(item, dict) or str(item.get("operation", "")).strip() != operation:
            continue
        observed = {}
        for key in RECORDED_PROMOTION_KEYS:
            value = item.get(key)
            if value is None:
                continue
            if key.endswith("_on") or key.endswith("_point"):
                rendered = value.isoformat() if isinstance(value, date) else str(value).strip()
                if not ISO_DATE_RE.match(rendered):
                    continue
                observed[key] = rendered
            else:
                observed[key] = one_line(value)
        if all(key in observed for key in RECORDED_PROMOTION_KEYS):
            return state, observed
        # A promotion too malformed to record as a mapping - a field missing, or
        # a date that is not a date - would fail ledger validation and lose the
        # whole entry, so it is recorded as no promotion. The guard refuses such
        # a record, and its refusal is in `preconditions`.
        return state, "none"
    return state, "none"


def read_source_commit(root: Path) -> str | None:
    """The commit the run read, when the root is a git repository that can name one."""
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    value = result.stdout.strip().lower()
    return value if COMMIT_RE.match(value) else None


# --- The guard's decision, in ledger shape ----------------------------------

def merge_preconditions(decision) -> list[dict]:
    """Turn one guard ``Decision`` into the entry's ``preconditions`` list.

    The guard may record the same precondition id more than once - a check that
    held for the operation asked about and failed for another entry in the same
    record, or two separate findings under one id. The ledger allows one item per
    id, and a failure is the finding that matters, so failures win and their
    messages are joined in the order the guard produced them.
    """
    merged: dict[str, dict] = {}
    for name in getattr(decision, "checked", []) or []:
        merged.setdefault(
            name,
            {
                "check": name,
                "result": "pass",
                "detail": f"Precondition '{name}' held when scripts/autonomy_guard.py evaluated it.",
            },
        )
    for refusal in getattr(decision, "refusals", []) or []:
        name = refusal.precondition
        message = one_line(refusal.message)
        if name in merged and merged[name]["result"] == "fail":
            merged[name]["detail"] = f"{merged[name]['detail']} | {message}"
        else:
            merged[name] = {"check": name, "result": "fail", "detail": message}
    return list(merged.values())


# --- The staging copy and the bound -----------------------------------------

def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(DIGEST_CHUNK), b""):
                digest.update(chunk)
    except OSError as error:
        return f"unreadable:{type(error).__name__}"
    return digest.hexdigest()


def snapshot_tree(root: Path) -> dict[str, str]:
    """Map every comparable path under ``root`` to a fingerprint of its content.

    Symlinks are fingerprinted by their target and never followed, so a symlink
    swapped for a file - or for a different target - reads as a change.
    """
    entries: dict[str, str] = {}
    for current, dirnames, filenames in os.walk(root, followlinks=False):
        base = Path(current)
        kept = []
        for name in sorted(dirnames):
            if name in IGNORED_DIRECTORY_NAMES:
                continue
            path = base / name
            if path.is_symlink():
                entries[path.relative_to(root).as_posix()] = "symlink:" + os.readlink(path)
                continue
            kept.append(name)
        dirnames[:] = kept
        for name in sorted(filenames):
            if name.endswith(IGNORED_FILE_SUFFIXES):
                continue
            path = base / name
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                entries[relative] = "symlink:" + os.readlink(path)
            else:
                entries[relative] = file_digest(path)
    return entries


def segment_match(relative: str, pattern: str) -> bool:
    """Match a repository-relative POSIX path against one write-scope glob.

    ``*`` and ``?`` match within a single path segment and never cross ``/``, so
    ``ops/status/*.md`` covers ``ops/status/today.md`` and does not cover
    ``ops/status/archive/old.md``. Plain ``fnmatch`` would admit the second,
    because its ``*`` crosses separators — a declared scope one directory level
    wider than it reads. A ``**`` segment matches zero or more whole segments,
    so a scope that genuinely wants a subtree has to say so.
    """
    parts = relative.split("/")
    globs = pattern.split("/")
    if "**" not in globs:
        if len(parts) != len(globs):
            return False
        return all(fnmatchcase(part, glob) for part, glob in zip(parts, globs))
    head, _, tail = pattern.partition("/**")
    tail = tail.lstrip("/")
    lead = head.split("/")
    if len(parts) < len(lead) or not all(
        fnmatchcase(part, glob) for part, glob in zip(parts[: len(lead)], lead)
    ):
        return False
    rest = parts[len(lead):]
    if not tail:
        return True
    for start in range(len(rest) + 1):
        if segment_match("/".join(rest[start:]), tail):
            return True
    return False


def matches_scope(relative: str, write_scope: list[str]) -> bool:
    """Match a repository-relative POSIX path against the declared scope.

    Segment-wise matching, deliberately stricter than the ``fnmatch`` reading
    used by ``glob_reaches_governed_path`` in ``scripts/autonomy_guard.py``.
    The asymmetry is intentional and both halves err toward refusing:

    - the guard asks whether a declared scope *could reach* a governed path and
      matches loosely, so it refuses a scope that is dangerous under the widest
      reading;
    - this function asks whether a path a command actually wrote *is inside*
      the declared scope and matches strictly, so it applies a write only under
      the narrowest reading.

    Do not "fix" the difference by making them agree. Making either one match
    the other widens what an unattended run may write.
    """
    return any(segment_match(relative, pattern) for pattern in write_scope)


class ExecutionResult:
    """What one bounded execution did, and whether its results may be applied."""

    def __init__(self) -> None:
        self.exit_code: int | None = None
        self.timed_out = False
        self.stdout = ""
        self.stderr = ""
        self.created: list[str] = []
        self.modified: list[str] = []
        self.deleted: list[str] = []
        self.out_of_scope: list[str] = []
        self.symlinked: list[str] = []
        self.applied: list[str] = []
        self.failure: str | None = None

    @property
    def violations(self) -> list[str]:
        return sorted(set(self.out_of_scope) | set(self.deleted) | set(self.symlinked))


def safe_private_target(root: Path, relative: str) -> Path:
    """Reject links/junctions instead of letting an output redirect writes."""
    target = root / relative
    for path in (target, *target.parents):
        if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
            raise ValueError("private output path contains a link or junction")
        if path == root:
            break
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError("private output escaped its root")
    return target


def export_committed_tree(root: Path, destination: Path, commit: str = "HEAD") -> None:
    """Export HEAD only: no ignored files, desktop credentials, or .git config."""
    result = subprocess.run(["git", "archive", "--format=tar", commit], cwd=root,
                            capture_output=True, check=True, timeout=60)
    destination.mkdir()
    with tarfile.open(fileobj=io.BytesIO(result.stdout)) as archive:
        for member in archive:
            if member.isdir():
                continue
            if not member.isfile() or Path(member.name).is_absolute() or ".." in Path(member.name).parts:
                raise ValueError("committed input contains a non-regular or escaping entry")
            target = safe_private_target(destination, member.name)
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.extractfile(member) as source, target.open("xb") as output:
                shutil.copyfileobj(source, output)


def execute_in_staging(root: Path, command: list[str], write_scope: list[str],
                       *, output_root: Path | None = None, source_commit: str = "HEAD") -> ExecutionResult:
    """Run ``command`` against a private copy of ``root`` and apply only in-scope results."""
    result = ExecutionResult()
    staging_parent = tempfile.mkdtemp(prefix="run-unattended-")
    try:
        staging = Path(staging_parent) / "repository"
        try:
            if output_root is None:
                shutil.copytree(root, staging, symlinks=True)
            else:
                export_committed_tree(root, staging, source_commit)
        except (OSError, shutil.Error, ValueError, subprocess.SubprocessError, tarfile.TarError) as error:
            result.failure = f"the staging copy of the repository could not be made: {error}"
            return result

        before = snapshot_tree(staging)

        environment = dict(os.environ) if output_root is None else {
            key: os.environ[key] for key in ("PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP")
            if key in os.environ
        }
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        environment["PYTHONUTF8"] = "1"
        try:
            completed = subprocess.run(
                [sys.executable, *command[1:]] if command[0] == "python3" else command,
                cwd=str(staging),
                env=environment,
                capture_output=True,
                text=True,
                timeout=COMMAND_TIMEOUT_SECONDS,
                check=False,
            )
        except subprocess.TimeoutExpired:
            result.timed_out = True
            result.failure = (
                f"the command did not finish within {COMMAND_TIMEOUT_SECONDS} seconds and was "
                "stopped; nothing it wrote was applied"
            )
        except OSError as error:
            result.failure = f"the command could not be started: {error}"
        else:
            result.exit_code = completed.returncode
            result.stdout = completed.stdout or ""
            result.stderr = completed.stderr or ""
            if completed.returncode != 0:
                result.failure = (
                    f"the command exited {completed.returncode}; a run that did not succeed is "
                    "never applied, whatever it wrote"
                )

        after = snapshot_tree(staging)
        result.created = sorted(path for path in after if path not in before)
        result.modified = sorted(path for path in after if path in before and after[path] != before[path])
        result.deleted = sorted(path for path in before if path not in after)
        touched = result.created + result.modified
        result.out_of_scope = sorted(path for path in touched if not matches_scope(path, write_scope))
        result.symlinked = sorted(path for path in touched if after[path].startswith("symlink:"))

        if result.violations:
            if result.failure is None:
                result.failure = (
                    "the command wrote outside the bound its catalog entry declares: "
                    f"{joined(result.violations)}"
                )
            return result
        if result.failure is not None:
            return result

        # Preflight ALL targets before applying any output. The private mode is
        # output routing, not a sandbox; isolated hosting remains a prerequisite.
        try:
            targets = {relative: safe_private_target(output_root, relative) if output_root
                       else root / relative for relative in touched}
        except ValueError as error:
            result.failure = str(error)
            return result
        for relative in touched:
            source = staging / relative
            target = targets[relative]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            result.applied.append(relative)
        result.applied.sort()
        return result
    finally:
        shutil.rmtree(staging_parent, ignore_errors=True)


# --- The entry --------------------------------------------------------------

def compose_reversal(catalog_reversal: str, applied: list[str], modified_existing: list[str]) -> str:
    """Build the reversal recorded for this run from the catalog entry's own sentence.

    The catalog is the authority on how an operation is undone. What this adds is
    the concrete paths the run touched, so the recorded reversal is a command a
    person can run rather than a description of one.
    """
    sentence = one_line(catalog_reversal)
    if not applied:
        return (
            "Nothing was applied to the repository, so there is nothing to undo. The reversal "
            f"recorded for this operation in {CATALOG_PATH} is: {sentence}"
        )
    created = [path for path in applied if path not in modified_existing]
    parts = [sentence]
    if created:
        parts.append(f"This run created: {joined(created)}. Undo it from the repository root with: rm {' '.join(created)}")
    if modified_existing:
        parts.append(
            f"This run changed: {joined(modified_existing)}. Restore it from the repository root "
            f"with: git checkout -- {' '.join(modified_existing)}"
        )
    return " ".join(parts)


def existing_run_ids(ledger_dir: Path) -> set[str]:
    """Every ``run_id`` already recorded in ``ledger_dir``."""
    found: set[str] = set()
    if not ledger_dir.is_dir():
        return found
    for path in sorted(ledger_dir.glob("*.md")):
        if path.name == "README.md":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        front_matter, _ = split_front_matter(text)
        if front_matter is None:
            continue
        try:
            data = yaml.safe_load(front_matter)
        except yaml.YAMLError:
            continue
        if isinstance(data, dict) and isinstance(data.get("run_id"), str):
            found.add(data["run_id"].strip())
    return found


def unique_run_id(candidate: str, taken: set[str]) -> str:
    """Advance ``candidate`` past any id already recorded in the ledger.

    ``next_run_id`` reads entry file names, so an entry whose name is exempt from
    the naming rule - the committed ``SAMPLE_run.md`` is one - can hold an id it
    would hand out again. A duplicate id makes ``supersedes`` ambiguous and fails
    ``scripts/ledger.py validate`` on the directory, so it is stepped over here.
    """
    if candidate not in taken:
        return candidate
    match = NUMBERED_RUN_ID_RE.match(candidate)
    if match:
        base = match.group("base")
        number = int(match.group("number"))
        width = len(match.group("number"))
        while True:
            number += 1
            following = f"{base}-{number:0{width}d}"
            if following not in taken:
                return following
    number = 2
    while f"{candidate}-{number}" in taken:
        number += 1
    return f"{candidate}-{number}"


def build_entry(
    *,
    run_id: str,
    run_date: str,
    operation: str,
    actor: str,
    trigger: str,
    kill_switch: str,
    promotion,
    preconditions: list[dict],
    command: list[str] | None,
    source_commit: str | None,
    write_scope: list[str],
    paths_read: list[str],
    paths_written: list[str],
    reversal: str,
    outcome: str,
) -> dict:
    entry = {
        "ledger_schema_version": LEDGER_SCHEMA_VERSION,
        "run_id": run_id,
        "run_date": run_date,
        "operation": operation,
        "actor": actor,
        "claimed_level": CLAIMED_LEVEL,
        "trigger": trigger,
        "kill_switch": kill_switch,
        "promotion": promotion,
        "preconditions": preconditions,
        "write_scope": list(write_scope),
        "paths_read": list(paths_read),
        "paths_written": list(paths_written),
        "reversal": reversal,
        "outcome": outcome,
    }
    if command:
        entry["command"] = list(command)
    if source_commit:
        entry["source_commit"] = source_commit
    return entry


# --- Reporting --------------------------------------------------------------

def excerpt(text: str, stream: str) -> list[str]:
    lines = [line for line in (text or "").splitlines() if line.strip()]
    if not lines:
        return []
    shown = lines[-OUTPUT_EXCERPT_LINES:]
    header = f"  {stream} (last {len(shown)} of {len(lines)} lines):"
    return [header, *[f"    {line}" for line in shown]]


# --- The run ----------------------------------------------------------------

def run(
    *,
    root: Path,
    operation: str,
    dry_run: bool,
    trigger: str,
    actor: str,
    as_of: date,
    ledger_dir: Path,
    private_root: Path | None = None,
    out=None,
    err=None,
) -> int:
    """Perform one run and return the process exit code."""
    # Resolved here rather than as a default argument so that a caller which has
    # redirected the standard streams - a test, or a workflow step - is honored.
    out = sys.stdout if out is None else out
    err = sys.stderr if err is None else err
    kill_switch, promotion = read_governance_state(root, operation)
    paths_read = [path for path in GUARD_INPUTS]
    source_commit = read_source_commit(root)

    try:
        decision = guard.evaluate(root, operation, as_of)
        guard_message = guard.render(decision)
        permitted = bool(decision.permitted)
        preconditions = merge_preconditions(decision)
        # The entry records the review point in force on the run date - the
        # promotion's own, or the latest covering renewal's - as the guard
        # computed it. The raw promotion field is what a reviewer would have to
        # correct by hand; the effective value is what the run was bound by.
        effective_review_point = getattr(decision, "review_point", None)
        if isinstance(promotion, dict) and isinstance(effective_review_point, str):
            promotion = dict(promotion, review_point=effective_review_point)
    except Exception as error:  # pragma: no cover - a guard fault is a refusal, not a run
        permitted = False
        guard_message = (
            f"REFUSED: '{operation}' may not run unattended. scripts/autonomy_guard.py raised "
            f"{type(error).__name__}: {error}\n"
        )
        preconditions = [
            {
                "check": "guard-evaluated",
                "result": "fail",
                "detail": one_line(
                    f"scripts/autonomy_guard.py raised {type(error).__name__}: {error}. A guard that "
                    "cannot reach a decision refuses."
                ),
            }
        ]
    out.write(guard_message)

    entry_record, catalog_problem = read_catalog_entry(root, operation)
    if entry_record is None:
        permitted = False
        preconditions.append(
            {
                "check": "catalog-entry-usable",
                "result": "fail",
                "detail": one_line(
                    f"{catalog_problem} The runner refuses an operation whose bound it cannot read, "
                    "whatever the guard concluded."
                ),
            }
        )
        out.write(f"REFUSED: {catalog_problem}\n")
        command = None
        write_scope: list[str] = []
        catalog_reversal = ""
    else:
        preconditions.append(
            {
                "check": "catalog-entry-usable",
                "result": "pass",
                "detail": one_line(
                    f"{CATALOG_PATH} records a command, a write scope, and a reversal for "
                    f"'{operation}', so the run has a bound to enforce."
                ),
            }
        )
        command = list(entry_record["command"])
        write_scope = [item.strip() for item in entry_record["write_scope"]]
        catalog_reversal = entry_record["reversal"]

    if private_root and permitted:
        # Bind the decision and input export to the same committed policy. A
        # private run cannot claim HEAD provenance for uncommitted governance.
        try:
            consistent = source_commit is not None and subprocess.run(
                ["git", "diff", "--quiet", source_commit, "--", *GUARD_INPUTS],
                cwd=root, capture_output=True, timeout=30, check=False,
            ).returncode == 0
        except (OSError, subprocess.SubprocessError):
            consistent = False
        preconditions.append({"check": "private-inputs-committed", "result": "pass" if consistent else "fail",
                              "detail": "Private input export requires committed governance matching the recorded source commit."})
        if not consistent:
            permitted = False

    # --- The dry run stops here, having written nothing at all.
    if dry_run:
        preconditions.append(
            {
                "check": "dry-run-requested",
                "result": "pass",
                "detail": one_line(
                    "The operator passed --dry-run, so the operation was simulated: no command ran, "
                    "nothing was written, and no ledger entry was appended."
                ),
            }
        )
        entry = build_entry(
            run_id=unique_run_id(next_run_id(operation, ledger_dir=ledger_dir), existing_run_ids(ledger_dir)),
            run_date=as_of.isoformat(),
            operation=operation,
            actor=actor,
            trigger=trigger,
            kill_switch=kill_switch,
            promotion=promotion,
            preconditions=preconditions,
            command=command,
            source_commit=source_commit,
            write_scope=write_scope,
            paths_read=paths_read,
            paths_written=[],
            reversal=compose_reversal(catalog_reversal or "No reversal is recorded in the catalog.", [], []),
            outcome="dry-run",
        )
        violations = validate_entry(entry, default_body(entry), "<dry run>", root)
        if violations:
            err.write(
                "run_unattended.py: the entry this dry run would append is not valid, which is a "
                f"defect in the runner rather than in the run:\n"
                + "".join(f"  - {violation}\n" for violation in violations)
            )
            return 1
        out.write(
            "\nDRY RUN: nothing was written. No command ran, no path was created or changed, and no "
            "ledger entry was appended. Exit 0 means the simulation finished, not that the operation "
            "was permitted; the preconditions below carry the guard's verdict.\n\n"
        )
        out.write(render_entry(entry))
        return 0

    # --- A refused run records the refusal and stops.
    if not permitted:
        outcome = "refused"
        paths_written: list[str] = []
        reversal = compose_reversal(catalog_reversal or "No reversal is recorded in the catalog.", [], [])
        execution = None
    else:
        # `permitted` is false whenever the catalog entry was unusable, so a run
        # that reaches here has a command and a scope to enforce.
        out.write(f"\nRunning: {' '.join(command)}\n")
        out.write(f"  write_scope: {joined(write_scope) if write_scope else '(writes nothing)'}\n")
        execution = (execute_in_staging(root, command, write_scope, output_root=private_root, source_commit=source_commit)
                     if private_root else execute_in_staging(root, command, write_scope))
        paths_read = paths_read + [command[1]]
        for line in ([] if private_root else excerpt(execution.stdout, "stdout") + excerpt(execution.stderr, "stderr")):
            out.write(line + "\n")
        if execution.failure is None:
            outcome = "completed"
            paths_written = list(execution.applied)
            preconditions.append(
                {
                    "check": "write-scope-enforced",
                    "result": "pass",
                    "detail": one_line(
                        "Every path the command created or changed in the staging copy of the "
                        f"repository is inside the declared write scope, so all {len(paths_written)} "
                        "of them were applied."
                    ),
                }
            )
            out.write(
                f"COMPLETED: {len(paths_written)} path(s) applied inside the bound"
                + (f": {joined(paths_written)}" if paths_written else "")
                + "\n"
            )
        else:
            outcome = "failed"
            paths_written = []
            if execution.violations:
                scope_detail = (
                    f"The command left its bound: {execution.failure}. Nothing was applied, the "
                    "staging copy was discarded, and the repository is unchanged."
                )
            else:
                scope_detail = (
                    "Every path the command created or changed is inside the declared write "
                    f"scope, but the run was not applied because {execution.failure}."
                )
            preconditions.append(
                {
                    "check": "write-scope-enforced",
                    "result": "fail" if execution.violations else "pass",
                    "detail": one_line(scope_detail),
                }
            )
            out.write(f"FAILED: {execution.failure}\n")
            out.write("Nothing was applied; the repository is unchanged.\n")
        reversal = compose_reversal(
            catalog_reversal,
            paths_written,
            [path for path in paths_written if path in (execution.modified if execution else [])],
        )
        if private_root:
            reversal = (
                "Canonical checkout was not modified. Review only these generated paths under "
                f"the private output root: {joined(paths_written) if paths_written else '(none)'}. "
                "Discard the generated draft or restore a previous private copy; never execute "
                "this reversal against the canonical checkout. "
                f"Catalog reversal: {one_line(catalog_reversal)}"
            )

    entry = build_entry(
        run_id=unique_run_id(next_run_id(operation, ledger_dir=ledger_dir), existing_run_ids(ledger_dir)),
        run_date=as_of.isoformat(),
        operation=operation,
        actor=actor,
        trigger=trigger,
        kill_switch=kill_switch,
        promotion=promotion,
        preconditions=preconditions,
        command=command,
        source_commit=source_commit,
        write_scope=write_scope,
        paths_read=paths_read,
        paths_written=paths_written,
        reversal=reversal,
        outcome=outcome,
    )
    try:
        written = append_entry(entry, ledger_dir=ledger_dir, root=private_root or root)
    except LedgerError as error:
        err.write(
            "run_unattended.py: the run happened but its ledger entry could not be written, so this "
            f"run is recorded nowhere. {SCHEMA_REF} describes the fields.\n{error.report()}\n"
        )
        return 1
    out.write(f"Ledger entry: {written}\n")
    return 0 if outcome == "completed" else 1


# --- CLI --------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="run_unattended.py",
        description=(
            "Run one catalogued operation inside its declared write scope and append a ledger "
            "entry. The guard decides whether it runs at all. Exit 0 completed or dry run, "
            "1 refused or failed, 2 usage error."
        ),
    )
    parser.add_argument("--operation", required=True, metavar="ID", help=f"operation id catalogued in {CATALOG_PATH}")
    parser.add_argument(
        "--root",
        default=str(DEFAULT_ROOT),
        metavar="PATH",
        help="repository root the run reads and writes (default: the repository containing this script)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="write nothing at all: render the ledger entry the run would append, then exit 0",
    )
    parser.add_argument(
        "--trigger",
        default="manual",
        choices=TRIGGERS,
        help="what started the run, recorded in the entry (default: manual)",
    )
    parser.add_argument(
        "--actor",
        default=None,
        metavar="SLUG",
        help="the role or automation label that ran the operation, never a personal name "
        "(default: local-operator, or scheduled-workflow with --trigger schedule)",
    )
    parser.add_argument(
        "--as-of",
        default=None,
        metavar="YYYY-MM-DD",
        help="the run date, and the date the promotion signature is checked against (default: today)",
    )
    parser.add_argument(
        "--ledger-dir",
        default=None,
        metavar="PATH",
        help="directory the entry is appended to (default: <root>/ops/ledger). The entry is always "
        "written; this only changes where, so a run directed elsewhere is absent from the "
        "repository's audit trail. Use it for tests and rehearsals.",
    )
    parser.add_argument("--private-root", type=Path, help="Apply committed-input rehearsal outputs and ledger outside the canonical checkout; does not establish privacy or isolation")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    root = Path(args.root)
    if not root.is_dir():
        print(
            f"run_unattended.py: --root {args.root!r} is not a directory. Pass the repository root, "
            "for example --root .",
            file=sys.stderr,
        )
        return 2
    root = root.resolve()

    operation = args.operation.strip()
    if not SLUG_RE.match(operation):
        print(
            f"run_unattended.py: --operation {args.operation!r} is not an operation id. Pass a "
            "lowercase slug such as cadence-snapshot.",
            file=sys.stderr,
        )
        return 2

    actor = (args.actor or DEFAULT_ACTOR[args.trigger]).strip()
    if not SLUG_RE.match(actor):
        print(
            f"run_unattended.py: --actor {args.actor!r} is not an actor label. Pass a lowercase slug "
            "naming a role or an automation, such as scheduled-workflow, never a personal name.",
            file=sys.stderr,
        )
        return 2

    as_of = date.today()
    if args.as_of is not None:
        if not ISO_DATE_RE.match(args.as_of):
            print(
                f"run_unattended.py: --as-of must be an ISO date such as 2026-09-02, got {args.as_of!r}.",
                file=sys.stderr,
            )
            return 2
        try:
            as_of = date.fromisoformat(args.as_of)
        except ValueError as error:
            print(f"run_unattended.py: --as-of is not a real date: {args.as_of} ({error}).", file=sys.stderr)
            return 2

    ledger_dir = Path(args.ledger_dir) if args.ledger_dir else root.joinpath(*DEFAULT_LEDGER_DIR)

    private_root = args.private_root
    if private_root:
        try:
            private_root = private_root.absolute()
            # Refuse broad, overlapping, or redirected targets before mkdir.
            if private_root.parent == private_root or private_root.resolve().is_relative_to(root) or root.is_relative_to(private_root.resolve()):
                raise ValueError("private root must be outside and not contain the canonical checkout")
            for path in (private_root, *private_root.parents):
                if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
                    raise ValueError("private root contains a link or junction")
            if args.ledger_dir:
                raise ValueError("--private-root owns its ledger directory; do not override it")
            if not args.dry_run:
                private_root.mkdir(parents=True, exist_ok=True)
            ledger_dir = safe_private_target(private_root, "ops/ledger")
        except (ValueError, OSError) as error:
            print(f"run_unattended.py: {error}", file=sys.stderr)
            return 2

    return run(
        root=root,
        operation=operation,
        dry_run=bool(args.dry_run),
        trigger=args.trigger,
        actor=actor,
        as_of=as_of,
        ledger_dir=ledger_dir,
        private_root=private_root,
    )


if __name__ == "__main__":
    sys.exit(main())
