#!/usr/bin/env bash
set -euo pipefail

APP="nemoclaw-control"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR"

echo "[1/5] Installing build dependencies (requires sudo)..."
sudo apt-get update
sudo apt-get install -y build-essential debhelper dh-python python3-all python3-setuptools python3-pyside6 python3-requests python3-keyring policykit-1

echo "[2/5] Building .deb..."
DEB_BUILD_OPTIONS=nocheck dpkg-buildpackage -us -uc -b

echo "[3/5] Installing .deb..."
DEB_FILE="$(ls -1 ../${APP}_*_all.deb | tail -n 1)"
sudo apt install -y "$DEB_FILE"

echo "[4/5] Launching app..."
nohup /usr/bin/${APP} >/dev/null 2>&1 &

echo "[5/5] Done. You can now find 'NemoClaw Control' in Ubuntu app menu."
echo "    Launcher logs: ~/.local/state/nemoclaw-control/launch.log"
