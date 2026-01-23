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

# Create server.py template in a safe location using printf for proper escaping
RUN printf 'from http.server import SimpleHTTPRequestHandler, HTTPServer\n' > /server.py.template && \
    printf 'import os\n' >> /server.py.template && \
    printf 'os.chdir("/data")\n' >> /server.py.template && \
    printf 'server = HTTPServer(("0.0.0.0", 8080), SimpleHTTPRequestHandler)\n' >> /server.py.template && \
    printf 'server.serve_forever()\n' >> /server.py.template

# Also create it directly in /data during build (will be overwritten by volume, but entrypoint will restore)
RUN cp /server.py.template /data/server.py

# Create entrypoint script that ensures server.py exists
RUN printf '#!/bin/sh\n' > /entrypoint.sh && \
    printf 'if [ ! -f /data/server.py ]; then\n' >> /entrypoint.sh && \
    printf '  cp /server.py.template /data/server.py\n' >> /entrypoint.sh && \
    printf 'fi\n' >> /entrypoint.sh && \
    printf 'exec python3 /data/server.py\n' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Create a volume for persistent storage
VOLUME ["/data"]

# Keep container running with HTTP server
CMD ["/entrypoint.sh"]

