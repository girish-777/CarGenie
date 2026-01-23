# Quick Start Guide

## Build and Run Database Container

### Step 1: Build the Image

From the **project root** directory:

```bash
docker build -t ai-automobile-db:latest -f docker/Dockerfile .
```

Or use the build script:

```bash
bash docker/build.sh
```

### Step 2: Run the Container

```bash
cd docker
docker-compose up -d
```

Or use the run script (from project root):

```bash
bash docker/run.sh
```

### Step 3: Verify

Check that the container is running:

```bash
docker ps | grep ai-automobile-db
```

View logs:

```bash
docker logs ai-automobile-db
```

## Connect Backend to Database

### Method 1: Using Docker Compose (Recommended)

1. Update `docker/docker-compose.backend.yml` with your backend configuration
2. Run:

```bash
cd docker
docker-compose -f docker-compose.backend.yml up -d
```

### Method 2: Manual Volume Mount

When running your backend container, mount the database volume:

```bash
docker run -d \
  --name backend \
  --volumes-from ai-automobile-db \
  -p 8000:8000 \
  your-backend-image
```

Or use the named volume:

```bash
docker run -d \
  --name backend \
  -v docker_db-storage:/app/db_deploy \
  -e DATABASE_URL=sqlite:////app/db_deploy/automobile.db \
  -p 8000:8000 \
  your-backend-image
```

## Database Paths

When the database volume is mounted to your backend:

- **SQLite:** `/app/db_deploy/automobile.db`
- **ChromaDB:** `/app/db_deploy/chroma_db/`

Update your backend configuration to use these paths, or set the `DATABASE_URL` environment variable.

## Stop and Remove

```bash
cd docker
docker-compose down
```

To also remove the volume (deletes all data):

```bash
docker-compose down -v
```

