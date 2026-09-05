"""ChatGPT-backed Codex transport. No credentials or raw diagnostics in results.

This is a trusted-process boundary, not an OS sandbox. Production use requires
an independently isolated runtime; the adapter does not copy authentication.
One invocation is not one billable request: provider-side retries/cancellation
and ChatGPT quota consumption cannot be inferred from this process count.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import queue
import re
import signal
import stat
import subprocess
import threading
import time
import tempfile

from context_pack_trial import PILOT_MODEL, PILOT_REASONING_EFFORT

MAX_PROMPT_BYTES = 65536
MAX_STDOUT_BYTES = 262144
MAX_STDERR_BYTES = 32768
MAX_TIMEOUT_SECONDS = 300
SUPPORTED_VERSION = "codex-cli 0.153.0"
DISABLED_FEATURES = (
    "shell_tool", "apps", "hooks", "multi_agent", "plugins",
    "skill_search", "skill_mcp_dependency_install", "browser_use", "computer_use",
    "image_generation", "view_image", "memories", "goals", "code_mode_host",
    "unbounded_connection_retries",
)


class TransportRefused(RuntimeError):
    """Sanitized refusal; ambiguous invocations remain reserved in the journal."""


def clean_environment(source=None):
    """Only local identity/system paths; no API keys, proxies, or session IDs."""
    source = os.environ if source is None else source
    allowed = {"SYSTEMROOT", "WINDIR", "PATH", "PATHEXT", "TEMP", "TMP",
               "USERPROFILE", "HOME", "LOCALAPPDATA", "APPDATA", "CODEX_HOME"}
    return {key: value for key, value in source.items() if key.upper() in allowed}


def parse_events(stdout):
    """Accept a single completed, text-only turn; fail on tool activity/errors."""
    if len(stdout.encode("utf-8")) > MAX_STDOUT_BYTES:
        raise TransportRefused("Codex output exceeded its local byte limit")
    messages, usage = [], None
    started = completed = 0
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except (TypeError, ValueError):
            raise TransportRefused("Malformed Codex event stream") from None
        if not isinstance(event, dict):
            raise TransportRefused("Malformed Codex event stream")
        kind = event.get("type")
        if completed:
            raise TransportRefused("Event after completed turn; do not retry")
        if kind == "thread.started":
            continue
        if kind == "turn.started":
            started += 1
            if started != 1:
                raise TransportRefused("Multiple turns are not a bounded invocation")
        elif kind == "turn.completed":
            if started != 1:
                raise TransportRefused("Completion without a started turn")
            completed += 1
            raw = event.get("usage")
            if raw is not None:
                if not isinstance(raw, dict):
                    raise TransportRefused("Malformed usage metadata")
                usage = {}
                for key in ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens"):
                    if key in raw:
                        if type(raw[key]) is not int or raw[key] < 0:
                            raise TransportRefused("Malformed usage metadata")
                        usage[key] = raw[key]
        elif kind in ("item.started", "item.updated", "item.completed"):
            if started != 1:
                raise TransportRefused("Item outside a started turn")
            item = event.get("item")
            if not isinstance(item, dict) or item.get("type") not in ("agent_message", "reasoning"):
                raise TransportRefused("Unexpected tool activity or item; do not retry")
            if kind == "item.completed" and item["type"] == "agent_message":
                text = item.get("text")
                if not isinstance(text, str) or not text or len(text) > 65536:
                    raise TransportRefused("Malformed final response")
                messages.append(text)
        else:
            # Never echo provider error text: it may contain paths or credentials.
            raise TransportRefused("Codex failed or emitted an unsupported event; do not retry")
    if started != 1 or completed != 1 or len(messages) != 1:
        raise TransportRefused("Expected one completed text-only turn; do not retry")
    return {"text": messages[0], "usage": usage, "cost_microusd": None}


class _WindowsJob:
    """Kill-on-close job: descendants cannot outlive a cancelled invocation."""

    def __init__(self, process):
        import ctypes
        from ctypes import wintypes

        class Basic(ctypes.Structure):
            _fields_ = [("PerProcessUserTimeLimit", ctypes.c_longlong),
                        ("PerJobUserTimeLimit", ctypes.c_longlong),
                        ("LimitFlags", wintypes.DWORD),
                        ("MinimumWorkingSetSize", ctypes.c_size_t),
                        ("MaximumWorkingSetSize", ctypes.c_size_t),
                        ("ActiveProcessLimit", wintypes.DWORD),
                        ("Affinity", ctypes.c_size_t),
                        ("PriorityClass", wintypes.DWORD),
                        ("SchedulingClass", wintypes.DWORD)]

        class Io(ctypes.Structure):
            _fields_ = [(name, ctypes.c_ulonglong) for name in
                        ("ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
                         "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]

        class Extended(ctypes.Structure):
            _fields_ = [("BasicLimitInformation", Basic), ("IoInfo", Io),
                        ("ProcessMemoryLimit", ctypes.c_size_t), ("JobMemoryLimit", ctypes.c_size_t),
                        ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t)]

        self.api = ctypes.WinDLL("kernel32", use_last_error=True)
        self.api.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
        self.api.CreateJobObjectW.restype = wintypes.HANDLE
        self.api.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
        self.api.SetInformationJobObject.restype = wintypes.BOOL
        self.api.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        self.api.AssignProcessToJobObject.restype = wintypes.BOOL
        self.api.CloseHandle.argtypes = [wintypes.HANDLE]
        self.api.CloseHandle.restype = wintypes.BOOL
        self.handle = self.api.CreateJobObjectW(None, None)
        limits = Extended()
        limits.BasicLimitInformation.LimitFlags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if (not self.handle or not self.api.SetInformationJobObject(self.handle, 9, ctypes.byref(limits), ctypes.sizeof(limits))
                or not self.api.AssignProcessToJobObject(self.handle, int(process._handle))):
            self.close()
            raise TransportRefused("Cannot establish Windows invocation process containment")

    def close(self):
        if self.handle:
            self.api.CloseHandle(self.handle)
            self.handle = None


def _terminate_tree(process):
    """Cancel the exact launched process tree, never a name-based process sweep."""
    if os.name == "nt":
        system_root = os.environ.get("SYSTEMROOT", r"C:\Windows")
        killer = Path(system_root) / "System32" / "taskkill.exe"
        try:
            subprocess.run([str(killer), "/PID", str(process.pid), "/T", "/F"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           timeout=10, creationflags=subprocess.CREATE_NO_WINDOW, check=False)
        finally:
            if process.poll() is None:
                process.kill()
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    process.wait(timeout=10)


def run_bounded(command, prompt, cwd, env, timeout_seconds, cancel=lambda: False, *, include_stderr=False,
                event_stream=False):
    """Bound process time and captured bytes. No shell, unbounded pipes, or retry."""
    if type(timeout_seconds) not in (int, float) or not 0 < timeout_seconds <= MAX_TIMEOUT_SECONDS:
        raise TransportRefused("Timeout must be positive and at most 300 seconds")
    payload = prompt.encode("utf-8")
    if len(payload) > MAX_PROMPT_BYTES:
        raise TransportRefused("Prompt exceeded its local byte limit")
    if cancel():
        raise TransportRefused("Owner stopped the invocation before launch")
    options = ({"creationflags": subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP}
               if os.name == "nt" else {"start_new_session": True})
    try:
        process = subprocess.Popen(command, cwd=cwd, env=env, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   shell=False, **options)
    except OSError:
        raise TransportRefused("Could not launch the pinned Codex executable") from None
    job = None
    try:
        if os.name == "nt":
            job = _WindowsJob(process)
    except BaseException:
        _terminate_tree(process)
        for stream in (process.stdin, process.stdout, process.stderr):
            stream.close()
        raise
    chunks = queue.Queue(maxsize=64)
    stop_reading = threading.Event()

    def collect(stream, name):
        try:
            while not stop_reading.is_set():
                chunk = stream.read1(4096)
                if not chunk:
                    break
                while not stop_reading.is_set():
                    try:
                        chunks.put((name, chunk), timeout=0.1)
                        break
                    except queue.Full:
                        pass
        finally:
            while not stop_reading.is_set():
                try:
                    chunks.put((name, None), timeout=0.1)
                    break
                except queue.Full:
                    pass

    def feed():
        try:
            process.stdin.write(payload)
            process.stdin.close()
        except (BrokenPipeError, OSError):
            pass

    readers = [threading.Thread(target=collect, args=(process.stdout, "out"), daemon=True),
               threading.Thread(target=collect, args=(process.stderr, "err"), daemon=True)]
    writer = threading.Thread(target=feed, daemon=True)
    for thread in [*readers, writer]:
        thread.start()
    collected = {"out": bytearray(), "err": bytearray()}
    limits = {"out": MAX_STDOUT_BYTES, "err": MAX_STDERR_BYTES}
    finished = set()
    event_buffer = bytearray()
    deadline = time.monotonic() + timeout_seconds
    try:
        while len(finished) < 2 or process.poll() is None:
            if cancel() or time.monotonic() >= deadline:
                raise TransportRefused("Codex cancelled or timed out; outcome uncertain, do not retry")
            try:
                name, chunk = chunks.get(timeout=0.05)
            except queue.Empty:
                continue
            if chunk is None:
                finished.add(name)
            else:
                if len(collected[name]) + len(chunk) > limits[name]:
                    raise TransportRefused("Codex output exceeded its local byte limit; do not retry")
                collected[name].extend(chunk)
                if event_stream and name == "out":
                    event_buffer.extend(chunk)
                    while b"\n" in event_buffer:
                        line, _, remainder = event_buffer.partition(b"\n")
                        event_buffer = bytearray(remainder)
                        try:
                            event = json.loads(line)
                        except (ValueError, UnicodeError):
                            raise TransportRefused("Malformed live event; do not retry") from None
                        if not isinstance(event, dict):
                            raise TransportRefused("Malformed live event; do not retry")
                        kind = event.get("type")
                        if kind not in ("thread.started", "turn.started", "turn.completed",
                                        "item.started", "item.updated", "item.completed"):
                            raise TransportRefused("Unexpected live event; outcome uncertain, do not retry")
                        if kind.startswith("item."):
                            item = event.get("item")
                            if not isinstance(item, dict) or item.get("type") not in ("agent_message", "reasoning"):
                                raise TransportRefused("Unexpected tool activity; outcome uncertain, do not retry")
        if process.returncode != 0:
            raise TransportRefused("Codex exited unsuccessfully; outcome uncertain, do not retry")
        try:
            output = collected["out"] + (collected["err"] if include_stderr else b"")
            return output.decode("utf-8")
        except UnicodeDecodeError:
            raise TransportRefused("Codex output was not UTF-8") from None
    finally:
        stop_reading.set()
        if job is not None:
            job.close()
            process.wait(timeout=10)
        elif os.name != "nt" or process.poll() is None:
            _terminate_tree(process)
        for thread in [*readers, writer]:
            thread.join(timeout=1)
        for stream in (process.stdin, process.stdout, process.stderr):
            if not stream.closed:
                stream.close()


def command_for(executable, schema_path):
    """Pinned documented controls, not a claim that all tools are unavailable."""
    args = [str(executable), "exec", "--strict-config", "--ignore-user-config", "--ignore-rules",
            "--ephemeral", "--skip-git-repo-check", "--sandbox", "read-only", "--json",
            "--output-schema", str(schema_path), "--model", PILOT_MODEL, "--color", "never"]
    for feature in DISABLED_FEATURES:
        args.extend(["--disable", feature])
    for override in ('forced_login_method="chatgpt"', 'model_reasoning_effort="medium"',
                     'cli_auth_credentials_store="file"',
                     'approval_policy="never"', 'web_search="disabled"', 'tools.view_image=false',
                     'history.persistence="none"', 'project_doc_max_bytes=0',
                     'shell_environment_policy.inherit="none"'):
        args.extend(["-c", override])
    return args + ["-"]


OUTPUT_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["checks", "escalate_to", "launch_approved"],
    "properties": {
        "checks": {"type": "array", "items": {"type": "object", "additionalProperties": False,
            "required": ["id", "status", "source"], "properties": {
                "id": {"type": "string"}, "status": {"type": "string", "enum": ["pass", "fail", "unknown"]},
                "source": {"type": "string"}}}},
        "escalate_to": {"type": ["string", "null"], "enum": ["release-maintainer", None]},
        "launch_approved": {"type": "boolean"},
    },
}


class CodexTransport:
    """Explicitly owner-attested isolated runtime; never default desktop auth.

    The attestation is an operator prerequisite, not a technical isolation
    proof. CLI controls alone cannot remove every tool, so this must not be
    enabled against a shared desktop profile or an untrusted CI checkout.
    """

    def __init__(self, executable, runtime_root, codex_home, *, isolated_runtime_confirmed=False,
                 timeout_seconds=180, cancel=lambda: False):
        from context_pack_store import _existing_components
        self.executable = Path(executable)
        self.runtime_root, self.codex_home = Path(runtime_root), Path(codex_home)
        for path in (self.executable, self.runtime_root, self.codex_home):
            if not path.is_absolute():
                raise TransportRefused("Executable and isolated runtime paths must be absolute")
            _existing_components(path)
        if not self.executable.is_file() or (os.name == "nt" and self.executable.suffix.lower() != ".exe"):
            raise TransportRefused("Use an explicit native Codex executable, not a shell wrapper")
        if not self.runtime_root.is_dir() or not self.codex_home.is_dir():
            raise TransportRefused("Isolated runtime and its separately authenticated Codex home must exist")
        self.runtime_root, self.codex_home = self.runtime_root.resolve(), self.codex_home.resolve()
        if not self.codex_home.is_relative_to(self.runtime_root) or self.codex_home == self.runtime_root:
            raise TransportRefused("Codex home must be a dedicated child of the isolated runtime")
        default_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))).resolve()
        if self.codex_home == default_home:
            raise TransportRefused("Do not reuse the driving desktop's Codex home")
        auth_path = self.codex_home / "auth.json"
        _existing_components(auth_path)
        if auth_path.exists():
            info = auth_path.stat()
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                raise TransportRefused("Isolated credentials must not use a linked/shared file")
        for parent in (self.runtime_root, *self.runtime_root.parents):
            if (parent / ".git").exists() or (parent / "AGENTS.md").exists() or (parent / ".codex" / "config.toml").exists():
                raise TransportRefused("Isolated runtime must not inherit a repository or ancestor agent configuration")
        self.isolated_runtime_confirmed = isolated_runtime_confirmed is True
        self.timeout_seconds, self.cancel = timeout_seconds, cancel
        self.env = clean_environment()
        self.env["CODEX_HOME"] = str(self.codex_home)

    def preflight(self):
        """Local version/auth diagnostics only; never opens or copies auth files."""
        version = run_bounded([str(self.executable), "--version"], "", self.runtime_root, self.env, 10).strip()
        if version != SUPPORTED_VERSION:
            raise TransportRefused("Codex version differs from the verified adapter contract")
        # login status prints to stderr on this release. Keep the same bounded
        # capture/process containment and never return its raw diagnostics.
        try:
            status = run_bounded([str(self.executable), "-c", 'cli_auth_credentials_store="file"',
                                  "login", "status"], "", self.runtime_root, self.env, 10, include_stderr=True)
            authenticated = status.strip() == "Logged in using ChatGPT"
        except TransportRefused:
            authenticated = False
        return {"cli_version": version, "chatgpt_authenticated": authenticated,
                "isolated_runtime_confirmed_by_owner": self.isolated_runtime_confirmed,
                "global_tool_deny_verified": False,
                "ready_for_supervised_run": authenticated and self.isolated_runtime_confirmed,
                "unattended_ready": False}

    def __call__(self, request):
        if set(request) != {"system", "prompt", "request_id", "model", "reasoning_effort"}:
            raise TransportRefused("Expected a request-accounted text-only envelope")
        if (request["model"], request["reasoning_effort"]) != (PILOT_MODEL, PILOT_REASONING_EFFORT):
            raise TransportRefused("Selected model or reasoning changed")
        if not self.isolated_runtime_confirmed:
            raise TransportRefused("Owner has not confirmed an independently isolated runtime")
        if not self.preflight()["ready_for_supervised_run"]:
            raise TransportRefused("Isolated ChatGPT authentication is not ready")
        if not all(isinstance(request[key], str) for key in ("system", "prompt", "request_id")):
            raise TransportRefused("Malformed text-only request")
        # The CLI retains its built-in instructions. We do not falsely claim
        # this text replaces the provider system message or exactly matches API behavior.
        prompt = request["system"] + "\n\n" + request["prompt"]
        with tempfile.TemporaryDirectory(prefix="invocation-", dir=self.runtime_root) as directory:
            cwd = Path(directory)
            schema = cwd / "response-schema.json"
            schema.write_text(json.dumps(OUTPUT_SCHEMA), encoding="utf-8")
            output = run_bounded(command_for(self.executable, schema), prompt, cwd, self.env,
                                 self.timeout_seconds, self.cancel, event_stream=True)
            return parse_events(output)
