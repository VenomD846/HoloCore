# Quickstart: HoloCore Baseline Validation

This guide validates the planned baseline through PowerShell. It is intentionally
an end-to-end check list, not an implementation recipe. Run from the HoloCore
repository root after the implementation tasks are complete.

## Prerequisites

- Windows PowerShell 5.1+ or PowerShell 7.
- Python 3.11+ available as `python`.
- Local Graphify, MemPalace, and the active Obsidian Archive source roots available.
- No external LLM API key configured; the keyless case is the required baseline.

```powershell
$ErrorActionPreference = 'Stop'
$repo = 'C:\Cursor projects\HoloCore'
$fixture = Join-Path $repo 'tests\fixtures\holocore-baseline'
Set-Location -LiteralPath $repo
python --version
```

## Scenario 1: initialize without destructive writes

Create a temporary World configuration that points at the fixture and the existing
local source roots. Use the implementation's documented option names for the
source roots; the contract requires the paths to be explicit.

```powershell
$world = 'holocore-baseline-fixture'
python -m holocore.cli init $world --archive-root (Join-Path $fixture 'archive') --atlas-root (Join-Path $fixture 'world') --atlas-output (Join-Path $fixture 'world\graphify-out') --animus-root (Join-Path $fixture 'episode')
python -m holocore.cli status $world --json
python -m holocore.cli doctor $world --json
```

Expected outcome: configuration and manifest are created only where absent;
`status` identifies Archive, Atlas, and Animus; `doctor` reports the local/keyless
baseline as usable or names an actionable missing dependency. No existing fixture
file is modified.

## Scenario 2: route each targeted information need

Run the queries below with the fixture's documented records. Use `--json` so the
route decision and source labels can be asserted by the acceptance test.

```powershell
python -m holocore.cli search 'durable architecture decision' --world $world --task-type durable --json
python -m holocore.cli search 'dependency path' --world $world --task-type structure --json
python -m holocore.cli search 'previous debugging attempt' --world $world --task-type history --json
```

Expected outcome: the first query selects Archive, the second selects Atlas, and the
third selects Animus. Each response includes source, source reference, provenance,
and the reason other sources were skipped. The unrelated fixture file is absent from
targeted context.

## Scenario 3: preserve upstream capability paths

Run one representative operation per adapter and one compatibility alias. The exact
alias names are implementation-defined by the manifest but MUST be discoverable in
help output.

```powershell
python -m holocore.cli --help
python -m holocore.cli status $world
python -m holocore.cli update $world --dry-run
python -m holocore.cli mine $world --sector debugging --dry-run
python -m holocore.cli promote --help
```

Expected outcome: help lists HoloCore terms and compatibility aliases; Atlas update
reports its AST-only default and graph output boundary; Animus mine requires a
declared Sector; Archive promotion exposes search-before-create/conflict behavior.

## Scenario 4: explicit writes are scoped and idempotent

After recording a baseline snapshot of fixture files, execute the write operations
against the fixture and repeat them with unchanged input.

```powershell
python -m holocore.cli update $world
python -m holocore.cli mine $world --sector debugging
python -m holocore.cli promote 'architecture-decision' --world $world
python -m holocore.cli update $world
python -m holocore.cli mine $world --sector debugging
python -m holocore.cli promote 'architecture-decision' --world $world
```

Expected outcome: Atlas refresh stays inside its declared output boundary; Animus
capture stays in the declared World/Sector; promotion creates or updates one Archive
entry with provenance; repeating unchanged operations produces no duplicate entry or
unscoped capture. Ambiguous promotion targets stop with a non-zero status and no
overwrite.

## Scenario 5: Windows path compatibility and no-key proof

Run the same checks with a temporary path containing spaces and with semantic-provider
credentials absent from the environment.

```powershell
$env:OPENAI_API_KEY = $null
$env:ANTHROPIC_API_KEY = $null
$pathWithSpaces = Join-Path $env:TEMP 'HoloCore Baseline Fixture'
python -m holocore.cli doctor $world --json
```

Expected outcome: paths with spaces remain intact in diagnostics and subprocess
arguments; missing optional credentials are reported as optional warnings, not as a
failure of the local/keyless baseline.

## Acceptance checklist

- [ ] Scenario 1 creates only missing local configuration and passes keyless health.
- [ ] Scenario 2 routes Archive, Atlas, and Animus correctly and excludes unrelated data.
- [ ] Scenario 3 demonstrates one preserved upstream capability and alias per source.
- [ ] Scenario 4 proves scoped, provenance-preserving, idempotent writes.
- [ ] Scenario 5 proves Windows path handling and no external LLM API key requirement.
