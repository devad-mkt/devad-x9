[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateScript({ Test-Path -LiteralPath $_ -PathType Leaf })]
    [string]$TelemetryPath,

    [Parameter(Mandatory = $true)]
    [ValidateSet('NATIVE_V1', 'NATIVE_V2', 'INDEPENDENT_EXEC')]
    [string]$Execution,

    [Parameter(Mandatory = $true)]
    [ValidateSet('gpt-5.6-sol', 'gpt-5.6-terra', 'gpt-5.6-luna')]
    [string]$RequestedModel,

    [string]$RequestedReasoningEffort,

    [string]$AttestedModel,

    [string]$AttestedReasoningEffort,

    [string]$ThreadReceipt,

    [ValidateRange(0, [int]::MaxValue)]
    [int]$DurationMilliseconds,

    [switch]$SumTurns,

    [ValidateRange(0, 365)]
    [int]$MaxPriceAgeDays = 7,

    [switch]$AllowStalePricing,

    [string]$OutputPath
)

$ErrorActionPreference = 'Stop'

function Get-PropertyValue {
    param(
        [Parameter(Mandatory = $true)]$Object,
        [Parameter(Mandatory = $true)][string[]]$Names
    )

    foreach ($name in $Names) {
        $property = $Object.PSObject.Properties[$name]
        if ($null -ne $property -and $null -ne $property.Value) {
            return [double]$property.Value
        }
    }
    return $null
}

function Get-UsageRecord {
    param(
        [Parameter(Mandatory = $true)]$Object,
        [string]$Receipt
    )

    $input = Get-PropertyValue -Object $Object -Names @('input_tokens', 'inputTokens')
    $cached = Get-PropertyValue -Object $Object -Names @('cached_input_tokens', 'cachedInputTokens')
    $output = Get-PropertyValue -Object $Object -Names @('output_tokens', 'outputTokens')
    if ($null -eq $input -or $null -eq $output) {
        return $null
    }
    $cacheWrite = Get-PropertyValue -Object $Object -Names @('cache_write_tokens', 'cacheWriteTokens', 'cache_write_input_tokens', 'cacheWriteInputTokens')
    $reasoning = Get-PropertyValue -Object $Object -Names @('reasoning_output_tokens', 'reasoningOutputTokens')
    return [pscustomobject]@{
        thread_receipt = $Receipt
        input_tokens = $input
        cached_input_tokens = if ($null -eq $cached) { 0 } else { $cached }
        output_tokens = $output
        reasoning_output_tokens = $reasoning
        cache_write_tokens = $cacheWrite
    }
}

function Find-UsageCandidate {
    param(
        [Parameter(Mandatory = $true)]$Object,
        [string]$Receipt
    )

    foreach ($name in @('last', 'last_token_usage', 'lastTokenUsage', 'usage', 'token_usage', 'tokenUsage')) {
        $property = $Object.PSObject.Properties[$name]
        if ($null -ne $property -and $null -ne $property.Value) {
            $candidate = Get-UsageRecord -Object $property.Value -Receipt $Receipt
            if ($null -ne $candidate) {
                return $candidate
            }
            $nested = Find-UsageCandidate -Object $property.Value -Receipt $Receipt
            if ($null -ne $nested) {
                return $nested
            }
        }
    }
    return Get-UsageRecord -Object $Object -Receipt $Receipt
}

$scriptRoot = Split-Path -Parent $PSCommandPath
$pricingPath = Join-Path (Split-Path -Parent $scriptRoot) 'references\pricing-2026-07-30.json'
$pricing = Get-Content -LiteralPath $pricingPath -Raw | ConvertFrom-Json
$pricingDate = [datetime]::ParseExact($pricing.effective_date, 'yyyy-MM-dd', [Globalization.CultureInfo]::InvariantCulture)
if (-not $AllowStalePricing -and ((Get-Date) - $pricingDate).TotalDays -gt $MaxPriceAgeDays) {
    throw "PRICING_STALE: $($pricing.effective_date) is older than $MaxPriceAgeDays days. Refresh the reference before a benchmark."
}

$records = New-Object System.Collections.Generic.List[object]
$latestCumulativeRecord = $null
$detectedReceipt = $null
foreach ($line in Get-Content -LiteralPath $TelemetryPath) {
    try {
        $event = $line | ConvertFrom-Json
    } catch {
        continue
    }

    if ($event.type -eq 'session_meta' -and $null -ne $event.payload -and $null -ne $event.payload.id) {
        # Native subagent rollout files persist their child receipt here.
        $detectedReceipt = [string]$event.payload.id
        continue
    }
    if ($event.type -eq 'thread.started' -and $null -ne $event.thread_id) {
        $detectedReceipt = [string]$event.thread_id
        continue
    }
    if ($event.type -eq 'turn.completed' -and $null -ne $event.usage) {
        $candidate = Get-UsageRecord -Object $event.usage -Receipt $(if ($ThreadReceipt) { $ThreadReceipt } else { $detectedReceipt })
        if ($null -ne $candidate) { $records.Add($candidate) }
        continue
    }
    if ($event.method -eq 'thread/tokenUsage/updated' -and $null -ne $event.params) {
        $eventReceipt = [string]$event.params.threadId
        if ($ThreadReceipt -and $eventReceipt -ne $ThreadReceipt) { continue }
        $candidate = $null
        if ($null -ne $event.params.tokenUsage -and $null -ne $event.params.tokenUsage.total) {
            $candidate = Get-UsageRecord -Object $event.params.tokenUsage.total -Receipt $eventReceipt
        }
        if ($null -eq $candidate) { $candidate = Find-UsageCandidate -Object $event.params -Receipt $eventReceipt }
        if ($null -ne $candidate) { $latestCumulativeRecord = $candidate }
        continue
    }
    if ($event.type -eq 'event_msg' -and $null -ne $event.payload -and $event.payload.type -eq 'token_count' -and $null -ne $event.payload.info) {
        # Persisted native child rollouts emit multiple snapshots. The final
        # total_token_usage is the child-wide cumulative value; summing those
        # snapshots or using only last_token_usage would miscount the run.
        $receipt = $(if ($ThreadReceipt) { $ThreadReceipt } else { $detectedReceipt })
        $candidate = $null
        if ($null -ne $event.payload.info.total_token_usage) {
            $candidate = Get-UsageRecord -Object $event.payload.info.total_token_usage -Receipt $receipt
        }
        if ($null -eq $candidate) { $candidate = Find-UsageCandidate -Object $event.payload.info -Receipt $receipt }
        if ($null -ne $candidate) { $latestCumulativeRecord = $candidate }
    }
}

if ($null -ne $latestCumulativeRecord) {
    $records.Clear()
    $records.Add($latestCumulativeRecord)
}

if ($records.Count -eq 0) {
    throw 'TOKEN_MEASUREMENT_MISSING: no parseable turn.completed.usage, thread/tokenUsage/updated, or persisted event_msg token_count record was found.'
}
if ($records.Count -gt 1 -and -not $SumTurns) {
    throw "TOKEN_MEASUREMENT_AMBIGUOUS: found $($records.Count) usage records. Use one log per test or pass -SumTurns deliberately."
}

if ($SumTurns) {
    $usage = [pscustomobject]@{
        thread_receipt = if ($ThreadReceipt) { $ThreadReceipt } else { $records[-1].thread_receipt }
        input_tokens = ($records | Measure-Object -Property input_tokens -Sum).Sum
        cached_input_tokens = ($records | Measure-Object -Property cached_input_tokens -Sum).Sum
        output_tokens = ($records | Measure-Object -Property output_tokens -Sum).Sum
        reasoning_output_tokens = if (($records.reasoning_output_tokens | Where-Object { $null -ne $_ }).Count) { ($records.reasoning_output_tokens | Where-Object { $null -ne $_ } | Measure-Object -Sum).Sum } else { $null }
        cache_write_tokens = if (($records.cache_write_tokens | Where-Object { $null -ne $_ }).Count) { ($records.cache_write_tokens | Where-Object { $null -ne $_ } | Measure-Object -Sum).Sum } else { $null }
    }
} else {
    $usage = $records[0]
}

if ($usage.cached_input_tokens -gt $usage.input_tokens) {
    throw 'TOKEN_MEASUREMENT_INVALID: cached input exceeds input.'
}

$pricingModel = if ([string]::IsNullOrWhiteSpace($AttestedModel)) { $RequestedModel } else { $AttestedModel }
$attestation = if ([string]::IsNullOrWhiteSpace($AttestedModel)) { 'UNATTESTED' } else { 'ATTESTED' }
$apiRate = $pricing.api_standard_per_million_tokens.$pricingModel
$creditRate = $pricing.codex_credits_per_million_tokens.$pricingModel
if ($null -eq $apiRate -or $null -eq $creditRate) {
    throw "PRICE_MODEL_UNKNOWN: $pricingModel is absent from the dated price reference."
}

$cacheWriteKnown = $null -ne $usage.cache_write_tokens
$cacheWrites = if ($cacheWriteKnown) { $usage.cache_write_tokens } else { 0 }
$ordinaryInput = $usage.input_tokens - $usage.cached_input_tokens - $cacheWrites
if ($ordinaryInput -lt 0) {
    throw 'TOKEN_MEASUREMENT_INVALID: cached and cache-write input exceeds input.'
}

$apiUsd = (($ordinaryInput * $apiRate.input) + ($usage.cached_input_tokens * $apiRate.cached_input) + ($cacheWrites * (1.25 * $apiRate.input)) + ($usage.output_tokens * $apiRate.output)) / 1000000
$codexCredits = ((($usage.input_tokens - $usage.cached_input_tokens) * $creditRate.input) + ($usage.cached_input_tokens * $creditRate.cached_input) + ($usage.output_tokens * $creditRate.output)) / 1000000

$result = [ordered]@{
    measurement_status = if ($attestation -eq 'ATTESTED') { 'READY_FOR_COMPARISON' } else { 'UNATTESTED_NOT_COMPARABLE' }
    execution = $Execution
    requested_model = $RequestedModel
    requested_reasoning_effort = $RequestedReasoningEffort
    attested_model = if ($AttestedModel) { $AttestedModel } else { $null }
    attested_reasoning_effort = if ($AttestedReasoningEffort) { $AttestedReasoningEffort } else { $null }
    thread_receipt = if ($ThreadReceipt) { $ThreadReceipt } else { $usage.thread_receipt }
    duration_ms = $DurationMilliseconds
    input_tokens = [int64]$usage.input_tokens
    cached_input_tokens = [int64]$usage.cached_input_tokens
    uncached_input_tokens = [int64]($usage.input_tokens - $usage.cached_input_tokens)
    cache_write_tokens = if ($cacheWriteKnown) { [int64]$usage.cache_write_tokens } else { $null }
    output_tokens = [int64]$usage.output_tokens
    reasoning_output_tokens = if ($null -ne $usage.reasoning_output_tokens) { [int64]$usage.reasoning_output_tokens } else { $null }
    api_usd_estimate = [math]::Round($apiUsd, 8)
    api_estimate_quality = if ($cacheWriteKnown) { 'COMPLETE_FOR_REPORTED_TOKEN_FIELDS' } else { 'LOWER_BOUND_CACHE_WRITES_NOT_EXPOSED' }
    codex_credit_estimate = [math]::Round($codexCredits, 6)
    pricing_effective_date = $pricing.effective_date
    pricing_model = $pricingModel
    price_sources = $pricing.sources
}

$json = $result | ConvertTo-Json -Depth 5
if ($OutputPath) {
    $outputDirectory = Split-Path -Parent $OutputPath
    if ($outputDirectory) { New-Item -ItemType Directory -Path $outputDirectory -Force | Out-Null }
    [System.IO.File]::WriteAllText($OutputPath, $json + [Environment]::NewLine, (New-Object System.Text.UTF8Encoding($false)))
}

$result
