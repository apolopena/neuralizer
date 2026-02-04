#!/bin/bash
# Stack Management Script for NeurALIzer
# Usage: ./scripts/stack.sh [up|down|restart|rebuild|logs|status] [--dev]

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

STACK_DIR="$(cd "$(dirname "$0")/../stack" && pwd)"

# Check for --dev flag
DEV_MODE=false
COMPOSE_FILES="-f docker-compose.yml"
for arg in "$@"; do
    if [ "$arg" = "--dev" ]; then
        DEV_MODE=true
        COMPOSE_FILES="-f docker-compose.yml -f docker-compose.dev.yml"
    fi
done

# Check if .env file exists
if [ ! -f "$STACK_DIR/.env" ]; then
    echo -e "${RED}Error: stack/.env not found!${NC}"
    echo "Run: cp stack/.env.example stack/.env"
    exit 1
fi

case "$1" in
    up)
        if $DEV_MODE; then
            echo -e "${BLUE}Starting NeurALIzer stack (dev mode)...${NC}"
        else
            echo -e "${BLUE}Starting NeurALIzer stack...${NC}"
        fi
        docker compose -f "$STACK_DIR/docker-compose.yml" ${DEV_MODE:+-f "$STACK_DIR/docker-compose.dev.yml"} --env-file "$STACK_DIR/.env" up -d
        echo -e "${GREEN}Stack started${NC}"
        echo ""
        echo "Services:"
        echo "  https://localhost/"
        echo "  https://localhost/health"
        if $DEV_MODE; then
            echo ""
            echo "Dev ports (bypasses Caddy):"
            echo "  Backend: http://localhost:8000"
        fi
        ;;

    down)
        echo -e "${BLUE}Stopping NeurALIzer stack...${NC}"
        docker compose -f "$STACK_DIR/docker-compose.yml" ${DEV_MODE:+-f "$STACK_DIR/docker-compose.dev.yml"} --env-file "$STACK_DIR/.env" down
        echo -e "${GREEN}Stack stopped${NC}"
        ;;

    restart)
        echo -e "${BLUE}Restarting NeurALIzer stack...${NC}"
        docker compose -f "$STACK_DIR/docker-compose.yml" ${DEV_MODE:+-f "$STACK_DIR/docker-compose.dev.yml"} --env-file "$STACK_DIR/.env" down
        sleep 2
        docker compose -f "$STACK_DIR/docker-compose.yml" ${DEV_MODE:+-f "$STACK_DIR/docker-compose.dev.yml"} --env-file "$STACK_DIR/.env" up -d
        echo -e "${GREEN}Stack restarted${NC}"
        ;;

    rebuild)
        echo -e "${BLUE}Rebuilding NeurALIzer stack...${NC}"
        docker compose -f "$STACK_DIR/docker-compose.yml" ${DEV_MODE:+-f "$STACK_DIR/docker-compose.dev.yml"} --env-file "$STACK_DIR/.env" down
        docker compose -f "$STACK_DIR/docker-compose.yml" ${DEV_MODE:+-f "$STACK_DIR/docker-compose.dev.yml"} --env-file "$STACK_DIR/.env" build --no-cache
        docker compose -f "$STACK_DIR/docker-compose.yml" ${DEV_MODE:+-f "$STACK_DIR/docker-compose.dev.yml"} --env-file "$STACK_DIR/.env" up -d
        echo -e "${GREEN}Stack rebuilt and started${NC}"
        ;;

    logs)
        SERVICE=${2:-}
        if [ "$SERVICE" = "--dev" ]; then SERVICE=""; fi
        if [ -z "$SERVICE" ]; then
            echo -e "${BLUE}Showing all logs (Ctrl+C to exit)...${NC}"
            docker compose -f "$STACK_DIR/docker-compose.yml" --env-file "$STACK_DIR/.env" logs -f
        else
            echo -e "${BLUE}Showing logs for $SERVICE...${NC}"
            docker compose -f "$STACK_DIR/docker-compose.yml" --env-file "$STACK_DIR/.env" logs -f "$SERVICE"
        fi
        ;;

    status)
        echo -e "${BLUE}NeurALIzer Stack Status:${NC}"
        echo ""
        docker compose -f "$STACK_DIR/docker-compose.yml" --env-file "$STACK_DIR/.env" ps
        ;;

    *)
        echo "NeurALIzer Stack Management"
        echo ""
        echo "Usage: $0 [command] [--dev]"
        echo ""
        echo "Commands:"
        echo "  up        Start the stack"
        echo "  down      Stop the stack"
        echo "  restart   Restart the stack"
        echo "  rebuild   Rebuild images and restart"
        echo "  logs      Show logs (optionally: logs <service>)"
        echo "  status    Show running containers"
        echo ""
        echo "Options:"
        echo "  --dev     Expose backend port to host (localhost:8000)"
        echo ""
        echo "Examples:"
        echo "  $0 up              # Start everything"
        echo "  $0 up --dev        # Start with backend port exposed"
        echo "  $0 logs backend    # Tail backend logs"
        echo "  $0 rebuild         # Full rebuild"
        exit 1
        ;;
esac
