# Install the video-studio skills and agents for your user (Windows PowerShell).
# Usage:  powershell -ExecutionPolicy Bypass -File video-studio\install.ps1 [-Force]
param([switch]$Force)
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$dest = if ($env:CLAUDE_HOME) { $env:CLAUDE_HOME } else { Join-Path $HOME ".claude" }
New-Item -ItemType Directory -Force -Path (Join-Path $dest "skills"), (Join-Path $dest "agents") | Out-Null
$copied = 0; $skipped = 0

foreach ($src in Get-ChildItem -Directory (Join-Path $here "skills")) {
  $target = Join-Path $dest ("skills\" + $src.Name)
  if ((Test-Path $target) -and -not $Force) { Write-Host "SKIP  skills/$($src.Name) (exists; use -Force to overwrite)"; $skipped++; continue }
  if (Test-Path $target) { Remove-Item -Recurse -Force $target }
  Copy-Item -Recurse $src.FullName $target
  Get-ChildItem $target -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
  Write-Host "OK    skills/$($src.Name)"; $copied++
}
foreach ($src in Get-ChildItem -File (Join-Path $here "agents") -Filter *.md) {
  $target = Join-Path $dest ("agents\" + $src.Name)
  if ((Test-Path $target) -and -not $Force) { Write-Host "SKIP  agents/$($src.Name) (exists; use -Force to overwrite)"; $skipped++; continue }
  Copy-Item $src.FullName $target -Force
  Write-Host "OK    agents/$($src.Name)"; $copied++
}
Write-Host "Done: $copied installed, $skipped skipped, into $dest"
Write-Host 'Start a NEW Claude Code session, then describe the video you want.'
