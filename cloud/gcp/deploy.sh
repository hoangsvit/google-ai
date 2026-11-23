#!/usr/bin/env bash
# Create an isolated GCE Android Emulator proof-of-concept VM.
# No Google Play purchases, account actions, or public ADB/WebRTC ports.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
command -v gcloud >/dev/null || { echo "Install Google Cloud CLI (Cloud Shell already has it)." >&2; exit 1; }

PROJECT_ID="$(printenv PROJECT_ID || true)"
if [ -z "$PROJECT_ID" ]; then
  PROJECT_ID="$(gcloud config get-value project 2>/dev/null || true)"
fi
[ -n "$PROJECT_ID" ] && [ "$PROJECT_ID" != "(unset)" ] || {
  echo "Set PROJECT_ID or run: gcloud config set project PROJECT_ID" >&2
  exit 1
}
ZONE="$(printenv ZONE || echo us-central1-a)"
REGION="$(printf '%s' "$ZONE" | sed 's/-[a-z]$//')"
VM_NAME="$(printenv VM_NAME || echo eplus-ai-cloud-poc)"
NETWORK="$(printenv NETWORK || echo eplus-ai-cloud-poc-net)"
SUBNET="$(printenv SUBNET || echo eplus-ai-cloud-poc-subnet)"
FIREWALL="$(printenv FIREWALL || echo eplus-ai-cloud-poc-iap-ssh)"
MACHINE_TYPE="$(printenv MACHINE_TYPE || echo n2-standard-4)"
GIT_REF="$(printenv GIT_REF || echo dev)"
ANDROID_IMAGE="$(printenv ANDROID_IMAGE || echo us-docker.pkg.dev/android-emulator-268719/images/30-google-x64:30.1.2)"

for resource in "$VM_NAME" "$NETWORK" "$SUBNET" "$FIREWALL"; do
  [[ "$resource" =~ ^[a-z]([-a-z0-9]*[a-z0-9])?$ ]] && [ "$resource" != "" ] || {
    echo "Invalid GCE resource name: $resource" >&2; exit 1;
  }
done
[[ "$ZONE" =~ ^[a-z]+-[a-z]+[0-9]+-[a-z]$ ]] || { echo "Invalid ZONE" >&2; exit 1; }
[[ "$MACHINE_TYPE" =~ ^(n2|n2d|c2|c2d)- ]] || {
  echo "Use a machine family supporting nested virtualization (e.g. n2-standard-4)." >&2; exit 1;
}
[[ "$GIT_REF" =~ ^[A-Za-z0-9._/-]+$ ]] || { echo "Invalid GIT_REF" >&2; exit 1; }
[[ "$ANDROID_IMAGE" == us-docker.pkg.dev/android-emulator-268719/images/* ]] || {
  echo "Only official Android Emulator demo images are accepted in this PoC." >&2; exit 1;
}
[ -f "$ROOT/startup.sh" ] || { echo "Missing startup.sh" >&2; exit 1; }

echo "Google Cloud project: $PROJECT_ID"
echo "Creating billable $MACHINE_TYPE VM $VM_NAME in $ZONE (80 GiB disk)."
echo "No public inbound access will be configured. SSH uses IAP TCP forwarding."
echo "This PoC does not guarantee Google Play, root or Frida compatibility."
if [ "$(printenv CONFIRM_COST || true)" != "yes" ]; then
  echo "To approve cloud charges, rerun with CONFIRM_COST=yes." >&2
  exit 2
fi

gcloud services enable compute.googleapis.com iap.googleapis.com --project="$PROJECT_ID"
if ! gcloud compute networks describe "$NETWORK" --project="$PROJECT_ID" >/dev/null 2>&1; then
  gcloud compute networks create "$NETWORK" --subnet-mode=custom --project="$PROJECT_ID" --quiet
fi
if ! gcloud compute networks subnets describe "$SUBNET" --region="$REGION" --project="$PROJECT_ID" >/dev/null 2>&1; then
  gcloud compute networks subnets create "$SUBNET" --network="$NETWORK" \
    --range=10.222.0.0/24 --region="$REGION" --project="$PROJECT_ID" --quiet
fi
if ! gcloud compute firewall-rules describe "$FIREWALL" --project="$PROJECT_ID" >/dev/null 2>&1; then
  gcloud compute firewall-rules create "$FIREWALL" --network="$NETWORK" \
    --direction=INGRESS --action=ALLOW --rules=tcp:22 \
    --source-ranges=35.235.240.0/20 --target-tags=eplus-ai-cloud-poc \
    --project="$PROJECT_ID" --quiet
fi

if gcloud compute instances describe "$VM_NAME" --zone="$ZONE" --project="$PROJECT_ID" >/dev/null 2>&1; then
  echo "VM already exists; refusing to overwrite. Check it with cloud/gcp/check.sh." >&2
  exit 3
fi
gcloud compute instances create "$VM_NAME" \
  --project="$PROJECT_ID" --zone="$ZONE" \
  --machine-type="$MACHINE_TYPE" --enable-nested-virtualization \
  --maintenance-policy=TERMINATE \
  --image-project=ubuntu-os-cloud --image-family=ubuntu-2404-lts-amd64 \
  --boot-disk-size=80GB --boot-disk-type=pd-balanced \
  --network="$NETWORK" --subnet="$SUBNET" \
  --tags=eplus-ai-cloud-poc \
  --metadata-from-file="startup-script=$ROOT/startup.sh" \
  --metadata="eplus_git_ref=$GIT_REF,eplus_android_image=$ANDROID_IMAGE" \
  --project="$PROJECT_ID" --quiet
echo "VM created. Startup installs Docker/ADB, clones the toolkit and starts one Android container."
echo "Startup can take several minutes. Run: PROJECT_ID=$PROJECT_ID ZONE=$ZONE VM_NAME=$VM_NAME bash cloud/gcp/check.sh"
echo "To avoid charges, stop/delete the VM when finished. See cloud/gcp/README.md."
