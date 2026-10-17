# SPDX-License-Identifier: GPL-3.0-or-later
# CODEMIND Serena interactive operator launcher for Windows.
[CmdletBinding()]
param(
    [string]$ProjectPath = "",
    [ValidateRange(1024, 65535)][int]$McpPort = 8765,
    [switch]$CheckOnly
)
$ErrorActionPreference = 'Stop'
$repositoryRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
if (-not (Test-Path -LiteralPath (Join-Path $repositoryRoot 'pyproject.toml'))) {
    throw 'Not a verified CODEMIND Serena source directory.'
}
if (-not $ProjectPath) { $ProjectPath = $repositoryRoot }
$ProjectPath = (Resolve-Path -LiteralPath $ProjectPath).Path
$uv = Get-Command uv -ErrorAction Stop
$env:UV_CONCURRENT_DOWNLOADS = '2'
$env:UV_CONCURRENT_INSTALLS = '1'
$env:UV_CONCURRENT_BUILDS = '1'
$env:UV_LINK_MODE = 'copy'
if (-not $env:LOCALAPPDATA) { throw 'LOCALAPPDATA is required for the operator token store.' }

# Generate a distinct dashboard operator token. Never use OpenAI credentials here.
if ([string]::IsNullOrWhiteSpace($env:CODEMIND_DASHBOARD_TOKEN)) {
    $store = Join-Path $env:LOCALAPPDATA 'CODEMIND-Serena'
    [void][IO.Directory]::CreateDirectory($store)
    $tokenFile = Join-Path $store 'dashboard-operator-token.txt'
    if (Test-Path -LiteralPath $tokenFile) {
        # Existing installation: do not alter ACLs or regenerate the key.
        $env:CODEMIND_DASHBOARD_TOKEN = [IO.File]::ReadAllText($tokenFile).Trim()
    } else {
        # Do not depend on Get-Acl/Set-Acl module autoload in detached
        # Windows PowerShell 5.1 hosts. Apply a user-only directory DACL
        # before the token file is created. icacls is available on Windows.
        $ownerSid = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
        $grant = '*' + $ownerSid + ':(OI)(CI)F'
        $icacls = Join-Path $env:WINDIR 'System32\\icacls.exe'
        if (-not (Test-Path -LiteralPath $icacls)) {
            throw 'Windows ACL utility is unavailable; refusing to store an unprotected token.'
        }
        $aclOutput = & $icacls $store '/inheritance:r' '/grant:r' $grant 2>&1
        $aclCode = $LASTEXITCODE
        if ($aclCode -ne 0) {
            throw ('Token directory access restriction failed (' + $aclCode + '): ' + $aclOutput)
        }
        # Works on Windows PowerShell 5.1 (.NET Framework) and PowerShell 7+.
        # The static RandomNumberGenerator.GetBytes(int) and Convert.ToHexString
        # APIs are unavailable on some supported runtimes.
        $tokenBytes = New-Object byte[] 32
        $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
        try {
            $rng.GetBytes($tokenBytes)
        } finally {
            $rng.Dispose()
        }
        $env:CODEMIND_DASHBOARD_TOKEN = ([BitConverter]::ToString($tokenBytes)).Replace('-', '')
        [IO.File]::WriteAllText($tokenFile, $env:CODEMIND_DASHBOARD_TOKEN, [Text.UTF8Encoding]::new($false))
    }
    Write-Host ('Dashboard operator token is stored in an ACL-restricted file: ' + $tokenFile)
}
if ($env:CODEMIND_DASHBOARD_TOKEN.Length -lt 32) { throw 'Dashboard token must be at least 32 characters.' }
if ($CheckOnly) {
    Write-Host ('CODEMIND_LAUNCHER_PREFLIGHT_PASS; PowerShell=' + $PSVersionTable.PSVersion.ToString())
    return
}
Write-Host 'CODEMIND Serena: Starting one local MCP process. No Commander restart will occur.'
Write-Host 'The dashboard URL is reported by Serena startup logs. The MCP endpoint port is not the dashboard port.'
Push-Location $repositoryRoot
$previousErrorActionPreference = $ErrorActionPreference
try {
    # PowerShell 5.1 emits native stderr as a NativeCommandError record.
    # uv writes routine build and progress messages to stderr, even on success.
    # Treat native stderr as visible diagnostic output, not a terminating PS error.
    # The native exit code remains authoritative and is checked immediately.
    $ErrorActionPreference = 'Continue'
    & $uv.Source run --locked --no-dev serena start-mcp-server --transport streamable-http --host 127.0.0.1 --port $McpPort --agent-interface tools --enable-web-dashboard true --open-web-dashboard false --project $ProjectPath
    $serenaExitCode = $LASTEXITCODE
} finally {
    $ErrorActionPreference = $previousErrorActionPreference
    Pop-Location
}
if ($serenaExitCode -ne 0) { throw ('Serena exited with code ' + $serenaExitCode) }
