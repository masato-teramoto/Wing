#!/usr/bin/env python3
"""Project-local launcher. No installation, network access or workflow policy."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
COMMON = ROOT / ".claude/skills/aidd-common"
STATE = ROOT / ".aidd/phase-progress.json"
ENTRIES = ("aidd-requirements-init", "aidd-requirements", "aidd-design", "aidd-tasks", "aidd-implement")


def command(mode, arguments):
    python = [sys.executable, "-X", "utf8", "-B"]
    if sys.flags.no_site:
        python.append("-S")
    if mode == "engine":
        return python + [str(COMMON / "bin/aidd.py"), "--root", str(ROOT),
                         "--state", str(STATE), "--config", str(COMMON)] + arguments
    return python + [str(COMMON / "scripts/workflow.py"), "--root", str(ROOT),
                     "--state", str(STATE)] + arguments


def doctor(runtime_only=False):
    """Read-only checks; never create state, logs, bytecode or approvals."""
    checks = []

    def check(name, passed, detail):
        checks.append({"name": name, "ok": bool(passed), "detail": detail})

    check("python", sys.version_info >= (3, 9), sys.version.split()[0])
    try:
        manifest = json.loads((ROOT / ".main-flow-assets.json").read_text(encoding="utf-8"))
        if manifest.get("schema") != 1 or not isinstance(manifest.get("assets"), dict):
            raise ValueError("invalid asset manifest")
        required = list(manifest["assets"]) + ["CLAUDE.md", ".claude/agents/check-runner.md"]
        required += [".claude/skills/%s/SKILL.md" % entry for entry in ENTRIES]
        missing = [name for name in required if not (ROOT / name).is_file()]
        check("assets", not missing, missing or "%d deployed assets" % len(manifest["assets"]))
        for path in COMMON.rglob("*.py"):
            compile(path.read_bytes(), str(path), "exec")
        check("python_sources", True, "syntax checked without bytecode")
    except (ValueError, OSError, SyntaxError) as error:
        check("assets", False, str(error))
    try:
        validation = subprocess.run(command("engine", ["validate", "--json"]), cwd=ROOT,
                                    capture_output=True, encoding="utf-8", timeout=30)
        data = json.loads(validation.stdout)
        check("engine_config", validation.returncode == 0, data if validation.returncode else "valid")
    except (ValueError, OSError, subprocess.TimeoutExpired) as error:
        check("engine_config", False, str(error))
    inputs = [p.relative_to(ROOT).as_posix() for p in (ROOT / ".aidd/rfp").rglob("*")
              if p.is_file() and not any(part.startswith(".") for part in p.relative_to(ROOT / ".aidd/rfp").parts)]
    check("rfp", bool(inputs), sorted(inputs) or "Place an RFP in .aidd/rfp/ before starting.")
    if not runtime_only:
        claude = shutil.which("claude")
        try:
            if not claude:
                raise OSError("Claude Code CLI is not on PATH. See README.md.")
            version = subprocess.run([claude, "--version"], capture_output=True,
                                     encoding="utf-8", timeout=15)
            check("claude_code", version.returncode == 0, version.stdout.strip() or version.stderr.strip())
        except (OSError, subprocess.TimeoutExpired) as error:
            check("claude_code", False, str(error))
    ok = all(item["ok"] for item in checks)
    print(json.dumps({"status": "ready" if ok else "not_ready", "root": str(ROOT),
                      "python": sys.executable, "runtime_only": runtime_only,
                      "checks": checks,
                      "note": "Login, project trust and LLM generation are checked in the Claude Code session."},
                     ensure_ascii=False, indent=2))
    return 0 if ok else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("doctor", "engine", "workflow"))
    parser.add_argument("arguments", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if sys.version_info < (3, 9):
        parser.exit(1, "Python 3.9 or later is required.\n")
    if args.mode == "doctor":
        if args.arguments not in ([], ["--runtime-only"]):
            parser.error("doctor accepts only --runtime-only")
        return doctor(bool(args.arguments))
    # The launcher always uses the folder containing this file, even after a
    # copy or when invoked from another working directory.
    # The delegated parsers accept abbreviated long options as well.
    options = [arg.split("=", 1)[0] for arg in args.arguments if arg.startswith("--")]
    if any(fixed.startswith(option) for option in options for fixed in ("--root", "--state", "--config")):
        parser.error("root, state and config are fixed to this project")
    try:
        return subprocess.call(command(args.mode, args.arguments), cwd=ROOT)
    except OSError as error:
        parser.exit(1, "aidd-run: %s\n" % error)


if __name__ == "__main__":
    raise SystemExit(main())
