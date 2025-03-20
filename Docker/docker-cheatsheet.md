# Docker Cheatsheet

## Installation & Setup
```bash
# Check Docker version
docker --version
docker version  # More detailed version info

# Check Docker system info
docker info

# Start Docker service (Linux)
sudo systemctl start docker
```

## Images
```bash
# List all local images
docker images
docker image ls

# Search for images in Docker Hub
docker search <image_name>

# Pull an image from a registry
docker pull <image_name>:<tag>

# Build an image from Dockerfile in current directory
docker build -t <name>:<tag> .

# Build with different Dockerfile
docker build -f <dockerfile_path> -t <name>:<tag> .

# Remove an image
docker rmi <image_id/name>

# Remove all unused images
docker image prune
docker image prune -a  # Remove all unused images, not just dangling ones

# Save an image to a tar archive
docker save <image_name> > <filename>.tar

# Load an image from a tar archive
docker load < <filename>.tar

# Tag an image
docker tag <source_image>:<tag> <target_image>:<tag>

# Inspect an image
docker image inspect <image_name/id>

# Show image history/layers
docker history <image_name/id>
```

## Containers
```bash
# Run a container
docker run <image_name>

# Common run options
docker run --name <container_name> <image_name>  # Assign a name
docker run -d <image_name>  # Run in detached mode (background)
docker run -it <image_name> <command>  # Interactive mode with pseudo-TTY
docker run -p <host_port>:<container_port> <image_name>  # Port mapping
docker run -v <host_path>:<container_path> <image_name>  # Volume mounting
docker run -e KEY=VALUE <image_name>  # Set environment variables
docker run --restart=always <image_name>  # Restart policy
docker run --rm <image_name>  # Remove container when it exits
docker run --network <network_name> <image_name>  # Connect to a network

# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Start/stop/restart containers
docker start <container_id/name>
docker stop <container_id/name>
docker restart <container_id/name>

# Rename a container
docker rename <old_name> <new_name>

# Remove a container
docker rm <container_id/name>
docker rm -f <container_id/name>  # Force remove a running container

# Remove all stopped containers
docker container prune

# Execute a command in a running container
docker exec <container_id/name> <command>
docker exec -it <container_id/name> bash  # Interactive shell

# View container logs
docker logs <container_id/name>
docker logs -f <container_id/name>  # Follow log output
docker logs --tail 100 <container_id/name>  # Last 100 lines
docker logs --since 1h <container_id/name>  # Logs from last hour

# Copy files between container and host
docker cp <container_id>:<container_path> <host_path>  # From container to host
docker cp <host_path> <container_id>:<container_path>  # From host to container

# Inspect a container
docker inspect <container_id/name>

# Show container resource usage
docker stats
docker stats <container_id/name>

# Show running processes in a container
docker top <container_id/name>

# Pause/unpause container processes
docker pause <container_id/name>
docker unpause <container_id/name>

# Create a new image from a container
docker commit <container_id/name> <new_image_name>:<tag>

# Attach to a running container
docker attach <container_id/name>

# Fetch the logs from a container
docker container logs <container_id/name>
```

## Volumes
```bash
# Create a volume
docker volume create <volume_name>

# List volumes
docker volume ls

# Inspect a volume
docker volume inspect <volume_name>

# Remove a volume
docker volume rm <volume_name>

# Remove all unused volumes
docker volume prune

# Run a container with a named volume
docker run -v <volume_name>:<container_path> <image_name>
```

## Networks
```bash
# Create a network
docker network create <network_name>
docker network create --driver bridge <network_name>  # Specify driver

# List networks
docker network ls

# Inspect a network
docker network inspect <network_name>

# Connect a container to a network
docker network connect <network_name> <container_id/name>

# Disconnect a container from a network
docker network disconnect <network_name> <container_id/name>

# Remove a network
docker network rm <network_name>

# Remove all unused networks
docker network prune
```

## Docker Compose
```bash
# Start services defined in docker-compose.yml
docker compose up
docker compose up -d  # Detached mode
docker compose up --build  # Rebuild images before starting
docker compose -f path/to/your-specific-compose-file.yml up # run a specific docker compoase file

# Stop services
docker compose down
docker compose down -v  # Also remove volumes
docker compose down --rmi all  # Also remove images

# List containers
docker compose ps

# View logs
docker compose logs
docker compose logs -f  # Follow log output
docker compose logs <service_name>  # Logs for specific service

# Run a command in a service container
docker compose exec <service_name> <command>
docker compose exec <service_name> bash  # Interactive shell

# Build/rebuild services
docker compose build
docker compose build <service_name>  # Build specific service

# Pull latest images
docker compose pull

# Show running processes
docker compose top

# Restart services
docker compose restart
docker compose restart <service_name>

# List images used by containers
docker compose images
```

## Dockerfile Reference
```dockerfile
# Base image
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Environment variables
ENV NODE_ENV=production
ENV PORT=3000

# Copy files
COPY package*.json ./
COPY . .

# Install dependencies
RUN npm install

# Build the application
RUN npm run build

# Expose ports
EXPOSE 3000

# Volume mounting point
VOLUME /app/data

# Define default command
CMD ["npm", "start"]

# Define entrypoint
ENTRYPOINT ["node", "app.js"]

# Add metadata
LABEL maintainer="dev@example.com"
LABEL version="1.0"

# Add health check
HEALTHCHECK --interval=30s --timeout=3s CMD curl -f http://localhost:3000/health || exit 1

# Set user
USER node
```

## System & Registry Management
```bash
# Remove all unused objects (images, containers, networks, volumes)
docker system prune
docker system prune -a  # Include unused images

# Show disk usage
docker system df

# Log in to a registry
docker login
docker login <registry_url>

# Log out from a registry
docker logout
docker logout <registry_url>

# Push an image to a registry
docker push <username/image_name>:<tag>

# Pull an image from a registry
docker pull <username/image_name>:<tag>
```

## Advanced Features
```bash
# Check security vulnerabilities in images
docker scan <image_name>

# Show changes to container's filesystem
docker diff <container_id/name>

# Create a container without running it
docker create <image_name>

# Run container and limit resources
docker run --memory="512m" --cpus="1.0" <image_name>

# Update container configuration
docker update --memory="1g" --cpus="2.0" <container_id/name>

# Show events in real-time
docker events

# Create a checkpoint for a running container
docker checkpoint create <container_id/name> <checkpoint_name>

# Start a container from a checkpoint
docker start --checkpoint <checkpoint_name> <container_id/name>

# Manage Docker content trust
docker trust sign <image_name>:<tag>
docker trust inspect <image_name>:<tag>
```

## Docker Swarm (Container Orchestration)
```bash
# Initialize a swarm
docker swarm init --advertise-addr <manager_ip>

# Get join token for workers
docker swarm join-token worker

# Get join token for managers
docker swarm join-token manager

# Join a swarm as a worker
docker swarm join --token <token> <manager_ip>:<port>

# List nodes in the swarm
docker node ls

# Create a service
docker service create --name <service_name> --replicas <num> <image_name>

# List services
docker service ls

# Scale a service
docker service scale <service_name>=<num_replicas>

# Update a service
docker service update --image <new_image> <service_name>

# Inspect a service
docker service inspect <service_name>

# Remove a service
docker service rm <service_name>

# Deploy a stack from a compose file
docker stack deploy -c <compose_file> <stack_name>

# List stacks
docker stack ls

# List services in a stack
docker stack services <stack_name>

# Remove a stack
docker stack rm <stack_name>

# Leave the swarm
docker swarm leave
docker swarm leave --force  # For manager nodes
```

## Common Docker Compose File (docker-compose.yml)
```yaml
version: '3.8'

services:
  webapp:
    build: 
      context: ./app
      dockerfile: Dockerfile
    image: webapp:latest
    container_name: webapp
    ports:
      - "8080:80"
    environment:
      - NODE_ENV=production
      - DB_HOST=db
    volumes:
      - ./app:/usr/src/app
      - /usr/src/app/node_modules
    depends_on:
      - db
    restart: always
    networks:
      - app-network

  db:
    image: postgres:13
    container_name: postgres_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=example
      - POSTGRES_USER=postgres
      - POSTGRES_DB=myapp
    networks:
      - app-network

volumes:
  postgres_data:

networks:
  app-network:
    driver: bridge
```
