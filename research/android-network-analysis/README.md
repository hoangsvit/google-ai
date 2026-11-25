# Android network analysis — isolated research

## Goal
Evaluate whether network diagnostics on an owned Android test application can explain DNS, timeout, HTTP and TLS failures independently of Frida. This is not an alternative offer acquisition engine. No change to Steps 0–5, launchers, dependencies or billing behavior.

## Feasibility
- mitmproxy supports standard HTTP(S) proxying; use only an owned debug application and an owned test endpoint in an isolated lab.
- Android apps do not universally trust user-installed CAs. Debug-only trust configuration applies to applications we control. Do not disable certificate verification or bypass third-party app protections.
- Play Billing eligibility is validated independently of network visibility; network diagnostics cannot establish eligibility or a successful subscription.
- No Google account, live Google response, checkout, certificate modification or payment action is necessary for this prototype.

## Run locally
From the repository root (Python 3.10+, standard library only):
```sh
python research/android-network-analysis/network_health.py --demo
python research/android-network-analysis/network_health.py --self-test
```
Use `python3` if required by your platform. Optional input: `--input sanitized.json`. Only synthetic/sanitized observations with an outcome and integer duration_ms are accepted. Example:
```json
[{"outcome":"ok","duration_ms":100},{"outcome":"tls_error","duration_ms":250}]
```
No URLs, headers, bodies, credentials, account identifiers or tokens are needed or accepted. The prototype does not capture or transmit traffic.

## Test matrix (not yet executed on devices)
| Test | Expected evidence |
| --- | --- |
| Owned debug app, direct connection | Baseline latency and success |
| Owned debug app, authorized proxy | Compare success and latency |
| Simulated DNS failure | dns_error classification |
| Simulated TLS failure | tls_error classification |
| Simulated timeout | timeout classification |
| Android emulator and physical device | Separate observations; no assumption of compatibility |

## Decision gates
1. Offline tests pass.
2. Demonstrate repeatable observations on a controlled app, without root or Frida.
3. Compare against direct connection and document limitations.
4. Decide whether generic diagnostics merit integration. Keep research separate until reviewed.

## References
- https://developer.android.com/privacy-and-security/security-config
- https://docs.mitmproxy.org/stable/concepts/modes/
- https://developer.android.com/google/play/billing/integrate

Status: offline prototype only; no live Android or Google One verification.
