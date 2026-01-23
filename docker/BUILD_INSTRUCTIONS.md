# Building the Database Docker Image

## Prerequisites

1. **Install Docker Desktop for Windows**
   - Download from: https://www.docker.com/products/docker-desktop/
   - Install and restart your computer
   - Make sure Docker Desktop is running

## Build Command

Once Docker is installed and running, execute this command from the **project root** directory:

```bash
docker build -t ai-automobile-db:latest -f docker/Dockerfile .
```

## Verify the Image

After building, verify the image was created:

```bash
docker images | grep ai-automobile-db
```

You should see:
```
ai-automobile-db   latest   <image-id>   <size>   <time>
```

## Run the Container

After building, you can run the container:

```bash
cd docker
docker-compose up -d
```

Or manually:

```bash
docker run -d \
  --name ai-automobile-db \
  -v db-storage:/data \
  ai-automobile-db:latest
```

## Alternative: Use the Build Script

If you have Git Bash or WSL installed:

```bash
bash docker/build.sh
```

## Troubleshooting

### Docker not found
- Make sure Docker Desktop is installed and running
- Restart your terminal/PowerShell after installing Docker
- Check Docker is in PATH: `where docker` (should show Docker path)

### Build fails
- Make sure you're in the project root directory
- Verify `db_deploy` folder exists with database files
- Check Docker Desktop is running (look for Docker icon in system tray)

### Permission errors
- Run PowerShell as Administrator
- Or ensure Docker Desktop has proper permissions

