#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${1:-$ROOT_DIR/.venv}"
PYTHON_BIN="${PYTHON_BIN:-}"
ICON_FILE="$ROOT_DIR/icon.svg"

if [ -z "$PYTHON_BIN" ]; then
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
  elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
  else
    echo "Python 3 is required but was not found on PATH." >&2
    exit 1
  fi
fi

if ! "$PYTHON_BIN" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >/dev/null 2>&1; then
  echo "Python 3.10 or newer is required." >&2
  exit 1
fi

echo "Creating virtual environment at $VENV_DIR"
"$PYTHON_BIN" -m venv "$VENV_DIR"

# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

python -m pip install --upgrade pip
python -m pip install -r "$ROOT_DIR/requirements.txt"

ENTRY_FILE="$(mktemp)"
cat > "$ENTRY_FILE" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Doc Assistant
Comment=Generate administrative documents
Exec=$VENV_DIR/bin/python "$ROOT_DIR/main.py"
Icon=$ICON_FILE
Path=$ROOT_DIR
Terminal=false
Categories=Office;
StartupNotify=true
EOF

chmod +x "$ENTRY_FILE"
mkdir -p "$HOME/.local/share/applications"
cp "$ENTRY_FILE" "$HOME/.local/share/applications/doc-assistant.desktop"

if [ -d "$HOME/Desktop" ]; then
  cp "$ENTRY_FILE" "$HOME/Desktop/doc-assistant.desktop"
fi

rm -f "$ENTRY_FILE"

echo "Installation complete."
echo "Activate the environment with: source $VENV_DIR/bin/activate"
echo "Run the app with: python $ROOT_DIR/main.py"
echo "Desktop launcher created in ~/.local/share/applications and on your desktop if available."

if command -v libreoffice >/dev/null 2>&1; then
  echo "LibreOffice detected. DOCX-to-PDF conversion is available."
else
  echo "LibreOffice was not found in PATH. Install it to enable DOCX-to-PDF conversion."
  echo "On Ubuntu/Debian, try: sudo apt-get update && sudo apt-get install -y libreoffice"
fi
