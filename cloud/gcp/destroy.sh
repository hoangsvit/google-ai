#!/usr/bin/env bash
# Explicit, scoped teardown for the isolated GCE PoC resources.
set -Eeuo pipefail
[ "$(printenv CONFIRM_DESTROY || true)" = "yes" ] || {
  echo "Deletion is destructive. Rerun with CONFIRM_DESTROY=yes." >&2
  exit 2
}
command -v gcloud >/dev/null || { echo "gcloud CLI is required." >&2; exit 1; }
PROJECT_ID="$(printenv PROJECT_ID || true)"
if [ -z "$PROJECT_ID" ]; then PROJECT_ID="$(gcloud config get-value project 2>/dev/null || true)"; fi
[ -n "$PROJECT_ID" ] && [ "$PROJECT_ID" != "(unset)" ] || { echo "Set PROJECT_ID" >&2; exit 1; }
ZONE="$(printenv ZONE || echo us-central1-a)"
REGION="$(printf '%s' "$ZONE" | sed 's/-[a-z]$//')"
VM_NAME="$(printenv VM_NAME || echo eplus-ai-cloud-poc)"
NETWORK="$(printenv NETWORK || echo eplus-ai-cloud-poc-net)"
SUBNET="$(printenv SUBNET || echo eplus-ai-cloud-poc-subnet)"
FIREWALL="$(printenv FIREWALL || echo eplus-ai-cloud-poc-iap-ssh)"
for resource in "$VM_NAME" "$NETWORK" "$SUBNET" "$FIREWALL"; do
  [[ "$resource" =~ ^[a-z]([-a-z0-9]*[a-z0-9])?$ ]] || { echo "Invalid name: $resource" >&2; exit 1; }
done

echo "Deleting $VM_NAME, $FIREWALL, $SUBNET, $NETWORK in project $PROJECT_ID."
if gcloud compute instances describe "$VM_NAME" --zone="$ZONE" --project="$PROJECT_ID" >/dev/null 2>&1; then
  gcloud compute instances delete "$VM_NAME" --zone="$ZONE" --project="$PROJECT_ID" --quiet
fi
if gcloud compute firewall-rules describe "$FIREWALL" --project="$PROJECT_ID" >/dev/null 2>&1; then
  gcloud compute firewall-rules delete "$FIREWALL" --project="$PROJECT_ID" --quiet
fi
if gcloud compute networks subnets describe "$SUBNET" --region="$REGION" --project="$PROJECT_ID" >/dev/null 2>&1; then
  gcloud compute networks subnets delete "$SUBNET" --region="$REGION" --project="$PROJECT_ID" --quiet
fi
if gcloud compute networks describe "$NETWORK" --project="$PROJECT_ID" >/dev/null 2>&1; then
  gcloud compute networks delete "$NETWORK" --project="$PROJECT_ID" --quiet
fi
echo "PoC resources removed. Verify any independent costs (logs, billing exports) separately."
