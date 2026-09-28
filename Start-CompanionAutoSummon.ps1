#requires -Version 5.1
<#
Starts the packaged experimental Companion Auto Summon mod for the supported Windows Steam build.
Run only after closing No Man's Sky. Dependencies stay in a separate user runtime.
Example: .\Start-CompanionAutoSummon.ps1 -GameDirectory 'D:\SteamLibrary\steamapps\common\No Man''s Sky'
Use -CheckOnly to validate an existing installation without setup or launch, even while the game is running.
#>
[CmdletBinding()]
param([string]$GameDirectory, [switch]$CheckOnly, [string]$Language, [switch]$NoDialog)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$runtimeVersion = '0.2.4'
$runtimeRequirement = "pymhf[gui]==$runtimeVersion"
$script:CasSupportedBuild = 'Cosmos 7.04 (Steam 25442159)'

function Read-LauncherCatalog {
    param([string]$Code)
    $path = Join-Path $PSScriptRoot "locales\$Code.json"
    $file = Get-Item -LiteralPath $path -ErrorAction Stop
    if ($file.Length -gt 65536) { throw 'Oversized launcher catalog' }
    $raw = [IO.File]::ReadAllText($path)
    $catalog = $raw | ConvertFrom-Json
    $review = if ($Code -eq 'en') { 'canonical' } else { 'draft_unreviewed' }
    if (($catalog.schema_version -isnot [int] -and $catalog.schema_version -isnot [long]) -or $catalog.schema_version -ne 1 -or
        $catalog.locale -cne $Code -or $catalog.scope -cne 'native_menu_hud_technology_launcher_panel' -or
        $catalog.review_status -cne $review -or $catalog.native_runtime_integrated -isnot [bool] -or $catalog.native_runtime_integrated) {
        throw 'Invalid launcher catalog metadata'
    }
    $keys = @('launcher.blocked_title','launcher.unsupported_game','launcher.unreadable_game','launcher.game_required',
              'launcher.invalid_package','launcher.wrong_framework','launcher.game_changed','launcher.game_running','launcher.preflight_passed')
    $result = @{}
    foreach ($key in $keys) {
        if ([regex]::Matches($raw, '(?<!\\)"' + [regex]::Escape($key) + '"\s*:').Count -ne 1) { throw 'Duplicate or missing launcher key' }
        $entry = $catalog.messages.PSObject.Properties[$key].Value
        if ($entry.text -isnot [string] -or -not $entry.text.Trim() -or
            [Text.Encoding]::UTF8.GetByteCount($entry.text) -gt 1024 -or $entry.text -match '[\x00-\x1F]' -or
            $entry.source_sha256 -isnot [string] -or $entry.source_sha256 -cnotmatch '^[0-9a-f]{64}$') { throw 'Invalid launcher text' }
        $expected = if ($key -eq 'launcher.unsupported_game') { '{build}' } elseif ($key -eq 'launcher.wrong_framework') { '{version}' } else { '' }
        $plain = $entry.text
        if ($expected) {
            if ([regex]::Matches($plain, [regex]::Escape($expected)).Count -ne 1) { throw 'Invalid launcher placeholders' }
            $plain = $plain.Replace($expected, '')
        }
        if ($plain -match '[{}]') { throw 'Invalid launcher placeholders' }
        if ($Code -eq 'en') {
            $hasher = [Security.Cryptography.SHA256]::Create()
            try { $digest = [BitConverter]::ToString($hasher.ComputeHash([Text.Encoding]::UTF8.GetBytes($entry.text))).Replace('-', '').ToLowerInvariant() }
            finally { $hasher.Dispose() }
            if ($digest -cne $entry.source_sha256) { throw 'Changed English launcher text' }
        }
        $result[$key] = $entry
    }
    return $result
}

function Get-LauncherMessage {
    param([string]$Key)
    # These two emergency strings are checked against the English catalog.
    $fallbackTitle = 'Companion Auto Summon for No Man''s Sky could not start'
    $fallbackBody = 'The mod package is incomplete or inconsistent. Extract a complete matching package and try again.'
    $code = $Language
    if (-not $code) { $code = [Globalization.CultureInfo]::CurrentUICulture.Name }
    $code = $code.Replace('_', '-').ToLowerInvariant()
    $aliases = @{'es'='es-ES'; 'pt'='pt-PT'; 'pt-br'='pt-BR'; 'pt-pt'='pt-PT'; 'zh-tw'='zh-Hant'; 'zh-hk'='zh-Hant'; 'zh-mo'='zh-Hant'; 'zh-hant'='zh-Hant'; 'zh'='zh-Hans'; 'zh-cn'='zh-Hans'; 'zh-sg'='zh-Hans'; 'zh-hans'='zh-Hans'}
    if ($aliases.ContainsKey($code)) { $code = $aliases[$code] }
    elseif ($code -like 'zh-hant-*') { $code = 'zh-Hant' }
    elseif ($code -like 'zh-hans-*') { $code = 'zh-Hans' }
    else {
        $code = $code.Split('-')[0]
        if ($aliases.ContainsKey($code)) { $code = $aliases[$code] }
        elseif ($code -notin @('en','fr','it','de','nl','ja','ko','pl','ru')) { $code = 'en' }
    }
    try {
        $english = Read-LauncherCatalog -Code 'en'
        if ($english['launcher.blocked_title'].text -cne $fallbackTitle -or $english['launcher.invalid_package'].text -cne $fallbackBody) { throw 'Emergency text differs' }
        $selected = if ($code -eq 'en') { $english } else { Read-LauncherCatalog -Code $code }
        foreach ($name in $english.Keys) {
            if ($selected[$name].source_sha256 -cne $english[$name].source_sha256 -or
                ($code -ne 'en' -and $selected[$name].text -ceq $english[$name].text)) { throw 'Stale or untranslated launcher text' }
        }
        return $selected[$Key].text.Replace('{build}', $script:CasSupportedBuild).Replace('{version}', $runtimeVersion)
    } catch { } # Corrupt translation resources cannot change the refusal decision.
    if ($Key -eq 'launcher.blocked_title') { return $fallbackTitle }
    return $fallbackBody
}

function Throw-LauncherCompatibility {
    param([string]$Key)
    $exception = [InvalidOperationException]::new($Key)
    $exception.Data['CAS.CompatibilityKey'] = $Key
    throw $exception
}

function Show-LauncherFailure {
    param([string]$Key)
    $message = Get-LauncherMessage -Key $Key
    Write-Error -Message $message -ErrorAction Continue
    if (-not $CheckOnly -and -not $NoDialog) {
        try {
            Add-Type -AssemblyName System.Windows.Forms
            [void][Windows.Forms.MessageBox]::Show($message, (Get-LauncherMessage -Key 'launcher.blocked_title'),
                [Windows.Forms.MessageBoxButtons]::OK, [Windows.Forms.MessageBoxIcon]::Warning)
        } catch { } # The console message remains available if desktop UI fails.
    }
}

function Get-GameRunning {
    try {
        $processes = @(Get-Process -ErrorAction Stop)
        return @($processes | Where-Object { $_.ProcessName -ieq 'NMS' }).Count -gt 0
    } catch {
        throw 'Could not verify whether No Man''s Sky is running. No setup or launch is permitted until process enumeration succeeds.'
    }
}

function Assert-GameClosed {
    if (Get-GameRunning) {
        Throw-LauncherCompatibility -Key 'launcher.game_running'
    }
}

function Get-PythonInfo {
    param([string]$Executable, [string[]]$Arguments = @())
    # Windows PowerShell 5.1 strips embedded double quotes in native arguments.
    # Python single-quoted literals survive that boundary unchanged.
    $probe = @'
import sys,os,struct,json,importlib.util as u,importlib.metadata as m; versions={d.metadata.get('Name','').lower():d.version for d in m.distributions()}; print(json.dumps({'exe':os.path.realpath(sys.executable),'major':sys.version_info.major,'minor':sys.version_info.minor,'bits':struct.calcsize('P')*8,'pymhf':versions.get('pymhf'),'dearpygui':versions.get('dearpygui') if u.find_spec('dearpygui') else None,'pymhflib_count':len(m.entry_points(group='pymhflib'))}))
'@
    try {
        $lines = @(& $Executable @Arguments -B -c $probe 2>$null)
        if ($LASTEXITCODE -ne 0 -or $lines.Count -ne 1) { return $null }
        $info = $lines[0] | ConvertFrom-Json
        if ($info.major -eq 3 -and $info.minor -ge 11 -and $info.minor -le 13 -and $info.bits -eq 64) {
            return $info
        }
    } catch { return $null }
    return $null
}

function Find-Python {
    $pyCommand = Get-Command py.exe -CommandType Application -ErrorAction SilentlyContinue
    if ($pyCommand) {
        foreach ($selector in @('-3.11', '-3.12', '-3.13')) {
            $info = Get-PythonInfo -Executable $pyCommand.Source -Arguments @($selector)
            if ($info) { return $info.exe }
        }
    }
    foreach ($name in @('python.exe', 'python3.exe')) {
        $command = Get-Command $name -CommandType Application -ErrorAction SilentlyContinue
        if ($command) {
            # Avoid invoking a Microsoft Store app-execution alias.
            if ($command.Source -like '*\Microsoft\WindowsApps\*') { continue }
            $info = Get-PythonInfo -Executable $command.Source
            if ($info) { return $info.exe }
        }
    }
    throw 'Install 64-bit Python 3.11, 3.12, or 3.13 from python.org, with the Python launcher or PATH option, then run this script again.'
}

function Find-SteamGameDirectories {
    $roots = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
    foreach ($registryPath in @('HKCU:\Software\Valve\Steam', 'HKLM:\SOFTWARE\WOW6432Node\Valve\Steam', 'HKLM:\SOFTWARE\Valve\Steam')) {
        $settings = Get-ItemProperty -LiteralPath $registryPath -ErrorAction SilentlyContinue
        if ($settings) {
            foreach ($propertyName in @('SteamPath', 'InstallPath')) {
                $property = $settings.PSObject.Properties[$propertyName]
                if ($property -and $property.Value -and (Test-Path -LiteralPath $property.Value -PathType Container)) {
                    [void]$roots.Add([IO.Path]::GetFullPath($property.Value))
                }
            }
        }
    }
    $programFiles86 = [Environment]::GetFolderPath('ProgramFilesX86')
    if ($programFiles86) {
        $defaultSteam = Join-Path $programFiles86 'Steam'
        if (Test-Path -LiteralPath $defaultSteam -PathType Container) { [void]$roots.Add($defaultSteam) }
    }
    $libraries = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
    foreach ($root in $roots) {
        [void]$libraries.Add($root)
        $vdfPath = Join-Path $root 'steamapps\libraryfolders.vdf'
        if (Test-Path -LiteralPath $vdfPath -PathType Leaf) {
            $vdf = [IO.File]::ReadAllText($vdfPath)
            foreach ($match in [regex]::Matches($vdf, '"path"\s*"((?:\\.|[^"\\])*)"')) {
                $library = $match.Groups[1].Value.Replace('\\', '\')
                if (Test-Path -LiteralPath $library -PathType Container) {
                    [void]$libraries.Add([IO.Path]::GetFullPath($library))
                }
            }
        }
    }
    foreach ($library in $libraries) {
        $appManifest = Join-Path $library 'steamapps\appmanifest_275850.acf'
        if (-not (Test-Path -LiteralPath $appManifest -PathType Leaf)) { continue }
        $acf = [IO.File]::ReadAllText($appManifest)
        if ($acf -notmatch '"appid"\s*"275850"') { continue }
        $installMatch = [regex]::Match($acf, '"installdir"\s*"([^"\\/]+)"')
        if (-not $installMatch.Success) { continue }
        $installName = $installMatch.Groups[1].Value
        if ($installName -eq '.' -or $installName -eq '..') { continue }
        $directory = Join-Path (Join-Path $library 'steamapps\common') $installName
        if (Test-Path -LiteralPath (Join-Path $directory 'Binaries\NMS.exe') -PathType Leaf) {
            [IO.Path]::GetFullPath($directory)
        }
    }
}

$setupLease = $null
try {
    # This must precede runtime creation, dependency installation, and launch.
    if (-not $CheckOnly) {
        # Handle lifetime is the lease: never acquire ownership or wait.
        $createdNew = $false
        $setupLease = [System.Threading.Mutex]::new($false, 'Local\CompanionAutoSummon.Setup.v1', [ref]$createdNew)
        if (-not $createdNew) { throw 'Another Companion Auto Summon setup or launcher is active. Use its existing window or wait for it to exit.' }
        Assert-GameClosed
    }
    if (-not $env:LOCALAPPDATA) { throw 'LOCALAPPDATA is unavailable. Run this launcher from your normal Windows account.' }
    $manifestPath = Join-Path $PSScriptRoot 'manifest.json'
    $modPath = Join-Path $PSScriptRoot 'CompanionAutoSummon.py'
    $bootstrapPath = Join-Path $PSScriptRoot 'Launch-CompanionAutoSummon.py'
    if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf) -or -not (Test-Path -LiteralPath $modPath -PathType Leaf) -or -not (Test-Path -LiteralPath $bootstrapPath -PathType Leaf)) {
        Throw-LauncherCompatibility -Key 'launcher.invalid_package'
    }
    $manifest = [IO.File]::ReadAllText($manifestPath) | ConvertFrom-Json
    if ($manifest.framework -ne $runtimeRequirement) { throw 'The manifest requires a different runtime. Download a complete matching Companion Auto Summon package.' }
    foreach ($scriptName in @('CompanionAutoSummon.py', 'Launch-CompanionAutoSummon.py', 'cas_compatibility.py', 'compatibility.json')) {
        $scriptEntries = @($manifest.files | Where-Object { $_.path -ceq $scriptName })
        if ($scriptEntries.Count -ne 1 -or $scriptEntries[0].sha256 -notmatch '^[0-9a-fA-F]{64}$') { Throw-LauncherCompatibility -Key 'launcher.invalid_package' }
        if (-not (Test-Path -LiteralPath (Join-Path $PSScriptRoot $scriptName) -PathType Leaf) -or
            (Get-FileHash -LiteralPath (Join-Path $PSScriptRoot $scriptName) -Algorithm SHA256).Hash -ine $scriptEntries[0].sha256) {
            Throw-LauncherCompatibility -Key 'launcher.invalid_package'
        }
    }
    $profile = [IO.File]::ReadAllText((Join-Path $PSScriptRoot 'compatibility.json')) | ConvertFrom-Json
    $expectedGameHash = $profile.exe_sha256
    if (($profile.schema_version -isnot [int] -and $profile.schema_version -isnot [long]) -or
        $profile.schema_version -ne 1 -or $expectedGameHash -notmatch '^[0-9a-f]{64}$' -or
        $profile.framework_version -ne $runtimeVersion -or $profile.steam_build -cne $manifest.steam_build -or
        $expectedGameHash -cne $manifest.supported_nms_exe_sha256) { Throw-LauncherCompatibility -Key 'launcher.invalid_package' }
    $script:CasSupportedBuild = "$($profile.game_release) (Steam $($profile.steam_build))"
    if ($GameDirectory) {
        $directories = @([IO.Path]::GetFullPath($GameDirectory))
    } else {
        $directories = @(Find-SteamGameDirectories | Sort-Object -Unique)
    }
    if ($directories.Count -eq 0) {
        Throw-LauncherCompatibility -Key 'launcher.game_required'
    }
    $matchingGames = @()
    foreach ($directory in $directories) {
        $exePath = Join-Path $directory 'Binaries\NMS.exe'
        try {
            if (-not (Test-Path -LiteralPath $exePath -PathType Leaf)) { Throw-LauncherCompatibility -Key 'launcher.unreadable_game' }
            if ((Get-FileHash -LiteralPath $exePath -Algorithm SHA256).Hash -ieq $expectedGameHash) { $matchingGames += $directory }
        } catch { Throw-LauncherCompatibility -Key 'launcher.unreadable_game' }
    }
    if ($matchingGames.Count -eq 0) { Throw-LauncherCompatibility -Key 'launcher.unsupported_game' }
    if ($matchingGames.Count -ne 1) { Throw-LauncherCompatibility -Key 'launcher.game_required' }
    Write-Host "Validated game: $($matchingGames[0])"
    if (-not $CheckOnly) { Write-Host 'Companion Auto Summon is experimental. Start Steam with the account that owns this installation.' }

    if (-not $CheckOnly) { Assert-GameClosed }
    # Reuse the legacy runtime location; virtual environments are not moved.
    $runtimeDirectory = Join-Path $env:LOCALAPPDATA "NMS-AutoPet\runtime-$runtimeVersion"
    $runtimePython = Join-Path $runtimeDirectory 'Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $runtimePython -PathType Leaf)) {
        if ($CheckOnly) { throw 'The existing Companion Auto Summon runtime is missing. Close NMS, then run this launcher without -CheckOnly to create it.' }
        $basePython = Find-Python
        Assert-GameClosed
        Write-Host "Creating isolated Python runtime: $runtimeDirectory"
        & $basePython -m venv $runtimeDirectory
        if ($LASTEXITCODE -ne 0) { throw 'Could not create the Companion Auto Summon Python environment.' }
    }
    $runtimeInfo = Get-PythonInfo -Executable $runtimePython
    if (-not $runtimeInfo) { throw "The isolated runtime is damaged or uses an unsupported Python version: $runtimeDirectory. Close NMS before repairing or recreating it; CheckOnly never repairs files." }
    if (($runtimeInfo.pymhflib_count -isnot [int] -and $runtimeInfo.pymhflib_count -isnot [long]) -or $runtimeInfo.pymhflib_count -ne 0) {
        Throw-LauncherCompatibility -Key 'launcher.invalid_package'
    }
    # Resolve Windows package/file virtualization before handing paths to NMS,
    # which is launched by Steam outside this launcher's filesystem context.
    $runtimePython = $runtimeInfo.exe
    if ($runtimeInfo.pymhf -ne $runtimeVersion -or -not $runtimeInfo.dearpygui) {
        if ($CheckOnly) { throw 'The existing runtime requires pyMHF 0.2.4 and Dear PyGui. Close NMS, then run this launcher without -CheckOnly to repair dependencies.' }
        Assert-GameClosed
        Write-Host "Installing pyMHF $runtimeVersion and its GUI dependencies into the isolated runtime..."
        & $runtimePython -m pip --disable-pip-version-check install $runtimeRequirement
        if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed. Check the pip error above and your internet connection.' }
        $runtimeInfo = Get-PythonInfo -Executable $runtimePython
        if (-not $runtimeInfo -or $runtimeInfo.pymhf -ne $runtimeVersion -or -not $runtimeInfo.dearpygui) { throw 'The installed pyMHF version and Dear PyGui dependency could not be verified.' }
    }
    if (($runtimeInfo.pymhflib_count -isnot [int] -and $runtimeInfo.pymhflib_count -isnot [long]) -or $runtimeInfo.pymhflib_count -ne 0) {
        Throw-LauncherCompatibility -Key 'launcher.invalid_package'
    }
    if ($CheckOnly) {
        $gameRunning = Get-GameRunning
        Write-Host "Validated exact game build: $($manifest.steam_build)"
        Write-Host "Validated existing runtime: Python $($runtimeInfo.major).$($runtimeInfo.minor) x$($runtimeInfo.bits), pyMHF $($runtimeInfo.pymhf), Dear PyGui $($runtimeInfo.dearpygui)"
        Write-Host "No Man's Sky running: $gameRunning"
        Write-Host 'CheckOnly completed. No setup, asset staging, game start or hook registration was performed. This does not verify in-game behavior.'
        return
    }
    Assert-GameClosed
    # Steam may have updated the executable while dependencies were installing.
    $verifiedExe = Join-Path $matchingGames[0] 'Binaries\NMS.exe'
    try { $finalHash = (Get-FileHash -LiteralPath $verifiedExe -Algorithm SHA256).Hash }
    catch { Throw-LauncherCompatibility -Key 'launcher.unreadable_game' }
    if ($finalHash -ine $expectedGameHash) { Throw-LauncherCompatibility -Key 'launcher.game_changed' }
    Write-Host 'Starting Companion Auto Summon through pyMHF and Steam. Keep this window open.'
    Push-Location -LiteralPath $PSScriptRoot
    try {
        Assert-GameClosed
        $hostOptions = @('--game-directory', $matchingGames[0])
        if ($Language) { $hostOptions += @('--language', $Language) }
        if ($NoDialog) { $hostOptions += '--no-dialog' }
        & $runtimePython $bootstrapPath $modPath @hostOptions
        if ($LASTEXITCODE -ne 0) { throw "pyMHF exited with code $LASTEXITCODE. See its output above." }
    } finally {
        Pop-Location
    }
} catch {
    if ($_.Exception.Data.Contains('CAS.CompatibilityKey')) {
        Show-LauncherFailure -Key $_.Exception.Data['CAS.CompatibilityKey']
    } else { Write-Error -Message $_.Exception.Message -ErrorAction Continue }
    exit 1
} finally {
    if ($null -ne $setupLease) { $setupLease.Dispose() }
}
