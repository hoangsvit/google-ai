import subprocess
import unittest
from unittest.mock import patch

import device_diagnostics as diag
from research_offer_catalog import OFFER_REFERENCES, reference_options


class ResearchOfferTests(unittest.TestCase):
    def test_catalogue_is_display_only(self):
        self.assertEqual(len(OFFER_REFERENCES), 16)
        self.assertEqual([index for _, index in reference_options()], list(range(16)))

    def test_opens_official_app_on_expected_device(self):
        def response(stdout):
            return subprocess.CompletedProcess([], 0, stdout, "")
        with patch.object(diag, "locate_adb", return_value="adb"), \
             patch.object(diag, "online_serials", return_value=["test-device"]), \
             patch.object(diag, "_run", side_effect=[
                 response("package:" + diag.GOOGLE_ONE + "\n"),
                 response("Status: ok\n"),
             ]) as run:
            self.assertEqual(diag.open_google_one_app("test-device"), "opened")
        self.assertEqual(run.call_count, 2)
        self.assertEqual(run.call_args.args[1][-2:], ["-p", diag.GOOGLE_ONE])

    def test_normal_launcher_fallback_resolves_package_activity(self):
        def response(stdout="", stderr="", returncode=0):
            return subprocess.CompletedProcess([], returncode, stdout, stderr)
        component = diag.GOOGLE_ONE + "/.MainActivity"
        with patch.object(diag, "locate_adb", return_value="adb"), \
             patch.object(diag, "online_serials", return_value=["test-device"]), \
             patch.object(diag, "_run", side_effect=[
                 response("package:" + diag.GOOGLE_ONE + "\n"),
                 response("Error: unable to resolve Intent"),
                 response(component + "\n"),
                 response("  Status: ok\n"),
             ]) as run:
            self.assertEqual(diag.open_google_one_app("test-device"), "opened")
        self.assertEqual(run.call_count, 4)
        self.assertEqual(run.call_args.args[1][-2:], ["-n", component])

    def test_fallback_never_starts_other_package(self):
        def response(stdout):
            return subprocess.CompletedProcess([], 0, stdout, "")
        with patch.object(diag, "locate_adb", return_value="adb"), \
             patch.object(diag, "online_serials", return_value=["test-device"]), \
             patch.object(diag, "_run", side_effect=[
                 response("package:" + diag.GOOGLE_ONE + "\n"),
                 response("Error: unable to resolve Intent"),
                 response("other.package/.MainActivity"),
             ]) as run:
            self.assertEqual(diag.open_google_one_app("test-device"), "launcher_unresolved")
        self.assertEqual(run.call_count, 3)

    def test_disconnected_device_does_not_launch(self):
        with patch.object(diag, "locate_adb", return_value="adb"), \
             patch.object(diag, "online_serials", return_value=["other"]), \
             patch.object(diag, "_run") as run:
            self.assertEqual(diag.open_google_one_app("test-device"), "device_offline")
        run.assert_not_called()

    def test_ambiguous_device_does_not_launch(self):
        with patch.object(diag, "locate_adb", return_value="adb"), \
             patch.object(diag, "online_serials", return_value=["one", "two"]), \
             patch.object(diag, "same_boot_transports", return_value=False), \
             patch.object(diag, "_run") as run:
            self.assertEqual(diag.open_google_one_app(), "multiple_devices")
        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
