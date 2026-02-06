#!/bin/bash
# Bootstrap iframe URL for server deployments.
# Local dev doesn't need this — Vite env injection handles it.
#
# Usage:
#   ./scripts/bootstrap-iframe.sh                          # Interactive
#   ./scripts/bootstrap-iframe.sh --host 192.168.1.50      # Non-interactive
#   ./scripts/bootstrap-iframe.sh --host my.server --port 9082

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CHATPANEL="$SCRIPT_DIR/../stack/frontend/src/components/ChatPanel.vue"

HOST=""
PORT="8082"
PROTOCOL="http"

usage() {
    echo "Bootstrap iframe URL for server deployments."
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --host <domain/ip>   Server hostname or IP (required for non-interactive)"
    echo "  --port <port>        Open WebUI port (default: 8082)"
    echo "  --protocol <proto>   http or https (default: http)"
    echo "  --help               Show this help"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Interactive mode"
    echo "  $0 --host 192.168.1.50                # Set URL to http://192.168.1.50:8082"
    echo "  $0 --host my.server --port 9082       # Custom port"
    echo "  $0 --host my.server --protocol https  # HTTPS"
}

# Parse args
while [[ $# -gt 0 ]]; do
    case "$1" in
        --host) HOST="$2"; shift 2 ;;
        --port) PORT="$2"; shift 2 ;;
        --protocol) PROTOCOL="$2"; shift 2 ;;
        --help) usage; exit 0 ;;
        *) echo "Unknown option: $1"; usage; exit 1 ;;
    esac
done

if [ ! -f "$CHATPANEL" ]; then
    echo "Error: ChatPanel.vue not found at $CHATPANEL"
    exit 1
fi

# Show current URL (sed is portable; avoids grep -oP which needs GNU grep)
CURRENT=$(sed -n "s/.*openWebuiUrl = ['\"]\([^'\"]*\)['\"].*/\1/p" "$CHATPANEL" 2>/dev/null)
[ -z "$CURRENT" ] && CURRENT="(dynamic — using window.location)"
echo "Current iframe URL: $CURRENT"
echo ""

# Interactive mode if no --host
if [ -z "$HOST" ]; then
    read -rp "Enter server hostname or IP (or 'reset' to restore dynamic URL): " HOST
    if [ "$HOST" = "reset" ]; then
        # Restore dynamic URL
        sed -i "s|const openWebuiUrl = .*|const openWebuiUrl = \`\${window.location.protocol}//\${window.location.hostname}:\${port}\`|" "$CHATPANEL"
        echo "Restored dynamic iframe URL (uses window.location)"
        exit 0
    fi
    if [ -z "$HOST" ]; then
        echo "No host provided. Aborting."
        exit 1
    fi
    read -rp "Enter Open WebUI port (default: $PORT): " INPUT_PORT
    [ -n "$INPUT_PORT" ] && PORT="$INPUT_PORT"
    read -rp "Protocol — http or https (default: $PROTOCOL): " INPUT_PROTO
    [ -n "$INPUT_PROTO" ] && PROTOCOL="$INPUT_PROTO"
fi

URL="${PROTOCOL}://${HOST}:${PORT}"
sed -i "s|const openWebuiUrl = .*|const openWebuiUrl = '${URL}'|" "$CHATPANEL"

echo ""
echo "Iframe URL set to: $URL"
echo ""
echo "Make sure OPENWEBUI_PORT=$PORT in stack/.env matches."
echo "Then restart: docker compose up -d"
