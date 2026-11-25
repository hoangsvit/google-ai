[CmdletBinding()]
param(
    [switch]$ProbeDevices,
    [string]$AdbPath,
    [switch]$FunctionsOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-DeviceSummary {
    param([AllowEmptyString()][string]$Output)
    $summary = [ordered]@{ Online = 0; Unauthorized = 0; Offline = 0; Other = 0 }
    $header = $false
    foreach ($line in ($Output -split '\r?\n')) {
        if ($line.Trim() -eq 'List of devices attached') {
            $header = $true
            continue
        }
        if (-not $header -or [string]::IsNullOrWhiteSpace($line)) { continue }
        if ($line -match '^\S+\s+(\S+)(?:\s+.*)?$') {
            switch ($Matches[1]) {
                'device' { $summary.Online++ }
                'unauthorized' { $summary.Unauthorized++ }
                'offline' { $summary.Offline++ }
                default { $summary.Other++ }
            }
        }
    }
    if (-not $header) { throw 'ADB did not return a recognized device-list header.' }
    [pscustomobject]$summary
}

function Find-Adb {
    $candidates = @()
    if ($PSScriptRoot) {
        $candidates += Join-Path $PSScriptRoot 'platform-tools\adb.exe'
    }
    if ($env:LOCALAPPDATA) {
        $candidates += Join-Path $env:LOCALAPPDATA 'Android\Sdk\platform-tools\adb.exe'
    }
    if ($env:ANDROID_HOME) {
        $candidates += Join-Path $env:ANDROID_HOME 'platform-tools\adb.exe'
    }
    if ($env:ANDROID_SDK_ROOT) {
        $candidates += Join-Path $env:ANDROID_SDK_ROOT 'platform-tools\adb.exe'
    }
    $command = Get-Command adb.exe -CommandType Application -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($command) { $candidates += $command.Source }
    @($candidates | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } |
        Select-Object -Unique)
}

function Invoke-DeviceProbe {
    param([Parameter(Mandatory)][string]$Path)
    if (-not [System.IO.Path]::IsPathRooted($Path) -or
        [System.IO.Path]::GetFileName($Path) -ine 'adb.exe' -or
        -not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw 'Provide the absolute path to a trusted adb.exe.'
    }
    $info = New-Object System.Diagnostics.ProcessStartInfo
    $info.FileName = (Resolve-Path -LiteralPath $Path).ProviderPath
    $info.Arguments = 'devices'
    $info.UseShellExecute = $false
    $info.CreateNoWindow = $true
    $info.RedirectStandardOutput = $true
    $info.RedirectStandardError = $true
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $info
    try {
        if (-not $process.Start()) { throw 'ADB could not start.' }
        $stdout = $process.StandardOutput.ReadToEndAsync()
        $stderr = $process.StandardError.ReadToEndAsync()
        if (-not $process.WaitForExit(10000)) {
            try { $process.Kill() } catch {}
            throw 'ADB device probe timed out.'
        }
        # Bound output-drain time even if a spawned process inherits a pipe.
        if (-not $stdout.Wait(2000) -or -not $stderr.Wait(2000)) {
            throw 'ADB output did not close in time.'
        }
        if ($process.ExitCode -ne 0) { throw 'ADB device probe failed.' }
        Get-DeviceSummary -Output $stdout.Result
    } finally {
        $process.Dispose()
    }
}

function Invoke-PortableDiagnostics {
    param([switch]$Probe, [string]$Path)
    Write-Host 'ePlus AI Toolkit - Portable Diagnostics (experimental)'
    Write-Host '---------------------------------------------------'
    Write-Host ("PowerShell: {0}" -f $PSVersionTable.PSVersion)
    Write-Host ("64-bit Windows host: {0}" -f [Environment]::Is64BitOperatingSystem)
    $python = Get-Command python.exe -CommandType Application -ErrorAction SilentlyContinue
    Write-Host ("Python command found (not executed): {0}" -f [bool]$python)
    $adb = @(Find-Adb)
    Write-Host ("ADB candidates found (not executed): {0}" -f $adb.Count)
    if ($adb.Count -eq 0) {
        Write-Host 'Install official Android SDK Platform-Tools or place them under platform-tools/.'
        Write-Host 'https://developer.android.com/tools/releases/platform-tools'
    }
    if (-not $Probe) {
        Write-Host 'Host inspection complete. No Android commands were executed.'
        Write-Host 'See README.md for the optional device-count check.'
        return
    }
    if ([string]::IsNullOrWhiteSpace($Path)) {
        throw 'The optional probe requires -AdbPath pointing to a trusted adb.exe.'
    }
    Write-Host 'Running the explicit ADB devices probe; this may start the local ADB server.'
    $summary = Invoke-DeviceProbe -Path $Path
    Write-Host ("Online: {0}; Unauthorized: {1}; Offline: {2}; Other: {3}" -f
        $summary.Online, $summary.Unauthorized, $summary.Offline, $summary.Other)
    Write-Host 'Device identifiers are not displayed or saved.'
}

if (-not $FunctionsOnly) {
    try {
        Invoke-PortableDiagnostics -Probe:$ProbeDevices -Path $AdbPath
    } catch {
        # Do not print raw subprocess errors, paths, or device identifiers.
        Write-Host 'Diagnostics could not complete. Check the trusted ADB path, permissions, and connection.'
        exit 1
    }
}
