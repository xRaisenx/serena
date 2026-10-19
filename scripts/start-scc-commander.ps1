# SPDX-License-Identifier: GPL-3.0-or-later
# Start SCC's independent Windows Commander. Never touches the NMBV service.
[CmdletBinding()]
param(
    [ValidateRange(1024,65535)][int]$Port = 8767,
    [string]$ProjectPath = "",
    [switch]$CheckOnly
)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$server = Join-Path $root 'tools\scc_commander\server.cjs'
if (-not (Test-Path -LiteralPath $server -PathType Leaf)) { throw 'SCC Commander entry point missing.' }
if (-not $ProjectPath) { $ProjectPath = $root }
$ProjectPath = (Resolve-Path -LiteralPath $ProjectPath).Path
$node = Get-Command node -ErrorAction Stop
if ($CheckOnly) {
    Write-Host ('SCC_COMMANDER_PREFLIGHT_PASS; PowerShell=' + $PSVersionTable.PSVersion.ToString())
    return
}
if (-not $env:LOCALAPPDATA) { throw 'LOCALAPPDATA is required.' }
$existing = @(Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue)
if ($existing.Count) { throw ('Port ' + $Port + ' already has a listener. Refusing duplicate Commander.') }
$store = Join-Path $env:LOCALAPPDATA 'CODEMIND-Serena\scc-commander'
$secretFile = Join-Path $store 'peer-token.txt'
if (-not (Test-Path -LiteralPath $store -PathType Container)) {
    [void][IO.Directory]::CreateDirectory($store)
    $sid = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
    $grant = '*' + $sid + ':(OI)(CI)F'
    $icacls = Join-Path $env:WINDIR 'System32\icacls.exe'
    if (-not (Test-Path -LiteralPath $icacls)) { throw 'Windows ACL utility unavailable.' }
    $output = & $icacls $store '/inheritance:r' '/grant:r' $grant 2>&1
    if ($LASTEXITCODE -ne 0) { throw ('Refusing insecure credential storage: ' + $output) }
}
if (-not (Test-Path -LiteralPath $secretFile -PathType Leaf)) {
    $bytes = New-Object byte[] 32
    $rng = [Security.Cryptography.RandomNumberGenerator]::Create()
    try { $rng.GetBytes($bytes) } finally { $rng.Dispose() }
    $secret = ([BitConverter]::ToString($bytes)).Replace('-','')
    [IO.File]::WriteAllText($secretFile, $secret, [Text.UTF8Encoding]::new($false))
}
$token = [IO.File]::ReadAllText($secretFile).Trim()
if ($token.Length -lt 32 -or $token.Contains([char]10) -or $token.Contains([char]13)) { throw 'SCC peer token is missing or invalid.' }
$env:SCC_COMMANDER_TOKEN = $token
$env:SCC_COMMANDER_PORT = [string]$Port
$env:SCC_COMMANDER_PROJECT_ROOT = $ProjectPath
Write-Host ('Starting SCC.WindowsCommander on 127.0.0.1:' + $Port + ', MCP /mcp; health /codemind/health.')
Write-Host ('Private SCC peer token: ' + $secretFile)
Write-Host 'Read-only MCP tools only. No NMBV processes or tunnel clients are started or stopped.'
Push-Location $root
try {
    & $node.Source $server
    if ($LASTEXITCODE -ne 0) { throw ('SCC Commander exited with code ' + $LASTEXITCODE) }
} finally {
    Pop-Location
    Remove-Item Env:SCC_COMMANDER_TOKEN -ErrorAction SilentlyContinue
}
