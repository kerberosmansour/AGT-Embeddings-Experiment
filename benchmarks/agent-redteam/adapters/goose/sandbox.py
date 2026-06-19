"""OS-enforced hermetic sandbox for the M6 live adapter — Linux, stdlib-only.

The load-bearing M6 security control (CWE-918 / sandbox escape). A live agent
can attempt real actions; this sandbox makes that structurally impossible by
running tool execution in a `bwrap` jail that is:

  * **no network** (`--unshare-all` → egress default-deny; a real subprocess
    cannot reach the internet OR the cloud-metadata endpoint 169.254.169.254),
  * **scrubbed env** (`--clearenv` → no host credential is visible),
  * **no host filesystem** (only a read-only `/usr` + a fresh `tmpfs /`; the
    host home / `~/.aws` / keychain paths are not mounted).

This is NOT an in-process Python guard — those are bypassable by a subprocess.
If `bwrap` is unavailable, the sandbox is UNAVAILABLE and the live path MUST
refuse (fail-closed, never fall back to an in-process guard, never emit L3).

This module is isolated under `adapters/goose/` and is NEVER imported by the
default (mock/L2) benchmark path.
"""
import shutil
import subprocess
import sys

# Hosts a live tool must never reach; proven blocked by the egress self-test.
METADATA_IP = "169.254.169.254"


class SandboxUnavailable(RuntimeError):
    """bwrap (or user namespaces) is not available — refuse the live path."""


def available():
    return shutil.which("bwrap") is not None


def _bwrap_prefix():
    # Hermetic: no net, cleared env, read-only /usr, fresh tmpfs root, no host fs.
    return [
        "bwrap",
        "--unshare-all",                 # includes network -> egress default-deny
        "--clearenv",                    # scrubbed env -> no host credentials
        "--setenv", "PATH", "/usr/bin:/usr/local/bin",
        "--ro-bind", "/usr", "/usr",     # read-only system only
        "--symlink", "usr/lib", "/lib",
        "--symlink", "usr/lib", "/lib64",
        "--symlink", "usr/bin", "/bin",
        "--symlink", "usr/bin", "/sbin",
        "--proc", "/proc",
        "--dev", "/dev",
        "--tmpfs", "/tmp",               # writable scratch only
    ]


def run(inner_argv, *, timeout=30, input_text=None):
    """Run `inner_argv` inside the hermetic sandbox. Fail-closed if unavailable."""
    if not available():
        raise SandboxUnavailable("bwrap not found; refusing the live sandbox path")
    proc = subprocess.run(
        _bwrap_prefix() + list(inner_argv),
        capture_output=True, text=True, timeout=timeout, input=input_text,
    )
    return proc.returncode, proc.stdout, proc.stderr


# Probe executed INSIDE the sandbox to prove the three controls hold.
_SELF_TEST = (
    "import os,socket,json\n"
    "leak=[k for k in os.environ if any(s in k.upper() for s in "
    "('KEY','TOKEN','SECRET','AWS','ANTHROPIC','OPENAI'))]\n"
    "home=os.path.exists('/home') and bool(os.listdir('/home')) if os.path.exists('/home') else False\n"
    "def blocked(h):\n"
    "    try:\n"
    "        socket.create_connection((h,80),timeout=2); return False\n"
    "    except OSError: return True\n"
    "print(json.dumps({'env_scrubbed': not leak, 'no_host_home': not home, "
    "'egress_inet_blocked': blocked('1.1.1.1'), "
    "'egress_metadata_blocked': blocked('169.254.169.254')}))\n"
)


def self_test(timeout=15):
    """Return the sandbox control results (all must be True to allow --live)."""
    import json
    rc, out, err = run([sys.executable, "-c", _SELF_TEST], timeout=timeout)
    if rc != 0:
        raise SandboxUnavailable(f"sandbox self-test failed to run: {err.strip()}")
    return json.loads(out.strip().splitlines()[-1])


def assert_secure():
    """Raise SandboxUnavailable unless every control holds. Call before any --live run."""
    results = self_test()
    failed = [k for k, ok in results.items() if not ok]
    if failed:
        raise SandboxUnavailable(f"sandbox controls NOT satisfied: {failed} ({results})")
    return results


if __name__ == "__main__":
    import json
    try:
        print(json.dumps(assert_secure(), sort_keys=True))
    except SandboxUnavailable as exc:
        print(f"SANDBOX UNAVAILABLE: {exc}", file=sys.stderr)
        raise SystemExit(1)
