#!/usr/bin/env bash
set -euo pipefail

SELF_USER="$(id -un)"
if [[ "$SELF_USER" != "apple" ]]; then
  echo "This script is intended to run from the MacBook primary machine as user apple." >&2
  exit 1
fi

HOSTNAME_VALUE="beacon.lbeaconcc.icu"
PORT_VALUE="18090"
TUNNEL_ID="7626a1f7-08f2-4b63-86f0-64a3bddca0b8"
PEER_USER="chenmingyao"
PEER_HOST="100.110.167.79"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/id_ed25519}"
SOURCE_DIR="${BEACON_PUBLIC_BOARD_SOURCE:-$HOME/.beacon/runtime-ledger/pocketbase/pb_public/}"
REMOTE_ROOT="${BEACON_PUBLIC_BOARD_REMOTE_ROOT:-/Users/chenmingyao/.beacon/runtime-ledger/pocketbase}"
VERIFY_ONLY=0
SKIP_DNS=0

usage() {
  cat <<'EOF'
Usage: scripts/setup_public_board_ingress.sh [options]

Options:
  --hostname <value>     Public hostname. Default: beacon.lbeaconcc.icu
  --port <value>         Remote static server port. Default: 18090
  --verify-only          Read-only verification without changing remote files or DNS
  --skip-dns             Do not run cloudflared tunnel route dns
  --help                 Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --hostname)
      HOSTNAME_VALUE="${2:?missing hostname}"
      shift 2
      ;;
    --port)
      PORT_VALUE="${2:?missing port}"
      shift 2
      ;;
    --verify-only)
      VERIFY_ONLY=1
      shift
      ;;
    --skip-dns)
      SKIP_DNS=1
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "Public board source directory missing: $SOURCE_DIR" >&2
  echo "Run beacon doctor rebuild-runtime-ledger first." >&2
  exit 1
fi

SSH_BASE=(
  env -u SSH_AUTH_SOCK ssh -n -F /dev/null
  -i "$SSH_KEY"
  -o IdentitiesOnly=yes
  -o PreferredAuthentications=publickey
  -o PubkeyAuthentication=yes
  -o StrictHostKeyChecking=accept-new
  -o UserKnownHostsFile="$HOME/.ssh/known_hosts"
  -o ConnectTimeout=8
  "${PEER_USER}@${PEER_HOST}"
)

RSYNC_RSH="env -u SSH_AUTH_SOCK ssh -F /dev/null -i $SSH_KEY -o IdentitiesOnly=yes -o PreferredAuthentications=publickey -o PubkeyAuthentication=yes -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile=$HOME/.ssh/known_hosts -o ConnectTimeout=8"

REMOTE_BOARD_DIR="$REMOTE_ROOT/pb_public"
REMOTE_SCRIPT="$REMOTE_ROOT/scripts/serve-public-board-static.sh"
REMOTE_PLIST="/Users/${PEER_USER}/Library/LaunchAgents/com.beacon.public-board.plist"
REMOTE_CLOUDFLARE_CONFIG="/Users/${PEER_USER}/.cloudflared/config-primary-hapi.yml"

echo "[1/5] verify peer reachability"
"${SSH_BASE[@]}" "echo peer-ok >/dev/null"

if [[ "$VERIFY_ONLY" -eq 0 ]]; then
  echo "[2/5] sync public board assets to Mac mini"
  "${SSH_BASE[@]}" "mkdir -p '$REMOTE_BOARD_DIR'"
  rsync -az --delete -e "$RSYNC_RSH" "$SOURCE_DIR" "${PEER_USER}@${PEER_HOST}:$REMOTE_BOARD_DIR/"

  echo "[3/5] install/update remote static board service"
  "${SSH_BASE[@]}" "PORT='$PORT_VALUE' REMOTE_ROOT='$REMOTE_ROOT' REMOTE_PLIST='$REMOTE_PLIST' python3 - <<'PY'
from pathlib import Path
import os

port = os.environ['PORT']
remote_root = Path(os.environ['REMOTE_ROOT'])
plist_path = Path(os.environ['REMOTE_PLIST'])
script_path = remote_root / 'scripts' / 'serve-public-board-static.sh'
log_dir = Path.home() / '.beacon' / 'runtime-ledger' / 'logs'
dollar = '$'
log_dir.mkdir(parents=True, exist_ok=True)
script_path.parent.mkdir(parents=True, exist_ok=True)
script_path.write_text(
    '#!/bin/sh\\n'
    'set -eu\\n'
    f'ROOT=\"{dollar}HOME/.beacon/runtime-ledger/pocketbase/pb_public\"\\n'
    f'PORT=\"{dollar}' + '{BEACON_PUBLIC_BOARD_PORT:-' + port + '}\"\\n'
    f'exec /usr/bin/python3 -m http.server \"{dollar}PORT\" --bind 127.0.0.1 --directory \"{dollar}ROOT\"\\n',
    encoding='utf-8',
)
script_path.chmod(0o755)
plist_path.parent.mkdir(parents=True, exist_ok=True)
plist_path.write_text(f'''<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">
<plist version=\"1.0\">
<dict>
  <key>Label</key>
  <string>com.beacon.public-board</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/sh</string>
    <string>-lc</string>
    <string>exec \"{dollar}HOME/.beacon/runtime-ledger/pocketbase/scripts/serve-public-board-static.sh\"</string>
  </array>
  <key>EnvironmentVariables</key>
  <dict>
    <key>BEACON_PUBLIC_BOARD_PORT</key>
    <string>{port}</string>
  </dict>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>{str(log_dir / 'public-board.stdout.log')}</string>
  <key>StandardErrorPath</key>
  <string>{str(log_dir / 'public-board.stderr.log')}</string>
</dict>
</plist>
''', encoding='utf-8')
PY
plutil -lint '$REMOTE_PLIST' >/dev/null
launchctl unload '$REMOTE_PLIST' >/dev/null 2>&1 || true
launchctl load -w '$REMOTE_PLIST'
sleep 1
curl -fsSI 'http://127.0.0.1:$PORT_VALUE/' | head -n 1"

  echo "[4/5] update remote cloudflared ingress"
  "${SSH_BASE[@]}" "HOSTNAME_VALUE='$HOSTNAME_VALUE' PORT_VALUE='$PORT_VALUE' CONFIG_PATH='$REMOTE_CLOUDFLARE_CONFIG' python3 - <<'PY'
from pathlib import Path
import os

config_path = Path(os.environ['CONFIG_PATH'])
hostname = os.environ['HOSTNAME_VALUE']
port = os.environ['PORT_VALUE']
service_line = f'    service: http://127.0.0.1:{port}'
block = f'  - hostname: {hostname}\\n{service_line}\\n'
text = config_path.read_text(encoding='utf-8')
if f'  - hostname: {hostname}\\n' in text:
    lines = text.splitlines()
    for index, line in enumerate(lines):
      if line.strip() == f'- hostname: {hostname}':
        if index + 1 < len(lines):
          lines[index + 1] = service_line
        break
    new_text = '\\n'.join(lines) + ('\\n' if text.endswith('\\n') else '')
else:
    marker = '  - service: http_status:404\\n'
    if marker not in text:
        raise SystemExit(f'fallback marker missing in {config_path}')
    new_text = text.replace(marker, block + marker)
backup_path = config_path.with_suffix(config_path.suffix + '.beacon-board.bak')
backup_path.write_text(text, encoding='utf-8')
config_path.write_text(new_text, encoding='utf-8')
PY
launchctl kickstart -k gui/\$(id -u)/com.hapi.mini.primary-cloudflared
sleep 2"
fi

if [[ "$SKIP_DNS" -eq 0 && "$VERIFY_ONLY" -eq 0 ]]; then
  echo "[5/5] bind hostname to Cloudflare tunnel"
  if [[ ! -f "$HOME/.cloudflared/cert.pem" ]]; then
    echo "Missing ~/.cloudflared/cert.pem; cannot create DNS route automatically." >&2
    exit 1
  fi
  cloudflared tunnel route dns --overwrite-dns "$TUNNEL_ID" "$HOSTNAME_VALUE"
else
  echo "[5/5] skip DNS mutation"
fi

echo "[verify] remote board service"
"${SSH_BASE[@]}" "curl -fsSI 'http://127.0.0.1:$PORT_VALUE/' | head -n 1"

echo "[verify] remote cloudflared config"
"${SSH_BASE[@]}" "grep -n 'hostname: $HOSTNAME_VALUE' '$REMOTE_CLOUDFLARE_CONFIG'"

echo "[verify] public hostname"
if ! curl -fsSI "https://$HOSTNAME_VALUE/" | head -n 1; then
  echo "WARN: public hostname is not resolvable from the current resolver yet." >&2
  echo "      Tunnel/service installation succeeded, but authoritative DNS still needs verification in Cloudflare." >&2
fi
