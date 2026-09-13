[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$Prompt,

    [Parameter(Mandatory = $true)]
    [ValidateScript({ Test-Path -LiteralPath $_ -PathType Container })]
    [string]$WorkingDirectory,

    [ValidateSet('read-only', 'workspace-write')]
    [string]$Sandbox = 'read-only',

    [ValidateSet('low', 'medium', 'high', 'xhigh', 'max')]
    [string]$ReasoningEffort = 'max',

    [switch]$PersistSession
)

$codexCommand = Get-Command codex -ErrorAction Stop
$resolvedWorkingDirectory = (Resolve-Path -LiteralPath $WorkingDirectory).Path

$arguments = @(
    'exec'
    '--skip-git-repo-check'
    '-C'
    $resolvedWorkingDirectory
    '-m'
    'gpt-5.6-luna'
    '-c'
    ('model_reasoning_effort="{0}"' -f $ReasoningEffort)
    '-s'
    $Sandbox
    '--json'
)

if (-not $PersistSession) {
    $arguments += '--ephemeral'
}

$arguments += $Prompt

& $codexCommand.Source @arguments
exit $LASTEXITCODE
