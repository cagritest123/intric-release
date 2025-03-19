# Intric Platform

Intric is an AI-powered knowledge management and conversational platform designed to provide intuitive access to organizational knowledge through natural language interactions.

## Technology Stack

### Backend
- **Language**: Python 3.10
- **Framework**: FastAPI
- **Database**: PostgreSQL 13 with pgvector for vector embeddings
- **Message Broker**: Redis
- **Dependency Management**: Poetry
- **Background Tasks**: ARQ (Redis-based task queue)

### Frontend
- **Framework**: SvelteKit
- **Package Manager**: pnpm
- **UI Components**: Custom component library
- **HTTP Client**: Axios/Fetch
- **Styling**: CSS/SCSS

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Web Server**: Nginx (for frontend)
- **Database Engine**: pgvector/pgvector:pg13

## System Architecture

The Intric platform consists of several components working together:

1. **Frontend**: SvelteKit application providing the user interface
2. **Backend API**: FastAPI service handling requests, authentication, and business logic
3. **Worker**: Background task processor for handling long-running operations
4. **Database**: PostgreSQL with pgvector extension for storing data and vector embeddings
5. **Redis**: In-memory data store for caching and task queuing

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│  Backend    │────▶│  Database   │
│   (Nginx)   │◀────│  (FastAPI)  │◀────│ (PostgreSQL)│
└─────────────┘     └─────────────┘     └─────────────┘
                         │  ▲
                         │  │
                         ▼  │
                    ┌─────────────┐     ┌─────────────┐
                    │   Worker    │────▶│    Redis    │
                    │             │◀────│             │
                    └─────────────┘     └─────────────┘
```

## Development vs Production Configuration

This repository contains two different Docker Compose configurations:

1. **Root docker-compose.yml**: The main configuration file intended for **production deployment**. This file defines all services required for a complete Intric platform deployment, including the containerized frontend and backend applications, worker processes, and infrastructure components.

2. **backend/docker-compose.yml**: A simplified configuration intended for **local development only**. This file only contains the infrastructure services (PostgreSQL with pgvector and Redis) needed during development. It does not include the application containers because in development mode, the frontend and backend are run directly on the host machine.

When deploying to production, always use the docker-compose.yml file in the root directory. The backend/docker-compose.yml file can be safely ignored for production deployments.

## Quick Start for Production Deployment

For a streamlined deployment process, follow these steps:

1. **Set up environment variables**:
   ```bash
   # Copy the example environment file and edit it
   cp .env.example .env
   nano .env  # Edit with your specific values
   ```

2. **Pull images from your registry**:
   ```bash
   # Ensure your NEXUS_REGISTRY and IMAGE_TAG are set correctly in .env
   docker-compose pull
   ```

3. **Start all services in detached mode**:
   ```bash
   docker-compose up -d
   ```

4. **Initialize the database** (first-time deployment only):
   ```bash
   docker-compose --profile init up db-init
   ```

5. **Verify deployment**:
   ```bash
   docker-compose ps
   ```

The deployment process uses only Docker Compose commands and doesn't require running any local binaries or code from the repository directly.

## Building and Publishing Images

The Intric platform is designed to be fully containerized with images stored in a Docker registry such as Nexus. This approach simplifies deployment and ensures consistency across environments.

### Prerequisites for Building

- Docker Engine 20.10.x or later
- Docker Compose 2.x or later
- Access to a Nexus registry or similar Docker registry

### Building Docker Images

1. **Set up environment variables** for the build:

   ```bash
   export NEXUS_REGISTRY="your.nexus.registry.com"
   export IMAGE_TAG="latest"  # or a specific version like "1.0.0"
   ```

2. **Build the backend image**:

   ```bash
   cd backend
   docker build -t ${NEXUS_REGISTRY}/intric/backend:${IMAGE_TAG} .
   ```

   The backend Dockerfile uses a multi-stage build process:
   - First stage installs build dependencies and Poetry
   - Second stage includes only runtime dependencies for a smaller image
   - Application code is copied into the container
   - The image exposes port 8123 and runs the FastAPI application with uvicorn

3. **Build the frontend image**:

   ```bash
   cd frontend
   docker build -t ${NEXUS_REGISTRY}/intric/frontend:${IMAGE_TAG} .
   ```

   The frontend Dockerfile also uses multi-stage builds:
   - Dependencies are installed using pnpm
   - UI packages are built first
   - Web application is built with proper environment settings
   - Final image is based on Nginx Alpine for serving static content
   - The image exposes port 3000 and runs Nginx with a custom configuration

4. **Push the images to your Nexus registry**:

   ```bash
   docker push ${NEXUS_REGISTRY}/intric/backend:${IMAGE_TAG}
   docker push ${NEXUS_REGISTRY}/intric/frontend:${IMAGE_TAG}
   ```

### CI/CD Integration

For automated builds, you can integrate these steps into a CI/CD pipeline:

1. **Set up authentication** to your Nexus registry:

   ```bash
   echo $NEXUS_PASSWORD | docker login ${NEXUS_REGISTRY} -u $NEXUS_USERNAME --password-stdin
   ```

2. **Build and tag** the images with proper versions:

   ```bash
   # Use Git commit hash or CI build number for versioning
   export IMAGE_TAG=$(git rev-parse --short HEAD)
   
   # Build images
   docker build -t ${NEXUS_REGISTRY}/intric/backend:${IMAGE_TAG} ./backend
   docker build -t ${NEXUS_REGISTRY}/intric/frontend:${IMAGE_TAG} ./frontend
   
   # Also tag as latest
   docker tag ${NEXUS_REGISTRY}/intric/backend:${IMAGE_TAG} ${NEXUS_REGISTRY}/intric/backend:latest
   docker tag ${NEXUS_REGISTRY}/intric/frontend:${IMAGE_TAG} ${NEXUS_REGISTRY}/intric/frontend:latest
   ```

3. **Push all images**:

   ```bash
   docker push ${NEXUS_REGISTRY}/intric/backend:${IMAGE_TAG}
   docker push ${NEXUS_REGISTRY}/intric/backend:latest
   docker push ${NEXUS_REGISTRY}/intric/frontend:${IMAGE_TAG}
   docker push ${NEXUS_REGISTRY}/intric/frontend:latest
   ```

## Production Deployment Guide

### Prerequisites
- Linux server with Docker Engine 20.10.x or later
- Docker Compose 2.x or later
- At least 4GB RAM (recommended), 1GB RAM (minimum)
- Sufficient disk space for database storage (consider the 25x multiplier for vector embeddings, **Intric on cloud uses around 50 GB currently**)
- Outbound internet connectivity to LLM APIs (**Not neccessary when running it on-prem**)
- Access to a Docker registry containing Intric images

### System Requirements

Since Intric uses pgvector for vector embeddings, its memory requirements are optimized compared to in-memory vector databases:

- **Recommended**: 4GB RAM
- **Minimum**: 1GB RAM

**Storage considerations**: Vector embeddings require approximately 25x the size of the original text data. For example, 1MB of text documents will result in roughly 25MB of vector data.

### Configuration

The entire Intric platform is configured through environment variables in a `.env` file:

> **Important Note**: The docker-compose.yml file uses the pattern `${VARIABLE_NAME:-default_value}` for environment variables. This means:
> - If the variable is defined in your .env file, that value will be used
> - If not defined in .env, the default value specified in docker-compose.yml will be used
> - You don't need to modify the docker-compose.yml file directly - all configuration should be done through the .env file

#### Network Configuration
- `SERVICE_FQDN_FRONTEND`: Frontend domain name
- `SERVICE_FQDN_BACKEND`: Backend domain name
- `FRONTEND_PORT`: Port for the frontend service (default: 3000)
- `BACKEND_PORT`: Port for the backend service (default: 8123)
- `NEXUS_REGISTRY`: URL of your Docker registry
- `IMAGE_TAG`: Version tag of the images to deploy

#### Database Configuration
- `POSTGRES_USER`: Database username (default: postgres)
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_PORT`: Database port (default: 5432)
- `POSTGRES_DB`: Database name (default: postgres)

#### Redis Configuration
- `REDIS_HOST`: Redis hostname (internal service name: redis)
- `REDIS_PORT`: Redis port (default: 6379)

#### Security and Authentication
- `JWT_SECRET`: Secret key for JWT tokens
- `JWT_AUDIENCE`: JWT audience claim (default: *)
- `JWT_ISSUER`: JWT issuer claim (default: EXAMPLE)
- `JWT_EXPIRY_TIME`: JWT token expiry time in seconds (default: 86000)
- `JWT_ALGORITHM`: Algorithm used for JWT (default: HS256)
- `JWT_TOKEN_PREFIX`: Prefix for JWT token in Authorization header
- `API_PREFIX`: Prefix for API routes (default: /api/v1)
- `API_KEY_LENGTH`: Length of API keys (default: 64)
- `API_KEY_HEADER_NAME`: Header name for API key (default: example)

#### LLM API Configuration
- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key
- `AZURE_API_KEY`: Azure API key
- `AZURE_MODEL_DEPLOYMENT`: Azure model deployment name
- `AZURE_ENDPOINT`: Azure API endpoint
- `AZURE_API_VERSION`: Azure API version

#### File Upload Limits
- `UPLOAD_FILE_TO_SESSION_MAX_SIZE`: Maximum file size for session uploads (default: 1048576 bytes)
- `UPLOAD_IMAGE_TO_SESSION_MAX_SIZE`: Maximum image size for session uploads (default: 1048576 bytes)
- `UPLOAD_MAX_FILE_SIZE`: Maximum file size for general uploads (default: 10485760 bytes)
- `TRANSCRIPTION_MAX_FILE_SIZE`: Maximum file size for transcription (default: 10485760 bytes)
- `MAX_IN_QUESTION`: Maximum files in question (default: 1)

#### Feature Flags
- `USING_ACCESS_MANAGEMENT`: Enable/disable access management (default: False)
- `USING_AZURE_MODELS`: Enable/disable Azure models (default: False)

#### MobilityGuard Authentication (Optional)
- `MOBILITYGUARD_DISCOVERY_ENDPOINT`: MobilityGuard discovery endpoint
- `MOBILITYGUARD_CLIENT_ID`: MobilityGuard client ID
- `MOBILITYGUARD_CLIENT_SECRET`: MobilityGuard client secret
- `MOBILITY_GUARD_AUTH`: MobilityGuard auth URL for frontend

#### Frontend Specific Settings
- `SHOW_TEMPLATES`: Enable/disable templates display
- `FEEDBACK_FORM_URL`: URL for feedback form

#### Logging
- `LOGLEVEL`: Log level (DEBUG, INFO, WARNING, ERROR) (default: INFO)

### Deployment Steps

1. **Create a `.env` file**:
   ```bash
   cp .env.example .env
   nano .env  # Edit with your specific values
   ```
   
   Ensure you set at least these required variables:
   ```
   NEXUS_REGISTRY=your.nexus.registry.com
   IMAGE_TAG=version_to_deploy
   POSTGRES_PASSWORD=secure_password
   JWT_SECRET=secure_random_string
   ```

2. **Pull the Docker images from your Nexus registry**:
   ```bash
   docker-compose pull
   ```

3. **Start the services**:
   ```bash
   docker-compose up -d
   ```
   This will start all container services defined in docker-compose.yml: frontend, backend, worker, db, and redis.

4. **Initialize the database** (first time only):
   ```bash
   docker-compose --profile init up db-init
   ```
   This command runs the database initialization container which sets up the database schema and initial data.

5. **Verify deployment**:
   ```bash
   docker-compose ps
   ```
   Ensure all services are running properly and check logs if needed:
   ```bash
   docker-compose logs -f [service_name]
   ```

### Production Considerations

1. **SSL/TLS Termination**: For production deployments, set up a reverse proxy (like Nginx or Traefik) for SSL/TLS termination.

2. **Data Persistence**: The Docker Compose configuration creates named volumes for database and Redis data. For production, consider mapping these volumes to specific host directories for easier backup management:
   ```yaml
   volumes:
     postgres_data:
       driver: local
       driver_opts:
         type: none
         device: /path/to/persistent/storage/postgres
         o: bind
     redis_data:
       driver: local
       driver_opts:
         type: none
         device: /path/to/persistent/storage/redis
         o: bind
     backend_data:
       driver: local
       driver_opts:
         type: none
         device: /path/to/persistent/storage/backend
         o: bind
   ```

3. **Backup Strategy**: Implement regular database backups:
   ```bash
   docker-compose exec db pg_dump -U postgres -d postgres > intric_backup_$(date +%Y%m%d).sql
   ```

4. **Monitoring**: Set up health checks and monitoring for the containers.

5. **Service Restart Policies**: All services are configured with `restart: unless-stopped` to automatically recover from failures.

## Maintenance

### Updating to a New Version
1. Update the `IMAGE_TAG` in your `.env` file
2. Pull the new images:
   ```bash
   docker-compose pull
   ```
3. Restart the services:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

### Scaling
For higher loads, consider:
- Scaling the worker service with multiple replicas
- Separate database server with optimized configuration
- Load balancing multiple frontend instances

### Troubleshooting

#### Common Issues

1. **Database Connection Failures**:
   - Check `POSTGRES_PASSWORD` is correctly set
   - Verify database service is healthy: `docker-compose ps db`
   - Check logs: `docker-compose logs db`

2. **Frontend Can't Reach Backend**:
   - Verify network connectivity between containers
   - Check `INTRIC_BACKEND_URL` is set correctly
   - Check logs: `docker-compose logs frontend`

3. **Authentication Issues**:
   - Ensure `JWT_SECRET` is consistent across services
   - Check MobilityGuard settings if using OIDC

4. **Worker Not Processing Tasks**:
   - Check Redis connection: `docker-compose exec redis redis-cli ping`
   - Verify worker logs: `docker-compose logs worker`

5. **Registry Authentication Issues**:
   - Check if you can log in to your registry: `docker login ${NEXUS_REGISTRY}`
   - Verify your credentials are correctly set in your CI/CD pipeline

## Support

For additional support or questions, please contact your system administrator or refer to the project documentation.