"""Linux regressions. Every Android and checkout operation is mocked."""
from contextlib import redirect_stdout
from io import StringIO
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch

import device_diagnostics as diagnostics
import macos_runner as adapter
from tui import Approval, SetupNotice, GoogleAITUI, main
from tui_core import command_for_step
from textual.widgets import Button, Select, Static

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(os.name == "posix", "requires a POSIX shell")
class LauncherTests(unittest.TestCase):
    def test_dispatch_and_validation_without_running_android(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copy(ROOT / "run-linux.sh", root)
            env = {**os.environ, "PATH": f"{root}:/usr/bin:/bin",
                   "ADB_PATH": str(root / "custom adb")}
            for name, body in {
                "uname": "echo Linux",
                "python3": "exit 0",
                "custom adb": "exit 99",
                ".venv/bin/python": (
                    'if [ "$1" != "-c" ]; then printf "%s\\n" "$@"; fi'
                ),
            }.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f"#!/bin/sh\n{body}\n")
                path.chmod(0o755)

            def invoke(*args, **overrides):
                return subprocess.run(["sh", str(root / "run-linux.sh"), *args],
                                      env={**env, **overrides}, text=True, capture_output=True)

            with self.subTest("syntax"):
                subprocess.run(["sh", "-n", str(root / "run-linux.sh")], check=True)
            self.assertIn("Steps 2–5 can submit real charges", invoke("--help").stdout)
            for args, expected in [
                ((), ["tui.py"]),
                (("--check",), ["macos_runner.py", "--step", "0"]),
                (("--list",), ["macos_runner.py", "--step", "1"]),
                (("--sequence",), ["tui.py", "--sequence"]),
                (("--step", "3", "--sequence"), ["tui.py", "--step", "3", "--sequence"]),
                *((("--step", str(i)), ["tui.py", "--step", str(i)]) for i in range(6)),
            ]:
                with self.subTest(args=args):
                    result = invoke(*args)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout.splitlines(), expected)
            for args in [("--step",), ("--step", "6"), ("--step", "1.5"),
                         ("--force",), ("--list", "--check")]:
                self.assertEqual(invoke(*args).returncode, 2)
            self.assertIn("ADB_PATH", invoke(ADB_PATH=str(root / "missing")).stderr)
            relative_adb = subprocess.run(
                ["sh", str(root / "run-linux.sh"), "--list"], cwd=root.parent,
                env={**env, "ADB_PATH": f"./{root.name}/custom adb"},
                text=True, capture_output=True,
            )
            self.assertEqual(relative_adb.returncode, 0, relative_adb.stderr)
            (root / ".venv/bin/python").unlink()
            (root / "python3").write_text('#!/bin/sh\n[ "$1" != "-m" ]\n')
            self.assertIn("python3-venv", invoke().stderr)


class LinuxAdapterTests(unittest.TestCase):
    def test_stage_routes_use_native_adapter(self):
        with patch("tui_core.sys.platform", "linux"):
            for step in range(6):
                command = command_for_step(step, ROOT)
                self.assertEqual(command[1:4], [str(ROOT / "macos_runner.py"), "--step", str(step)])
                self.assertEqual("--confirmed" in command, step >= 2)
                self.assertEqual("--active-confirmed" in command, step >= 3)

    def test_linux_isolates_engine_temporary_files(self):
        paths = []

        def run_stage(step, serial, env, *_args):
            self.assertEqual(env["TMPDIR"], env[adapter.LINUX_WORKDIR])
            directory = Path(env["TMPDIR"])
            self.assertTrue(directory.is_dir())
            paths.append(directory)
            return 0

        with patch("macos_runner.sys.platform", "linux"), \
             patch.object(adapter, "preflight", return_value=("/example/adb", "mock-device")), \
             patch.object(adapter, "run_stage", side_effect=run_stage):
            self.assertEqual(adapter.main(["--step", "0"]), 0)
            self.assertEqual(adapter.main(["--step", "0"]), 0)
        self.assertNotEqual(*paths)
        self.assertFalse(any(path.exists() for path in paths))

    def test_adb_path_is_used_before_path_and_missing_adb_is_actionable(self):
        with patch.dict(os.environ, {"ADB_PATH": "/opt/custom/adb"}), \
             patch.object(diagnostics.shutil, "which", return_value=None) as which, \
             patch("macos_runner.sys.platform", "linux"):
            with self.assertRaisesRegex(RuntimeError, "ADB_PATH"):
                adapter.preflight()
        which.assert_called_once_with("/opt/custom/adb")

    def test_no_device_and_unauthorized_device_have_usb_guidance(self):
        for suffix, guidance in [("", "Connect the rooted phone by USB"),
                                 ("test-serial unauthorized\n", "approve its USB debugging"),
                                 ("test-serial no permissions\n", "USB device rules")]:
            with self.subTest(state=suffix), \
                 patch("macos_runner.sys.platform", "linux"), \
                 patch("macos_runner.locate_adb", return_value="/example/adb"), \
                 patch("device_diagnostics.locate_adb", return_value="/example/adb"), \
                 patch("macos_runner.metadata.version", return_value="16.5.9"), \
                 patch("macos_runner.online_serials", return_value=[]), \
                 patch("device_diagnostics._run", return_value=subprocess.CompletedProcess(
                     [], 0, f"List of devices attached\n{suffix}", "")):
                with self.assertRaisesRegex(RuntimeError, guidance):
                    adapter.preflight()

    def test_ambiguous_device_fails_before_engine(self):
        with patch("macos_runner.sys.platform", "linux"), \
             patch("macos_runner.locate_adb", return_value="/example/adb"), \
             patch("macos_runner.metadata.version", return_value="16.5.9"), \
             patch("macos_runner.online_serials", return_value=["first", "second"]), \
             patch("macos_runner.auto_select_device", return_value="first") as choose, \
             patch("macos_runner.run_engine") as engine, redirect_stdout(StringIO()):
            self.assertEqual(adapter.main(["--step", "1"]), 1)
            choose.assert_not_called()
            engine.assert_not_called()

    def test_android_16_and_newer_block_every_stage_before_engine(self):
        for sdk in ("36", "37", ""):
            with self.subTest(sdk=sdk), patch("macos_runner.sys.platform", "linux"), \
                 patch("macos_runner.locate_adb", return_value="/example/adb"), \
                 patch("macos_runner.metadata.version", return_value="16.5.9"), \
                 patch("macos_runner.online_serials", return_value=["mock-device"]), \
                 patch("device_diagnostics._run", return_value=subprocess.CompletedProcess(
                     [], 0, sdk + "\n", "")) as adb, \
                 patch("macos_runner.run_engine") as engine, \
                 patch("sys.stderr", new_callable=StringIO) as errors:
                for step in range(6):
                    args = ["--step", str(step)]
                    if step >= 2:
                        args.append("--confirmed")
                    if step >= 3:
                        args.append("--active-confirmed")
                    self.assertEqual(adapter.main(args), 1)
                engine.assert_not_called()
                adb.assert_called_with("/example/adb", [
                    "-s", "mock-device", "shell", "getprop", "ro.build.version.sdk",
                ])
                self.assertIn("predates Android 16" if sdk else "Could not read", errors.getvalue())

    def test_android_15_preflight_can_select_the_single_device(self):
        with patch("macos_runner.sys.platform", "linux"), \
             patch("macos_runner.locate_adb", return_value="/example/adb"), \
             patch("macos_runner.metadata.version", return_value="16.5.9"), \
             patch("macos_runner.online_serials", return_value=["mock-device"]), \
             patch("device_diagnostics._run", return_value=subprocess.CompletedProcess(
                 [], 0, "35\n", "")):
            self.assertEqual(adapter.preflight(), ("/example/adb", "mock-device"))

    def test_paid_guards_and_result_matching_for_each_linux_stage(self):
        account = "verified@example.test"
        for step, (plan, offer_id, stack) in adapter.STAGES.items():
            product = adapter.CHECKOUT_PRODUCT
            for detected, looked_up, listed_product, offer, micros, passes in (
                (account, account, product, offer_id, 0, True),
                (account, account, product, "other-offer", 0, False),
                (account, account, "g1.play.2tb.ai", offer_id, 0, False),
                (account, account, product, offer_id, 1000, False),
                (account, "other@example.test", product, offer_id, 0, False),
                (account, "", product, offer_id, 0, False),
                ("", account, product, offer_id, 0, False),
            ):
                with self.subTest(step=step, detected=detected, looked_up=looked_up,
                                  product=listed_product, offer=offer, micros=micros), tempfile.TemporaryDirectory() as tmp:
                    env = {adapter.LINUX_WORKDIR: tmp}
                    report = {"status": "listed", "detected_play_account": detected,
                              "offers": [{"product": listed_product, "id": offer, "micros": micros}]}

                    def engine(command, environment):
                        if "--check" not in command:
                            directory = Path(tmp) / "ultra0-report"
                            directory.mkdir()
                            (directory / "account-mock.json").write_text(json.dumps({
                                "status": "checkout_requested", "email": account,
                                "offerToken": "never-print-me",
                            }))
                            self.assertIn(plan, command)
                            self.assertEqual("--stack" in command, stack)
                        return 0

                    result = Path(tmp) / "result.json"
                    with patch.object(adapter, "run_engine", side_effect=engine) as invoke, \
                         patch.object(adapter, "list_offers", return_value=report), \
                         patch.object(adapter, "read_play_account", return_value=looked_up), \
                         redirect_stdout(StringIO()) as output:
                        with self.assertRaisesRegex(RuntimeError, "confirmations"):
                            adapter.run_stage(step, "private-serial", env)
                        invoke.assert_not_called()
                        if passes:
                            self.assertEqual(adapter.run_stage(step, "private-serial", env, True, True, result), 0)
                            self.assertEqual(json.loads(result.read_text()), {"status": "checkout_requested"})
                            self.assertEqual(invoke.call_count, 2)
                            self.assertNotIn(account, output.getvalue())
                        else:
                            with self.assertRaises(RuntimeError):
                                adapter.run_stage(step, "private-serial", env, True, True, result)
                            self.assertEqual(invoke.call_count, 1)
                            self.assertFalse(result.exists())

    def test_listing_refuses_stale_previous_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = {adapter.LINUX_WORKDIR: tmp}
            directory = Path(tmp) / "ultra0-report"
            directory.mkdir()
            report = directory / "current.json"
            report.write_text('{"status": "listed", "offers": []}')
            os.utime(report, (1, 1))
            with patch.object(adapter, "run_engine", return_value=0):
                with self.assertRaisesRegex(RuntimeError, "older invocation"):
                    adapter.list_offers("device-mock", env)

    def test_account_change_after_offer_validation_blocks_checkout(self):
        report = {"status": "listed", "detected_play_account": "verified@example.test",
                  "offers": [{"product": adapter.CHECKOUT_PRODUCT, "id": "12months-eft", "micros": 0}]}
        with patch.object(adapter, "run_engine", return_value=0) as invoke, \
             patch.object(adapter, "list_offers", return_value=report), \
             patch.object(adapter, "read_play_account",
                          side_effect=["verified@example.test", "changed@example.test"]), \
             redirect_stdout(StringIO()):
            with self.assertRaisesRegex(RuntimeError, "account changed"):
                adapter.run_stage(2, "device-mock", {adapter.LINUX_WORKDIR: "/private"}, True)
        invoke.assert_called_once()
        self.assertIn("--check", invoke.call_args.args[0])

    def test_linux_listing_publishes_only_fresh_public_offer_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env = {adapter.LINUX_WORKDIR: tmp}

            def engine(command, environment):
                directory = root / "ultra0-report"
                directory.mkdir()
                listing = directory / "current.json"
                listing.write_text(json.dumps({
                    "status": "listed", "detected_play_account": "verified@example.test",
                    "offers": [{"product": "mock-pro", "id": "mock-offer", "period": "P1M",
                                "micros": 0, "offerToken": "never-print"}],
                }))
                os.utime(listing, (1, 1))
                self.assertIn("--list", command)
                return 0

            result = root / "result.json"
            with patch.object(adapter, "run_engine", side_effect=engine) as invoke, \
                 patch.object(adapter, "read_play_account") as lookup, \
                 redirect_stdout(StringIO()) as output:
                self.assertEqual(adapter.run_stage(1, "private-serial", env, result_file=result), 0)
            invoke.assert_called_once()
            lookup.assert_not_called()
            self.assertNotIn("verified@example.test", output.getvalue())
            data = json.loads(result.read_text())
            self.assertEqual(data, {"status": "listed", "offers": [
                {"product": "mock-pro", "id": "mock-offer", "period": "P1M", "micros": 0},
            ]})

    def test_unverified_profile_does_not_hide_linux_offer_results(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = Path(tmp) / "result.json"
            report = {"status": "listed", "detected_play_account": "", "offers": []}
            with patch.object(adapter, "list_offers", return_value=report), \
                 patch.object(adapter, "read_play_account") as lookup, \
                 redirect_stdout(StringIO()) as output:
                self.assertEqual(adapter.run_stage(
                    1, "device-mock", {adapter.LINUX_WORKDIR: tmp}, result_file=result), 0)
            lookup.assert_not_called()
            self.assertIn("Google Play account could not be verified.", output.getvalue())
            self.assertEqual(json.loads(result.read_text()), {"status": "listed", "offers": []})

    def test_verified_checkout_projection_is_allow_listed(self):
        with tempfile.TemporaryDirectory() as tmp:
            result_file = Path(tmp) / "result.json"
            adapter.publish_result(result_file, {
                "status": "checkout_requested", "email": "private@example.test",
                "offerToken": "hidden",
                "sheet": {
                    "reason": "zero_today_and_duration_verified", "confirmed": True,
                    "payment_card": "secret", "account": "private@example.test",
                },
            })
            self.assertEqual(json.loads(result_file.read_text()), {
                "status": "checkout_requested",
                "sheet": {"reason": "zero_today_and_duration_verified", "confirmed": True},
            })

    def test_engine_drops_raw_private_output(self):
        child = Mock()
        child.stdout = iter(["Connected ADB device: device-private\n",
                             "Account private@example.test\n",
                             "Read existing purchase token (secret)\n",
                             "Action required: card details\n"])
        child.wait.return_value = 0
        with patch.object(adapter.subprocess, "Popen") as popen, redirect_stdout(StringIO()) as output:
            popen.return_value.__enter__.return_value = child
            self.assertEqual(adapter.run_engine(["python"], {adapter.LINUX_WORKDIR: "/private"}), 0)
        self.assertEqual(output.getvalue().splitlines(), [
            "Android device connected.",
            "Action required: Complete the prompt on Android, then confirm here.",
        ])


@unittest.skipUnless(os.name == "posix", "requires POSIX process groups")
class LinuxDashboardTests(unittest.IsolatedAsyncioTestCase):
    async def test_layout_and_preselection_at_both_terminal_sizes(self):
        for size in ((90, 20), (110, 35)):
            for guided in (False, True):
                with self.subTest(size=size, guided=guided), patch("tui.sys.platform", "linux"):
                    app = GoogleAITUI(repo=ROOT, selected_step=2 if guided else 1,
                                      start_sequence=guided, show_advanced=guided)
                    with patch.object(app, "run_stage") as run:
                        async with app.run_test(size=size) as pilot:
                            await pilot.pause()
                            for selector in ("#quickstart", "#state"):
                                widget = app.query_one(selector)
                                self.assertTrue(widget.visible)
                                self.assertGreater(widget.region.height, 0)
                                if not guided:
                                    self.assertLess(widget.region.y, size[1])
                            self.assertEqual(app.query_one("#mode", Select).value, "from" if guided else "single")
                            self.assertEqual(app.query_one("#step", Select).value, 2 if guided else 1)
                            self.assertEqual(app.query_one("#workflow_actions").display, guided)
                            self.assertEqual(len(app.query("#workflow .workflow-step")), 6)
                            run.assert_not_called()

    async def test_decline_quick_check_stop_and_checkout_exit(self):
        with patch("tui.sys.platform", "linux"):
            app = GoogleAITUI(repo=ROOT)
            with patch.object(app, "run_stage") as run:
                async with app.run_test(size=(90, 20)) as pilot:
                    # Current TUI refuses to offer checkout before an
                    # account-bound Step 1 has verified a unique device.
                    app._confirm_stage(2, True)
                    await pilot.pause()
                    self.assertNotIsInstance(app.screen, Approval)
                    run.assert_not_called()
                    app._selected_account = "verified@example.test"
                    app._offer_ready_account = "verified@example.test"
                    app._offer_ready_device = "mock-device"
                    app._connection_state = diagnostics.ConnectionStatus(
                        "connected", ("mock-device",))
                    app._offer_check_ready = True
                    app._confirm_stage(2, True)
                    await pilot.pause()
                    self.assertIsInstance(app.screen, Approval)
                    app.screen.dismiss(False)
                    await pilot.pause()
                    run.assert_not_called()
                    await pilot.click("#quickstart")
                    run.assert_called_once_with(1)
                    await pilot.pause()
                    self.assertTrue(app.query_one("#stop", Button).display)
                    self.assertGreater(app.query_one("#stop", Button).region.height, 0)
                    child = Mock(pid=9876)
                    child.poll.return_value = None
                    app._child = child
                    with patch("tui.os.killpg") as kill:
                        await pilot.click("#stop")
                        await app.workers.wait_for_complete()
                        kill.assert_called_once_with(9876, signal.SIGTERM)
                    self.assertTrue(app._cancel_requested)
                    app.busy = False
                    app._offer_check_ready = True
                    app._offer_ready_device = "mock-device"
                    app._connection_state = diagnostics.ConnectionStatus(
                        "connected", ("mock-device",))
                    app._confirm_stage(3, True)
                    await pilot.pause()
                    app.screen.dismiss(True)
                    await pilot.pause()
                    run.assert_called_with(3)
                    with patch("tui.os.killpg") as kill:
                        app.action_quit_safely()
                        kill.assert_not_called()
                    self.assertTrue(app._exit_after_step)
                    self.assertTrue(app._stop_after_step)

    async def test_native_lookup_messages_show_no_identifiers(self):
        with patch("tui.sys.platform", "linux"):
            app = GoogleAITUI(repo=ROOT)
        async with app.run_test() as pilot:
            app._received("Android device connected.")
            app._received("Google Play account verified.")
            self.assertIn("Connected", str(app.query_one("#device", Static).content))
            self.assertIn("Verified", str(app.query_one("#account", Static).content))

    async def test_quick_check_displays_only_its_invocation_result(self):
        with tempfile.TemporaryDirectory() as tmp, patch("tui.sys.platform", "linux"):
            repo = Path(tmp)
            (repo / "macos_runner.py").touch()
            reports = repo / "ultra0-report"
            reports.mkdir()
            (reports / "current.json").write_text('{"status": "listed", "offers": [{}, {}]}')
            app = GoogleAITUI(repo=repo)
            result_paths = []

            def invoke(command):
                result = Path(command[command.index("--result-file") + 1])
                self.assertEqual(command[command.index("--step") + 1], "1")
                result_paths.append(result)
                if len(result_paths) == 1:
                    result.write_text('{"status": "listed", "offers": [{}]}')
                return 0

            with patch.object(app, "_execute", side_effect=invoke):
                async with app.run_test(size=(110, 35)) as pilot:
                    await pilot.click("#quickstart")
                    await app.workers.wait_for_complete()
                    self.assertIn("1 offers returned", str(app.query_one("#step_result", Static).content))
                    # Without a selected account, the current TUI shows a
                    # safety notice rather than unlocking paid stages.
                    if isinstance(app.screen, SetupNotice):
                        app.screen.dismiss(None)
                        await pilot.pause()
                    await pilot.click("#quickstart")
                    await app.workers.wait_for_complete()
                    self.assertEqual(app._last_outcome.code, "missing_report")
            self.assertNotEqual(*result_paths)
            self.assertFalse(any(path.exists() for path in result_paths))


class LinuxEntryTests(unittest.TestCase):
    def test_cli_step_and_sequence_open_advanced_without_starting_stage(self):
        for args, step, guided in [([], 1, False), (["--step", "0"], 0, False),
                                   (["--sequence"], 2, True),
                                   (["--step", "5", "--sequence"], 5, True)]:
            with self.subTest(args=args), patch("tui.sys.platform", "linux"), \
                 patch("tui.GoogleAITUI") as create:
                self.assertEqual(main(args), 0)
                self.assertEqual(create.call_args.kwargs["selected_step"], step)
                self.assertEqual(create.call_args.kwargs["start_sequence"], guided)
                self.assertEqual(create.call_args.kwargs["show_advanced"], bool(args))
