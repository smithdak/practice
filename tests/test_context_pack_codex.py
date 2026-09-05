import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import context_pack_codex as codex


def events(*rows):
    return "".join(json.dumps(row, separators=(",", ":")) + "\n" for row in rows)


def pid_alive(pid):
    if os.name != "nt":
        try:
            os.kill(pid, 0)
            return True
        except (ProcessLookupError, PermissionError):
            return False
    import ctypes
    kernel = ctypes.windll.kernel32
    handle = kernel.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
    if not handle:
        return False
    code = ctypes.c_ulong()
    try:
        return bool(kernel.GetExitCodeProcess(handle, ctypes.byref(code)) and code.value == 259)
    finally:
        kernel.CloseHandle(handle)


class CodexEventTests(unittest.TestCase):
    def completed(self, usage=None, text="{\"ok\":true}"):
        return events({"type": "thread.started"}, {"type": "turn.started"},
                      {"type": "item.completed", "item": {"type": "agent_message", "text": text}},
                      {"type": "turn.completed", "usage": usage})

    def test_single_jsonl_turn_preserves_text_usage_and_unknown_cost(self):
        result = codex.parse_events(self.completed({"input_tokens": 4, "cached_input_tokens": 1,
                                                    "output_tokens": 3, "reasoning_output_tokens": 2}))
        self.assertEqual(result, {"text": '{"ok":true}',
                                  "usage": {"input_tokens": 4, "cached_input_tokens": 1,
                                             "output_tokens": 3, "reasoning_output_tokens": 2},
                                  "cost_microusd": None})
        self.assertIsNone(codex.parse_events(self.completed(None))["usage"])

    def test_malformed_unknown_error_and_tool_events_are_refused_without_echo(self):
        streams = [
            "not-json\n",
            events({"type": "provider.error", "message": "SECRET_TOKEN"}),
            events({"type": "turn.started"}, {"type": "item.completed",
                                                   "item": {"type": "tool_call", "input": "SECRET_TOKEN"}}),
            events({"type": "turn.started"}, {"type": "turn.completed", "usage": None}),
        ]
        for stream in streams:
            with self.subTest(stream=stream):
                with self.assertRaises(codex.TransportRefused) as caught:
                    codex.parse_events(stream)
                self.assertNotIn("SECRET_TOKEN", str(caught.exception))

    def test_missing_completion_and_invalid_usage_are_refused(self):
        missing = events({"type": "thread.started"}, {"type": "turn.started"},
                         {"type": "item.completed", "item": {"type": "agent_message", "text": "x"}})
        with self.assertRaises(codex.TransportRefused):
            codex.parse_events(missing)
        for usage in ({"input_tokens": -1}, {"output_tokens": "3"}, [], {"input_tokens": True}):
            with self.subTest(usage=usage), self.assertRaises(codex.TransportRefused):
                codex.parse_events(self.completed(usage))

    def test_event_after_completion_and_multiple_turns_are_refused(self):
        after = self.completed(None) + events({"type": "thread.started"})
        with self.assertRaises(codex.TransportRefused):
            codex.parse_events(after)
        multiple = events({"type": "turn.started"}, {"type": "turn.completed", "usage": None},
                          {"type": "turn.started"})
        with self.assertRaises(codex.TransportRefused):
            codex.parse_events(multiple)

    def test_parse_event_and_prompt_byte_limits(self):
        with self.assertRaises(codex.TransportRefused):
            codex.parse_events("{}" * ((codex.MAX_STDOUT_BYTES // 2) + 1))
        with self.assertRaises(codex.TransportRefused):
            codex.run_bounded([sys.executable, "-c", ""], "x" * (codex.MAX_PROMPT_BYTES + 1),
                              Path.cwd(), dict(), 1)


class CodexEnvironmentTests(unittest.TestCase):
    def test_environment_allows_only_local_runtime_paths(self):
        source = {"PATH": "path", "SYSTEMROOT": "root", "TEMP": "temp", "HOME": "home",
                  "CODEX_HOME": "codex", "OPENAI_API_KEY": "secret", "HTTPS_PROXY": "proxy",
                  "HTTP_PROXY": "proxy", "CODEX_THREAD_ID": "session", "CODEX_SESSION_ID": "session",
                  "LD_PRELOAD": "bad"}
        cleaned = codex.clean_environment(source)
        self.assertEqual(cleaned, {"PATH": "path", "SYSTEMROOT": "root", "TEMP": "temp",
                                   "HOME": "home", "CODEX_HOME": "codex"})


class CodexCommandTests(unittest.TestCase):
    def test_command_is_pinned_and_explicitly_restrictive(self):
        schema = Path("/tmp/schema.json")
        command = codex.command_for(Path("/runtime/codex"), schema)
        self.assertEqual(command[-1], "-")
        for flag in ("--strict-config", "--ignore-user-config", "--ignore-rules", "--ephemeral",
                     "--sandbox", "read-only", "--json", "--model", codex.PILOT_MODEL,
                     "--output-schema", str(schema)):
            self.assertIn(flag, command)
        self.assertNotIn("shell", command[:3])
        overrides = [command[i + 1] for i, value in enumerate(command[:-1]) if value == "-c"]
        self.assertIn('model_reasoning_effort="medium"', overrides)
        self.assertIn('cli_auth_credentials_store="file"', overrides)
        self.assertIn('approval_policy="never"', overrides)
        self.assertIn('shell_environment_policy.inherit="none"', overrides)
        self.assertTrue(all(feature in command for feature in codex.DISABLED_FEATURES))


class CodexTransportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.runtime = base / "runtime"
        self.home = self.runtime / "codex-home"
        self.runtime.mkdir()
        self.home.mkdir()

    def transport(self, **kwargs):
        original_exists = Path.exists

        def exists(path):
            # The host user's real .codex policy must not contaminate this
            # synthetic temp runtime fixture.
            if path.name in {".git", "AGENTS.md"} or path.name == "config.toml" and ".codex" in path.parts:
                return False
            return original_exists(path)

        with mock.patch.object(Path, "exists", exists):
            return codex.CodexTransport(sys.executable, self.runtime, self.home, **kwargs)

    def run_child(self, code, timeout=2, cancel=lambda: False):
        env = codex.clean_environment({"PATH": str(Path(sys.executable).parent),
                                       "SYSTEMROOT": str(Path(sys.executable).anchor),
                                       "TEMP": str(Path.cwd())})
        return codex.run_bounded([sys.executable, "-c", code], "hello", self.runtime,
                                 env, timeout, cancel)

    def test_constructor_requires_real_isolated_paths_and_preflight_is_local(self):
        transport = self.transport(isolated_runtime_confirmed=True)
        calls = []

        def fake(command, prompt, cwd, env, timeout, cancel=lambda: False, **kwargs):
            calls.append((command, prompt, cwd, env, kwargs))
            if command[1:] == ["--version"]:
                return codex.SUPPORTED_VERSION + "\n"
            return "Logged in using ChatGPT"

        with mock.patch.object(codex, "run_bounded", side_effect=fake):
            result = transport.preflight()
        self.assertTrue(result["chatgpt_authenticated"])
        self.assertTrue(result["ready_for_supervised_run"])
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[1][4], {"include_stderr": True})
        self.assertEqual(calls[1][3]["CODEX_HOME"], str(self.home.resolve()))

    def test_preflight_refuses_version_mismatch_and_missing_auth(self):
        transport = self.transport(isolated_runtime_confirmed=True)
        with mock.patch.object(codex, "run_bounded", return_value="wrong\n"):
            with self.assertRaises(codex.TransportRefused):
                transport.preflight()
        calls = iter([codex.SUPPORTED_VERSION + "\n", "not-authenticated"])
        with mock.patch.object(codex, "run_bounded", side_effect=lambda *a, **k: next(calls)):
            result = transport.preflight()
        self.assertFalse(result["chatgpt_authenticated"])
        self.assertFalse(result["ready_for_supervised_run"])

    def test_call_requires_owner_isolation_before_preflight_and_valid_envelope(self):
        transport = self.transport(isolated_runtime_confirmed=False)
        with mock.patch.object(transport, "preflight") as preflight:
            with self.assertRaises(codex.TransportRefused):
                transport({"system": "s", "prompt": "p", "request_id": "r",
                            "model": codex.PILOT_MODEL, "reasoning_effort": codex.PILOT_REASONING_EFFORT})
        preflight.assert_not_called()
        transport = self.transport(isolated_runtime_confirmed=True)
        base = {"system": "s", "prompt": "p", "request_id": "r",
                "model": codex.PILOT_MODEL, "reasoning_effort": codex.PILOT_REASONING_EFFORT}
        for bad in (dict(base, model="other"), dict(base, reasoning_effort="high"),
                    dict(base, extra="x")):
            with self.subTest(bad=bad), self.assertRaises(codex.TransportRefused):
                transport(bad)

    def test_cancel_kills_descendant_process(self):
        if os.name == "nt" and not hasattr(subprocess, "CREATE_NEW_PROCESS_GROUP"):
            self.skipTest("Windows process-group controls unavailable")
        pid_file = Path(self.temp.name) / "child.pid"
        child_code = "import time; time.sleep(30)"
        code = ("import pathlib,subprocess,sys,time; "
                f"p=subprocess.Popen([sys.executable,'-c',{child_code!r}]); "
                f"pathlib.Path({str(pid_file)!r}).write_text(str(p.pid)); "
                "sys.stdout.flush(); p.wait()")
        started = time.monotonic()
        with self.assertRaises(codex.TransportRefused):
            self.run_child(code, timeout=3, cancel=lambda: pid_file.exists() and time.monotonic() - started > .15)
        child_pid = int(pid_file.read_text())
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            if not pid_alive(child_pid):
                break
            time.sleep(.05)
        else:
            self.fail("descendant survived cancellation")


class CodexProcessTests(unittest.TestCase):
    def run_child(self, code, prompt="hello", timeout=2, cancel=lambda: False):
        env = codex.clean_environment({"PATH": str(Path(sys.executable).parent),
                                       "SYSTEMROOT": str(Path(sys.executable).anchor),
                                       "TEMP": str(Path.cwd())})
        return codex.run_bounded([sys.executable, "-c", code], prompt, Path.cwd(), env, timeout, cancel)

    def test_successful_stdin_and_stdout(self):
        code = "import sys,json; value=sys.stdin.read(); print(json.dumps({'received':value}))"
        self.assertEqual(json.loads(self.run_child(code)), {"received": "hello"})

    def test_timeout_is_sanitized_and_process_is_stopped(self):
        code = "import time; time.sleep(5)"
        started = time.monotonic()
        with self.assertRaisesRegex(codex.TransportRefused, "uncertain"):
            self.run_child(code, timeout=0.1)
        self.assertLess(time.monotonic() - started, 3)

    def test_output_flood_is_byte_bounded(self):
        code = "import sys; sys.stdout.write('x' * 400000); sys.stdout.flush()"
        with self.assertRaisesRegex(codex.TransportRefused, "byte limit"):
            self.run_child(code)
        code = "import sys; sys.stderr.write('x' * 50000); sys.stderr.flush()"
        with self.assertRaisesRegex(codex.TransportRefused, "byte limit"):
            self.run_child(code)

    def test_nonzero_exit_is_sanitized(self):
        code = "import sys; sys.stderr.write('SECRET_PATH'); sys.exit(7)"
        with self.assertRaises(codex.TransportRefused) as caught:
            self.run_child(code)
        self.assertNotIn("SECRET_PATH", str(caught.exception))

    def test_tool_event_stops_live_capture_before_child_completes(self):
        code = ("import json,time; "
                "print(json.dumps({'type':'item.started','item':{'type':'command_execution'}}), flush=True); "
                "time.sleep(5)")
        started = time.monotonic()
        with self.assertRaisesRegex(codex.TransportRefused, "tool activity"):
            codex.run_bounded([sys.executable, "-c", code], "", Path.cwd(),
                              codex.clean_environment(), 3, event_stream=True)
        self.assertLess(time.monotonic() - started, 3)

    def test_cancellation_callback_stops_running_child(self):
        started = time.monotonic()
        code = "import time; time.sleep(5)"
        with self.assertRaisesRegex(codex.TransportRefused, "uncertain"):
            self.run_child(code, timeout=3, cancel=lambda: time.monotonic() - started > 0.15)
        self.assertLess(time.monotonic() - started, 3)


if __name__ == "__main__":
    unittest.main()
