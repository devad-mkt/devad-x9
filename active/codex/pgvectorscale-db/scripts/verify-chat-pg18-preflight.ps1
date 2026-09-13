[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$Worktree,

    [string]$GuideRelativePath = '.devad/features/chat-full-migration-1/PG18-SELF-EXECUTION-GUIDE.md',

    [string]$ManifestRelativePath = '.devad/features/chat-full-migration-1/PG18-ONE-LEASE-PROOF-MANIFEST.md',

    [string]$TailnetReceiptRelativePath,

    [string]$CapabilityReceiptRelativePath,

    [string]$ClientProfilePath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Stop-Safely
{
    [Console]::Error.WriteLine('PG18 preflight failed safely.')
    exit 1
}

function Resolve-LocalPath
{
    param(
        [string]$Path,
        [switch]$RequireExisting
    )

    if ([string]::IsNullOrWhiteSpace($Path) -or $Path -match '^(\\\\|//)') {
        Stop-Safely
    }

    $resolvedPath = [System.IO.Path]::GetFullPath($Path)
    $root = [System.IO.Path]::GetPathRoot($resolvedPath)

    if ($root -notmatch '^[A-Za-z]:\\$') {
        Stop-Safely
    }

    try {
        $drive = [System.IO.DriveInfo]::new($root)
    } catch {
        Stop-Safely
    }

    if ($drive.DriveType -notin @([System.IO.DriveType]::Fixed, [System.IO.DriveType]::Ram)) {
        Stop-Safely
    }

    if ($RequireExisting) {
        if (-not (Test-Path -LiteralPath $resolvedPath)) {
            Stop-Safely
        }

        $ancestorPath = $resolvedPath

        while ($true) {
            $item = Get-Item -LiteralPath $ancestorPath -Force

            if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
                Stop-Safely
            }

            $parentPath = [System.IO.Path]::GetDirectoryName($ancestorPath)

            if ([string]::IsNullOrWhiteSpace($parentPath) -or $parentPath -eq $ancestorPath) {
                break
            }

            $ancestorPath = $parentPath
        }
    }

    return $resolvedPath
}

function Resolve-WorktreeChildPath
{
    param(
        [string]$Root,
        [string]$RelativePath
    )

    if ([string]::IsNullOrWhiteSpace($RelativePath) -or [System.IO.Path]::IsPathRooted($RelativePath) -or $RelativePath -match '(^|[\\/])\.\.([\\/]|$)') {
        Stop-Safely
    }

    $resolvedRoot = Resolve-LocalPath -Path $Root -RequireExisting

    if ($resolvedRoot.Length -gt 3) {
        $resolvedRoot = $resolvedRoot.TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)
    }
    $resolvedPath = [System.IO.Path]::GetFullPath((Join-Path $resolvedRoot $RelativePath))

    if (-not $resolvedPath.StartsWith("$resolvedRoot$([System.IO.Path]::DirectorySeparatorChar)", [System.StringComparison]::OrdinalIgnoreCase)) {
        Stop-Safely
    }

    return (Resolve-LocalPath -Path $resolvedPath -RequireExisting)
}

function Get-RequiredMatch
{
    param(
        [string]$Content,
        [string]$Pattern
    )

    $match = [System.Text.RegularExpressions.Regex]::Match(
        $Content,
        $Pattern,
        [System.Text.RegularExpressions.RegexOptions]::Multiline
    )

    if (-not $match.Success) {
        Stop-Safely
    }

    return $match.Groups['value'].Value
}

function Get-Sha256
{
    param(
        [byte[]]$Bytes
    )

    $sha256 = [System.Security.Cryptography.SHA256]::Create()

    try {
        return ([System.BitConverter]::ToString($sha256.ComputeHash($Bytes))).Replace('-', '').ToLowerInvariant()
    } finally {
        $sha256.Dispose()
    }
}

function Get-GitBlob
{
    param(
        [string]$Root,
        [string]$Revision,
        [string]$Path
    )

    $result = @(& git -C $Root rev-parse "$Revision`:$Path" 2>$null)

    if ($LASTEXITCODE -ne 0 -or $result.Count -ne 1 -or $result[0] -notmatch '^[0-9a-f]{40}$') {
        Stop-Safely
    }

    return $result[0]
}

function Get-SanitizedReceiptLines
{
    param(
        [string]$Root,
        [string]$RelativePath
    )

    $normalizedRelativePath = $RelativePath.Replace('\', '/')

    if ($normalizedRelativePath -notmatch '^\.devad/features/chat-full-migration-1/artifacts/[A-Za-z0-9][A-Za-z0-9._-]*\.txt$') {
        Stop-Safely
    }

    $path = Resolve-WorktreeChildPath -Root $Root -RelativePath $normalizedRelativePath

    if (-not (Test-Path -LiteralPath $path -PathType Leaf) -or (Get-Item -LiteralPath $path -Force).Length -gt 8192) {
        Stop-Safely
    }

    $content = [System.IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)

    if ($content.IndexOf([char]0) -ge 0) {
        Stop-Safely
    }

    return @($content.Replace("`r`n", "`n").Replace("`r", "`n").Trim().Split("`n"))
}

function Test-TailnetReceipt
{
    param(
        [string]$Root,
        [string]$RelativePath
    )

    $lines = Get-SanitizedReceiptLines -Root $Root -RelativePath $RelativePath
    $pattern = @(
        '^CHAT_PG18_TAILNET_PRINCIPAL_READY$',
        '^host_fingerprint_sha256=[0-9a-f]{64}$',
        '^principal=chatproof$',
        '^transport=OPENSSH_OVER_TAILNET$',
        '^tailnet_tcp_rule=PASS$',
        '^listener_bind=TAILNET_ONLY$',
        '^listener_identity_sha256=[0-9a-f]{64}$'
    )

    if ($lines.Count -ne $pattern.Count) {
        Stop-Safely
    }

    for ($index = 0; $index -lt $pattern.Count; $index++) {
        if ($lines[$index] -notmatch $pattern[$index]) {
            Stop-Safely
        }
    }

    return [pscustomobject]@{
        ListenerIdentitySha256 = $lines[6].Substring('listener_identity_sha256='.Length)
    }
}

function Test-CapabilityReceipt
{
    param(
        [string]$Root,
        [string]$RelativePath
    )

    $lines = Get-SanitizedReceiptLines -Root $Root -RelativePath $RelativePath
    $pattern = @(
        '^CHAT_PG18_CAPABILITY_INSTALLED$',
        '^gateway_path=/usr/local/sbin/devad-chat-pg18-proof$',
        '^gateway_sha256=[0-9a-f]{64}$',
        '^executor_path=/usr/local/libexec/devad/chat-pg18-proof/[0-9a-f]{64}/executor$',
        '^executor_sha256=[0-9a-f]{64}$',
        '^policy_path=/usr/local/share/devad/chat-pg18-proof/[0-9a-f]{64}/manifest$',
        '^policy_sha256=[0-9a-f]{64}$',
        '^pg_image_digest=sha256:[0-9a-f]{64}$',
        '^runner_image_digest=sha256:[0-9a-f]{64}$',
        '^repository=<DEVAD_CORE_REPO>$',
        '^principal=chatproof$',
        '^tailnet_principal=ready$',
        '^transport=OPENSSH_OVER_TAILNET$',
        '^listener_bind=TAILNET_ONLY$',
        '^listener_identity_sha256=[0-9a-f]{64}$',
        '^client_profile_path=/usr/local/share/devad/chat-pg18-proof/profiles/[0-9a-f]{64}/client\\.conf$',
        '^client_profile_sha256=[0-9a-f]{64}$',
        '^tailnet_accept_env=0$',
        '^fixed_shell_commands=run,reconcile$',
        '^command_enforcement=HOST_SIDE_ONLY$',
        '^command_gate=PASS$',
        '^channel_gate=PASS$',
        '^pty=0$',
        '^forwarding=0$',
        '^agent=0$',
        '^sftp=0$',
        '^general_shell=0$',
        '^sudoers_setenv=0$',
        '^max_runtime_seconds=2700$'
    )

    if ($lines.Count -ne $pattern.Count) {
        Stop-Safely
    }

    for ($index = 0; $index -lt $pattern.Count; $index++) {
        if ($lines[$index] -notmatch $pattern[$index]) {
            Stop-Safely
        }
    }

    $executorPathHash = $lines[3].Split('/')[6]
    $executorHash = $lines[4].Substring('executor_sha256='.Length)
    $policyPathHash = $lines[5].Split('/')[6]
    $policyHash = $lines[6].Substring('policy_sha256='.Length)
    $clientProfilePathHash = $lines[15].Split('/')[7]
    $clientProfileHash = $lines[16].Substring('client_profile_sha256='.Length)

    if ($executorPathHash -ne $executorHash -or $policyPathHash -ne $policyHash -or $clientProfilePathHash -ne $clientProfileHash) {
        Stop-Safely
    }

    return [pscustomobject]@{
        ListenerIdentitySha256 = $lines[14].Substring('listener_identity_sha256='.Length)
        ClientProfilePath = $lines[15].Substring('client_profile_path='.Length)
        ClientProfileSha256 = $clientProfileHash
        PolicySha256 = $policyHash
    }
}

try {
    $resolvedWorktree = Resolve-LocalPath -Path $Worktree -RequireExisting

    if (-not (Test-Path -LiteralPath $resolvedWorktree -PathType Container) -or -not (Test-Path -LiteralPath (Join-Path $resolvedWorktree '.git'))) {
        Stop-Safely
    }

    $guidePath = Resolve-WorktreeChildPath -Root $resolvedWorktree -RelativePath $GuideRelativePath
    $manifestPath = Resolve-WorktreeChildPath -Root $resolvedWorktree -RelativePath $ManifestRelativePath

    if (-not (Test-Path -LiteralPath $guidePath -PathType Leaf) -or -not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
        Stop-Safely
    }

    $guide = [System.IO.File]::ReadAllText($guidePath, [System.Text.Encoding]::UTF8)
    $manifest = [System.IO.File]::ReadAllText($manifestPath, [System.Text.Encoding]::UTF8)
    $guideFrozen = [System.Text.RegularExpressions.Regex]::Match($guide, '## Frozen execution identity\s+```text\s*(?<value>.*?)\s*```', [System.Text.RegularExpressions.RegexOptions]::Singleline)

    if (-not $guideFrozen.Success) {
        Stop-Safely
    }

    $candidate = Get-RequiredMatch -Content $manifest -Pattern '^candidate=(?<value>[0-9a-f]{40})$'
    $lockfile = Get-RequiredMatch -Content $manifest -Pattern '^lockfile=(?<value>[A-Za-z0-9._-]+)$'
    $lockfileBlob = Get-RequiredMatch -Content $manifest -Pattern '^lockfile_blob=(?<value>[0-9a-f]{40})$'
    $argvHash = Get-RequiredMatch -Content $manifest -Pattern '^argv_sha256=(?<value>[0-9a-f]{64})$'
    $argvBytes = [int](Get-RequiredMatch -Content $manifest -Pattern '^argv_bytes=(?<value>[0-9]+)$')
    $guideCandidate = Get-RequiredMatch -Content $guideFrozen.Groups['value'].Value -Pattern '^candidate=(?<value>[0-9a-f]{40})$'
    $guideManifestHash = Get-RequiredMatch -Content $guideFrozen.Groups['value'].Value -Pattern '^policy_packet_sha256=(?<value>[0-9a-f]{64})$'
    $guideManifestBytes = [int](Get-RequiredMatch -Content $guideFrozen.Groups['value'].Value -Pattern '^manifest_bytes=(?<value>[0-9]+)$')
    $guideArgvHash = Get-RequiredMatch -Content $guideFrozen.Groups['value'].Value -Pattern '^argv_sha256=(?<value>[0-9a-f]{64})$'
    $guideArgvBytes = [int](Get-RequiredMatch -Content $guideFrozen.Groups['value'].Value -Pattern '^argv_bytes=(?<value>[0-9]+)$')

    if ($candidate -ne $guideCandidate -or $argvHash -ne $guideArgvHash -or $argvBytes -ne $guideArgvBytes -or (Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $guideManifestHash -or (Get-Item -LiteralPath $manifestPath).Length -ne $guideManifestBytes) {
        Stop-Safely
    }

    & git -C $resolvedWorktree cat-file -e ($candidate + '^{commit}') 2>$null

    if ($LASTEXITCODE -ne 0 -or (Get-GitBlob -Root $resolvedWorktree -Revision $candidate -Path $lockfile) -ne $lockfileBlob) {
        Stop-Safely
    }

    $boundBlobs = [System.Text.RegularExpressions.Regex]::Matches($manifest, '(?m)^(?<path>(?:database|tests)/[^=\r\n]+)=(?<blob>[0-9a-f]{40})$')

    if ($boundBlobs.Count -eq 0) {
        Stop-Safely
    }

    foreach ($boundBlob in $boundBlobs) {
        if ((Get-GitBlob -Root $resolvedWorktree -Revision $candidate -Path $boundBlob.Groups['path'].Value) -ne $boundBlob.Groups['blob'].Value) {
            Stop-Safely
        }
    }

    $argvBlock = [System.Text.RegularExpressions.Regex]::Match($manifest, '(?s)The executor receives only this NUL-delimited argv;.*?```text\s*(?<value>.*?)\s*```')

    if (-not $argvBlock.Success) {
        Stop-Safely
    }

    $argv = @($argvBlock.Groups['value'].Value.Replace("`r`n", "`n").Replace("`r", "`n").Trim().Split("`n"))
    $argvBytesActual = [System.Text.Encoding]::UTF8.GetBytes([string]::Join([char]0, $argv))

    if ($argvBytesActual.Length -ne $argvBytes -or (Get-Sha256 -Bytes $argvBytesActual) -ne $argvHash) {
        Stop-Safely
    }

    Write-Output 'Preflight source identity: PASS.'

    $tailnetPresent = -not [string]::IsNullOrWhiteSpace($TailnetReceiptRelativePath)
    $capabilityPresent = -not [string]::IsNullOrWhiteSpace($CapabilityReceiptRelativePath)

    if ($tailnetPresent) {
        $tailnetReceipt = Test-TailnetReceipt -Root $resolvedWorktree -RelativePath $TailnetReceiptRelativePath
        Write-Output 'Preflight Tailnet principal receipt: PASS.'
    } else {
        Write-Output 'Preflight Tailnet principal receipt: MISSING.'
    }

    if ($capabilityPresent) {
        $capabilityReceipt = Test-CapabilityReceipt -Root $resolvedWorktree -RelativePath $CapabilityReceiptRelativePath
        Write-Output 'Preflight installed capability receipt: PASS.'
    } else {
        Write-Output 'Preflight installed capability receipt: MISSING.'
    }

    if (-not $tailnetPresent -or -not $capabilityPresent) {
        Write-Output 'RESUME_ON=CHAT_PG18_TAILNET_PRINCIPAL_READY+CHAT_PG18_CAPABILITY_INSTALLED'
        exit 2
    }

    if ($tailnetReceipt.ListenerIdentitySha256 -ne $capabilityReceipt.ListenerIdentitySha256) {
        Stop-Safely
    }

    if ($capabilityReceipt.PolicySha256 -ne $guideManifestHash) {
        Stop-Safely
    }

    if ([string]::IsNullOrWhiteSpace($ClientProfilePath)) {
        Stop-Safely
    }

    $resolvedClientProfilePath = Resolve-LocalPath -Path $ClientProfilePath -RequireExisting

    if (-not (Test-Path -LiteralPath $resolvedClientProfilePath -PathType Leaf) -or (Get-FileHash -LiteralPath $resolvedClientProfilePath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $capabilityReceipt.ClientProfileSha256) {
        Stop-Safely
    }

    Write-Output 'Preflight admission readiness: REQUIRES_FRESH_COLLISION_CLAIM.'
    exit 0
} catch {
    Stop-Safely
}
