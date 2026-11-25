$ErrorActionPreference = 'Stop'
$script = Join-Path $PSScriptRoot '../tools/windows/portable/diagnose.ps1'
. $script -FunctionsOnly

function Assert-Equal($Actual, $Expected) {
    if ($Actual -ne $Expected) { throw "Expected $Expected, got $Actual" }
}

$sample = @'
* daemon started successfully
List of devices attached
synthetic-serial-1 device
synthetic-serial-2 unauthorized
synthetic-serial-3 offline
synthetic-serial-4 recovery
'@
$result = Get-DeviceSummary -Output $sample
Assert-Equal $result.Online 1
Assert-Equal $result.Unauthorized 1
Assert-Equal $result.Offline 1
Assert-Equal $result.Other 1
Assert-Equal ((Get-DeviceSummary -Output "List of devices attached").Online) 0
if (($result | ConvertTo-Json) -match 'synthetic-serial') { throw 'Serial leak' }

$failed = $false
try { Get-DeviceSummary -Output 'unexpected output' | Out-Null } catch { $failed = $true }
if (-not $failed) { throw 'Malformed device list accepted' }

# Mock all host discovery and fail if default inspection attempts ADB execution.
function Find-Adb { @('C:\fake\adb.exe') }
function Invoke-DeviceProbe { throw 'Unexpected probe during host-only inspection' }
Invoke-PortableDiagnostics
$failed = $false
try { Invoke-PortableDiagnostics -Probe } catch { $failed = $true }
if (-not $failed) { throw 'Probe without explicit ADB path was accepted' }
Write-Host 'Portable diagnostics offline checks passed.'
