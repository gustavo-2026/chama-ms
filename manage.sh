#!/bin/bash
# Chama Microservices Manager
# Start/Stop/Restart all microservices

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Service configuration
declare -A SERVICES=(
    ["core"]="8001 services/core-service/main.py"
    ["marketplace"]="8002 services/marketplace-service/main.py"
    ["payments"]="8003 services/payments-service/main.py"
    ["notifications"]="8004 services/notifications-service/main.py"
    ["messaging"]="8005 services/messaging-service/main.py"
    ["kafka"]="9093 services/kafka-service/main.py"
)

PID_DIR="/tmp/chama-ms-pids"
LOG_DIR="/tmp/chama-ms-logs"

mkdir -p "$PID_DIR" "$LOG_DIR"

# Function to check if port is in use
is_port_running() {
    local port=$1
    curl -s "http://localhost:$port/health" > /dev/null 2>&1
}

# Start all services
start() {
    echo -e "${GREEN}Starting Chama Microservices...${NC}\n"
    
    for service in "${!SERVICES[@]}"; do
        port="${SERVICES[$service]%% *}"
        script="${SERVICES[$service]#* }"
        
        if is_port_running "$port"; then
            echo -e "${YELLOW}✓ $service (port $port) already running${NC}"
        else
            echo -e "Starting $service on port $port..."
            if [[ "$service" == "kafka" ]]; then
                nohup python3 -m uvicorn services.kafka-service.main:app --host 0.0.0.0 --port 9093 > "$LOG_DIR/$service.log" 2>&1 &
            else
                nohup python3 "$script" > "$LOG_DIR/$service.log" 2>&1 &
            fi
            echo $! > "$PID_DIR/$service.pid"
            sleep 1
        fi
    done
    
    sleep 3
    echo -e "\n${GREEN}Services Status:${NC}"
    status
}

# Stop all services
stop() {
    echo -e "${RED}Stopping Chama Microservices...${NC}\n"
    
    for service in "${!SERVICES[@]}"; do
        pid_file="$PID_DIR/$service.pid"
        
        if [[ -f "$pid_file" ]]; then
            pid=$(cat "$pid_file")
            if kill -0 "$pid" 2>/dev/null; then
                kill "$pid" 2>/dev/null
                echo "Stopped $service (PID: $pid)"
            fi
            rm -f "$pid_file"
        else
            # Try by port
            pkill -f "$service-service" 2>/dev/null
        fi
    done
    
    # Also kill any remaining
    pkill -f "core-service/main.py" 2>/dev/null
    pkill -f "marketplace-service/main.py" 2>/dev/null
    pkill -f "payments-service/main.py" 2>/dev/null
    pkill -f "notifications-service/main.py" 2>/dev/null
    pkill -f "messaging-service/main.py" 2>/dev/null
    pkill -f "kafka-service" 2>/dev/null
    
    echo -e "\n${RED}All services stopped${NC}"
}

# Restart all services
restart() {
    stop
    sleep 2
    start
}

# Check status
status() {
    echo -e "\n${GREEN}=== Service Status ===${NC}\n"
    
    all_running=true
    
    for service in "${!SERVICES[@]}"; do
        port="${SERVICES[$service]%% *}"
        
        if is_port_running "$port"; then
            echo -e "${GREEN}✓${NC} $service - Port $port - RUNNING"
        else
            echo -e "${RED}✗${NC} $service - Port $port - STOPPED"
            all_running=false
        fi
    done
    
    if $all_running; then
        echo -e "\n${GREEN}All services running!${NC}"
    else
        echo -e "\n${YELLOW}Some services are not running. Use './manage.sh start' to start them.${NC}"
    fi
}

# View logs
logs() {
    service=$1
    if [[ -z "$service" ]]; then
        echo "Usage: $0 logs <service_name>"
        echo "Available: ${!SERVICES[@]}"
        exit 1
    fi
    
    if [[ -f "$LOG_DIR/$service.log" ]]; then
        tail -50 "$LOG_DIR/$service.log"
    else
        echo "No logs found for $service"
    fi
}

# Main
case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    logs)
        logs "$2"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs <service>}"
        echo ""
        echo "Commands:"
        echo "  start           - Start all microservices"
        echo "  stop            - Stop all microservices"
        echo "  restart         - Restart all microservices"
        echo "  status          - Check service status"
        echo "  logs <service>  - View logs for a service"
        exit 1
        ;;
esac
