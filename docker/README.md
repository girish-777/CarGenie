# Docker Database Setup

This folder contains Docker configuration for the AI Automobile Website databases (SQLite and ChromaDB).

## Overview

The database setup uses Docker volumes to persist SQLite and ChromaDB files. Since both are file-based databases, we use a data container approach with named volumes.

## Files

- **Dockerfile** - Creates a Docker image containing the database files
- **docker-compose.yml** - Standalone database container setup
- **docker-compose.backend.yml** - Example configuration showing how to connect backend to database
- **.dockerignore** - Files to exclude from Docker build

## Quick Start

### Option 1: Build and Run Database Container Only

1. **Build the database image:**
   ```bash
   # From project root
   docker build -t ai-automobile-db:latest -f docker/Dockerfile .
   ```

2. **Run with docker-compose:**
   ```bash
   docker-compose up -d
   ```

3. **Verify the container is running:**
   ```bash
   docker ps
   ```

### Option 2: Use with Backend (Recommended)

1. **Build the database image first:**
   ```bash
   # From project root
   docker build -t ai-automobile-db:latest -f docker/Dockerfile .
   ```

2. **Update docker-compose.backend.yml** with your backend configuration

3. **Run both services:**
   ```bash
   docker-compose -f docker-compose.backend.yml up -d
   ```

## Database Volume

The databases are stored in a Docker named volume called `db-storage`. This ensures:
- Data persists even if containers are removed
- Easy backup and restore
- Shared access between containers

### Accessing the Database Volume

**View volume details:**
```bash
docker volume inspect docker_db-storage
```

**Backup the database:**
```bash
# Create a backup container
docker run --rm -v docker_db-storage:/data -v $(pwd):/backup alpine tar czf /backup/db-backup.tar.gz /data
```

**Restore from backup:**
```bash
# Restore from backup
docker run --rm -v docker_db-storage:/data -v $(pwd):/backup alpine sh -c "cd /data && tar xzf /backup/db-backup.tar.gz"
```

## Connecting Backend to Database

### Method 1: Using Docker Compose (Recommended)

Use the `docker-compose.backend.yml` file and mount the volume:

```yaml
volumes:
  - db-storage:/app/db_deploy
```

Then update your backend's `config.py` to use `/app/db_deploy/automobile.db` or set `DATABASE_URL` environment variable.

### Method 2: Using Volume Mounts Directly

If running backend separately, mount the volume:

```bash
docker run -d \
  --name backend \
  --volumes-from ai-automobile-db \
  -v /path/to/backend:/app \
  your-backend-image
```

### Method 3: Bind Mount (Development)

For development, you can bind mount the local `db_deploy` folder:

```bash
docker run -d \
  --name backend \
  -v $(pwd)/db_deploy:/app/db_deploy \
  your-backend-image
```

## Environment Variables

The backend can use these environment variables to connect:

- `DATABASE_URL` - SQLite database path (default: `sqlite:///db_deploy/automobile.db`)
- For ChromaDB, the path is set in `vectordb.py` to use `/data/chroma_db` or mounted volume

## Database Paths in Container

- **SQLite:** `/data/automobile.db` (in db container) or `/app/db_deploy/automobile.db` (when mounted to backend)
- **ChromaDB:** `/data/chroma_db` (in db container) or `/app/db_deploy/chroma_db` (when mounted to backend)

## Troubleshooting

### Database files not found

1. Check if the volume exists:
   ```bash
   docker volume ls
   ```

2. Check container logs:
   ```bash
   docker logs ai-automobile-db
   ```

3. Verify files in container:
   ```bash
   docker exec -it ai-automobile-db ls -la /data
   ```

### Backend cannot connect

1. Ensure the volume is mounted correctly in backend container
2. Check the `DATABASE_URL` environment variable or config
3. Verify file permissions (SQLite needs write access)

### Reset Database

To start fresh:

```bash
# Stop and remove containers
docker-compose down

# Remove the volume (WARNING: This deletes all data!)
docker volume rm docker_db-storage

# Rebuild and start
docker-compose up -d
```

## Production Considerations

For production, consider:

1. **Regular Backups:** Set up automated backups of the `db-storage` volume
2. **Volume Location:** Use a specific volume driver or bind mount to a known location
3. **Permissions:** Ensure proper file permissions for database files
4. **Monitoring:** Monitor disk space for SQLite and ChromaDB files
5. **Migration to PostgreSQL:** For production, consider migrating from SQLite to PostgreSQL for better concurrency

## Notes

- SQLite and ChromaDB are file-based, so they work well with Docker volumes
- The database container is a "data-only" container that just holds the files
- For better performance in production, consider using PostgreSQL instead of SQLite
- ChromaDB can also be run as a separate service if needed

