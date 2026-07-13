$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH = Join-Path $repo 'src'
$world = Join-Path $env:TEMP ('holocore-smoke-' + [guid]::NewGuid().ToString('N'))
try {
    python -m holocore.cli --root $world --json init | Out-Null
    python -m holocore.cli --root $world --json archive-init | Out-Null
    Set-Content -LiteralPath (Join-Path $world 'sample.py') -Value "def hello():`n    return 'world'" -Encoding utf8
    $atlas = python -m holocore.cli --root $world --json atlas-refresh | ConvertFrom-Json
    python -m holocore.cli --root $world --json remember 'native memory works' --sector project | Out-Null
    $recall = python -m holocore.cli --root $world --json recall 'native memory' --sector project | ConvertFrom-Json
    $tools = '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python -m holocore.mcp_server
    if ($atlas.nodes -lt 1) { throw 'Atlas did not map the World' }
    if ($recall.Count -lt 1) { throw 'Animus did not recall the Memory Shard' }
    if ($tools -notmatch 'holocore_archive_search') { throw 'MCP surface missing Archive tools' }
    foreach ($path in @('.git','Archive','AGENTS.md','CLAUDE.md','GEMINI.md','.cursor\mcp.json','opencode.json')) {
        if (-not (Test-Path -LiteralPath (Join-Path $world $path))) { throw "Missing installed artifact: $path" }
    }
    Write-Output 'HoloCore native installation scenario passed.'
} finally {
    if (Test-Path -LiteralPath $world) { Remove-Item -LiteralPath $world -Recurse -Force }
}
