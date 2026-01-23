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

# Expose a port for Render (required for Web Service)
EXPOSE 8080

# Install Python for simple HTTP server
RUN apk add --no-cache python3

# Copy server.py file (no escaping issues!)
COPY docker/server.py /server.py.template

# Create entrypoint script that ensures server.py exists in /data
RUN echo '#!/bin/sh' > /entrypoint.sh && \
    echo 'if [ ! -f /data/server.py ]; then' >> /entrypoint.sh && \
    echo '  cp /server.py.template /data/server.py' >> /entrypoint.sh && \
    echo 'fi' >> /entrypoint.sh && \
    echo 'exec python3 /data/server.py' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Create a volume for persistent storage
VOLUME ["/data"]

# Keep container running with HTTP server
CMD ["/entrypoint.sh"]

