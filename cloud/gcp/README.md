# Google Compute Engine Android Emulator — experimental PoC

This folder provides an **opt-in, billable** GCE deployment of a single Android Emulator container and the Python ePlus AI Toolkit. It is intended to answer the Android/ADB/Frida feasibility question **before** attempting a shared web service.

**This is NOT a 100%-cloud subscription website.** There is no login dashboard, per-user session isolation, hosted checkout, billing automation or public WebRTC frontend in this PoC. None of Steps 0–5 are started automatically. The hosted demo image may not include the official Google Play Store, does not promise root, and does not prove that Frida or Google One works.

## Prerequisites

- An active **billable** Google Cloud project (free-tier micro VM is not sufficient).
- Cloud Shell or another host with Google Cloud CLI, authenticated to the project.
- Permissions to enable Compute Engine, create VPC/subnet/firewall/VM resources and connect via IAP SSH. IAP TCP forwarding and appropriate SSH/OS Login permissions may need configuration.
- Nested virtualization allowed by project/organization policy, quota for an N2 machine in the chosen zone.
- No accounts, payment cards or verification secrets should be placed in VM metadata or scripts.

The default VM is N2 4-vCPU/16-GiB with an 80-GiB balanced persistent disk. **Running/stopped storage and other resources can cost money.** The VM has a temporary public IP for fetching system packages/images, but the dedicated VPC permits only IAP-to-SSH inbound traffic. The Docker ADB (5555) and gRPC (8554) bindings are loopback-only; no ports are exposed publicly. Do not copy these images into a multi-tenant server.

## Deploy from Google Cloud Shell

~~~bash
git clone https://github.com/hoangsvit/google-ai.git
cd google-ai
git checkout feat/gcp-android-cloud-poc  # Before the Draft PR is merged; later use dev

export PROJECT_ID="YOUR_GCP_PROJECT_ID"
export ZONE="us-central1-a"  # Choose supported region/zone; e.g. asia-southeast1-b
GIT_REF=feat/gcp-android-cloud-poc CONFIRM_COST=yes bash cloud/gcp/deploy.sh
~~~

Deploy provisions a dedicated custom VPC, subnet, IAP SSH firewall rule, and Ubuntu 24.04 Compute Engine VM with nested virtualization. During first boot, the VM installs Docker, Python, ADB and Frida 16.5.9, clones this repository's selected ref (default: dev; select the feature branch to test the PR), and starts an official prebuilt Android Emulator image.

The official demo image used by default is **us-docker.pkg.dev/android-emulator-268719/images/30-google-x64:30.1.2** (an experimental image; not a verified Play Store/root environment). You can change its image under the same official registry using ANDROID_IMAGE when deploying, but compatibility must be tested. Use GIT_REF to choose a reviewed repository branch.

~~~bash
PROJECT_ID="YOUR_GCP_PROJECT_ID" ZONE="us-central1-a" \
  bash cloud/gcp/check.sh
~~~

The check connects through IAP SSH and displays KVM, Docker and ADB status, Android boot completion and whether the Play Store package is present. It **does not buy subscriptions or run Steps 2–5**. If startup has not finished, it prints the latest startup log.

To access the VM for **manual diagnostics only**:

~~~bash
gcloud compute ssh eplus-ai-cloud-poc \
  --project="$PROJECT_ID" --zone="$ZONE" --tunnel-through-iap

# On the VM:
sudo eplus-ai-cloud-check
sudo tail -n 100 /var/log/eplus-ai-cloud-startup.log
sudo docker logs --tail 100 eplus-ai-android
# Toolkit is at /opt/eplus-ai-toolkit, venv at /opt/eplus-ai-venv
~~~

Do not run paid-step commands until a compatible authorized Play Store/device exists and the user has independently reviewed/approved the charge. A Google Play sign-in cannot be replaced by your website's Google OAuth login.

## Stop charging for the VM

To stop compute charges but retain the disk, stop the VM using gcloud. Disk storage still incurs cost:

~~~bash
gcloud compute instances stop eplus-ai-cloud-poc --project="$PROJECT_ID" --zone="$ZONE"
~~~

To delete this PoC's VM, firewall, subnet and network, run:

~~~bash
CONFIRM_DESTROY=yes bash cloud/gcp/destroy.sh
~~~

Both scripts accept PROJECT_ID, ZONE, VM_NAME; the deploy/destroy scripts also accept NETWORK, SUBNET, FIREWALL. Keep names consistent for deletion. Do **not** use the default resource names in a project where those names are already used for unrelated infrastructure. The teardown only deletes resources with the selected names; it cannot refund charges incurred.

## Limitations / acceptance gates

1. Host reports /dev/kvm present, Docker emulator booted (sys.boot_completed=1), ADB device online.
2. Explicitly check Play Store and Google One availability on **the target Android image**. Google APIs-only images are not equivalent to certified Play Store images.
3. Check whether Frida host/server can work on that Android build with root permissions. This PoC installs **host Frida**, but does not install/inject frida-server or run a billing hook automatically.
4. Stop if verified Play Store, root and Frida cannot coexist under supported policies; do not bypass Google/device integrity, eligibility or payment security checks.
5. Only after these gates pass should separate PRs implement protected WebRTC access, a browser dashboard, isolated user sessions, accounting and per-stage explicit approvals.

See [Google's emulator container documentation](https://github.com/google/android-emulator-container-scripts), [GCE nested virtualization](https://cloud.google.com/compute/docs/instances/nested-virtualization/enabling) and [IAP TCP forwarding](https://cloud.google.com/iap/docs/using-tcp-forwarding).
