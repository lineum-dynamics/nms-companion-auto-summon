param(
    [Parameter(Mandatory = $true)][string]$InputPath,
    [Parameter(Mandatory = $true)][ValidatePattern('^[0-9a-f]{64}$')][string]$ExpectedSha256,
    [Parameter(Mandatory = $true)][string]$ReportPath
)

# This reads an exact reproduced module on an ephemeral runner. It never
# changes protection, restores a blocked input, executes the module or deploys.
$ErrorActionPreference = 'Stop'
if ($env:GITHUB_ACTIONS -ne 'true' -or $env:GITHUB_REPOSITORY -ne 'lineum-dynamics/nms-companion-auto-summon') {
    throw 'Run only in the repository isolated GitHub Actions workflow'
}
$target = [IO.Path]::GetFullPath($InputPath)
$prefix = 'C:\Projects\nms-companion-auto-summon-compat-cosmos-706\build\'
if (-not $target.StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase) -or [IO.Path]::GetFileName($target) -ne 'CompanionAutoSummon.asi') {
    throw 'Expected the explicitly reproduced module in the owned CI build directory'
}
$report = [ordered]@{
    schema = 1; kind = 'exact-module-defender-custom-scan'; expected_sha256 = $ExpectedSha256
    source_revision = $env:SUBJECT_REVISION; controller_revision = $env:GITHUB_SHA
    started_utc = [DateTime]::UtcNow.ToString('o'); input_name = 'CompanionAutoSummon.asi'
    result = 'TOOL_ERROR'; scan_performed = $false; scan_completed = $false
    protection_configuration_changed = $false; game_access = $false; binary_uploaded = $false
    global_clearance_established = $false; other_vendor_verdict_established = $false
}

function Get-EngineEvidence {
    Get-MpComputerStatus | Select-Object AMServiceEnabled,AntivirusEnabled,RealTimeProtectionEnabled,AMRunningMode,AMProductVersion,AMEngineVersion,AntivirusSignatureVersion,AntivirusSignatureLastUpdated
}
function Get-PreferenceDigest {
    $json = Get-MpPreference | Select-Object DisableRealtimeMonitoring,DisableBehaviorMonitoring,DisableIOAVProtection,ExclusionPath,ExclusionExtension,ExclusionProcess,MAPSReporting,SubmitSamplesConsent | ConvertTo-Json -Compress -Depth 5
    [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes($json))).ToLowerInvariant()
}
function Get-MatchingDetections {
    @(Get-MpThreatDetection -ErrorAction Stop | Where-Object {
        $matchesTarget = $false
        foreach ($resource in $_.Resources) {
            if ([string]$resource -and ([string]$resource).IndexOf($target,[StringComparison]::OrdinalIgnoreCase) -ge 0) { $matchesTarget = $true }
        }
        $matchesTarget
    } | Select-Object DetectionID,ThreatID,ActionSuccess,ThreatStatusID,InitialDetectionTime,LastThreatStatusChangeTime)
}

$exitCode = 3
try {
    $report.engine_before = Get-EngineEvidence
    if (-not $report.engine_before.AMServiceEnabled -or -not $report.engine_before.AntivirusEnabled -or (Get-Service WinDefend).Status -ne 'Running') {
        throw 'The stock antivirus scan service is unavailable'
    }
    $report.preference_sha256_before = Get-PreferenceDigest
    $report.input_sha256 = (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($report.input_sha256 -ne $ExpectedSha256) { $report.result = 'INPUT_MISMATCH'; throw 'Frozen module hash mismatch before scan' }
    $report.input_bytes = (Get-Item -LiteralPath $target).Length
    $platform = Join-Path $env:ProgramData 'Microsoft/Windows Defender/Platform'
    $allTools = @(Get-ChildItem -LiteralPath $platform -Directory | ForEach-Object {
        $candidate = Join-Path $_.FullName 'MpCmdRun.exe'
        if (Test-Path -LiteralPath $candidate -PathType Leaf) { Get-Item -LiteralPath $candidate }
    })
    $report.scanner_inventory = @($allTools | ForEach-Object {
        $info = $_.VersionInfo
        [pscustomobject]@{platform_directory=$_.Directory.Name;file_version=$info.FileVersion;numeric_version=('{0}.{1}.{2}.{3}' -f $info.FileMajorPart,$info.FileMinorPart,$info.FileBuildPart,$info.FilePrivatePart)}
    })
    $tools = @($allTools | Where-Object {
        $info = $_.VersionInfo
        ('{0}.{1}.{2}.{3}' -f $info.FileMajorPart,$info.FileMinorPart,$info.FileBuildPart,$info.FilePrivatePart) -eq $report.engine_before.AMProductVersion
    })
    if ($tools.Count -ne 1) { throw 'A unique scanner matching the active platform version was not found' }
    $scanner = $tools[0].FullName
    $signature = Get-AuthenticodeSignature -LiteralPath $scanner
    if ($signature.Status -ne 'Valid' -or $signature.SignerCertificate.Subject -notmatch 'Microsoft') { throw 'Scanner signature is not valid Microsoft provenance' }
    $report.scanner = [ordered]@{version=$tools[0].VersionInfo.FileVersion;sha256=(Get-FileHash -LiteralPath $scanner -Algorithm SHA256).Hash.ToLowerInvariant();signature_status=[string]$signature.Status;signer=$signature.SignerCertificate.Subject}
    $check = (& $scanner -CheckExclusion -Path $target 2>&1 | Out-String)
    $report.exclusion_check_exit_code = $LASTEXITCODE
    $report.exclusion_check_output = $check.Replace($target,'<exact-module>').Trim()
    if ($LASTEXITCODE -ne 1 -or $check -notmatch 'is not excluded') { $report.result = 'EXCLUDED_OR_CHECK_FAILED'; throw 'No verified non-excluded input; refuse a clean-scan claim' }
    $report.detections_before = @(Get-MatchingDetections)
    if ($report.detections_before.Count) { $report.result = 'DETECTED_BEFORE_CUSTOM_SCAN'; $exitCode = 2; throw 'A detection already applies to this exact input; do not restore or rescan another copy' }
    $report.scan_performed = $true
    $output = (& $scanner -Scan -ScanType 3 -File $target 2>&1 | Out-String)
    $report.scan_exit_code = $LASTEXITCODE
    $report.scan_output = $output.Replace($target,'<exact-module>').Trim()
    $report.detections_after = @(Get-MatchingDetections)
    $report.engine_after = Get-EngineEvidence
    $report.preference_sha256_after = Get-PreferenceDigest
    if ($report.preference_sha256_before -ne $report.preference_sha256_after) { throw 'Protection configuration changed during the observation' }
    if ($report.detections_after.Count) {
        $report.result = 'DETECTED'; $exitCode = 2
    } elseif ($report.scan_exit_code -ne 0 -or $output -notmatch 'Scan finished') {
        throw 'Scanner did not report a completed successful custom scan'
    } else {
        $report.input_sha256_after = (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($report.input_sha256_after -ne $ExpectedSha256) { throw 'Input changed during scan' }
        $report.scan_completed = $true; $report.result = 'NO_DETECTION_RECORDED'; $exitCode = 0
    }
} catch {
    $report.error = [ordered]@{type=$_.Exception.GetType().FullName;hresult=$_.Exception.HResult;message=$_.Exception.Message.Replace($target,'<exact-module>')}
} finally {
    $report.finished_utc = [DateTime]::UtcNow.ToString('o')
    $report | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $ReportPath -Encoding utf8
    [pscustomobject]@{result=$report.result;scan_performed=$report.scan_performed;scan_completed=$report.scan_completed;expected_sha256=$ExpectedSha256} | ConvertTo-Json -Compress
}
exit $exitCode
