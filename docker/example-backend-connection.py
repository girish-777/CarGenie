"""
Example: How to connect backend to the database container

This file shows the configuration changes needed in your backend
to connect to the database running in Docker.
"""

# Option 1: Update backend/app/core/config.py
# Change the database path to use the mounted volume:
"""
# In backend/app/core/config.py
_db_path = os.path.join('/app', 'db_deploy', 'automobile.db').replace('\\', '/')
# Or use environment variable:
DATABASE_URL: str = os.getenv('DATABASE_URL', f"sqlite:///{_db_path}")
"""

# Option 2: Use environment variable in docker-compose
# In docker-compose.backend.yml:
"""
environment:
  - DATABASE_URL=sqlite:////app/db_deploy/automobile.db
"""

# Option 3: For ChromaDB, update backend/app/core/vectordb.py
# Change the path to use mounted volume:
"""
_chroma_db_path = os.path.join('/app', 'db_deploy', 'chroma_db').replace('\\', '/')
"""

# When running backend in Docker, mount the database volume:
"""
docker run -d \
  --name backend \
  -v docker_db-storage:/app/db_deploy \
  -e DATABASE_URL=sqlite:////app/db_deploy/automobile.db \
  your-backend-image
"""

