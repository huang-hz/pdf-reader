# install.ps1 — link paseoweb4scholar skills into Claude Code and Codex.
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$targets = @(
    (Join-Path $HOME ".claude\skills"),
    (Join-Path $HOME ".codex\skills")
)

Get-ChildItem (Join-Path $root "skills") -Directory | ForEach-Object {
    $name = $_.Name
    $source = $_.FullName
    foreach ($base in $targets) {
        New-Item -ItemType Directory -Force -Path $base | Out-Null
        $link = Join-Path $base $name
        if (Test-Path $link) {
            $item = Get-Item $link -Force
            if ($item.LinkType) {
                # Remove the link itself, never the target.
                [System.IO.Directory]::Delete($link)
            } else {
                Write-Warning "$link is a real directory; leaving it untouched."
                continue
            }
        }
        try {
            New-Item -ItemType SymbolicLink -Path $link -Target $source -ErrorAction Stop | Out-Null
        } catch [System.UnauthorizedAccessException] {
            # Symlinks need elevation or Developer Mode; junctions do not.
            New-Item -ItemType Junction -Path $link -Target $source | Out-Null
        }
        Write-Host "linked $link -> $source"
    }
}

Write-Host ""
Write-Host "Userscript: import userscripts\paseo-web-latex-renderer\paseo-web-latex-renderer.user.js into Tampermonkey."
