#requires -Version 5.1
<#
Starts the packaged experimental Companion Auto Summon mod for the supported Windows Steam build.
Run only after closing No Man's Sky. Dependencies stay in a separate user runtime.
Example: .\Start-CompanionAutoSummon.ps1 -GameDirectory 'D:\SteamLibrary\steamapps\common\No Man''s Sky'
#>
[CmdletBinding()]
param([string]$GameDirectory)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$runtimeVersion = '0.2.4'
$runtimeRequirement = "pymhf[gui]==$runtimeVersion"

function Assert-GameClosed {
    if (Get-Process -Name NMS -ErrorAction SilentlyContinue) {
        throw 'No Man''s Sky is running. Close it before starting Companion Auto Summon; this launcher will not attach to an existing game.'
    }
}

function Get-PythonInfo {
    param([string]$Executable, [string[]]$Arguments = @())
    $probe = 'import sys,os,struct,json,importlib.util as u,importlib.metadata as m; versions={d.metadata.get("Name","").lower():d.version for d in m.distributions()}; print(json.dumps({"exe":os.path.realpath(sys.executable),"major":sys.version_info.major,"minor":sys.version_info.minor,"bits":struct.calcsize("P")*8,"pymhf":versions.get("pymhf"),"dearpygui":versions.get("dearpygui") if u.find_spec("dearpygui") else None}))'
    try {
        $lines = @(& $Executable @Arguments -c $probe 2>$null)
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

try {
    # This must precede runtime creation, dependency installation, and launch.
    Assert-GameClosed
    if (-not $env:LOCALAPPDATA) { throw 'LOCALAPPDATA is unavailable. Run this launcher from your normal Windows account.' }
    $manifestPath = Join-Path $PSScriptRoot 'manifest.json'
    $modPath = Join-Path $PSScriptRoot 'CompanionAutoSummon.py'
    $bootstrapPath = Join-Path $PSScriptRoot 'Launch-CompanionAutoSummon.py'
    if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf) -or -not (Test-Path -LiteralPath $modPath -PathType Leaf) -or -not (Test-Path -LiteralPath $bootstrapPath -PathType Leaf)) {
        throw 'The Companion Auto Summon package is incomplete. Extract the entire ZIP before running this launcher.'
    }
    $manifest = [IO.File]::ReadAllText($manifestPath) | ConvertFrom-Json
    if ($manifest.framework -ne $runtimeRequirement) { throw 'The manifest requires a different runtime. Download a complete matching Companion Auto Summon package.' }
    foreach ($scriptName in @('CompanionAutoSummon.py', 'Launch-CompanionAutoSummon.py')) {
        $scriptEntries = @($manifest.files | Where-Object { $_.path -ceq $scriptName })
        if ($scriptEntries.Count -ne 1 -or $scriptEntries[0].sha256 -notmatch '^[0-9a-fA-F]{64}$') { throw "The manifest has no valid $scriptName checksum." }
        if ((Get-FileHash -LiteralPath (Join-Path $PSScriptRoot $scriptName) -Algorithm SHA256).Hash -ine $scriptEntries[0].sha256) {
            throw "$scriptName does not match the package manifest. Re-extract an intact package before launching."
        }
    }
    $expectedGameHash = $manifest.supported_nms_exe_sha256
    if ($expectedGameHash -notmatch '^[0-9a-fA-F]{64}$') { throw 'The package has no valid supported-game checksum.' }
    if ($GameDirectory) {
        $directories = @([IO.Path]::GetFullPath($GameDirectory))
    } else {
        $directories = @(Find-SteamGameDirectories | Sort-Object -Unique)
    }
    if ($directories.Count -eq 0) {
        throw 'No Steam installation of No Man''s Sky was found. Run again with -GameDirectory pointing to its installation folder.'
    }
    $matchingGames = @()
    foreach ($directory in $directories) {
        $exePath = Join-Path $directory 'Binaries\NMS.exe'
        if ((Test-Path -LiteralPath $exePath -PathType Leaf) -and (Get-FileHash -LiteralPath $exePath -Algorithm SHA256).Hash -ieq $expectedGameHash) {
            $matchingGames += $directory
        }
    }
    if ($matchingGames.Count -eq 0) { throw "The game executable is unsupported. This package requires the exact Steam build $($manifest.steam_build) listed in manifest.json. No mod was launched." }
    if ($matchingGames.Count -ne 1) { throw 'Multiple supported installations were found. Select the active Steam installation with -GameDirectory.' }
    Write-Host "Validated game: $($matchingGames[0])"
    Write-Host 'Companion Auto Summon is experimental. Start Steam with the account that owns this installation.'

    Assert-GameClosed
    # Reuse the legacy runtime location; virtual environments are not moved.
    $runtimeDirectory = Join-Path $env:LOCALAPPDATA "NMS-AutoPet\runtime-$runtimeVersion"
    $runtimePython = Join-Path $runtimeDirectory 'Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $runtimePython -PathType Leaf)) {
        $basePython = Find-Python
        Assert-GameClosed
        Write-Host "Creating isolated Python runtime: $runtimeDirectory"
        & $basePython -m venv $runtimeDirectory
        if ($LASTEXITCODE -ne 0) { throw 'Could not create the Companion Auto Summon Python environment.' }
    }
    $runtimeInfo = Get-PythonInfo -Executable $runtimePython
    if (-not $runtimeInfo) { throw "The isolated runtime is damaged or uses an unsupported Python version: $runtimeDirectory. Rename that folder and try again." }
    # Resolve Windows package/file virtualization before handing paths to NMS,
    # which is launched by Steam outside this launcher's filesystem context.
    $runtimePython = $runtimeInfo.exe
    if ($runtimeInfo.pymhf -ne $runtimeVersion -or -not $runtimeInfo.dearpygui) {
        Assert-GameClosed
        Write-Host "Installing pyMHF $runtimeVersion and its GUI dependencies into the isolated runtime..."
        & $runtimePython -m pip --disable-pip-version-check install $runtimeRequirement
        if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed. Check the pip error above and your internet connection.' }
        $runtimeInfo = Get-PythonInfo -Executable $runtimePython
        if (-not $runtimeInfo -or $runtimeInfo.pymhf -ne $runtimeVersion -or -not $runtimeInfo.dearpygui) { throw 'The installed pyMHF version and Dear PyGui dependency could not be verified.' }
    }
    Assert-GameClosed
    # Steam may have updated the executable while dependencies were installing.
    $verifiedExe = Join-Path $matchingGames[0] 'Binaries\NMS.exe'
    if ((Get-FileHash -LiteralPath $verifiedExe -Algorithm SHA256).Hash -ine $expectedGameHash) { throw 'The game executable changed during setup. Companion Auto Summon was not launched.' }
    Write-Host 'Starting Companion Auto Summon through pyMHF and Steam. Keep this window open.'
    Push-Location -LiteralPath $PSScriptRoot
    try {
        Assert-GameClosed
        & $runtimePython $bootstrapPath $modPath
        if ($LASTEXITCODE -ne 0) { throw "pyMHF exited with code $LASTEXITCODE. See its output above." }
    } finally {
        Pop-Location
    }
} catch {
    Write-Error -Message $_.Exception.Message -ErrorAction Continue
    exit 1
}
