param(
    [string]$CodexHome = "$HOME\.codex",
    [string]$ProjectRoot = "",
    [string]$Python = "python",
    [string]$SkillValidator = "",
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
    "x9-project-docs",
    "dokploy",
    "devad-docs",
    "tldr",
    "smooth-coding",
    "sdlc",
    "xplan",
    "devad-adoptions"
)

$ManifestPath = Join-Path $PackageRoot "SOURCE_MANIFEST.sha256"

function Assert-ManifestTree {
    param(
        [Parameter(Mandatory = $true)][string]$Tree,
        [Parameter(Mandatory = $true)][string]$ManifestPrefix
    )

    if (-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)) {
        throw "Source manifest is missing: $ManifestPath"
    }
    if (-not (Test-Path -LiteralPath $Tree -PathType Container)) {
        throw "Manifest tree is missing: $Tree"
    }
    $TreeItem = Get-Item -LiteralPath $Tree -Force
    if (($TreeItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw "Manifest tree cannot be a reparse path: $Tree"
    }
    $TreeFull = [System.IO.Path]::GetFullPath($Tree)
    $TreeBoundary = $TreeFull.TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
    $Expected = @{}
    foreach ($Line in Get-Content -LiteralPath $ManifestPath -Encoding UTF8) {
        if (-not $Line) { continue }
        if ($Line -notmatch '^([0-9a-f]{64})  (.+)$') {
            throw "Invalid source manifest line."
        }
        $Digest = $Matches[1]
        $Relative = $Matches[2]
        if (-not $Relative.StartsWith($ManifestPrefix, [System.StringComparison]::Ordinal)) {
            continue
        }
        $Local = $Relative.Substring($ManifestPrefix.Length)
        $Parts = $Local.Split('/')
        if (-not $Local -or $Local.Contains('\') -or
            [System.IO.Path]::IsPathRooted($Local) -or
            $Parts -contains '' -or $Parts -contains '..' -or
            $Parts -contains '.' -or $Parts[0].Contains(':')) {
            throw "Unsafe source manifest path: $Relative"
        }
        if ($Expected.ContainsKey($Local)) {
            throw "Duplicate source manifest path: $Relative"
        }
        $Expected[$Local] = $Digest
    }
    if ($Expected.Count -eq 0) {
        throw "Source manifest has no entries for: $ManifestPrefix"
    }

    $Seen = @{}
    foreach ($Item in Get-ChildItem -LiteralPath $Tree -Recurse -Force) {
        if (($Item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw "Manifest tree contains a reparse path: $($Item.FullName)"
        }
        if ($Item.PSIsContainer) { continue }
        $Full = [System.IO.Path]::GetFullPath($Item.FullName)
        if (-not $Full.StartsWith($TreeBoundary, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "Manifest tree file escapes root: $Full"
        }
        $Local = $Full.Substring($TreeBoundary.Length).Replace('\', '/')
        if (-not $Expected.ContainsKey($Local)) {
            throw "Unexpected file outside source manifest: $Local"
        }
        $Actual = (Get-FileHash -LiteralPath $Full -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($Actual -ne $Expected[$Local]) {
            throw "Source manifest byte mismatch: $Local"
        }
        $Seen[$Local] = $true
    }
    if ($Seen.Count -ne $Expected.Count) {
        $Missing = @($Expected.Keys | Where-Object { -not $Seen.ContainsKey($_) })
        throw "Source manifest tree is incomplete: $($Missing -join ', ')"
    }
}

function Copy-ManifestTree {
    param(
        [Parameter(Mandatory = $true)][string]$SourceTree,
        [Parameter(Mandatory = $true)][string]$ManifestPrefix,
        [Parameter(Mandatory = $true)][string]$Destination
    )

    $SourceFull = [System.IO.Path]::GetFullPath($SourceTree)
    $SourceBoundary = $SourceFull.TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
    $Copied = 0
    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    foreach ($Line in Get-Content -LiteralPath $ManifestPath -Encoding UTF8) {
        if (-not $Line -or
            $Line -notmatch '^([0-9a-f]{64})  (.+)$' -or
            -not $Matches[2].StartsWith($ManifestPrefix, [System.StringComparison]::Ordinal)) {
            continue
        }
        $Digest = $Matches[1]
        $Local = $Matches[2].Substring($ManifestPrefix.Length)
        $Parts = $Local.Split('/')
        if (-not $Local -or $Local.Contains('\') -or
            [System.IO.Path]::IsPathRooted($Local) -or
            $Parts -contains '' -or $Parts -contains '..' -or
            $Parts -contains '.' -or $Parts[0].Contains(':')) {
            throw "Unsafe source manifest path: $($Matches[2])"
        }
        $Source = [System.IO.Path]::GetFullPath((Join-Path $SourceFull $Local))
        if (-not $Source.StartsWith($SourceBoundary, [System.StringComparison]::OrdinalIgnoreCase) -or
            -not (Test-Path -LiteralPath $Source -PathType Leaf)) {
            throw "Manifest source file is missing or escapes root: $Local"
        }
        $Actual = (Get-FileHash -LiteralPath $Source -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($Actual -ne $Digest) {
            throw "Source manifest byte mismatch before staging: $Local"
        }
        $Target = Join-Path $Destination $Local
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Target) | Out-Null
        Copy-Item -LiteralPath $Source -Destination $Target
        $Copied += 1
    }
    if ($Copied -eq 0) {
        throw "Source manifest has no entries for: $ManifestPrefix"
    }
}

Write-Host "X9 Loop Style source (with experimental Code trial): $PackageRoot"
Write-Host "Codex home: $CodexHome"

if (-not $Apply) {
    Write-Host "DRY RUN: no files changed."
    foreach ($Skill in $Skills) {
        Write-Host "Would stage, validate, back up, and install: $Skill"
    }
    if ($ProjectRoot) {
        Write-Host "Would create and initialize a V7.3 Lite .devad only if absent: $ProjectRoot"
    }
    exit 0
}

& $Python -B (Join-Path $PSScriptRoot "validate_suite.py")
if ($LASTEXITCODE -ne 0) {
    throw "Package validation failed before install."
}

$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$SkillsRoot = Join-Path $CodexHome "skills"
$StageRoot = Join-Path $CodexHome "x9-install-staging\$Stamp"
$BackupRoot = Join-Path $CodexHome "x9-install-backups\$Stamp"
$FailedRoot = Join-Path $CodexHome "x9-install-failed\$Stamp"
New-Item -ItemType Directory -Force -Path $SkillsRoot, $StageRoot, $BackupRoot | Out-Null

foreach ($Skill in $Skills) {
    $Source = Join-Path $PackageRoot "skills\$Skill"
    $Stage = Join-Path $StageRoot $Skill
    if (-not (Test-Path -LiteralPath $Source)) {
        throw "Missing package skill: $Skill"
    }
    Copy-ManifestTree $Source "skills/$Skill/" $Stage
}

if (-not $SkillValidator) {
    Write-Host "VALIDATOR_DEPENDENCY_UNAVAILABLE: optional external quick_validate was not supplied; dependency-free package validation plus manifest verification remain active."
}
else {
    foreach ($Skill in $Skills) {
        & $Python -B $SkillValidator (Join-Path $StageRoot $Skill)
        if ($LASTEXITCODE -ne 0) {
            throw "Official skill validation failed in staging: $Skill"
        }
    }
}

foreach ($Skill in $Skills) {
    Assert-ManifestTree (Join-Path $StageRoot $Skill) "skills/$Skill/"
}

$Installed = New-Object System.Collections.Generic.List[string]
$ProjectStage = $null
$ProjectInstalled = $false
$DevadTarget = $null
try {
    foreach ($Skill in $Skills) {
        $Target = Join-Path $SkillsRoot $Skill
        $Backup = Join-Path $BackupRoot $Skill
        $Stage = Join-Path $StageRoot $Skill
        if (Test-Path -LiteralPath $Target) {
            Move-Item -LiteralPath $Target -Destination $Backup
        }
        Move-Item -LiteralPath $Stage -Destination $Target
        $Installed.Add($Skill)
        Assert-ManifestTree $Target "skills/$Skill/"
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
        $LoopCtl = Join-Path $SkillsRoot "devad-x9-loop\scripts\loopctl.py"
        & $Python -B $LoopCtl init --repo $ProjectRoot --json
        if ($LASTEXITCODE -ne 0) {
            throw "V7.3 Lite project initialization failed: $ProjectRoot"
        }
        $Snapshot = Get-Content -Raw -LiteralPath (
            Join-Path $DevadTarget "manager\loop-lite\SNAPSHOT.json"
        ) | ConvertFrom-Json
        $Profile = Get-Content -Raw -LiteralPath (
            Join-Path $DevadTarget "manager\loop-lite\PROJECT_PROFILE.json"
        ) | ConvertFrom-Json
        if ($Snapshot.schema -ne "x9-loop-lite-snapshot-v3" -or
            $Profile.schema -ne "x9-loop-project-profile-v1") {
            throw "V7.3 Lite project identity validation failed: $ProjectRoot"
        }
    }
    foreach ($Skill in $Skills) {
        Assert-ManifestTree (Join-Path $SkillsRoot $Skill) "skills/$Skill/"
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
    foreach ($Skill in $Skills) {
        $Backup = Join-Path $BackupRoot $Skill
        $Target = Join-Path $SkillsRoot $Skill
        if ((Test-Path -LiteralPath $Backup) -and -not (Test-Path -LiteralPath $Target)) {
            Move-Item -LiteralPath $Backup -Destination $Target
        }
    }
    throw
}

Write-Host "PASS: installed X9 Loop Style plus experimental Code trial and sixteen skills"
Write-Host "Rollback backup: $BackupRoot"
