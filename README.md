# sense360-firmware

[![Release workflow](https://github.com/OWNER/sense360-firmware/actions/workflows/release.yml/badge.svg)](https://github.com/OWNER/sense360-firmware/actions/workflows/release.yml)

## Project purpose

Sense360 firmware packages the ESPHome configurations that drive the Sense360 family of sensors and automation accessories. Each YAML definition captures the device-specific configuration, pins the ESPHome runtime used to build it, and produces reproducible binaries for release and over-the-air (OTA) deployment. The repository also tracks release artifacts so the team can ship audited firmware images.

## Repository layout

- `devices/` &mdash; individual ESPHome YAML definitions for supported devices.
- `dist/` &mdash; generated firmware binaries and manifest archives (ignored by Git).
- `.esphome/` and `.pio/` &mdash; local build and compilation caches created by the ESPHome CLI (ignored by Git).
- GitHub Actions workflows automate linting, compilation, and release packaging.

## Adding a new device configuration

1. Create a new YAML file in `devices/` (for example, `devices/<device_name>.yaml`). Use an existing device file as a template when possible.
2. Reference common substitutions and secrets through the `!secret` directive to avoid leaking credentials. Add any new required secrets to your local `secrets.yaml` (which stays untracked) and update the "GitHub secrets" section below if a release secret is required.
3. Run `esphome compile devices/<device_name>.yaml` locally to validate the configuration. This will populate `.esphome/` and `.pio/` caches that are ignored by Git.
4. Commit the new YAML with a clear summary of the hardware revision and capabilities.
5. Open a pull request and confirm that the release workflow succeeds so the resulting firmware is available with the next tag.

## Release process

### Tagging

1. Merge the desired changes to the `main` branch.
2. Update `CHANGELOG.md` with a summary of the release.
3. Create an annotated tag matching semantic versioning (for example, `git tag -a v1.2.0 -m "v1.2.0"`).
4. Push the tag to GitHub (`git push origin v1.2.0`). This triggers the release workflow.

### Release artifacts

The release workflow publishes compiled firmware binaries and manifest archives as GitHub Release assets. When the optional `GH_PAGES_PUBLISH` secret is configured, the same artifacts are also uploaded to the `gh-pages` branch so they can be served over HTTPS (for example, via ESPHome's OTA URL). The artifacts created by local development builds remain in `dist/` and should not be committed.

## OTA password handling

ESPHome OTA authentication relies on the `ota.password` value defined in each device YAML. Locally, provide the password via your personal `secrets.yaml`. In CI, the release workflow injects the hashed password that ESPHome expects by reading the `OTA_PASSWORD` GitHub secret. Keep the secret strong and rotate it when necessary; updating the secret automatically hardens all subsequent firmware builds.

## ESPHome version pinning

To guarantee reproducible binaries, the release workflow installs a fixed ESPHome version (`pip install esphome==<version>`). Update the pinned version only after validating each device configuration against the new release. This helps us avoid unexpected breaking changes in the ESPHome ecosystem.

## GitHub secrets

| Secret | Required | Purpose |
| --- | --- | --- |
| `OTA_PASSWORD` | ✅ | Provides the OTA password consumed by the release workflow to hash and embed into each firmware image. |
| `GH_PAGES_PUBLISH` | Optional | When set to `true`, enables publishing release assets to the `gh-pages` branch for static hosting. |
| `GH_PAGES_CNAME` | Optional | Custom domain (CNAME) to write into the `gh-pages` branch so hosted artifacts resolve under a vanity domain. |

Ensure secrets are configured in the repository settings before running the release workflow.

## Contributing

- Keep configuration changes small and well-documented in commit messages.
- Update `CHANGELOG.md` with user-visible changes.
- Follow the formatting enforced by `.editorconfig` for consistent indentation, newlines, and character encoding.

## License

This project is released under the MIT License. See [LICENSE](LICENSE) for details.
