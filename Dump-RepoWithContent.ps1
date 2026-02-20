param(
    [Parameter(Mandatory=$true)]
    [string]$RootPath,

    [Parameter(Mandatory=$true)]
    [string[]]$Extensions,

    [Parameter(Mandatory=$true)]
    [string]$OutputFile
)

# Resolve full paths
$RootPath = Resolve-Path $RootPath
$OutputFile = Resolve-Path -Path (Split-Path $OutputFile -Parent) -ErrorAction SilentlyContinue `
    ? (Resolve-Path $OutputFile) `
    : $OutputFile

# Overwrite output file
"" | Out-File -FilePath $OutputFile -Encoding UTF8

Write-Host "Scanning: $RootPath"
Write-Host "Writing output to: $OutputFile"

# Get all files and directories
$items = Get-ChildItem -Path $RootPath -Recurse -Force

foreach ($item in $items) {

    # Always dump folder/file path
    Add-Content -Path $OutputFile -Value $item.FullName

    if ($item.PSIsContainer) {
        continue
    }

    # Check extension match
    if ($Extensions -contains $item.Extension) {

        # Check if git ignores this file
        $relativePath = Resolve-Path $item.FullName -Relative
        $gitCheck = git -C $RootPath check-ignore $relativePath 2>$null

        if (-not $gitCheck) {

            Add-Content -Path $OutputFile -Value "----- BEGIN FILE: $($item.FullName) -----"
            try {
                Get-Content $item.FullName -Raw -ErrorAction Stop |
                    Add-Content -Path $OutputFile
            }
            catch {
                Add-Content -Path $OutputFile -Value "[Error reading file]"
            }
            Add-Content -Path $OutputFile -Value "----- END FILE: $($item.FullName) -----"
            Add-Content -Path $OutputFile -Value ""
        }
    }
}

Write-Host "Done."