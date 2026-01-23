# Database Deployment Folder

This folder contains all database-related files and scripts for deploying and managing the database for the AI Automobile Website backend.

## Contents

### Database Files
- **automobile.db** - Main SQLite database file containing all application data
- **chroma_db/** - ChromaDB vector database folder for storing car embeddings

### Database Setup Scripts
- **setup.py** - Initialize database tables (creates schema)
- **seed_data.py** - Populate database with sample car data and create admin user
- **create_admin_user.py** - Create admin user with default credentials

### Database Migration Scripts
- **add_engine_condition.py** - Add engine_condition column to cars table
- **add_price_history_table.py** - Add price_history table to database

### Data Management Scripts
- **generate_embeddings.py** - Generate and store embeddings for all cars in ChromaDB
- **add_car_descriptions.py** - Add descriptions to cars
- **assign_car_images.py** - Assign local images to cars
- **sync_cars_to_images.py** - Sync database cars with available images
- **update_car_prices.py** - Update car prices based on engine condition
- **update_cars_to_used.py** - Update all cars to be used cars with realistic mileage

## Deployment Instructions

### Initial Setup

1. **Initialize Database Schema**
   ```bash
   python setup.py
   ```
   This creates all necessary database tables.

2. **Run Migrations (if needed)**
   ```bash
   python add_engine_condition.py
   python add_price_history_table.py
   ```

3. **Seed Initial Data**
   ```bash
   python seed_data.py
   ```
   This populates the database with sample cars and creates an admin user.

4. **Create Admin User (if not done by seed_data.py)**
   ```bash
   python create_admin_user.py
   ```
   Default credentials:
   - Email: `admin@cargenie.com`
   - Password: `admin123`

5. **Generate Embeddings (requires OpenAI API key)**
   ```bash
   python generate_embeddings.py
   ```
   Make sure to set `OPENAI_API_KEY` in your `.env` file before running this.

### Database Location

The database files are configured to be in this `db_deploy` folder:
- SQLite database: `db_deploy/automobile.db`
- ChromaDB: `db_deploy/chroma_db/`

The backend application is configured to connect to these files automatically. The paths are set in:
- `backend/app/core/config.py` - SQLite database path
- `backend/app/core/vectordb.py` - ChromaDB path

### Running Scripts

All scripts in this folder are configured to:
1. Go up one level to the project root
2. Access the `backend` folder for imports
3. Connect to the database files in this `db_deploy` folder

Example:
```bash
# From project root
cd db_deploy
python seed_data.py
```

Or from project root:
```bash
python db_deploy/seed_data.py
```

### Backup and Restore

**Backup:**
```bash
# Backup SQLite database
cp automobile.db automobile.db.backup

# Backup ChromaDB (copy entire folder)
cp -r chroma_db chroma_db.backup
```

**Restore:**
```bash
# Restore SQLite database
cp automobile.db.backup automobile.db

# Restore ChromaDB
cp -r chroma_db.backup chroma_db
```

### Notes

- All database files should remain in this `db_deploy` folder
- The backend application expects the database files to be in this location
- Do not move database files outside of this folder without updating the configuration
- Keep regular backups of the database files, especially before major updates

