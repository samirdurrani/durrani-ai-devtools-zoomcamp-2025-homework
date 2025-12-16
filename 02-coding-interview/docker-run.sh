#!/bin/bash

# Docker build and run helper script
# Usage: ./docker-run.sh [dev|prod|build|stop|logs|shell]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default to production
MODE=${1:-prod}

# Functions
print_header() {
    echo -e "${BLUE}=====================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}=====================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Main logic
case $MODE in
    dev)
        print_header "Starting Development Environment"
        echo "Building development image..."
        docker-compose -f docker-compose.dev.yml build
        
        echo "Starting services..."
        docker-compose -f docker-compose.dev.yml up
        ;;
    
    prod)
        print_header "Starting Production Environment"
        echo "Building production image..."
        docker-compose build
        
        echo "Starting services..."
        docker-compose up -d
        
        print_success "Production services started!"
        echo ""
        echo "Access the application at:"
        echo "  🌐 http://localhost:8000"
        echo "  📚 API Docs: http://localhost:8000/docs"
        echo ""
        echo "View logs: ./docker-run.sh logs"
        echo "Stop services: ./docker-run.sh stop"
        ;;
    
    build)
        print_header "Building Docker Images"
        
        echo "Building production image..."
        docker build -t coding-interview-platform:latest .
        print_success "Production image built!"
        
        echo ""
        echo "Building development image..."
        docker build -f Dockerfile.dev -t coding-interview-platform:dev .
        print_success "Development image built!"
        
        echo ""
        docker images | grep coding-interview-platform
        ;;
    
    stop)
        print_header "Stopping All Services"
        docker-compose down
        docker-compose -f docker-compose.dev.yml down
        print_success "All services stopped!"
        ;;
    
    clean)
        print_header "Cleaning Docker Resources"
        print_warning "This will remove all containers, images, and volumes!"
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker-compose down -v --rmi all
            docker-compose -f docker-compose.dev.yml down -v --rmi all
            print_success "Cleanup complete!"
        else
            print_warning "Cleanup cancelled."
        fi
        ;;
    
    logs)
        print_header "Viewing Logs"
        docker-compose logs -f
        ;;
    
    logs-dev)
        print_header "Viewing Development Logs"
        docker-compose -f docker-compose.dev.yml logs -f
        ;;
    
    shell)
        print_header "Opening Shell in Container"
        docker-compose exec coding-platform /bin/bash
        ;;
    
    shell-dev)
        print_header "Opening Shell in Development Container"
        docker-compose -f docker-compose.dev.yml exec coding-platform-dev /bin/bash
        ;;
    
    test)
        print_header "Running Tests in Container"
        docker-compose run --rm coding-platform pytest /app/backend/tests -v
        ;;
    
    status)
        print_header "Container Status"
        echo "Production containers:"
        docker-compose ps
        echo ""
        echo "Development containers:"
        docker-compose -f docker-compose.dev.yml ps
        ;;
    
    help|--help|-h)
        print_header "Docker Helper Script"
        echo "Usage: ./docker-run.sh [command]"
        echo ""
        echo "Commands:"
        echo "  dev       - Start development environment with hot reload"
        echo "  prod      - Start production environment (default)"
        echo "  build     - Build both production and development images"
        echo "  stop      - Stop all running services"
        echo "  clean     - Remove all containers, images, and volumes"
        echo "  logs      - View production logs"
        echo "  logs-dev  - View development logs"
        echo "  shell     - Open shell in production container"
        echo "  shell-dev - Open shell in development container"
        echo "  test      - Run tests in container"
        echo "  status    - Show container status"
        echo "  help      - Show this help message"
        ;;
    
    *)
        print_error "Unknown command: $MODE"
        echo "Use './docker-run.sh help' for available commands"
        exit 1
        ;;
esac

