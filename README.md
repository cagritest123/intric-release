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

## Deployment Guide

### Prerequisites
- Docker Engine 20.10.x or later
- Docker Compose 2.x or later
- Access to a Docker registry containing Intric images

### Configuration

#### Environment Variables

The Intric platform is configured through environment variables defined in the `.env` file:

**Image Settings**
- `NEXUS_REGISTRY`: URL of your Docker registry
- `IMAGE_TAG`: Version tag of the images to deploy

**Network Settings**
- `SERVICE_FQDN_FRONTEND`: Frontend domain name
- `SERVICE_FQDN_BACKEND`: Backend domain name
- `FRONTEND_PORT`: Port for the frontend service (default: 3000)
- `BACKEND_PORT`: Port for the backend service (default: 8123)

**Database Settings**
- `POSTGRES_USER`: Database username
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_PORT`: Database port
- `POSTGRES_DB`: Database name

**Security Settings**
- `JWT_SECRET`: Secret key for JWT tokens
- `JWT_AUDIENCE`: JWT audience claim
- `JWT_ISSUER`: JWT issuer claim
- `JWT_EXPIRY_TIME`: JWT token expiry time
- `JWT_ALGORITHM`: Algorithm used for JWT
- `JWT_TOKEN_PREFIX`: Prefix for JWT token in Authorization header

**API Configuration**
- `API_PREFIX`: Prefix for API routes
- `API_KEY_LENGTH`: Length of API keys
- `API_KEY_HEADER_NAME`: Header name for API key

**File Upload Limits**
- `UPLOAD_FILE_TO_SESSION_MAX_SIZE`: Maximum file size for session uploads
- `UPLOAD_IMAGE_TO_SESSION_MAX_SIZE`: Maximum image size for session uploads
- `UPLOAD_MAX_FILE_SIZE`: Maximum file size for general uploads
- `TRANSCRIPTION_MAX_FILE_SIZE`: Maximum file size for transcription
- `MAX_IN_QUESTION`: Maximum files in question

**Feature Flags**
- `USING_ACCESS_MANAGEMENT`: Enable/disable access management
- `USING_AZURE_MODELS`: Enable/disable Azure models

**API Keys**
- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key
- `AZURE_API_KEY`: Azure API key
- `AZURE_MODEL_DEPLOYMENT`: Azure model deployment name
- `AZURE_ENDPOINT`: Azure API endpoint
- `AZURE_API_VERSION`: Azure API version

**Authentication**
- `MOBILITYGUARD_DISCOVERY_ENDPOINT`: MobilityGuard discovery endpoint
- `MOBILITYGUARD_CLIENT_ID`: MobilityGuard client ID
- `MOBILITYGUARD_CLIENT_SECRET`: MobilityGuard client secret

**Frontend Specific**
- `MOBILITY_GUARD_AUTH`: MobilityGuard auth URL
- `SHOW_TEMPLATES`: Enable/disable templates display
- `FEEDBACK_FORM_URL`: URL for feedback form

**Logging**
- `LOGLEVEL`: Log level (DEBUG, INFO, WARNING, ERROR)

### Deployment Steps

1. **Prepare your environment file**:
   ```bash
   cp .env.example .env
   nano .env  # Edit with your values
   ```

2. **Start the services**:
   ```bash
   docker-compose up -d
   ```

3. **Initialize the database** (first time only):
   ```bash
   docker-compose --profile init up db-init
   ```

## Building Docker Images

The following instructions are for development teams who need to build and push updated images:

### Backend Image

To build the backend image:

```bash
cd backend
docker build -t ${NEXUS_REGISTRY}/intric/backend:${IMAGE_TAG} .
docker push ${NEXUS_REGISTRY}/intric/backend:${IMAGE_TAG}
```

### Frontend Image

To build the frontend image:

```bash
cd frontend
docker build -t ${NEXUS_REGISTRY}/intric/frontend:${IMAGE_TAG} --build-arg INTRIC_BACKEND_URL=http://backend:8123 .
docker push ${NEXUS_REGISTRY}/intric/frontend:${IMAGE_TAG}
```

## Maintenance

### Updating the Application
```bash
# Update IMAGE_TAG in .env, then:
docker-compose pull
docker-compose down
docker-compose up -d
```

### Database Backups
```bash
docker-compose exec db pg_dump -U postgres -d postgres > intric_backup_$(date +%Y%m%d).sql
```

### Viewing Logs
```bash
docker-compose logs -f [service_name]
```

## Troubleshooting

### Common Issues

1. **Database Connection Failures**:
   - Check `POSTGRES_PASSWORD` is correctly set
   - Verify database service is healthy: `docker-compose ps db`

2. **Frontend Can't Reach Backend**:
   - Verify network connectivity between containers
   - Check `INTRIC_BACKEND_URL` is set correctly

3. **Authentication Issues**:
   - Ensure `JWT_SECRET` is consistent across services
   - Check MobilityGuard settings if used

## Support

For additional support or questions, please contact your system administrator or refer to the project documentation.