param(
    [string]$CodexHome = "$HOME\.codex",
    [string]$ProjectRoot = "",
    [string]$Python = "python",
    [string]$SkillValidator = "",
    [switch]$CodeTrial,
    [switch]$LegacyStyle,
    [switch]$Apply
)

$ErrorActionPreference = "Stop"
$PackageRoot = Split-Path -Parent $PSScriptRoot
$Skills = @(
    "devad-x9",
    "x9-loop-style",
    "x9-loop-code",
    "devad-x9-loop",
    "devad-x9-manager",
    "codex-x9-backup",
    "codex-token-budget",
    "devad-memory",
    "x9-project-docs"
)
$LegacySkills = @($Skills)
$UseActiveCatalog = -not $LegacyStyle
$ActiveEntries = @()

function Resolve-CatalogSource {
    param([string]$RelativePath)
    $relative = $RelativePath.Replace('/', '\')
    $root = [System.IO.Path]::GetFullPath($PackageRoot).TrimEnd('\')
    $source = [System.IO.Path]::GetFullPath((Join-Path $root $relative))
    if (-not $source.StartsWith($root + '\', [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Active catalog path escapes package root: $RelativePath"
    }
    return $source
}

if ($UseActiveCatalog) {
    $CatalogPath = Join-Path $PackageRoot "active\catalog.json"
    if (-not (Test-Path -LiteralPath $CatalogPath)) {
        throw "Missing active catalog: $CatalogPath"
    }
    $Catalog = Get-Content -LiteralPath $CatalogPath -Raw | ConvertFrom-Json
    $ActiveEntries = @($Catalog.entries)
    if (-not $ActiveEntries.Count) {
        throw "Active catalog has no entrypoints: $CatalogPath"
    }
    $Skills = @($ActiveEntries | ForEach-Object { $_.name })
    $InstallEntries = @($ActiveEntries | ForEach-Object {
        [pscustomobject]@{ Name = $_.name; Source = (Resolve-CatalogSource $_.path) }
    })
}
else {
    $InstallEntries = @($LegacySkills | ForEach-Object {
        [pscustomobject]@{ Name = $_; Source = (Join-Path $PackageRoot "skills\$_") }
    })
}

Write-Host "X9 Loop Style source (with archived Code trial): $PackageRoot"
Write-Host "Codex home: $CodexHome"

if ($ProjectRoot -and -not $CodeTrial) {
    throw "STYLE_PROJECT_OVERLAY_DISABLED: normal Style work never initializes controller state. Use -CodeTrial only for an owner-approved fresh disposable canary."
}

if (-not $Apply) {
    Write-Host "DRY RUN: no files changed."
    foreach ($Entry in $InstallEntries) {
        Write-Host "Would stage, validate, back up, and install: $($Entry.Name)"
    }
    if ($ProjectRoot) {
        Write-Host "Would create a legacy controller-trial .devad only if absent: $ProjectRoot"
    }
    exit 0
}

& $Python (Join-Path $PSScriptRoot "validate_suite.py")
if ($LASTEXITCODE -ne 0) {
    throw "Package validation failed before install."
}

$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$SkillsRoot = Join-Path $CodexHome "skills"
$StageRoot = Join-Path $CodexHome "x9-install-staging\$Stamp"
$BackupRoot = Join-Path $CodexHome "x9-install-backups\$Stamp"
$FailedRoot = Join-Path $CodexHome "x9-install-failed\$Stamp"
New-Item -ItemType Directory -Force -Path $SkillsRoot, $StageRoot, $BackupRoot | Out-Null

foreach ($Entry in $InstallEntries) {
    $Skill = $Entry.Name
    $Source = $Entry.Source
    $Stage = Join-Path $StageRoot $Skill
    if (-not (Test-Path -LiteralPath $Source)) {
        throw "Missing package skill: $Skill"
    }
    Copy-Item -LiteralPath $Source -Destination $Stage -Recurse
}

if (-not $SkillValidator) {
    $Candidate = Join-Path $CodexHome "skills\.system\skill-creator\scripts\quick_validate.py"
    if (Test-Path -LiteralPath $Candidate) {
        $SkillValidator = $Candidate
    }
}

if ($SkillValidator) {
    foreach ($Entry in $InstallEntries) {
        $Skill = $Entry.Name
        & $Python $SkillValidator (Join-Path $StageRoot $Skill)
        if ($LASTEXITCODE -ne 0) {
            throw "Official skill validation failed in staging: $Skill"
        }
    }
}

$Installed = New-Object System.Collections.Generic.List[string]
$ProjectStage = $null
$ProjectInstalled = $false
$DevadTarget = $null
try {
    foreach ($Entry in $InstallEntries) {
        $Skill = $Entry.Name
        $Target = Join-Path $SkillsRoot $Skill
        $Backup = Join-Path $BackupRoot $Skill
        $Stage = Join-Path $StageRoot $Skill
        if (Test-Path -LiteralPath $Target) {
            Move-Item -LiteralPath $Target -Destination $Backup
        }
        Move-Item -LiteralPath $Stage -Destination $Target
        $Installed.Add($Skill)
    }

    if ($ProjectRoot) {
        $ProjectRoot = [System.IO.Path]::GetFullPath($ProjectRoot)
        if (-not (Test-Path -LiteralPath $ProjectRoot -PathType Container)) {
            throw "Project root is missing: $ProjectRoot"
        }
        $projectItem = Get-Item -LiteralPath $ProjectRoot -Force
        if (($projectItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw "Project root cannot be a reparse path: $ProjectRoot"
        }
        $DevadTarget = Join-Path $ProjectRoot ".devad"
        if (Test-Path -LiteralPath $DevadTarget) {
            throw "Project .devad exists. Use migrate_project.py; installer never overwrites it."
        }
        $ProjectStage = Join-Path $ProjectRoot ".devad.x9-stage-$Stamp"
        if (Test-Path -LiteralPath $ProjectStage) {
            throw "Project stage already exists: $ProjectStage"
        }
        $Template = Join-Path $PackageRoot "templates\x9-project\.devad"
        Copy-Item -LiteralPath $Template -Destination $ProjectStage -Recurse
        if (-not (Test-Path -LiteralPath (Join-Path $ProjectStage "ROUTER.md") -PathType Leaf)) {
            throw "Project template staging validation failed: $ProjectStage"
        }
        Move-Item -LiteralPath $ProjectStage -Destination $DevadTarget
        $ProjectInstalled = $true
    }
}
catch {
    New-Item -ItemType Directory -Force -Path $FailedRoot | Out-Null
    if ($ProjectInstalled -and $DevadTarget -and (Test-Path -LiteralPath $DevadTarget)) {
        Move-Item -LiteralPath $DevadTarget -Destination (Join-Path $FailedRoot "project-overlay-installed")
    }
    elseif ($ProjectStage -and (Test-Path -LiteralPath $ProjectStage)) {
        Move-Item -LiteralPath $ProjectStage -Destination (Join-Path $FailedRoot "project-overlay-stage")
    }
    foreach ($Skill in $Installed) {
        $Target = Join-Path $SkillsRoot $Skill
        if (Test-Path -LiteralPath $Target) {
            Move-Item -LiteralPath $Target -Destination (Join-Path $FailedRoot $Skill)
        }
    }
    foreach ($Entry in $InstallEntries) {
        $Skill = $Entry.Name
        $Backup = Join-Path $BackupRoot $Skill
        $Target = Join-Path $SkillsRoot $Skill
        if ((Test-Path -LiteralPath $Backup) -and -not (Test-Path -LiteralPath $Target)) {
            Move-Item -LiteralPath $Backup -Destination $Target
        }
    }
    throw
}

if ($UseActiveCatalog) {
    Write-Host "PASS: installed $($InstallEntries.Count) sanitized active catalog skills"
}
else {
    Write-Host "PASS: installed nine Style/default and Code-trial skills"
}
Write-Host "Rollback backup: $BackupRoot"
