#!/usr/bin/env bash
# Diagnose the billable GCE Android PoC VM using IAP SSH (no public ADB).
set -Eeuo pipefail
command -v gcloud >/dev/null || { echo "gcloud CLI is required." >&2; exit 1; }
PROJECT_ID="$(printenv PROJECT_ID || true)"
if [ -z "$PROJECT_ID" ]; then PROJECT_ID="$(gcloud config get-value project 2>/dev/null || true)"; fi
[ -n "$PROJECT_ID" ] && [ "$PROJECT_ID" != "(unset)" ] || { echo "Set PROJECT_ID" >&2; exit 1; }
ZONE="$(printenv ZONE || echo us-central1-a)"
VM_NAME="$(printenv VM_NAME || echo eplus-ai-cloud-poc)"
echo "Inspecting $VM_NAME in $PROJECT_ID/$ZONE via IAP..."
gcloud compute ssh "$VM_NAME" --project="$PROJECT_ID" --zone="$ZONE" \
  --tunnel-through-iap --command="sudo bash -lc 'if [ -x /usr/local/bin/eplus-ai-cloud-check ]; then /usr/local/bin/eplus-ai-cloud-check; else echo Startup is not finished; tail -n 35 /var/log/eplus-ai-cloud-startup.log; fi'"
