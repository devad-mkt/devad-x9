[CmdletBinding()]
param(
    [ValidateSet('Plan', 'Apply', 'Rollback')]
    [string]$Mode = 'Plan',

    [string]$CodexHome = '$CODEX_HOME',

    [string]$BackupDirectory
)

$ErrorActionPreference = 'Stop'

function Write-Utf8NoBom {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Content
    )

    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $Content, $utf8NoBom)
}

function Set-TopLevelTomlString {
    param(
        [Parameter(Mandatory = $true)][string]$Text,
        [Parameter(Mandatory = $true)][string]$Key,
        [Parameter(Mandatory = $true)][string]$Value
    )

    $pattern = '(?m)^\s*' + [regex]::Escape($Key) + '\s*=\s*.*$'
    $matches = [regex]::Matches($Text, $pattern)
    if ($matches.Count -gt 1) {
        throw "CONFIG_CONFLICT: multiple top-level '$Key' values."
    }

    $line = $Key + ' = "' + $Value + '"'
    if ($matches.Count -eq 1) {
        return [regex]::Replace($Text, $pattern, [System.Text.RegularExpressions.MatchEvaluator]{ param($match) $line }, 1)
    }

    $firstTable = [regex]::Match($Text, '(?m)^\s*\[[^\]]+\]\s*$')
    if ($firstTable.Success) {
        return $Text.Insert($firstTable.Index, $line + [Environment]::NewLine)
    }

    return $Text.TrimEnd() + [Environment]::NewLine + $line + [Environment]::NewLine
}

function Set-FeatureTomlBool {
    param(
        [Parameter(Mandatory = $true)][string]$Text,
        [Parameter(Mandatory = $true)][string]$Key,
        [Parameter(Mandatory = $true)][bool]$Value
    )

    if ($Key -eq 'multi_agent_v2' -and [regex]::IsMatch($Text, '(?m)^\s*\[features\.multi_agent_v2\]\s*$')) {
        throw 'CONFIG_CONFLICT: [features.multi_agent_v2] is a table and cannot safely coexist with boolean features.multi_agent_v2.'
    }

    $features = [regex]::Match($Text, '(?ms)^\s*\[features\]\s*\r?\n(?<body>.*?)(?=^\s*\[[^\]]+\]\s*$|\z)')
    $line = $Key + ' = ' + $Value.ToString().ToLowerInvariant()
    if (-not $features.Success) {
        return $Text.TrimEnd() + [Environment]::NewLine + [Environment]::NewLine + '[features]' + [Environment]::NewLine + $line + [Environment]::NewLine
    }

    $body = $features.Groups['body'].Value
    $pattern = '(?m)^\s*' + [regex]::Escape($Key) + '\s*=\s*.*$'
    $matches = [regex]::Matches($body, $pattern)
    if ($matches.Count -gt 1) {
        throw "CONFIG_CONFLICT: multiple [features] '$Key' values."
    }
    if ($matches.Count -eq 1) {
        $newBody = [regex]::Replace($body, $pattern, [System.Text.RegularExpressions.MatchEvaluator]{ param($match) $line }, 1)
    } else {
        $separator = if ($body.Length -eq 0 -or $body.EndsWith("`n")) { '' } else { [Environment]::NewLine }
        $newBody = $body + $separator + $line + [Environment]::NewLine
    }

    return $Text.Substring(0, $features.Groups['body'].Index) + $newBody + $Text.Substring($features.Groups['body'].Index + $features.Groups['body'].Length)
}

function Get-CatalogProfile {
    param(
        [Parameter(Mandatory = $true)]$Catalog,
        [Parameter(Mandatory = $true)][string]$Slug
    )

    $profile = @($Catalog.models | Where-Object { $_.slug -eq $Slug })
    if ($profile.Count -ne 1) {
        throw "CATALOG_GUARD: expected one '$Slug' profile, found $($profile.Count)."
    }
    if ($null -eq $profile[0].PSObject.Properties['multi_agent_version']) {
        throw "CATALOG_GUARD: '$Slug' does not define multi_agent_version."
    }
    return $profile[0]
}

$resolvedCodexHome = (Resolve-Path -LiteralPath $CodexHome).Path
$configPath = Join-Path $resolvedCodexHome 'config.toml'
$catalogPath = Join-Path $resolvedCodexHome 'models-luna-v1.json'
$agentsDirectory = Join-Path $resolvedCodexHome 'agents'
$agentPath = Join-Path $agentsDirectory 'luna-max-worker.toml'

if (-not (Test-Path -LiteralPath $configPath -PathType Leaf)) {
    throw "CONFIG_MISSING: $configPath"
}

if ($Mode -eq 'Rollback') {
    if ([string]::IsNullOrWhiteSpace($BackupDirectory)) {
        throw 'ROLLBACK_REQUIRES_BACKUP: pass -BackupDirectory from a successful Apply result.'
    }
    $resolvedBackup = (Resolve-Path -LiteralPath $BackupDirectory).Path
    $backupConfig = Join-Path $resolvedBackup 'config.toml'
    if (-not (Test-Path -LiteralPath $backupConfig -PathType Leaf)) {
        throw "ROLLBACK_BACKUP_INVALID: missing $backupConfig"
    }
    Copy-Item -LiteralPath $backupConfig -Destination $configPath -Force

    $backupAgent = Join-Path $resolvedBackup 'luna-max-worker.toml'
    if (Test-Path -LiteralPath $backupAgent -PathType Leaf) {
        New-Item -ItemType Directory -Path $agentsDirectory -Force | Out-Null
        Copy-Item -LiteralPath $backupAgent -Destination $agentPath -Force
    } elseif (Test-Path -LiteralPath $agentPath -PathType Leaf) {
        Move-Item -LiteralPath $agentPath -Destination (Join-Path $resolvedBackup 'luna-max-worker.toml.generated-after-rollback') -Force
    }

    Write-Output "ROLLBACK_APPLIED: $resolvedBackup"
    Write-Output 'GENERATED_CATALOG_RETAINED: it is no longer referenced after config restoration.'
    Write-Output 'RESTART_REQUIRED: start a fresh Codex process before testing native subagents.'
    exit 0
}

$codex = Get-Command codex -ErrorAction Stop
$rawCatalog = (& $codex.Source debug models 2>$null | Out-String).Trim()
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($rawCatalog)) {
    throw 'CATALOG_READ_FAILED: codex debug models did not return a catalog.'
}
try {
    $catalog = $rawCatalog | ConvertFrom-Json
} catch {
    throw "CATALOG_PARSE_FAILED: $($_.Exception.Message)"
}
if ($null -eq $catalog.models) {
    throw 'CATALOG_GUARD: root models array is absent.'
}

$configText = [System.IO.File]::ReadAllText($configPath)
if ([regex]::IsMatch($configText, '(?m)^\s*\[features\.multi_agent_v2\]\s*$')) {
    throw 'CONFIG_CONFLICT: [features.multi_agent_v2] exists. Preserve it and resolve manually before this bridge can apply.'
}

$sol = Get-CatalogProfile -Catalog $catalog -Slug 'gpt-5.6-sol'
$terra = Get-CatalogProfile -Catalog $catalog -Slug 'gpt-5.6-terra'
$luna = Get-CatalogProfile -Catalog $catalog -Slug 'gpt-5.6-luna'
$needsBridge = $sol.multi_agent_version -eq 'v2' -and $terra.multi_agent_version -eq 'v2' -and $luna.multi_agent_version -eq 'v1'
$bridgeActive = $sol.multi_agent_version -eq 'v1' -and $terra.multi_agent_version -eq 'v1' -and $luna.multi_agent_version -eq 'v1'
if (-not $needsBridge -and -not $bridgeActive) {
    throw "CATALOG_GUARD: expected Sol=v2, Terra=v2, Luna=v1 or an active all-V1 bridge; found Sol=$($sol.multi_agent_version), Terra=$($terra.multi_agent_version), Luna=$($luna.multi_agent_version)."
}

$existingCatalog = [regex]::Match($configText, '(?m)^\s*model_catalog_json\s*=\s*"(?<path>[^"]+)"\s*$')
$forwardCatalogPath = $catalogPath.Replace('\', '/')
$configReferencesBridge = $existingCatalog.Success -and ($existingCatalog.Groups['path'].Value.Replace('\', '/') -eq $forwardCatalogPath)
$featuresEnabled = [regex]::IsMatch($configText, '(?ms)^\s*\[features\]\s*\r?\n(?:(?!^\s*\[[^\]]+\]).)*^\s*multi_agent\s*=\s*true\s*$')
$v2Disabled = [regex]::IsMatch($configText, '(?ms)^\s*\[features\]\s*\r?\n(?:(?!^\s*\[[^\]]+\]).)*^\s*multi_agent_v2\s*=\s*false\s*$')
if ($bridgeActive) {
    if (-not $configReferencesBridge -or -not $featuresEnabled -or -not $v2Disabled -or -not (Test-Path -LiteralPath $agentPath -PathType Leaf)) {
        throw 'BRIDGE_STATE_INCOMPLETE: catalog is V1 but the expected config or luna-max-worker profile is missing. Restore from backup or repair manually; this script will not guess.'
    }
    Write-Output 'BRIDGE_ALREADY_ACTIVE: Sol, Terra, and Luna resolve as V1 with the Luna Max role installed.'
    Write-Output 'VALIDATION_ONLY: no files were changed.'
    exit 0
}

$updatedConfig = Set-TopLevelTomlString -Text $configText -Key 'model_catalog_json' -Value $forwardCatalogPath
$updatedConfig = Set-FeatureTomlBool -Text $updatedConfig -Key 'multi_agent' -Value $true
$updatedConfig = Set-FeatureTomlBool -Text $updatedConfig -Key 'multi_agent_v2' -Value $false

$agentContent = @'
name = "luna-max-worker"
description = "Luna Max worker for bounded, clear, repeatable tasks with explicit proof gates."
model = "gpt-5.6-luna"
model_reasoning_effort = "max"
developer_instructions = """
Follow the owner packet exactly. Keep the scope bounded, preserve the parent sandbox and approvals, and return compact evidence with every uncertainty marked UNKNOWN. Do not make authority, security, production, or destructive decisions for the manager.
"""
'@.TrimStart()

Write-Output "CATALOG_GUARD_PASS: Sol=$($sol.multi_agent_version), Terra=$($terra.multi_agent_version), Luna=$($luna.multi_agent_version)"
Write-Output "TARGET_CATALOG: $catalogPath"
Write-Output 'PLANNED_CATALOG_MUTATIONS: gpt-5.6-sol.multi_agent_version=v1; gpt-5.6-terra.multi_agent_version=v1'
Write-Output 'PLANNED_CONFIG_MUTATIONS: model_catalog_json=<target>; features.multi_agent=true; features.multi_agent_v2=false'
Write-Output "PLANNED_AGENT_PROFILE: $agentPath (gpt-5.6-luna max)"

if ($Mode -eq 'Plan') {
    Write-Output 'PLAN_ONLY: no files were changed.'
    exit 0
}

$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$backupPath = Join-Path (Join-Path $resolvedCodexHome 'backups') ('luna-native-subagent-' + $timestamp)
New-Item -ItemType Directory -Path $backupPath -Force | Out-Null
Copy-Item -LiteralPath $configPath -Destination (Join-Path $backupPath 'config.toml') -Force
Write-Utf8NoBom -Path (Join-Path $backupPath 'models-before.json') -Content ($rawCatalog + [Environment]::NewLine)
if ($existingCatalog.Success -and (Test-Path -LiteralPath $existingCatalog.Groups['path'].Value -PathType Leaf)) {
    Copy-Item -LiteralPath $existingCatalog.Groups['path'].Value -Destination (Join-Path $backupPath 'model-catalog-before.json') -Force
}
if (Test-Path -LiteralPath $agentPath -PathType Leaf) {
    Copy-Item -LiteralPath $agentPath -Destination (Join-Path $backupPath 'luna-max-worker.toml') -Force
}

$sol.multi_agent_version = 'v1'
$terra.multi_agent_version = 'v1'
$generatedCatalog = $catalog | ConvertTo-Json -Depth 100
try {
    $verifiedCatalog = $generatedCatalog | ConvertFrom-Json
    foreach ($required in @('gpt-5.6-sol', 'gpt-5.6-terra', 'gpt-5.6-luna')) {
        if ((Get-CatalogProfile -Catalog $verifiedCatalog -Slug $required).multi_agent_version -ne 'v1') {
            throw "JSON verification failed for $required."
        }
    }
} catch {
    throw "GENERATED_CATALOG_INVALID: $($_.Exception.Message)"
}

Write-Utf8NoBom -Path $catalogPath -Content ($generatedCatalog + [Environment]::NewLine)
Write-Utf8NoBom -Path $configPath -Content $updatedConfig
New-Item -ItemType Directory -Path $agentsDirectory -Force | Out-Null
Write-Utf8NoBom -Path $agentPath -Content ($agentContent + [Environment]::NewLine)

$manifest = @(
    "backup_directory=$backupPath"
    "config_sha256_before=$((Get-FileHash -LiteralPath (Join-Path $backupPath 'config.toml') -Algorithm SHA256).Hash)"
    "config_sha256_after=$((Get-FileHash -LiteralPath $configPath -Algorithm SHA256).Hash)"
    "catalog_sha256_after=$((Get-FileHash -LiteralPath $catalogPath -Algorithm SHA256).Hash)"
    "agent_sha256_after=$((Get-FileHash -LiteralPath $agentPath -Algorithm SHA256).Hash)"
) -join [Environment]::NewLine
Write-Utf8NoBom -Path (Join-Path $backupPath 'MANIFEST.txt') -Content ($manifest + [Environment]::NewLine)

Write-Output "APPLY_COMPLETE: $backupPath"
Write-Output 'RESTART_REQUIRED: close/reopen Codex or use a fresh CLI process before testing native subagents.'
Write-Output "ROLLBACK: & '$PSCommandPath' -Mode Rollback -BackupDirectory '$backupPath'"
