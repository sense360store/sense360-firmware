# ESPHome CI/CD Bootstrap

Automate your ESPHome firmware builds with GitHub Actions. This bootstrap script sets up complete CI/CD workflows in your repository - no web server, no complex configuration, just working automation.

## Quick Start

```bash
# Basic CI (validate + compile + artifacts)
bash bootstrap_ci.sh

# Full CI (includes tagged releases + WebFlash manifest)
MODE=full bash bootstrap_ci.sh
```

## What Gets Created

### Lite Mode (Default)
- ✅ `.github/workflows/esphome-lite.yml` - Validates and compiles on every push
- ✅ `esphome/secrets.example.yaml` - Placeholder secrets for CI
- ✅ `webflash/manifest.template.json` - WebFlash manifest template

**Result:** Every push to `esphome/**` triggers validation and compilation. Download `.bin` files from GitHub Actions artifacts.

### Full Mode
Everything from lite mode, plus:
- ✅ `.github/workflows/esphome-release.yml` - Tag-triggered releases
- ✅ `scripts/rename_bins.py` - Version-tagged firmware renaming
- ✅ `scripts/gen_manifest.py` - WebFlash manifest generation

**Result:** Create a version tag (`v1.0.0`) to automatically build, rename, and publish firmware as a GitHub Release with WebFlash manifest.

## Usage

### 1. Run Bootstrap Script

```bash
# For basic CI
bash bootstrap_ci.sh

# For full CI with releases
MODE=full bash bootstrap_ci.sh
```

The script:
- Creates `.github/workflows/` with CI/CD workflows
- Adds placeholder configuration files
- Git commits the changes (safe to run multiple times)

### 2. Push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 3. Configure GitHub Actions

Go to: **Settings → Actions → General**

- ✅ Allow all actions and reusable workflows
- ✅ Workflow permissions: **Read and write permissions**
- ✅ Allow GitHub Actions to create and approve pull requests

### 4. Trigger Builds

**Automatic CI (Lite & Full Mode):**
```bash
# Make any change to ESPHome configs
git add esphome/configs/my-device.yaml
git commit -m "Update device config"
git push
```

View artifacts: **Actions → [workflow run] → Artifacts → firmware-bins**

**Create Release (Full Mode Only):**
```bash
git tag v1.0.0
git push origin v1.0.0
```

View release: **Releases** - Download renamed `.bin` files and `manifest.json`

## CI/CD Workflows

### ESPHome Lite CI
**Triggers:** Push or PR affecting `esphome/**`

**What it does:**
1. Installs Python 3.12 + ESPHome 2024.11.0+
2. Creates `esphome/secrets.yaml` from example (for CI)
3. Validates all non-factory configs: `esphome config <file>`
4. Compiles all validated configs: `esphome compile <file>`
5. Uploads `.bin` artifacts to GitHub

### ESPHome Tag Release (Full Mode)
**Triggers:** Git tags matching `v*.*.*` (e.g., `v1.0.0`)

**What it does:**
1. Installs dependencies and compiles firmware
2. Renames binaries: `sense360-{product}-{profile}-{version}.bin`
3. Generates WebFlash `manifest.json` from template
4. Creates GitHub Release with all artifacts

## Configuration Files

### secrets.example.yaml
Placeholder secrets for CI compilation:

```yaml
wifi_ssid: "YOUR_WIFI_SSID"
wifi_password: "YOUR_WIFI_PASSWORD"
api_key: "REPLACE_WITH_BASE64_32B_KEY"   # openssl rand -base64 32
ota_password: "REPLACE_WITH_STRONG_PASSWORD"
```

**Note:** CI uses this automatically. For local development, copy to `esphome/secrets.yaml` with real values.

### manifest.template.json
WebFlash manifest template for ESP Web Tools:

```json
{
  "$schema": "https://esphome.io/web/manifest-schema.json",
  "name": "Sense360",
  "version": "vX.Y.Z",
  "builds": [
    {
      "chipFamily": "ESP32-S3",
      "parts": [{ "path": "sense360-airiq-basic-vX.Y.Z.bin", "offset": 0 }],
      "capabilities": ["airiq","sen55","scd4x","ld2412","basic"]
    }
  ]
}
```

The `gen_manifest.py` script replaces `vX.Y.Z` with actual version tags.

## Helper Scripts (Full Mode)

### rename_bins.py
Renames compiled firmware with version tags:

```bash
python3 scripts/rename_bins.py dist/ v1.0.0 release/
# Input:  dist/.esphome/build/airiq-basic/.pioenvs/airiq-basic/firmware.bin
# Output: release/sense360-airiq-basic-v1.0.0.bin
```

### gen_manifest.py
Generates versioned WebFlash manifest:

```bash
python3 scripts/gen_manifest.py webflash/manifest.template.json v1.0.0 release/manifest.json
# Replaces all vX.Y.Z with v1.0.0 in template
```

## Repository Structure

```
your-esphome-repo/
├── bootstrap_ci.sh              # Run this to set up CI/CD
├── .github/
│   └── workflows/
│       ├── esphome-lite.yml     # CI workflow (always created)
│       └── esphome-release.yml  # Release workflow (full mode only)
├── scripts/                      # Full mode only
│   ├── rename_bins.py
│   └── gen_manifest.py
├── esphome/
│   ├── configs/                 # Your ESPHome device configs
│   │   ├── device1.yaml
│   │   └── device2.yaml
│   ├── secrets.yaml             # Your actual secrets (gitignored)
│   └── secrets.example.yaml     # Placeholder for CI
└── webflash/
    └── manifest.template.json   # WebFlash manifest template
```

## FAQ

### Can I run the bootstrap script multiple times?
Yes! The script is idempotent - it safely overwrites existing files and won't duplicate git commits.

### Will this modify my existing ESPHome configs?
No. The bootstrap script never touches files under `esphome/configs/`. Your device configurations are safe.

### What if I don't have any configs yet?
The CI workflow will run but report "No non-factory configs found." Add configs under `esphome/configs/` and push again.

### How do I update workflows later?
Run `bash bootstrap_ci.sh` (or `MODE=full`) again to regenerate workflows with latest changes.

### Can I customize the workflows?
Yes! After bootstrapping, edit `.github/workflows/*.yml` directly. Changes persist until you re-run the bootstrap script.

### Where do I add my real WiFi passwords?
1. Copy `esphome/secrets.example.yaml` to `esphome/secrets.yaml`
2. Fill in your real credentials
3. Add `esphome/secrets.yaml` to `.gitignore` (should already be ignored)

CI automatically uses the example file, so your secrets stay safe.

## Troubleshooting

### "No .bin files found"
- Ensure your configs are under `esphome/configs/` (not root `esphome/`)
- Check workflow logs for compilation errors
- Verify configs don't have `_factory.yaml` suffix (those are skipped)

### "Permission denied" on script execution
```bash
chmod +x bootstrap_ci.sh
bash bootstrap_ci.sh
```

### Workflow fails with "secrets.yaml not found"
The workflow should automatically create it from `secrets.example.yaml`. Check that the example file exists.

### Artifacts not uploaded
Check **Settings → Actions → General → Workflow permissions** is set to "Read and write".

## License

MIT

## Contributing

This bootstrap script is designed to be simple and maintainable. To suggest improvements:

1. Test changes with both `bash bootstrap_ci.sh` and `MODE=full bash bootstrap_ci.sh`
2. Verify idempotency (running twice should be safe)
3. Ensure existing ESPHome configs are never modified
4. Keep scripts POSIX-compliant for broad compatibility

---

**Need help?** Check workflow logs in GitHub Actions or review the generated `.github/workflows/*.yml` files for details.
