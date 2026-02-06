#!/bin/bash
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

STACK_DIR="$(cd "$(dirname "$0")/../stack" && pwd)"

# Check if .env file exists
if [ ! -f "$STACK_DIR/.env" ]; then
    echo -e "${RED}Error: stack/.env not found!${NC}"
    echo "Run: cp stack/.env.sample stack/.env"
    exit 1
fi

cd "$STACK_DIR"

case "$1" in
    up)
        echo -e "${BLUE}Starting NeurALIzer stack...${NC}"
        docker compose up -d
        echo -e "${GREEN}Stack started${NC}"
        echo ""
        echo "Services:"
        echo "  http://localhost/"
        echo "  http://localhost/health"
        ;;
    down)
        echo -e "${BLUE}Stopping NeurALIzer stack...${NC}"
        docker compose down
        echo -e "${GREEN}Stack stopped${NC}"
        ;;
    restart)
        echo -e "${BLUE}Restarting NeurALIzer stack...${NC}"
        docker compose down
        sleep 2
        docker compose up -d
        echo -e "${GREEN}Stack restarted${NC}"
        ;;
    rebuild)
        echo -e "${BLUE}Rebuilding NeurALIzer stack...${NC}"
        docker compose down
        docker compose build --no-cache
        docker compose up -d
        echo -e "${GREEN}Stack rebuilt and started${NC}"
        ;;
    logs)
        SERVICE=${2:-}
        if [ -z "$SERVICE" ]; then
            echo -e "${BLUE}Showing all logs (Ctrl+C to exit)...${NC}"
            docker compose logs -f
        else
            echo -e "${BLUE}Showing logs for $SERVICE...${NC}"
            docker compose logs -f "$SERVICE"
        fi
        ;;
    status)
        echo -e "${BLUE}NeurALIzer Stack Status:${NC}"
        echo ""
        docker compose ps
        ;;
    *)
        echo "NeurALIzer Stack Management"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  up        Start the stack"
        echo "  down      Stop the stack"
        echo "  restart   Restart the stack"
        echo "  rebuild   Rebuild images and restart"
        echo "  logs      Show logs (optionally: logs <service>)"
        echo "  status    Show running containers"
        echo ""
        echo "Configuration is driven by stack/.env (see stack/.env.sample)"
        echo ""
        echo "Examples:"
        echo "  $0 up              # Start everything"
        echo "  $0 logs backend    # Tail backend logs"
        echo "  $0 rebuild         # Full rebuild"
        exit 1
        ;;
esac
