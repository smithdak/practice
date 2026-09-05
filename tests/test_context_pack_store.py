from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import context_pack_store as store


class PrivateStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.canonical = self.base / "checkout"
        self.canonical.mkdir()
        self.private = self.base / "private"

    def test_prepare_root_is_outside_checkout_and_allows_nonempty(self):
        (self.private / "existing.txt").parent.mkdir(parents=True)
        (self.private / "existing.txt").write_text("keep", encoding="utf-8")
        self.assertEqual(store.prepare_private_root(self.private, self.canonical), self.private)
        with self.assertRaises(store.StoreRefused):
            store.prepare_private_root(self.canonical / "private", self.canonical)
        with self.assertRaises(store.StoreRefused):
            store.prepare_private_root(self.canonical.parent, self.canonical)

    def test_ids_are_strict_and_journal_is_separate(self):
        root = store.prepare_private_root(self.private, self.canonical)
        journal = store.journal_path(root, "session_1")
        self.assertEqual(journal, root / "sessions" / "session_1" / "journal.sqlite")
        self.assertNotEqual(journal.parent, root / "sessions" / "session_1" / "reports")
        for value in ("", ".", "../x", "a/b", "a\\b", "é", "a" * 81,
                      "CON", "nul", "AUX", "PRN", "COM1", "LPT9"):
            with self.subTest(value=value), self.assertRaises(store.StoreRefused):
                store.journal_path(root, value)
            with self.subTest(value=value), self.assertRaises(store.StoreRefused):
                store.persist_report(root, "ok", value, {"x": 1})

        link_target = self.base / "journal-target"
        link_target.write_text("", encoding="utf-8")
        try:
            journal.symlink_to(link_target)
        except (OSError, NotImplementedError):
            self.skipTest("filesystem does not support symlinks")
        with self.assertRaises(store.StoreRefused):
            store.journal_path(root, "session_1")

    def test_idempotence_and_conflict(self):
        root = store.prepare_private_root(self.private, self.canonical)
        first = store.persist_report(root, "session", "trial-1", {"b": 2, "a": 1})
        self.assertEqual(first.read_bytes(), b'{"a":1,"b":2}\n')
        self.assertEqual(store.persist_report(root, "session", "trial-1", {"a": 1, "b": 2}), first)
        with self.assertRaises(store.StoreRefused):
            store.persist_report(root, "session", "trial-1", {"a": 3})
        self.assertEqual(first.read_bytes(), b'{"a":1,"b":2}\n')

    def test_directory_and_file_symlinks_are_refused_when_supported(self):
        root = store.prepare_private_root(self.private, self.canonical)
        outside = self.base / "outside"
        outside.mkdir()
        linked_dir = root / "sessions"
        try:
            linked_dir.symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            linked_dir = None
        if linked_dir is None:
            self.skipTest("filesystem does not support directory symlinks")
        with self.assertRaises(store.StoreRefused):
            store.persist_report(root, "s", "t", {"x": 1})
        self.assertFalse((outside / "s").exists(), "refusal must not create outside session data")

        # Use a fresh root so the directory-link check does not interfere.
        root = store.prepare_private_root(self.base / "private-files", self.canonical)
        reports = root / "sessions" / "s" / "reports"
        reports.mkdir(parents=True)
        target = reports / "t.json"
        try:
            target.symlink_to(outside / "target.json")
        except (OSError, NotImplementedError):
            self.skipTest("filesystem does not support symlinks")
        with self.assertRaises(store.StoreRefused):
            store.persist_report(root, "s", "t", {"x": 1})

    def test_reparse_component_is_refused(self):
        with patch.object(store, "_reparse", return_value=True):
            with self.assertRaises(store.StoreRefused):
                store.prepare_private_root(self.private, self.canonical)

    def test_existing_hardlinks_are_not_treated_as_private_targets(self):
        root = store.prepare_private_root(self.private, self.canonical)
        report = store.persist_report(root, "s", "t", {"x": 1})
        report_link = self.base / "report-link.json"
        report_link.hardlink_to(report)
        self.assertEqual(store.persist_report(root, "s", "t", {"x": 1}), report)
        self.assertEqual(report_link.read_bytes(), b'{"x":1}\n')
        journal = store.journal_path(root, "s")
        journal.write_text("", encoding="utf-8")
        journal_link = self.base / "journal-link.sqlite"
        journal_link.hardlink_to(journal)
        with self.assertRaises(store.StoreRefused):
            store.journal_path(root, "s")

    def test_concurrent_same_report_publishes_one_consistent_file(self):
        root = store.prepare_private_root(self.private, self.canonical)
        results = []
        errors = []

        def publish():
            try:
                results.append(store.persist_report(root, "parallel", "trial", {"value": 7}))
            except Exception as exc:  # assert all errors below with context
                errors.append(exc)

        threads = [threading.Thread(target=publish) for _ in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertFalse(errors, errors)
        self.assertEqual(len(results), 8)
        target = root / "sessions" / "parallel" / "reports" / "trial.json"
        self.assertEqual(target.read_bytes(), b'{"value":7}\n')


if __name__ == "__main__":
    unittest.main()
