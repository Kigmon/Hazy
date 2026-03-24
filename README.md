# NemoClaw Control (Ubuntu-first)

NemoClaw Control is a native PySide6 Ubuntu desktop app for installing, detecting, repairing, and operating a NemoClaw + OpenShell + Ollama setup from a single GUI.

## Download

### If the repo is public

```bash
git clone https://github.com/<owner>/Hazy.git
cd Hazy
```

### If the repo is private

Use one of these:

1. **GitHub CLI (easiest)**
```bash
gh auth login
gh repo clone <owner>/Hazy
cd Hazy
```

2. **HTTPS with Personal Access Token (PAT)**
```bash
git clone https://github.com/<owner>/Hazy.git
# username: your github username
# password: paste a PAT (not your GitHub password)
cd Hazy
```

3. **SSH (recommended long-term)**
```bash
ssh-keygen -t ed25519 -C "you@example.com"
cat ~/.ssh/id_ed25519.pub
# add key in GitHub > Settings > SSH and GPG keys

git clone git@github.com:<owner>/Hazy.git
cd Hazy
```

## Publish to GitHub (owner one-time step)

If your GitHub repo still only has `.gitkeep`, publish this code to `main` with one command:

```bash
./scripts/publish-main-and-build.sh https://github.com/<owner>/Hazy.git
```

This will:
1. move current local code to branch `main`
2. push `main` to GitHub
3. trigger the `.deb` build workflow (if `gh` is installed)

## GitHub push troubleshooting (important)

If you hit:

- `pre-receive hook declined`
- `HTTP 403` from `gh api repos/<owner>/<repo>/rulesets` with message:
  `Upgrade to GitHub Pro or make this repository public to enable this feature.`

that is a GitHub plan/feature limitation for **rulesets API access on private repos**. It does **not** always mean your repo is broken.

Use this practical flow:

1. **Make the repository public temporarily** (or upgrade to GitHub Pro), then retry publish.
2. If org/repo protections still block `main`, push a feature branch and open a PR.
3. Run the diagnostic helper:

```bash
./scripts/github-push-doctor.sh
```

The script checks auth, repo permissions, branch protections, and gives next actions.

## IMPORTANT: Why your clone looked empty

If `git log` only shows `Initialize repository` and the repo only contains `.gitkeep`, then the app commits were never pushed to `origin/main` yet. In that case there is nothing to launch locally until the code is pushed.

## Zero-terminal install path (after code is pushed)

1. Open the repo in browser: `https://github.com/<owner>/Hazy`
2. Open **Actions** → **Build Debian Package**
3. Open the latest successful run and download artifact **nemoclaw-control-deb**
4. Double-click the downloaded `.deb` in Ubuntu Software and click Install
5. Open app menu and launch **NemoClaw Control**

## What this first version automates

- Immediate visible launch (splash) and persistent launch logs.
- Health detection of Docker, Ollama service state, Ollama reachability, model list, OpenShell path/version, NemoClaw path/version, gateway reachability, sandbox evidence, dashboard reachability.
- Predefined recovery actions in GUI (no arbitrary shell):
  - Start/restart Docker
  - Start/restart Ollama
  - Run `nemoclaw onboard`
  - Run `nemoclaw goat connect`
  - Pull default model `nemotron-3-nano:30b`
- NemoClaw-first recovery recommendation logic when sandbox exists but gateway is unhealthy.
- Twitch credential capture and token validation (`id.twitch.tv/oauth2/validate`).
- In-app logs + disk logs under `~/.local/state/nemoclaw-control/`.

## What still needs credentials/admin confirmation

- Admin privileges are required for service operations (`pkexec systemctl ...`).
- Twitch requires user-provided token/client credentials and correct scopes.
- Installing Docker/Ollama/OpenShell/NemoClaw binaries themselves is environment-dependent and not bundled by this app.

## Handling existing/partial installs

Detection is multi-signal:
- command availability and versions
- service active state
- network socket probes
- `nemoclaw status` output + return code
- known credentials file (`~/.nemoclaw/credentials.json`)

The app avoids destructive recreation by default and recommends safe repair steps first.

## Known-good target setup alignment (Ubuntu 24.04)

Default assumptions in this version match your known-good profile:
- Sandbox: `goat`
- Gateway name: `nemoclaw`
- Expected default model: `nemotron-3-nano:30b`
- Dashboard URL button: `http://127.0.0.1:18789/`
- Gateway health probe: `127.0.0.1:8080`
- Ollama health probe: `127.0.0.1:11434`

> Note: bind-address repair for `0.0.0.0:11434` override path is represented as health checks and admin actions in this version; policy-specific file edits can be added as a next hardening step.

## Package layout

- Python package: `src/nemoclaw_control/`
- Debian packaging: `debian/`
- Desktop entry: `packaging/nemoclaw-control.desktop`
- Launcher script: `scripts/nemoclaw-control-launcher`
- Tests: `tests/`

## Fastest way to download, install, and launch

If you already cloned this repo, run one command:

```bash
./scripts/easy-install-and-launch.sh
```

This will:
1. install required Ubuntu packages
2. build the `.deb`
3. install the `.deb`
4. launch **NemoClaw Control**

If you prefer manual install, use the steps below.

## Build and install `.deb`

```bash
sudo apt-get install -y build-essential debhelper dh-python python3-all python3-setuptools
DEB_BUILD_OPTIONS=nocheck dpkg-buildpackage -us -uc -b
sudo apt install ../nemoclaw-control_0.1.0-1_all.deb
```

Launch from Ubuntu app menu: **NemoClaw Control**.

## Dev run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
nemoclaw-control
```

## Test

```bash
pytest -q
```
