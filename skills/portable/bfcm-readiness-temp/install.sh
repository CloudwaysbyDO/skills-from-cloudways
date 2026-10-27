#!/usr/bin/env bash
# Install the bfcm-readiness skill into whichever agent runtime is present.
#
#   ./install.sh              detect the runtime and install
#   ./install.sh hermes       force Hermes
#   ./install.sh openclaw     force OpenClaw
#   ./install.sh --dest DIR   install into an explicit skills root
#
# Safe to re run. Installing over an existing copy replaces it.

set -euo pipefail

SKILL_NAME="bfcm-readiness"
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -f "$SRC/SKILL.md" ]; then
  echo "SKILL.md not found next to this script. Run it from inside the skill directory." >&2
  exit 1
fi

DEST_ROOT=""
TARGET="${1:-auto}"

if [ "$TARGET" = "--dest" ]; then
  DEST_ROOT="${2:?--dest needs a directory}"
  RUNTIME="explicit"
fi

detect() {
  if [ -d "$HOME/.hermes" ] && [ -d "$HOME/.openclaw" ]; then
    echo "Both ~/.hermes and ~/.openclaw exist. Pass hermes or openclaw explicitly." >&2
    exit 1
  fi
  if [ -d "$HOME/.hermes" ]; then echo hermes; return; fi
  if [ -d "$HOME/.openclaw" ]; then echo openclaw; return; fi
  echo "Neither ~/.hermes nor ~/.openclaw found. Pass a runtime or use --dest." >&2
  exit 1
}

if [ -z "$DEST_ROOT" ]; then
  RUNTIME="$TARGET"
  [ "$RUNTIME" = "auto" ] && RUNTIME="$(detect)"

  case "$RUNTIME" in
    hermes)
      # Hermes reads every skill under ~/.hermes/skills, category subfolders included.
      DEST_ROOT="$HOME/.hermes/skills/ecommerce"
      ;;
    openclaw)
      # Prefer the workspace root when it exists, else the personal root shared across agents.
      if [ -d "$HOME/.openclaw/workspace/skills" ]; then
        DEST_ROOT="$HOME/.openclaw/workspace/skills"
      else
        DEST_ROOT="$HOME/.openclaw/skills"
      fi
      ;;
    *)
      echo "Unknown runtime '$RUNTIME'. Use hermes, openclaw, or --dest DIR." >&2
      exit 1
      ;;
  esac
fi

DEST="$DEST_ROOT/$SKILL_NAME"
mkdir -p "$DEST_ROOT"
rm -rf "$DEST"
mkdir -p "$DEST"

cp "$SRC/SKILL.md" "$DEST/"
cp -R "$SRC/references" "$DEST/"
cp -R "$SRC/scripts" "$DEST/"
chmod +x "$DEST/scripts/freeze_window.py"

echo "Installed $SKILL_NAME to $DEST"

if command -v python3 >/dev/null 2>&1; then
  echo "Freeze window script check:"
  python3 "$DEST/scripts/freeze_window.py" | sed 's/^/  /'
else
  echo "python3 not found. The skill still works, it will read the table instead."
fi

echo
case "${RUNTIME:-explicit}" in
  hermes)
    echo "Verify   hermes skills list | grep $SKILL_NAME"
    echo "Refresh  start a new session, or /reset in the current one"
    echo "Invoke   /$SKILL_NAME audit my WooCommerce fleet for BFCM"
    ;;
  openclaw)
    echo "Verify   openclaw skills list | grep $SKILL_NAME"
    echo "Refresh  the file watcher picks it up, else openclaw gateway restart"
    echo "Invoke   /$SKILL_NAME audit my WooCommerce fleet for BFCM"
    ;;
  *)
    echo "Installed to an explicit path. Restart or refresh your runtime to pick it up."
    ;;
esac
