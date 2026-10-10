"""Unattended judging launch with writable temporary CLI state and audit log."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "judging"


def now():
    return datetime.now(timezone.utc).isoformat()


def status(stage, **details):
    path = OUT / "background-status.json"
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(dict(pid=os.getpid(), timestamp=now(), stage=stage, **details), indent=2), encoding="utf-8")
    os.replace(temp, path)


def main():
    log_path = OUT / ("run-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S") + ".log")
    status("starting", log=str(log_path))
    with log_path.open("x", encoding="utf-8", buffering=1) as log:
        try:
            # Credentials remain local, never printed, and are removed on exit.
            with tempfile.TemporaryDirectory(prefix="bias-judge-cli-") as task_home:
                shutil.copyfile(Path.home() / ".codex" / "auth.json", Path(task_home) / "auth.json")
                task_env = dict(os.environ, CODEX_HOME=task_home, PYTHONUNBUFFERED="1")
                before = json.loads((OUT / "summary.json").read_text(encoding="utf-8"))
                if before["failed_judgments"] or before["interrupted_items"]:
                    raise RuntimeError("Existing failed or interrupted judgments need inspection")
                test_remaining = max(0, 10 - before["successful_judgments"])
                commands = []
                if test_remaining:
                    commands.append(("test", ["--run", "--limit", str(test_remaining)]))
                commands.append(("full_pass", ["--run"]))
                for stage, args in commands:
                    status(stage, log=str(log_path))
                    log.write(now() + " Starting " + stage + "\n")
                    result = subprocess.run([sys.executable, str(ROOT / "judge.py"), *args],
                                            cwd=ROOT, env=task_env, stdout=log, stderr=subprocess.STDOUT)
                    if result.returncode:
                        raise RuntimeError(stage + " stopped with exit code " + str(result.returncode))
                    progress = json.loads((OUT / "summary.json").read_text(encoding="utf-8"))
                    if progress["failed_judgments"] or progress["interrupted_items"]:
                        raise RuntimeError(stage + " produced failed or interrupted judgments")
                    if stage == "test" and progress["successful_judgments"] < 10:
                        raise RuntimeError("Ten-item test did not finish")
                if progress["remaining"]:
                    raise RuntimeError("Full pass exited with items remaining")
                status("complete", log=str(log_path), summary=progress)
                log.write(now() + " All blinded judgments completed\n")
        except Exception as error:
            status("stopped", log=str(log_path), error=str(error))
            log.write(now() + " Stopped: " + str(error) + "\n")
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
