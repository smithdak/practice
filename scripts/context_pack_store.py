"""Small owner-selected private result store for the context-pack pilot.

This module provides path-safety and recovery-safe local persistence only.  A
private root is not an ACL boundary or encrypted retention system: the owner
chooses a host path and remains responsible for its host permissions and
retention policy.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import stat
import tempfile


class StoreRefused(RuntimeError):
    """The requested private-store operation cannot be performed safely."""


_ID = re.compile(r"[A-Za-z0-9_-]{1,80}\Z", re.ASCII)
_DEVICE_IDS = {"CON", "NUL", "AUX", "PRN", *(f"COM{i}" for i in range(1, 10)),
               *(f"LPT{i}" for i in range(1, 10))}


def _reparse(path: Path) -> bool:
    try:
        info = os.lstat(path)
    except FileNotFoundError:
        return False
    if stat.S_ISLNK(info.st_mode):
        return True
    # st_file_attributes is present on Windows; junctions and other reparse
    # points are refused even when they are not represented as symlinks.
    flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(getattr(info, "st_file_attributes", 0) & flag)


def _existing_components(path: Path) -> None:
    """Reject links/reparse points in all existing components of *path*."""
    absolute = Path(os.path.abspath(os.fspath(path)))
    current = Path(absolute.anchor)
    for component in absolute.parts[1:]:
        current /= component
        if _reparse(current):
            raise StoreRefused(f"reparse point or symlink in store path: {current}")


def _resolved(path: Path) -> Path:
    try:
        return path.resolve(strict=False)
    except OSError as exc:
        raise StoreRefused(f"cannot resolve store path: {path}") from exc


def _under_or_equal(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def _check_root(root: Path) -> Path:
    if not isinstance(root, Path):
        root = Path(root)
    if not root.is_absolute():
        raise StoreRefused("private root must be an absolute explicit path")
    _existing_components(root)
    resolved = _resolved(root)
    if resolved.exists() and not resolved.is_dir():
        raise StoreRefused("private root is not a directory")
    return resolved


def prepare_private_root(root: Path, canonical_root: Path) -> Path:
    """Create/validate an owner-selected root outside the canonical checkout."""
    if not isinstance(canonical_root, Path):
        canonical_root = Path(canonical_root)
    if not canonical_root.is_absolute():
        raise StoreRefused("canonical root must be an absolute path")
    _existing_components(canonical_root)
    canonical = _resolved(canonical_root)
    if not canonical.exists() or not canonical.is_dir():
        raise StoreRefused("canonical root must be an existing directory")
    candidate = _check_root(root)
    # Neither side may contain the other: this rejects the checkout itself,
    # descendants inside it, and an enclosing ancestor such as its parent.
    if _under_or_equal(candidate, canonical) or _under_or_equal(canonical, candidate):
        raise StoreRefused("private root overlaps the canonical checkout or an ancestor")
    try:
        candidate.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise StoreRefused("cannot create private root") from exc
    _existing_components(candidate)
    if not candidate.is_dir():
        raise StoreRefused("private root is not a directory")
    return candidate


def _safe_id(value: str, label: str) -> str:
    if (not isinstance(value, str) or not _ID.fullmatch(value)
            or value.upper() in _DEVICE_IDS):
        raise StoreRefused(f"invalid {label}; use 1-80 ASCII letters, digits, '_' or '-'")
    return value


def _session_dir(root: Path, session_id: str) -> Path:
    session = _safe_id(session_id, "session ID")
    base = _check_root(root)
    target = base / "sessions" / session
    _existing_components(base)
    _existing_components(target)
    try:
        target.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise StoreRefused("cannot create session directory") from exc
    _existing_components(target)
    if not target.is_dir():
        raise StoreRefused("session path is not a directory")
    return target


def journal_path(root: Path, session_id: str) -> Path:
    """Return the persistent SQLite journal path for a session."""
    target = _session_dir(root, session_id) / "journal.sqlite"
    _existing_components(target)
    if target.exists():
        info = os.lstat(target)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise StoreRefused("journal path is not a private regular file")
    return target


def persist_report(root: Path, session_id: str, trial_id: str, report) -> Path:
    """Publish one report, allowing identical retries but never overwrites."""
    trial = _safe_id(trial_id, "trial ID")
    session = _session_dir(root, session_id)
    reports = session / "reports"
    _existing_components(reports)
    try:
        reports.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise StoreRefused("cannot create reports directory") from exc
    _existing_components(reports)
    target = reports / f"{trial}.json"
    _existing_components(target)
    if target.exists():
        info = os.lstat(target)
        if not stat.S_ISREG(info.st_mode):
            raise StoreRefused("existing report is not a private regular file")
    try:
        payload = (json.dumps(report, sort_keys=True, separators=(",", ":"),
                              ensure_ascii=False) + "\n").encode("utf-8")
    except (TypeError, ValueError, UnicodeError) as exc:
        raise StoreRefused("report is not JSON-serializable") from exc

    temporary = None
    try:
        fd, temporary_name = tempfile.mkstemp(prefix=f".{trial}.", suffix=".tmp", dir=reports)
        temporary = Path(temporary_name)
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temporary, target)
        except FileExistsError:
            _existing_components(target)
            info = os.lstat(target)
            if not stat.S_ISREG(info.st_mode):
                raise StoreRefused("existing report is not a private regular file")
            try:
                existing = target.read_bytes()
            except OSError as exc:
                raise StoreRefused("existing report cannot be read safely") from exc
            if existing != payload:
                raise StoreRefused("report already exists with different content")
        return target
    except StoreRefused:
        raise
    except OSError as exc:
        raise StoreRefused("report publication refused") from exc
    finally:
        if temporary is not None:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass
            except OSError:
                # A published link remains valid; a bounded temp cleanup
                # failure must not turn success into an overwrite.
                pass
