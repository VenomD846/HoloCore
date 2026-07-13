# Installation guide

![HoloCore installation connects one local World to supported AI clients](assets/workflow-install-ai.svg)

## Requirements

- Windows with PowerShell (first-class baseline)
- Python 3.11 or newer
- Git only if you want `holocore init` to initialize a repository

No external LLM key and no original Obsidian Second Brain, Graphify, or MemPalace installation is required.

See [prerequisites and optional graph tools](prerequisites.md) for the required software, the difference between the Atlas and Archive graph views, and optional Obsidian setup.

## Install from this checkout

HoloCore can be stored in any folder. The package installation location is managed by Python or `uv`; the World and its data are placed wherever you select with `--root`.

```powershell
$HoloCoreSource = Read-Host "Enter the folder containing the HoloCore source"
Set-Location -LiteralPath $HoloCoreSource
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
$WorldRoot = Read-Host "Enter the project folder to use as a HoloCore World"
holocore --root $WorldRoot init
holocore --root $WorldRoot status
```

The selected World may be an existing project or a new folder. HoloCore keeps its generated state under that World rather than assuming a fixed machine-specific location.

Use `init --no-git` to avoid Git initialization. Bootstrap creates only missing files and reports existing files under `skipped`.

### Folders created by `init`

| Path | Purpose |
|---|---|
| `Archive/Inbox` | Temporary landing area for knowledge that still needs curation |
| `Archive/wiki` | Durable linked Archive Entries |
| `Archive/system/index.md` | Starting index used to navigate the Archive |
| `.holocore/raw-chats` | Protected raw-chat audit copies |
| `.holocore` | Configuration, Atlas JSON, Animus database, policy, and generated state |
| Client-specific command/skill folders | HoloCore commands for the selected AI clients |

Every path is checked before creation. Initialization does not overwrite an existing file, recreate the project recursively, or invoke a HoloCore route.

## Upgrade or uninstall

For an editable checkout, pull or replace the checkout and reinstall with `python -m pip install -e .`. Uninstall the package with `python -m pip uninstall holocore`. Project-created `.holocore`, Archive, and client files are user data and are intentionally not deleted automatically.

## Portable release status

The local wheel is built with `uv build` and was validated in a fresh temporary virtual environment. Install it on another computer with:

```powershell
uv tool install .\holocore-0.3.0-py3-none-any.whl
holocore --root "C:\path\to\project" init
```

A public package registry and signed graphical installer are not yet provided.
