#!/bin/bash

# Market Data Service Docker Management Script
# Usage: ./docker.sh [build|run|stop|logs|shell]

set -e

IMAGE_NAME="market-data-service"
CONTAINER_NAME="market-data-service-container"
PORT=8002

case "$1" in
    build)
        echo "🔨 Building Docker image..."
        docker build -t $IMAGE_NAME .
        echo "✅ Build completed!"
        ;;
    
    run)
        echo "🚀 Starting container..."
        # Stop existing container if running
        docker stop $CONTAINER_NAME 2>/dev/null || true
        docker rm $CONTAINER_NAME 2>/dev/null || true
        
        # Run new container
        docker run -d \
            --name $CONTAINER_NAME \
            -p $PORT:$PORT \
            --env-file .env \
            --restart unless-stopped \
            $IMAGE_NAME
        
        echo "✅ Container started on port $PORT"
        echo "📊 Health check: http://localhost:$PORT/health"
        echo "📚 API docs: http://localhost:$PORT/docs"
        ;;
    
    stop)
        echo "🛑 Stopping container..."
        docker stop $CONTAINER_NAME 2>/dev/null || echo "Container not running"
        docker rm $CONTAINER_NAME 2>/dev/null || echo "Container not found"
        echo "✅ Container stopped"
        ;;
    
    logs)
        echo "📋 Container logs:"
        docker logs -f $CONTAINER_NAME
        ;;
    
    shell)
        echo "🐚 Opening shell in container..."
        docker exec -it $CONTAINER_NAME /bin/bash
        ;;
    
    debug)
        echo "🔍 Debugging container environment..."
        echo "Container info:"
        docker exec $CONTAINER_NAME pwd
        echo "Python path:"
        docker exec $CONTAINER_NAME python -c "import sys; print('\\n'.join(sys.path))"
        echo "Environment variables:"
        docker exec $CONTAINER_NAME env | grep -E "(PYTHON|PATH|DEBUG|PORT)" | sort
        echo "App directory structure:"
        docker exec $CONTAINER_NAME find /app -type f -name "*.py" | head -20
        echo "Testing imports:"
        docker exec $CONTAINER_NAME python -c "import sys; sys.path.insert(0, '/app/app'); from api.market_data import router; print('✅ Import successful')" || echo "❌ Import failed"
        ;;
    
    test-import)
        echo "🧪 Testing Python imports..."
        docker exec $CONTAINER_NAME /bin/bash -c "cd /app && python -c 'from app.main import app; print(\"✅ App import successful\")'"
        ;;
    
    status)
        echo "📊 Container status:"
        docker ps -a | grep $CONTAINER_NAME || echo "Container not found"
        ;;
    
    rebuild)
        echo "🔄 Rebuilding and restarting..."
        $0 stop
        $0 build
        $0 run
        ;;
    
    *)
        echo "Usage: $0 {build|run|stop|logs|shell|debug|test-import|status|rebuild}"
        echo ""
        echo "Commands:"
        echo "  build       - Build the Docker image"
        echo "  run         - Run the container"
        echo "  stop        - Stop and remove the container"
        echo "  logs        - Show container logs"
        echo "  shell       - Open shell in container"
        echo "  debug       - Debug container environment and imports"
        echo "  test-import - Test Python imports"
        echo "  status      - Show container status"
        echo "  rebuild     - Stop, build, and run"
        exit 1
        ;;
esac
