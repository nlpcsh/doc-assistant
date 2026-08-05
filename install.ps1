param(
    [string]$VenvPath = "$PSScriptRoot/.venv"
)

$ErrorActionPreference = 'Stop'

function Require-Command {
    param([string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "$Name is required but was not found on PATH."
    }
}

$pythonCommand = $null
if (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCommand = 'py'
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCommand = 'python'
} else {
    throw 'Python 3 is required but was not found on PATH.'
}

$pythonVersionOutput = & $pythonCommand -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
if ([version]$pythonVersionOutput -lt [version]'3.10') {
    throw 'Python 3.10 or newer is required.'
}

Write-Host "Creating virtual environment at $VenvPath"
& $pythonCommand -m venv $VenvPath

$activateScript = Join-Path $VenvPath 'Scripts/Activate.ps1'
if (-not (Test-Path $activateScript)) {
    throw "Virtual environment activation script not found at $activateScript"
}

. $activateScript

python -m pip install --upgrade pip
python -m pip install -r (Join-Path $PSScriptRoot 'requirements.txt')

$desktopPath = [Environment]::GetFolderPath('Desktop')
if ($desktopPath) {
    $shortcutPath = Join-Path $desktopPath 'Doc Assistant.lnk'
    $wshell = New-Object -ComObject WScript.Shell
    $shortcut = $wshell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = (Join-Path $VenvPath 'Scripts/python.exe')
    $shortcut.Arguments = '"{0}"' -f (Join-Path $PSScriptRoot 'main.py')
    $shortcut.WorkingDirectory = $PSScriptRoot
    $shortcut.IconLocation = (Join-Path $VenvPath 'Scripts/python.exe')
    $shortcut.Description = 'Launch Doc Assistant'
    $shortcut.Save()
}

Write-Host 'Installation complete.'
Write-Host "Activate the environment with: .\$($VenvPath.Replace('/', '\'))\\Scripts\\Activate.ps1"
Write-Host "Run the app with: python .\\main.py"
Write-Host 'Desktop shortcut created on the Windows Desktop.'

if (Get-Command soffice -ErrorAction SilentlyContinue) {
    Write-Host 'LibreOffice detected. DOCX-to-PDF conversion is available.'
} else {
    Write-Host 'LibreOffice was not found in PATH. Install it to enable DOCX-to-PDF conversion.'
    Write-Host 'You can install LibreOffice from https://www.libreoffice.org/'
}
