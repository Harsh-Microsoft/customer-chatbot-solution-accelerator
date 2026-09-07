$ErrorActionPreference = 'Stop'

$scenarioPath = $env:SCENARIO_PATH
if ([string]::IsNullOrWhiteSpace($scenarioPath)) {
    throw "SCENARIO_PATH is required. Set it to the composed scenario folder before running this pattern."
}

$resolvedPath = Resolve-Path -LiteralPath $scenarioPath -ErrorAction SilentlyContinue
if (-not $resolvedPath) {
    throw "Scenario folder not found: $scenarioPath"
}

$manifestPath = Join-Path $resolvedPath.Path 'manifest.json'
if (-not (Test-Path -LiteralPath $manifestPath)) {
    throw "Scenario manifest not found: $manifestPath"
}

$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
$requiredKeys = @('host', 'welcome', 'catalog', 'presentation')
foreach ($key in $requiredKeys) {
    if (-not $manifest.PSObject.Properties[$key]) {
        throw "Scenario manifest is missing required key '$key' (see config/scenario-config.schema.json)."
    }
}

Write-Host "Scenario folder: $($resolvedPath.Path)"
Write-Host "Scenario manifest validated against the required config keys: $($requiredKeys -join ', ')."
