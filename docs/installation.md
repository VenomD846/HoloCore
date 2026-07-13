# Installation guide

![HoloCore installation connects one local World to supported AI clients](assets/workflow-install-ai.svg)

## Requirements

- Windows with PowerShell (first-class baseline)
- Python 3.11 or newer
- Git only if you want `holocore init` to initialize a repository

No external LLM key and no original Obsidian Second Brain, Graphify, or MemPalace installation is required.

## Install from this checkout

```powershell
Set-Location "C:\Cursor projects\HoloCore"
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
holocore --help
holocore-mcp --help
```

`holocore-mcp` is a stdio server and normally waits for JSON-RPC input; AI clients launch it for you.

## Initialize a project

```powershell
holocore --root "C:\path\to\project" init
holocore --root "C:\path\to\project" status
```

Use `init --no-git` to avoid Git initialization. Bootstrap creates only missing files and reports existing files under `skipped`.

## Upgrade or uninstall

For an editable checkout, pull or replace the checkout and reinstall with `python -m pip install -e .`. Uninstall the package with `python -m pip uninstall holocore`. Project-created `.holocore`, Archive, and client files are user data and are intentionally not deleted automatically.

## Portable release status

The local wheel is built with `uv build` and was validated in a fresh temporary virtual environment. Install it on another computer with:

```powershell
uv tool install .\holocore-0.2.0-py3-none-any.whl
holocore --root "C:\path\to\project" init
```

A public package registry and signed graphical installer are not yet provided.
