# SPDX-License-Identifier: GPL-3.0-or-later
# CODEMIND Serena interactive operator launcher for Windows.
[CmdletBinding()]
param(
    [string]$ProjectPath = "",
    [ValidateRange(1024, 65535)][int]$McpPort = 8765
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
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent().Name
    $acl = Get-Acl -LiteralPath $store
    $acl.SetAccessRuleProtection($true, $false)
    $rule = [Security.AccessControl.FileSystemAccessRule]::new(
        $identity, 'FullControl', 'ContainerInherit,ObjectInherit', 'None', 'Allow'
    )
    $acl.AddAccessRule($rule)
    Set-Acl -LiteralPath $store -AclObject $acl
    $tokenFile = Join-Path $store 'dashboard-operator-token.txt'
    if (Test-Path -LiteralPath $tokenFile) {
        $env:CODEMIND_DASHBOARD_TOKEN = [IO.File]::ReadAllText($tokenFile).Trim()
    } else {
        $env:CODEMIND_DASHBOARD_TOKEN = [Convert]::ToHexString(
            [Security.Cryptography.RandomNumberGenerator]::GetBytes(32)
        )
        [IO.File]::WriteAllText($tokenFile, $env:CODEMIND_DASHBOARD_TOKEN, [Text.UTF8Encoding]::new($false))
    }
    Write-Host ('Dashboard operator token is stored in an ACL-restricted file: ' + $tokenFile)
}
if ($env:CODEMIND_DASHBOARD_TOKEN.Length -lt 32) { throw 'Dashboard token must be at least 32 characters.' }
Write-Host 'CODEMIND Serena: Starting one local MCP process. No Commander restart will occur.'
Write-Host 'The dashboard URL is reported by Serena startup logs. The MCP endpoint port is not the dashboard port.'
Push-Location $repositoryRoot
try {
    & $uv.Source run --locked --no-dev serena start-mcp-server --transport streamable-http --host 127.0.0.1 --port $McpPort --agent-interface tools --enable-web-dashboard true --open-web-dashboard false --project $ProjectPath
    if ($LASTEXITCODE -ne 0) { throw ('Serena exited with code ' + $LASTEXITCODE) }
} finally {
    Pop-Location
}
