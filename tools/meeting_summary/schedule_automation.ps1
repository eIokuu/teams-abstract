<#
.SYNOPSIS Teams meeting auto-summary schedule script
#>

param([switch]$Setup,[switch]$Remove)
$sp = Split-Path -Parent $MyInvocation.MyCommand.Path
$py = Join-Path $sp "run.py"
$exe = (Get-Command python).Source

if (-not $Setup -and -not $Remove) {
    & $exe $py --watch
    exit 0
}

if ($Setup) {
    $tn = "SAM3_MeetingSummary"
    $tg = New-ScheduledTaskTrigger -Daily -At "09:00" -RepetitionInterval (New-TimeSpan -Minutes 30) -RepetitionDuration (New-TimeSpan -Days 365)
    $inner = "-NoProfile -WindowStyle Hidden -File ""$sp\schedule_automation.ps1"""
    $ac = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $inner
    $pr = New-ScheduledTaskPrincipal -UserId SYSTEM -LogonType ServiceAccount -RunLevel Highest
    Register-ScheduledTask -TaskName $tn -Action $ac -Trigger $tg -Principal $pr -Force
    Write-Host "OK: Task $tn registered"
}

if ($Remove) {
    Unregister-ScheduledTask -TaskName SAM3_MeetingSummary -Confirm:$false
}
