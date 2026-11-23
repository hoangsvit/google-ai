#!/usr/bin/env bash
# GCE startup metadata script. Runs as root on Ubuntu 24.04.
# Deliberately does NOT start Google Play checkout or collect credentials.
set -Eeuo pipefail
exec >>/var/log/eplus-ai-cloud-startup.log 2>&1
echo "=== ePlus AI cloud PoC startup: $(date -u) ==="
export DEBIAN_FRONTEND=noninteractive

if [ ! -c /dev/kvm ]; then
  echo "ERROR: /dev/kvm is unavailable. Verify GCE nested virtualization support and policy." >&2
  exit 1
fi

apt-get update
apt-get install -y docker.io adb git python3 python3-venv python3-pip curl ca-certificates
systemctl enable --now docker

metadata() {
  curl --fail --silent --show-error --max-time 3 \
    -H 'Metadata-Flavor: Google' \
    "http://metadata.google.internal/computeMetadata/v1/instance/attributes/$1"
}
GIT_REF="$(metadata eplus_git_ref || printf '%s' dev)"
ANDROID_IMAGE="$(metadata eplus_android_image || printf '%s' us-docker.pkg.dev/android-emulator-268719/images/30-google-x64:30.1.2)"
[[ "$GIT_REF" =~ ^[A-Za-z0-9._/-]+$ ]] || { echo "Invalid toolkit ref"; exit 1; }
[[ "$ANDROID_IMAGE" == us-docker.pkg.dev/android-emulator-268719/images/* ]] || {
  echo "Unexpected Docker image; refusing startup"; exit 1;
}

mkdir -p /opt/eplus-ai-toolkit /root/.android
chmod 700 /root/.android
if [ ! -f /root/.android/adbkey ]; then
  adb keygen /root/.android/adbkey >/dev/null
fi
chmod 600 /root/.android/adbkey

if [ ! -d /opt/eplus-ai-toolkit/.git ]; then
  git clone --no-checkout https://github.com/hoangsvit/google-ai.git /opt/eplus-ai-toolkit
fi
git -C /opt/eplus-ai-toolkit fetch --depth=1 origin "$GIT_REF"
git -C /opt/eplus-ai-toolkit checkout --detach FETCH_HEAD

if [ ! -x /opt/eplus-ai-venv/bin/python ]; then
  python3 -m venv /opt/eplus-ai-venv
fi
/opt/eplus-ai-venv/bin/pip install --disable-pip-version-check --no-cache-dir \
  "frida==16.5.9" -r /opt/eplus-ai-toolkit/requirements-tui.txt

# Keep ADB and emulator gRPC/WebRTC bound ONLY to the VM loopback interface.
# Never add firewall rules for ports 5555 or 8554.
docker pull "$ANDROID_IMAGE"
docker rm -f eplus-ai-android >/dev/null 2>&1 || true
export ADBKEY
ADBKEY="$(cat /root/.android/adbkey)"
docker run -d --name eplus-ai-android --restart unless-stopped \
  --device /dev/kvm \
  --publish 127.0.0.1:5555:5555/tcp \
  --publish 127.0.0.1:8554:8554/tcp \
  --env ADBKEY \
  "$ANDROID_IMAGE"
unset ADBKEY

cat >/usr/local/bin/eplus-ai-cloud-check <<'CHECK_SCRIPT'
#!/usr/bin/env bash
set -u
echo "KVM device:"
ls -l /dev/kvm || exit 1
echo "Docker container:"
docker ps --filter name=eplus-ai-android --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
echo "ADB connecting to loopback-only emulator:"
adb connect 127.0.0.1:5555 || true
adb devices
echo "Android boot completed (1 means booted):"
adb -s 127.0.0.1:5555 shell getprop sys.boot_completed || true
echo "Google Play Store package (not guaranteed by this demo image):"
adb -s 127.0.0.1:5555 shell pm path com.android.vending || true
echo "Current Android shell identity (does not elevate privileges):"
adb -s 127.0.0.1:5555 shell id || true
echo "Do not assume Google One or Frida compatibility from an emulator boot."
CHECK_SCRIPT
chmod 755 /usr/local/bin/eplus-ai-cloud-check
echo "PoC environment provisioned; no billing step executed."
echo "Use sudo eplus-ai-cloud-check after the emulator finishes booting."
