# ESPHome CI/CD Bootstrap

## Overview

This is a **repository bootstrap tool** that writes GitHub Actions workflows and helper scripts directly to your ESPHome firmware repository. It automates firmware validation, compilation, and release processes for ESPHome-based IoT devices.

**This is NOT a web application** - it's a simple shell script that sets up CI/CD automation in your local repository.

## What It Does

Running the bootstrap script writes these files to your repository:
- **GitHub Actions workflows** for CI/CD automation
- **Python helper scripts** for firmware renaming and manifest generation
- **Configuration templates** for secrets and WebFlash manifests
- **Git commits** the changes (idempotent - safe to run multiple times)

## Usage

### Lite Mode (Default)
Creates basic CI workflow that validates and compiles ESPHome configs on every push:

```bash
bash bootstrap_ci.sh
```

This creates:
- `.github/workflows/esphome-lite.yml` - Validates + compiles on PR/push, uploads `.bin` artifacts
- `esphome/secrets.example.yaml` - Placeholder secrets for CI
- `webflash/manifest.template.json` - WebFlash manifest template

### Full Mode
Adds release automation with tagged releases and WebFlash manifest generation:

```bash
MODE=full bash bootstrap_ci.sh
```

This creates everything from lite mode, plus:
- `.github/workflows/esphome-release.yml` - Tag-triggered release workflow
- `scripts/rename_bins.py` - Renames firmware binaries with version tags
- `scripts/gen_manifest.py` - Generates WebFlash manifest from template

## Architecture

### No Web Server
- **No Express/Flask/Vite/Next.js** - This is a local bootstrap script only
- **No HTML/CSS/JS frontends** - Command-line tool
- **No download endpoints** - Files written directly to filesystem

### No Database
- **Stateless operation** - No persistence needed
- **No user accounts** - Simple script execution
- **No API** - Direct file system operations

### Bootstrap Script Design
The `bootstrap_ci.sh` script:
1. Creates directory structure (`.github/workflows`, `scripts`, `esphome`, `webflash`)
2. Writes workflow YAML files using heredocs
3. Writes Python helper scripts (in full mode)
4. Creates placeholder configuration files if missing
5. Performs git init and commits changes (idempotent)
6. Outputs instructions for GitHub setup

## GitHub Setup (After Bootstrap)

1. **Push to GitHub:**
   ```bash
   git remote add origin <YOUR_GITHUB_REPO_URL>
   git push -u origin main
   ```

2. **Enable GitHub Actions:**
   - Go to: `Settings → Actions → General`
   - Allow all actions
   - Workflow permissions: Read & write

3. **Trigger CI:**
   - Push any change under `esphome/**` to trigger validation and compilation
   - Artifacts appear under `Actions → [workflow run] → Artifacts → firmware-bins`

4. **Create Releases (Full Mode Only):**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
   - Creates GitHub Release with renamed `.bin` files and `manifest.json`

## File Generation Details

### esphome-lite.yml
- Triggers on: push/PR affecting `esphome/**` files
- Validates all non-factory YAML configs
- Compiles firmware to `.bin` files
- Uploads artifacts for download

### esphome-release.yml (Full Mode)
- Triggers on: version tags (`v*.*.*`)
- Compiles all configs
- Renames binaries with version tags
- Generates WebFlash manifest
- Creates GitHub Release with artifacts

### Python Scripts (Full Mode)
- **rename_bins.py**: Renames firmware files to `sense360-{product}-{profile}-{version}.bin`
- **gen_manifest.py**: Replaces `vX.Y.Z` placeholders in manifest template with actual version

## Repository Structure

```
.
├── bootstrap_ci.sh                 # Bootstrap script
├── .github/
│   └── workflows/
│       ├── esphome-lite.yml       # CI workflow (always)
│       └── esphome-release.yml    # Release workflow (full mode)
├── scripts/
│   ├── rename_bins.py             # Firmware renaming (full mode)
│   └── gen_manifest.py            # Manifest generation (full mode)
├── esphome/
│   ├── configs/                   # Your ESPHome YAML configs
│   └── secrets.example.yaml       # Placeholder secrets
└── webflash/
    └── manifest.template.json     # WebFlash manifest template
```

## Existing ESPHome Content

**Important:** The bootstrap script **does not touch** existing `esphome/**` content. Your existing firmware configurations are preserved.

## User Preferences

Preferred communication style: Simple, everyday language.
