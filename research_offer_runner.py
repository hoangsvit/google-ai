"""Run individual research steps by opening the official app for manual review."""
import argparse

from device_diagnostics import open_google_one_app, open_youtube_app
from research_offer_catalog import STEP_REFERENCES, research_step_label


def run_step(step, serial=""):
    if step not in STEP_REFERENCES:
        return "invalid_step"
    opener = open_youtube_app if STEP_REFERENCES[step] == 15 else open_google_one_app
    return opener(serial)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--step", type=int, choices=tuple(STEP_REFERENCES), required=True)
    parser.add_argument("--serial", default="")
    args = parser.parse_args()
    print(f"Step {args.step}: {research_step_label(args.step)}")
    print("Reported reference only. Verify actual availability, account and full pricing in the official app.")
    try:
        status = run_step(args.step, args.serial)
    except Exception:
        status = "launch_failed"
    print(f"EPLUS_RESEARCH_RESULT:{status}")
    if status == "opened":
        print("Review and redeem manually in the official app. No checkout or purchase was initiated by this script.")
        return 0
    print("Could not open the official app. Check Android, ADB and the installed application.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
