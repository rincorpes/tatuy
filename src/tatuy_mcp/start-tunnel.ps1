[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$TunnelClientPath,

    [string]$Profile = "tatuy",

    [string]$EnvFile = (
        Join-Path $PSScriptRoot "..\..\.env"
    ),

    [string]$PythonExecutable = "python"
)

$ErrorActionPreference = "Stop"

$clientExecutable = (
    Resolve-Path -LiteralPath $TunnelClientPath
).Path

if (-not (Test-Path -LiteralPath $clientExecutable -PathType Leaf)) {
    throw "Tunnel client executable not found: $TunnelClientPath"
}

$previousApiKey = $env:CONTROL_PLANE_API_KEY

try {
    if ([string]::IsNullOrWhiteSpace($env:CONTROL_PLANE_API_KEY)) {
        $resolvedEnvFile = (
            Resolve-Path -LiteralPath $EnvFile
        ).Path

        # Send source over stdin to preserve quotes in Windows PowerShell 5.1.
        $loadedApiKey = @'
import sys
from dotenv import dotenv_values

values = dotenv_values(sys.argv[1], interpolate=False)
key = values.get("CONTROL_PLANE_API_KEY")

if not key or not key.strip():
    sys.exit("CONTROL_PLANE_API_KEY is missing or empty in .env")

sys.stdout.write(key.strip())
'@ | & $PythonExecutable - $resolvedEnvFile

        if ($LASTEXITCODE -ne 0) {
            throw "Could not load the tunnel API key from .env."
        }

        $env:CONTROL_PLANE_API_KEY = $loadedApiKey
        Remove-Variable loadedApiKey
    }

    Write-Host "Checking tunnel profile '$Profile'..."

    & $clientExecutable doctor --profile $Profile --explain

    if ($LASTEXITCODE -ne 0) {
        throw "Tunnel validation failed. Review the output above."
    }

    Write-Host "Starting tunnel. Keep this terminal open."
    Write-Host "Press Ctrl+C to stop."

    & $clientExecutable run --profile $Profile

    if ($LASTEXITCODE -ne 0) {
        throw "Tunnel client exited with code $LASTEXITCODE."
    }
}
finally {
    $env:CONTROL_PLANE_API_KEY = $previousApiKey
}
