"""Conservative source updates; no Android, account or billing operations."""
from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

SOURCE_URL = "https://github.com/hoangsvit/google-ai.git"
UPDATE_REF = "refs/eplus-update/main"


class UpdateError(RuntimeError):
    """A safe, user-facing update failure (never raw Git output)."""


@dataclass(frozen=True)
class UpdateInfo:
    state: str
    message: str
    current: str = ""
    target: str = ""


def _git(repo: Path, *args: str) -> str:
    env = os.environ.copy()
    env.update(GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")
    try:
        result = subprocess.run(
            ["git", *args], cwd=repo, env=env, capture_output=True,
            text=True, encoding="utf-8", errors="replace", timeout=20,
            check=False, **({"creationflags": subprocess.CREATE_NO_WINDOW}
                            if os.name == "nt" else {}),
        )
    except (OSError, subprocess.TimeoutExpired):
        raise UpdateError("Update check failed. Check Git/network access and retry.") from None
    if result.returncode:
        raise UpdateError("Git could not complete the update. Check network/access and retry; do not reset local files.")
    return result.stdout.strip()


def _validate_checkout(repo: Path) -> str:
    if not (repo / ".git").exists():
        raise UpdateError("Updates need a Git clone. Install the latest source in a separate folder.")
    if Path(_git(repo, "rev-parse", "--show-toplevel")).resolve() != repo.resolve():
        raise UpdateError("Open the toolkit from its own Git clone to update.")
    if _git(repo, "rev-parse", "--abbrev-ref", "HEAD") != "main":
        raise UpdateError("Automatic updates require main. Update development branches manually.")
    origin = _git(repo, "remote", "get-url", "origin")
    if origin not in (SOURCE_URL, SOURCE_URL.removesuffix(".git"),
                      "git@github.com:hoangsvit/google-ai.git"):
        raise UpdateError("Automatic updates require the official hoangsvit/google-ai clone.")
    if _git(repo, "status", "--porcelain", "--untracked-files=normal"):
        raise UpdateError("Local changes found. Save or move them before updating.")
    for operation in ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "rebase-merge", "rebase-apply"):
        path = Path(_git(repo, "rev-parse", "--git-path", operation))
        if (repo / path).exists():
            raise UpdateError("Finish the current Git operation before updating.")
    return _git(repo, "rev-parse", "HEAD")


def check_for_update(repo: Path) -> UpdateInfo:
    """Fetch official main in the background; never modify working source files."""
    try:
        current = _validate_checkout(repo)
        _git(repo, "fetch", "--no-tags", SOURCE_URL,
             f"+refs/heads/main:{UPDATE_REF}")
        target = _git(repo, "rev-parse", UPDATE_REF)
        if current == target:
            return UpdateInfo("current", f"Up to date · {current[:8]}", current, target)
        try:
            _git(repo, "merge-base", "--is-ancestor", current, target)
        except UpdateError:
            raise UpdateError("Local main cannot advance to this version. Review Git history and update manually.") from None
        return UpdateInfo("available", f"New version · {current[:8]} → {target[:8]}", current, target)
    except UpdateError as error:
        return UpdateInfo("error", str(error))


def install_update(repo: Path, info: UpdateInfo) -> None:
    """Apply the displayed revision without resetting, stashing or merging histories."""
    if info.state != "available" or not re.fullmatch(r"[0-9a-f]{40}", info.target):
        raise UpdateError("Check for a new version before updating.")
    if _validate_checkout(repo) != info.current:
        raise UpdateError("Source changed since the check. Check for updates again.")
    _git(repo, "merge-base", "--is-ancestor", info.current, info.target)
    _git(repo, "merge", "--ff-only", "--no-overwrite-ignore", info.target)
    if _git(repo, "rev-parse", "HEAD") != info.target:
        raise UpdateError("Could not verify the installed version. Reopen the toolkit manually.")


def restart_command(repo: Path, platform: str | None = None) -> list[str]:
    """Re-enter the native launcher with no stage, sequence or payment flags."""
    platform = sys.platform if platform is None else platform
    if platform == "darwin":
        return ["/bin/sh", str(repo / "run-macos.sh")]
    if platform == "win32":
        shell = shutil.which("pwsh") or shutil.which("powershell.exe")
        if shell:
            return [shell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                    str(repo / "run-all.ps1")]
        raise UpdateError("Cannot restart automatically: PowerShell was not found. Check its installation and retry.")
    return [sys.executable, str(repo / "tui.py")]
