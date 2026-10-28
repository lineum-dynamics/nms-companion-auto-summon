param(
    [Parameter(Mandatory = $true)][string]$InputPath,
    [Parameter(Mandatory = $true)][ValidatePattern('^[0-9a-f]{64}$')][string]$ExpectedSha256,
    [Parameter(Mandatory = $true)][string]$ReportPath
)

# Use the documented read-only custom-scan mode on an ephemeral runner so
# stock file exclusions cannot skip the input. A harmless EICAR control must
# be detected in that same mode. No machine-wide protection setting changes.
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
    protection_configuration_changed = $false; game_access = $false; explicit_binary_upload_performed = $false
    automatic_cloud_transmission = 'NOT CHECKED'
    global_clearance_established = $false; other_vendor_verdict_established = $false
}

function Get-EngineEvidence {
    Get-MpComputerStatus | Select-Object AMServiceEnabled,AntivirusEnabled,RealTimeProtectionEnabled,AMRunningMode,AMProductVersion,AMEngineVersion,AntivirusSignatureVersion,AntivirusSignatureLastUpdated
}
function Wait-ReadyEngine {
    $report.engine_readiness_checks = @()
    for ($attempt = 0; $attempt -lt 12; $attempt++) {
        try {
            $state = Get-EngineEvidence
            $running = (Get-Service WinDefend -ErrorAction Stop).Status -eq 'Running'
            $ready = $running -and $state.AMServiceEnabled -and $state.AntivirusEnabled -and
                $state.AMEngineVersion -and $state.AMEngineVersion -ne '0.0.0.0' -and
                $state.AntivirusSignatureVersion
            $report.engine_readiness_checks += [ordered]@{attempt=$attempt;ready=[bool]$ready;state=$state}
            if ($ready) { return $state }
        } catch {
            $report.engine_readiness_checks += [ordered]@{attempt=$attempt;ready=$false;error_hresult=$_.Exception.HResult}
        }
        if ($attempt -lt 11) { Start-Sleep -Seconds 5 }
    }
    throw 'Active scan engine did not become ready within the bounded post-update wait'
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
    try { Update-MpSignature -ErrorAction Stop; $report.signature_update = 'completed' }
    catch { $report.signature_update = 'failed-check-active-engine-evidence'; $report.signature_update_hresult = $_.Exception.HResult }
    # A signature update can replace the platform and temporarily stop its RPC
    # service. Wait without changing service/protection settings, then resolve
    # the active scanner again instead of retaining the pre-update executable.
    $report.scan_engine_before = Wait-ReadyEngine
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
        # CurrentVersion is an alias of the versioned directory on the runner.
        # Select the explicit active platform directory, not both representations.
        $_.Directory.Name -match ('^'+[regex]::Escape($report.scan_engine_before.AMProductVersion)+'(?:-\d+)?$') -and
        ('{0}.{1}.{2}.{3}' -f $info.FileMajorPart,$info.FileMinorPart,$info.FileBuildPart,$info.FilePrivatePart) -eq $report.scan_engine_before.AMProductVersion
    })
    if ($tools.Count -ne 1) { throw 'A unique scanner matching the active platform version was not found' }
    $scanner = $tools[0].FullName
    $signature = Get-AuthenticodeSignature -LiteralPath $scanner
    if ($signature.Status -ne 'Valid' -or $signature.SignerCertificate.Subject -notmatch 'Microsoft') { throw 'Scanner signature is not valid Microsoft provenance' }
    $report.scanner = [ordered]@{version=$tools[0].VersionInfo.FileVersion;sha256=(Get-FileHash -LiteralPath $scanner -Algorithm SHA256).Hash.ToLowerInvariant();signature_status=[string]$signature.Status;signer=$signature.SignerCertificate.Subject}
    $check = (& $scanner -CheckExclusion -Path $target 2>&1 | Out-String)
    $report.exclusion_check_exit_code = $LASTEXITCODE
    $report.exclusion_check_output = $check.Replace($target,'<exact-module>').Trim()
    if ($report.exclusion_check_exit_code -notin @(0,1)) { throw 'Effective stock exclusion check failed' }
    $report.scan_mode = [ordered]@{type='read-only custom scan';switch='-DisableRemediation';machine_wide_preferences_changed=$false;file_exclusions_ignored_by_documented_mode=$true;detections_reported_in='command output, not UI or event log'}
    $report.scan_policy_sha256 = Get-PreferenceDigest
    if ($report.preference_sha256_before -ne $report.scan_policy_sha256) {
        $report.protection_configuration_changed = $true
        throw 'Protection configuration changed during the platform/signature update'
    }
    $controlDirectory = Join-Path ([IO.Path]::GetDirectoryName($target)) 'owned-engine-control'
    if (Test-Path -LiteralPath $controlDirectory) { throw 'Refuse an existing positive-control directory' }
    New-Item -ItemType Directory -Path $controlDirectory | Out-Null
    $control = Join-Path $controlDirectory 'engine-control.asi'
    Invoke-WebRequest -Uri 'https://secure.eicar.org/eicar.com.txt' -OutFile $control
    if ((Get-Item -LiteralPath $control).Length -ne 68) { throw 'Official harmless EICAR control size differs; do not substitute another input' }
    $controlHash = (Get-FileHash -LiteralPath $control -Algorithm SHA256).Hash.ToLowerInvariant()
    $controlOutput = (& $scanner -Scan -ScanType 3 -File $control -DisableRemediation 2>&1 | Out-String)
    $controlExit = $LASTEXITCODE
    $report.positive_control = [ordered]@{source='https://secure.eicar.org/eicar.com.txt';bytes=68;sha256=$controlHash;exit_code=$controlExit;output=$controlOutput.Replace($control,'<harmless-engine-control>').Trim();passed=($controlExit -eq 2 -and $controlOutput -match 'EICAR')}
    if (-not $report.positive_control.passed) { throw 'Positive engine detection was not established; refuse a no-detection claim' }
    $report.detections_before = @(Get-MatchingDetections)
    if ($report.detections_before.Count) { $report.result = 'DETECTED_BEFORE_CUSTOM_SCAN'; $exitCode = 2; throw 'A detection already applies to this exact input; do not restore or rescan another copy' }
    $report.scan_performed = $true
    $output = (& $scanner -Scan -ScanType 3 -File $target -DisableRemediation 2>&1 | Out-String)
    $report.scan_exit_code = $LASTEXITCODE
    $report.scan_output = $output.Replace($target,'<exact-module>').Trim()
    $report.detections_after = @(Get-MatchingDetections)
    $report.engine_after = Get-EngineEvidence
    $report.preference_sha256_after = Get-PreferenceDigest
    if ($report.scan_policy_sha256 -ne $report.preference_sha256_after) {
        $report.protection_configuration_changed = $true
        throw 'Protection configuration changed during the scan'
    }
    if ($report.detections_after.Count) {
        $report.result = 'DETECTED'; $exitCode = 2
    } elseif ($report.scan_exit_code -ne 0 -or $output -notmatch 'Scan finished') {
        $report.result = 'DETECTION_OR_SCAN_ERROR'
        throw 'Nonzero or incomplete read-only scan; inspect command output rather than treating it as clean'
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
