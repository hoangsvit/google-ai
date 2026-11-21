"""Offline source updater regressions. No GitHub, Android or billing access."""
import subprocess
import os
import shutil
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from app_update import (
    SOURCE_URL, UPDATE_REF, UpdateError, UpdateInfo, check_for_update,
    install_update, restart_command,
)

OLD = "a" * 40
NEW = "b" * 40


class SourceUpdateTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.repo = Path(self.directory.name).resolve()
        (self.repo / ".git").mkdir()
        self.responses = {
            ("rev-parse", "--show-toplevel"): str(self.repo),
            ("rev-parse", "--abbrev-ref", "HEAD"): "main",
            ("remote", "get-url", "origin"): SOURCE_URL,
            ("status", "--porcelain", "--untracked-files=normal"): "",
            ("rev-parse", "HEAD"): OLD,
            ("rev-parse", UPDATE_REF): NEW,
        }

    def git(self, repo, *args):
        self.assertEqual(repo, self.repo)
        if args[:2] == ("rev-parse", "--git-path"):
            return str(self.repo / ".git" / args[2])
        value = self.responses.get(args, "")
        if isinstance(value, Exception):
            raise value
        return value

    def test_check_fetches_only_official_main_without_changing_source(self):
        with patch("app_update._git", side_effect=self.git) as git:
            info = check_for_update(self.repo)
        self.assertEqual(info, UpdateInfo("available", f"New version · {OLD[:8]} → {NEW[:8]}", OLD, NEW))
        git.assert_any_call(self.repo, "fetch", "--no-tags", SOURCE_URL,
                            f"+refs/heads/main:{UPDATE_REF}")
        self.assertFalse(any(c.args[1] == "merge" for c in git.call_args_list))

    def test_up_to_date(self):
        self.responses[("rev-parse", UPDATE_REF)] = OLD
        with patch("app_update._git", side_effect=self.git):
            self.assertEqual(check_for_update(self.repo).state, "current")

    def test_non_main_fork_and_local_changes_never_fetch_or_merge(self):
        for command, value in (
            (("rev-parse", "--abbrev-ref", "HEAD"), "dev"),
            (("remote", "get-url", "origin"), "https://example.org/fork.git"),
            (("status", "--porcelain", "--untracked-files=normal"), " M tui.py"),
        ):
            original = self.responses[command]
            self.responses[command] = value
            with self.subTest(command=command), patch("app_update._git", side_effect=self.git) as git:
                self.assertEqual(check_for_update(self.repo).state, "error")
                with self.assertRaises(UpdateError):
                    install_update(self.repo, UpdateInfo("available", "", OLD, NEW))
                self.assertFalse(any(c.args[1] in ("fetch", "merge") for c in git.call_args_list))
            self.responses[command] = original

    def test_git_operation_blocks_update_even_with_clean_status(self):
        (self.repo / ".git" / "rebase-merge").mkdir()
        with patch("app_update._git", side_effect=self.git) as git:
            self.assertIn("Git operation", check_for_update(self.repo).message)
            self.assertFalse(any(c.args[1] == "fetch" for c in git.call_args_list))

    def test_zip_never_runs_git(self):
        with tempfile.TemporaryDirectory() as directory, patch("app_update.subprocess.run") as run:
            self.assertIn("Git clone", check_for_update(Path(directory)).message)
            run.assert_not_called()

    def test_divergent_history_does_not_offer_update(self):
        self.responses[("merge-base", "--is-ancestor", OLD, NEW)] = UpdateError("History differs")
        with patch("app_update._git", side_effect=self.git):
            self.assertEqual(check_for_update(self.repo).state, "error")

    def test_install_revalidates_and_uses_exact_checked_commit(self):
        head_calls = 0

        def git(repo, *args):
            nonlocal head_calls
            if args == ("rev-parse", "HEAD"):
                head_calls += 1
                return OLD if head_calls == 1 else NEW
            return self.git(repo, *args)

        with patch("app_update._git", side_effect=git) as run:
            install_update(self.repo, UpdateInfo("available", "", OLD, NEW))
        run.assert_any_call(self.repo, "merge", "--ff-only", "--no-overwrite-ignore", NEW)
        self.assertFalse(any(c.args[1] in ("reset", "stash", "pull", "checkout") for c in run.call_args_list))

    def test_source_changed_since_check_blocks_install(self):
        self.responses[("rev-parse", "HEAD")] = "c" * 40
        with patch("app_update._git", side_effect=self.git) as git:
            with self.assertRaisesRegex(UpdateError, "Source changed"):
                install_update(self.repo, UpdateInfo("available", "", OLD, NEW))
            self.assertFalse(any(c.args[1] == "merge" for c in git.call_args_list))

    def test_invalid_or_unavailable_target_never_runs_git(self):
        for info in (UpdateInfo("current", "", OLD, NEW),
                     UpdateInfo("available", "", OLD, "--unsafe")):
            with patch("app_update._git") as git, self.assertRaises(UpdateError):
                install_update(self.repo, info)
            git.assert_not_called()

    def test_git_failures_are_sanitized_and_noninteractive(self):
        from app_update import _git
        for result in (subprocess.TimeoutExpired("secret account", 20),
                       FileNotFoundError("private path"),
                       subprocess.CompletedProcess([], 1, "private token", "private email")):
            with patch("app_update.subprocess.run", side_effect=result if isinstance(result, Exception) else None,
                       return_value=result) as run:
                with self.assertRaises(UpdateError) as error:
                    _git(self.repo, "fetch")
                self.assertNotIn("private", str(error.exception))
                self.assertNotIn("secret", str(error.exception))
                self.assertEqual(run.call_args.kwargs["timeout"], 20)
                self.assertEqual(run.call_args.kwargs["env"]["GIT_TERMINAL_PROMPT"], "0")

    def test_restart_uses_native_launcher_without_any_stage_flags(self):
        with patch("app_update.shutil.which", return_value="powershell.exe"):
            windows = restart_command(self.repo, "win32")
        mac = restart_command(self.repo, "darwin")
        self.assertEqual(windows[-1], str(self.repo / "run-all.ps1"))
        self.assertEqual(mac, ["/bin/sh", str(self.repo / "run-macos.sh")])
        for command in (windows, mac):
            for flag in ("-Step", "--step", "-AllStages", "--sequence", "-Force", "--force"):
                self.assertNotIn(flag, command)


@unittest.skipUnless(shutil.which("git"), "Git is required for local integration tests")
class LocalGitUpdateTests(unittest.TestCase):
    def test_real_fast_forward_preserves_ignored_files_and_refuses_later_edits(self):
        from app_update import _git
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {"GIT_CONFIG_COUNT": "0"}):
            repo = Path(directory)

            def git(*args):
                return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True,
                                      text=True, timeout=10).stdout.strip()

            git("init", "-b", "main")
            git("config", "user.name", "Offline Test")
            git("config", "user.email", "test@example.invalid")
            git("config", "commit.gpgsign", "false")
            git("config", "core.hooksPath", str(repo / ".git" / "offline-hooks"))
            git("remote", "add", "origin", SOURCE_URL)
            (repo / ".gitignore").write_text("logs/\n", encoding="utf-8")
            (repo / "version.txt").write_text("old", encoding="utf-8")
            git("add", ".")
            git("commit", "-m", "Initial offline fixture")
            old = git("rev-parse", "HEAD")
            git("switch", "-c", "release-fixture")
            (repo / "version.txt").write_text("new", encoding="utf-8")
            git("commit", "-am", "New offline fixture")
            new = git("rev-parse", "HEAD")
            git("update-ref", UPDATE_REF, new)
            git("switch", "main")
            (repo / "logs").mkdir()
            local_log = repo / "logs" / "test.log"
            local_log.write_text("local mock data", encoding="utf-8")

            def offline_git(path, *args):
                if args[0] == "fetch":
                    return ""  # The local fixture already supplies the fetched revision.
                return _git(path, *args)

            with patch("app_update._git", side_effect=offline_git):
                info = check_for_update(repo)
                self.assertEqual((info.current, info.target), (old, new))
                self.assertEqual((repo / "version.txt").read_text(), "old")
                (repo / "version.txt").write_text("local edit", encoding="utf-8")
                with self.assertRaisesRegex(UpdateError, "Local changes"):
                    install_update(repo, info)
                self.assertEqual(git("rev-parse", "HEAD"), old)
                (repo / "version.txt").write_text("old", encoding="utf-8")
                install_update(repo, info)
            self.assertEqual(git("rev-parse", "HEAD"), new)
            self.assertEqual((repo / "version.txt").read_text(), "new")
            self.assertEqual(local_log.read_text(), "local mock data")


class UpdateUITests(unittest.IsolatedAsyncioTestCase):
    async def test_update_banner_and_primary_status_fit_terminal_sizes(self):
        from tui import GoogleAITUI
        from textual.widgets import Button, Static
        for size in ((110, 35), (90, 20), (60, 20)):
            with self.subTest(size=size), tempfile.TemporaryDirectory() as directory:
                app = GoogleAITUI(repo=Path(directory))
                with patch("tui.check_for_update", return_value=UpdateInfo("available", "New version", OLD, NEW)):
                    async with app.run_test(size=size) as pilot:
                        await pilot.pause()
                        self.assertEqual(str(app.query_one("#update", Button).label), "Update & Restart")
                        for selector in ("#update", "#quickstart", "#state"):
                            widget = app.query_one(selector)
                            self.assertGreater(widget.region.height, 0)
                            self.assertGreaterEqual(widget.region.y, 0)
                            self.assertLessEqual(widget.region.bottom, size[1] - 1)
                            self.assertLessEqual(widget.region.right, size[0])
                        self.assertIn("Ready", str(app.query_one("#state", Static).render()))
                        self.assertFalse(app.busy)
                        app.query_one("#update", Button).focus()
                        await pilot.pause()
                        self.assertEqual(app.focused.id, "update")
                        app.advanced_pressed()
                        await pilot.pause()
                        run = app.query_one("#run", Button)
                        run.focus()
                        run.scroll_visible(animate=False)
                        await pilot.pause()
                        self.assertEqual(app.focused.id, "run")
                        self.assertGreater(run.region.intersection(app.query_one("#content").region).height, 0)

    async def test_update_is_locked_during_step_diagnosis_sequence_and_approval(self):
        from tui import GoogleAITUI
        from textual.widgets import Button
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch("tui.check_for_update", return_value=UpdateInfo("available", "New version", OLD, NEW)), \
                 patch.object(GoogleAITUI, "apply_app_update") as install:
                async with app.run_test() as pilot:
                    await pilot.pause()
                    for flag in ("busy", "_diagnosing", "sequence", "_approval_pending"):
                        setattr(app, flag, True)
                        app._refresh_update_controls()
                        self.assertTrue(app.query_one("#update", Button).disabled)
                        app.update_pressed()
                        install.assert_not_called()
                        setattr(app, flag, False)

    async def test_update_locks_all_stage_entry_points_and_restores_on_failure(self):
        from tui import GoogleAITUI
        from textual.widgets import Button, Select, Static
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch("tui.check_for_update", return_value=UpdateInfo("available", "New version", OLD, NEW)), \
                 patch.object(GoogleAITUI, "apply_app_update") as install, \
                 patch.object(GoogleAITUI, "run_stage") as stage:
                async with app.run_test(size=(110, 35)) as pilot:
                    await pilot.pause()
                    app.query_one("#mode", Select).value = "all"
                    await pilot.pause()
                    await pilot.click("#update")
                    self.assertTrue(app._updating)
                    install.assert_called_once()
                    for selector in ("#quickstart", "#diagnose", "#run", "#mode", "#step"):
                        self.assertTrue(app.query_one(selector).disabled)
                    app.quickstart_pressed()
                    app.sequence_pressed()
                    app._start(2, False)
                    app.diagnose_pressed()
                    await pilot.press("r", "q", "ctrl+c")
                    stage.assert_not_called()
                    self.assertFalse(app.busy)
                    self.assertTrue(app.is_running)
                    app._app_update_done("No network. Retry the update check.")
                    self.assertFalse(app._updating)
                    self.assertFalse(app.restart_requested)
                    self.assertFalse(app.query_one("#quickstart", Button).disabled)
                    self.assertTrue(app.query_one("#step", Select).disabled)  # all mode
                    self.assertIn("No network", str(app.query_one("#update_status", Static).render()))

    async def test_success_exits_only_after_installer_finishes(self):
        from tui import GoogleAITUI
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch("tui.check_for_update", return_value=UpdateInfo("current", "Up to date")), \
                 patch("tui.install_update") as install, \
                 patch("tui.restart_command", return_value=["native-launcher"]):
                async with app.run_test() as pilot:
                    await pilot.pause()
                    app._update_check_done(UpdateInfo("available", "New version", OLD, NEW))
                    app.update_pressed()
                    await pilot.pause()
                install.assert_called_once()
                self.assertTrue(app.restart_requested)

    async def test_worker_failure_keeps_dashboard_open_and_retry_available(self):
        from tui import GoogleAITUI
        from textual.widgets import Button, Static
        with tempfile.TemporaryDirectory() as directory:
            app = GoogleAITUI(repo=Path(directory))
            with patch("tui.check_for_update", return_value=UpdateInfo("available", "New version", OLD, NEW)), \
                 patch("tui.restart_command", return_value=["native-launcher"]), \
                 patch("tui.install_update", side_effect=UpdateError("Local changes found. Save them first.")):
                async with app.run_test() as pilot:
                    await pilot.pause()
                    app.update_pressed()
                    await pilot.pause()
                    self.assertTrue(app.is_running)
                    self.assertFalse(app._updating)
                    self.assertFalse(app.restart_requested)
                    self.assertFalse(app.query_one("#update", Button).disabled)
                    self.assertEqual(str(app.query_one("#update", Button).label), "Check for updates")
                    self.assertIn("Local changes", str(app.query_one("#message", Static).render()))

    def test_main_reopens_native_launcher_after_dashboard_closes(self):
        from tui import main
        app = Mock(restart_requested=True)
        events = []
        app.run.side_effect = lambda: events.append("closed")
        with patch("tui.GoogleAITUI", return_value=app), \
             patch("tui.restart_command", return_value=["native-launcher"]), \
             patch("tui.subprocess.call", side_effect=lambda *a, **kw: events.append("reopened") or 0):
            self.assertEqual(main(["--step", "4", "--sequence"]), 0)
        self.assertEqual(events, ["closed", "reopened"])
