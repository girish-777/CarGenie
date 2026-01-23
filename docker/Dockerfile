# Dockerfile for Database Container
# This container holds the SQLite and ChromaDB database files
# Build from project root: docker build -t ai-automobile-db:latest -f docker/Dockerfile .
FROM alpine:latest

# Install sqlite3 for database utilities (optional, for debugging)
RUN apk add --no-cache sqlite

# Create directory for databases
WORKDIR /data

# Copy database files from db_deploy
# Note: Build context should be project root, so db_deploy is at ./db_deploy
# Copy the entire db_deploy directory structure
COPY db_deploy/ /data/

# Ensure chroma_db directory exists (in case it's empty)
RUN mkdir -p /data/chroma_db

# Create a volume for persistent storage
VOLUME ["/data"]

# Keep container running (data-only container)
CMD ["tail", "-f", "/dev/null"]

