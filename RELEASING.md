# Release Checklist

## Before releasing

1. Ensure pykomfovent is released first if this release depends on new features
2. Ensure all tests pass: `uv run pytest`
3. Ensure linting passes: `uv run ruff check custom_components/ tests/`
4. Ensure type checking passes: `uv run pyright custom_components/`

## Release steps

1. Update version in `custom_components/pykomfovent/manifest.json`
2. Update pykomfovent requirement version if needed
3. Update `CHANGELOG.md` with release notes
4. Commit changes: `git commit -am "Release vX.Y.Z"`
5. Push to main: `git push origin main`
6. Create GitHub release:
   - Go to https://github.com/mostaszewski/hass-pykomfovent/releases/new
   - Tag: `vX.Y.Z` (e.g., `v1.0.0`)
   - Title: `vX.Y.Z`
   - Description: Copy from CHANGELOG.md
   - Click "Publish release"
7. CI will automatically create and attach the zip file

## Dependency order

If releasing both packages:

1. Release pykomfovent first
2. Wait for PyPI to update (~5 minutes)
3. Update hass-pykomfovent's manifest.json requirement
4. Release hass-pykomfovent
