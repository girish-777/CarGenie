CarGenie - AI-Powered Automobile Marketplace

An intelligent car marketplace powered by AI, featuring advanced search, personalized recommendations, and an AI chatbot assistant.

================================================================================
TABLE OF CONTENTS
================================================================================

- Overview
- Features
- System Architecture
- Technology Stack
- Quick Start
- Project Structure
- API Documentation
- Advanced Search Feature
- MCP Server
- Development
- Documentation
- Contributing
- License

================================================================================
OVERVIEW
================================================================================

CarGenie is a modern, AI-powered automobile marketplace that helps users discover, compare, and make informed decisions about cars. The platform combines traditional e-commerce features with cutting-edge AI capabilities to provide a superior car shopping experience.

Key Highlights:

- AI-Powered: Chatbot assistant, intelligent recommendations, and review summarization
- Advanced Search: Typo-tolerant fuzzy search (like Google)
- Personalized: Recommendations based on user preferences
- Smart Comparisons: Side-by-side car comparison
- Interactive: Global chatbot available on all pages
- Secure: JWT authentication and password hashing

================================================================================
FEATURES
================================================================================

Core Features

1. User Authentication
   - Secure registration and login
   - JWT token-based authentication
   - Password hashing with bcrypt
   - User profiles and preferences

2. Car Listings and Browsing
   - Grid view with pagination (12 cars per page)
   - Advanced filtering (make, model, year, price, fuel type, transmission)
   - Multiple sorting options (price, year, mileage, newest)
   - Responsive design for all devices

3. Advanced Search (Fuzzy Search)
   - Word-by-word typo tolerance: Corrects misspellings like "tuyata" to "Toyota"
   - Similarity-based matching: Finds cars even with typos
   - Smart threshold: Only corrects when similarity is high enough (72-74%)
   - Google-like experience: Shows "Did you mean?" suggestions
   - Works across all fields: Searches in make, model, and descriptions

4. Car Details
   - Comprehensive car information
   - Specifications (engine, horsepower, MPG, etc.)
   - Reliability and safety scores
   - Image gallery
   - User reviews and ratings
   - Similar cars recommendations

5. Favorites System
   - Save cars for later viewing
   - Quick access to favorite cars
   - Persistent storage per user

6. Car Comparison
   - Compare up to multiple cars side-by-side
   - Compare specifications, prices, and features
   - Visual comparison table

7. Reviews and Ratings
   - Write and read reviews
   - 1-5 star ratings
   - AI-powered review summarization
   - One review per user per car

AI Features

8. AI Chatbot Assistant
   - Global floating widget (available on all pages)
   - Context-aware (knows which car you're viewing)
   - General car buying advice
   - RAG (Retrieval Augmented Generation) for accurate answers
   - Conversation history
   - Smart follow-up suggestions

9. Personalized Recommendations
   - AI-powered car recommendations on homepage
   - Based on user favorites and preferences
   - Displays 6 recommended cars
   - Similarity scoring

10. Similar Cars Recommendation
    - Vector-based similarity search using ChromaDB
    - Finds cars similar to the one you're viewing
    - Uses OpenAI embeddings for semantic matching

11. AI Review Summarization
    - Automatically summarizes all reviews for a car
    - Highlights pros and cons
    - Uses OpenAI GPT-3.5-turbo

12. Price Predictions
    - Future price predictions
    - Based on historical data and trends
    - Helps users make informed decisions

================================================================================
SYSTEM ARCHITECTURE
================================================================================

High-Level Architecture

The system follows a three-tier architecture:

Client Layer
- Browser (Frontend)
- Mobile (Future)
- Desktop (Future)

Backend API Layer
- FastAPI Application
  - Auth endpoints
  - Cars endpoints
  - Reviews endpoints
  - AI endpoints
  - Recommendations endpoints
  - Favorites endpoints
  - Predictions endpoints

Database Layer
- SQLite/PostgreSQL (Relational Database)
  - Users table
  - Cars table
  - Reviews table
  - Favorites table
  - Alerts table

- ChromaDB (Vector Database)
  - Car embeddings
  - Similarity search

External Services
- OpenAI API
  - Embeddings generation
  - Chatbot (GPT)
  - Review summarization

Component Architecture

Frontend (Static HTML/CSS/JS)
- index.html (Homepage)
- listings.html (Car listings)
- car-detail.html (Car details)
- favorites.html (User favorites)
- compare.html (Car comparison)
- login.html / signup.html (Authentication)
- js/ directory contains JavaScript files:
  - main.js (Navigation, auth state)
  - listings.js (Car listings, search)
  - car-detail.js (Car details)
  - chatbot.js (AI chatbot)
  - recommendations.js (Personalized recommendations)
  - And other utility files

Backend (FastAPI)
- app/main.py (FastAPI app, CORS, routes)
- app/api/v1/ contains API endpoints:
  - auth.py (Authentication)
  - cars.py (Car listings, search)
  - ai.py (Chatbot, similar cars)
  - reviews.py (Reviews)
  - favorites.py (Favorites)
  - recommendations.py (Personalized recommendations)
  - predictions.py (Price predictions)
- app/models/ (SQLAlchemy models)
- app/schemas/ (Pydantic schemas)
- app/core/ contains core utilities:
  - config.py (Settings)
  - security.py (Password hashing, JWT)
  - embeddings.py (OpenAI embeddings)
  - vectordb.py (ChromaDB integration)
- app/db/database.py (Database connection)
- seed_data.py (Database seeding)

MCP Server
- mcp_server/server.py (MCP server implementation)
- mcp_server/tools/ contains MCP tools:
  - car_search.py
  - car_details.py
  - recommendations.py

================================================================================
TECHNOLOGY STACK
================================================================================

Frontend
- HTML5: Structure and semantic markup
- CSS3: Styling and responsive design
- JavaScript (Vanilla): Client-side interactivity
- No Framework: Pure JavaScript for simplicity and performance

Backend
- FastAPI: Modern, fast Python web framework
- Python 3.13: Programming language
- SQLAlchemy: ORM for database operations
- Pydantic: Data validation and settings management
- Uvicorn: ASGI server

Database
- SQLite: Development database (file-based)
- PostgreSQL: Production database (recommended)
- ChromaDB: Vector database for AI embeddings

AI/ML Services
- OpenAI API:
  - text-embedding-3-small: Car embeddings (1536 dimensions)
  - gpt-3.5-turbo: Chatbot and review summarization

Authentication and Security
- JWT (JSON Web Tokens): Stateless authentication
- Bcrypt: Password hashing
- python-jose: JWT encoding/decoding

Additional Tools
- Alembic: Database migrations
- httpx: Async HTTP client (for MCP server)
- python-dotenv: Environment variable management

================================================================================
QUICK START
================================================================================

Prerequisites

- Python 3.13+ (or Python 3.10+)
- pip (Python package manager)
- Git (optional, for version control)

Installation Steps

1. Clone the repository (or download the project)
   git clone <repository-url>
   cd ai-automobile-website

2. Install dependencies
   pip install -r requirements.txt

3. Set up environment variables
   Copy the example .env file:
   cp .env.example .env
   
   Edit .env and add your OpenAI API key:
   OPENAI_API_KEY=your-api-key-here

4. Initialize the database
   python setup.py

5. Seed the database with sample data
   python backend/seed_data.py

6. Generate car embeddings (for AI features)
   python backend/generate_embeddings.py

7. Start the backend server
   cd backend
   python -m uvicorn app.main:app --reload
   
   Backend will run on http://localhost:8000

8. Open the frontend
   Option 1: Open frontend/index.html directly in your browser
   
   Option 2: Use a local server:
   cd frontend
   python -m http.server 8080
   
   Access at http://localhost:8080

Default Credentials

- Admin User: admin@cargenie.com / admin123
- Regular Users: Create account via signup page

================================================================================
PROJECT STRUCTURE
================================================================================

ai-automobile-website/
├── backend/                 # Backend API code
│   ├── app/
│   │   ├── api/v1/         # API endpoints
│   │   ├── core/           # Core utilities (config, security, AI)
│   │   ├── db/             # Database connection
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   └── main.py         # FastAPI application
│   ├── alembic/            # Database migrations
│   ├── generate_embeddings.py  # Generate car embeddings
│   └── seed_data.py        # Seed database with sample data
│
├── frontend/               # Frontend code
│   ├── index.html          # Homepage
│   ├── listings.html       # Car listings page
│   ├── car-detail.html     # Car detail page
│   ├── favorites.html      # User favorites
│   ├── compare.html        # Car comparison
│   ├── login.html          # Login page
│   ├── signup.html         # Signup page
│   ├── css/                # Stylesheets
│   ├── js/                 # JavaScript files
│   └── images/             # Car images
│
├── mcp_server/             # MCP server for AI tools
│   ├── server.py           # MCP server implementation
│   └── tools/              # MCP tools
│
├── chroma_db/              # ChromaDB vector database (auto-generated)
├── automobile.db           # SQLite database (auto-generated)
│
├── requirements.txt        # Python dependencies
├── setup.py                # Database initialization script
├── FEATURE_SYSTEM_DESIGN.md  # Feature design documentation
├── SDLC.md                 # Software Development Life Cycle
└── README.md               # This file

================================================================================
API DOCUMENTATION
================================================================================

Base URL
http://localhost:8000

Authentication
Most endpoints require JWT authentication. Include the token in the Authorization header:
Authorization: Bearer <your-jwt-token>

Main Endpoints

Authentication
- POST /api/v1/auth/signup - Register new user
- POST /api/v1/auth/login - Login and get JWT token
- GET /api/v1/auth/me - Get current user info

Cars
- GET /api/v1/cars/ - List cars with filters and pagination
- GET /api/v1/cars/{car_id} - Get car details
- GET /api/v1/cars/makes/list - Get all car makes
- GET /api/v1/cars/fuel-types/list - Get all fuel types

Favorites
- GET /api/v1/favorites - Get user's favorites
- POST /api/v1/favorites - Add car to favorites
- DELETE /api/v1/favorites/{car_id} - Remove from favorites

Reviews
- GET /api/v1/reviews/car/{car_id} - Get reviews for a car
- POST /api/v1/reviews - Create a review
- PUT /api/v1/reviews/{review_id} - Update review
- DELETE /api/v1/reviews/{review_id} - Delete review

AI Features
- POST /api/v1/ai/chat/{car_id} - Chatbot (car-specific)
- POST /api/v1/ai/chat/general - Chatbot (general questions)
- GET /api/v1/ai/cars/{car_id}/similar - Get similar cars

Recommendations
- GET /api/v1/recommendations - Get personalized recommendations

Predictions
- GET /api/v1/predictions/car/{car_id} - Get price predictions

Interactive API Docs
FastAPI automatically generates interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

================================================================================
ADVANCED SEARCH FEATURE
================================================================================

Overview
The Advanced Search feature provides typo-tolerant fuzzy search similar to Google's search engine. It automatically corrects misspellings and finds relevant cars even when users make typing errors.

How It Works

1. Word-by-Word Correction
   - Searches are tokenized into individual words
   - Each word is corrected independently
   - Example: "tuyata camry" becomes "Toyota camry"

2. Vocabulary Building
   The system builds a vocabulary from:
   - All car makes (Toyota, BMW, Mercedes-Benz, etc.)
   - All car models (Camry, i4, C-Class, etc.)
   - All words from car descriptions (minimum 3 characters)

3. Similarity Matching
   - Uses Python's difflib.SequenceMatcher for similarity calculation
   - Compares normalized strings (lowercase, no punctuation)
   - Returns similarity score (0.0 to 1.0)

4. Smart Thresholds
   - Short words (4 characters or less): 74% similarity threshold
     Example: "binz" to "benz" (75% match) - Corrected
   - Longer words: 72% similarity threshold
     Example: "tuyata" to "Toyota" (80% match) - Corrected
   - Too different: No correction
     Example: "hzhz" to "benz" (25% match) - Not corrected

5. Search Flow

   User searches: "tuyata camry"
   ↓
   [No exact results found]
   ↓
   Split into words: ["tuyata", "camry"]
   ↓
   Build vocabulary from database
   ↓
   Fix "tuyata":
     Compare with "Toyota" → 80% match - Corrected
     Compare with "BMW" → 20% match - Not corrected
     Best match: "Toyota"
   ↓
   Fix "camry":
     Compare with "Camry" → 100% match - Corrected
     Best match: "Camry"
   ↓
   Rebuild: "Toyota Camry"
   ↓
   Search again → Find results
   ↓
   Show: "Showing results for Toyota Camry (from 'tuyata camry')"

Implementation Details

Backend (backend/app/api/v1/cars.py):
- Tokenizes search query
- Builds vocabulary from car data
- Performs fuzzy matching for each token
- Re-runs search with corrected terms
- Returns correction metadata

Frontend (frontend/js/listings.js):
- Displays correction hint when search is corrected
- Shows: "Showing results for Toyota (from 'tuyata')"

Example Searches

User Input: binz
Corrected To: benz
Result: Shows Mercedes-Benz cars

User Input: tuyata
Corrected To: Toyota
Result: Shows Toyota cars

User Input: tuyata camry
Corrected To: Toyota camry
Result: Shows Toyota Camry cars

User Input: hzhz
Corrected To: (no correction)
Result: No results (too different)

User Input: mercedez
Corrected To: Mercedes
Result: Shows Mercedes-Benz cars

================================================================================
MCP SERVER
================================================================================

CarGenie includes a Model Context Protocol (MCP) server that exposes backend capabilities as callable tools for AI assistants like Cursor or Claude Desktop.

What is MCP?
MCP allows AI assistants to interact with your application through standardized tools, enabling them to search cars, get details, and provide recommendations.

Tools Exposed

1. search_cars
   - Search cars with filters (make, model, year, price, etc.)
   - Returns paginated results

2. get_car_details
   - Get detailed information about a specific car by ID
   - Returns full car data including specs and scores

3. get_recommendations
   - Get personalized car recommendations
   - Supports optional user authentication

Running the MCP Server

From project root:
python -m mcp_server

Configuration

Set environment variable (optional):
set CARGENIE_BACKEND_URL=http://localhost:8000

Usage with Cursor/Claude Desktop

The MCP server communicates via JSON-RPC over stdin/stdout, allowing AI assistants to:
- Search for cars based on user queries
- Get car details when users ask about specific cars
- Provide personalized recommendations

See mcp_server/README.md for detailed documentation.

================================================================================
DEVELOPMENT
================================================================================

Running in Development Mode

Backend (with auto-reload):
cd backend
python -m uvicorn app.main:app --reload

Frontend (using Python HTTP server):
cd frontend
python -m http.server 8080

Database Migrations

Create a new migration:
cd backend
alembic revision --autogenerate -m "Description of changes"

Apply migrations:
alembic upgrade head

Adding New Cars

1. Manual: Use the admin panel (if implemented) or database directly
2. Script: Modify backend/seed_data.py and run it
3. API: Use the admin endpoints (requires authentication)

Generating Embeddings

After adding new cars, regenerate embeddings:
python backend/generate_embeddings.py

Code Style

- Python: Follow PEP 8 style guide
- JavaScript: Use modern ES6+ syntax
- Comments: Document complex logic

================================================================================
DOCUMENTATION
================================================================================

Available Documentation

1. README.md (This file)
   - Project overview, setup, and quick reference

2. FEATURE_SYSTEM_DESIGN.md
   - Detailed explanation of each feature
   - System diagrams and data flows
   - Component descriptions

3. SDLC.md
   - Software Development Life Cycle
   - Development phases and timeline
   - Methodology and best practices

4. API Documentation
   - Auto-generated by FastAPI at /docs
   - Interactive Swagger UI
   - ReDoc format available

5. MCP Server Documentation
   - mcp_server/README.md
   - Tool descriptions and usage

Reading Order

1. Start with README.md (this file) for overview
2. Read FEATURE_SYSTEM_DESIGN.md for feature details
3. Check SDLC.md for development process
4. Use /docs endpoint for API reference

================================================================================
TESTING
================================================================================

Manual Testing Checklist

- User registration and login
- Browse car listings
- Search with typos (fuzzy search)
- Filter cars by various criteria
- View car details
- Add/remove favorites
- Compare cars
- Write and edit reviews
- Use AI chatbot
- View personalized recommendations
- Check similar cars recommendations

Test Accounts

- Admin: admin@cargenie.com / admin123
- Regular User: Create via signup

================================================================================
SECURITY
================================================================================

Implemented Security Features

- Password Hashing: Bcrypt with salt
- JWT Tokens: Secure, stateless authentication
- CORS: Configured for localhost development
- Input Validation: Pydantic schemas validate all inputs
- SQL Injection Protection: SQLAlchemy ORM prevents SQL injection
- XSS Protection: HTML escaping in frontend

Security Best Practices

- Never commit .env file (already in .gitignore)
- Use strong passwords in production
- Enable HTTPS in production
- Regularly update dependencies
- Validate all user inputs

================================================================================
DEPLOYMENT
================================================================================

Production Checklist

- Set up PostgreSQL database
- Configure environment variables
- Set CORS_ORIGINS to production domain
- Generate secure SECRET_KEY
- Enable HTTPS
- Set up database backups
- Configure monitoring
- Generate embeddings for all cars
- Test all features in production environment

Recommended Hosting

Backend:
- Railway
- Render
- Heroku
- AWS EC2
- DigitalOcean

Frontend:
- Netlify
- Vercel
- GitHub Pages
- AWS S3 + CloudFront

Database:
- PostgreSQL on Railway/Render
- AWS RDS
- DigitalOcean Managed Database

================================================================================
CONTRIBUTING
================================================================================

Contributions are welcome! Here's how you can help:

1. Report Bugs: Open an issue describing the bug
2. Suggest Features: Propose new features or improvements
3. Submit Pull Requests: Follow the code style and include tests
4. Improve Documentation: Help make docs clearer

Development Workflow

1. Fork the repository
2. Create a feature branch (git checkout -b feature/amazing-feature)
3. Make your changes
4. Test thoroughly
5. Commit your changes (git commit -m 'Add amazing feature')
6. Push to the branch (git push origin feature/amazing-feature)
7. Open a Pull Request

================================================================================
LICENSE
================================================================================

This project is licensed under the MIT License - see the LICENSE file for details.

================================================================================
ACKNOWLEDGMENTS
================================================================================

- OpenAI for AI capabilities (embeddings, GPT)
- FastAPI for the excellent web framework
- ChromaDB for vector database capabilities
- SQLAlchemy for database ORM

================================================================================
SUPPORT
================================================================================

For questions, issues, or contributions:
- Open an issue on GitHub
- Check the documentation files
- Review the API docs at /docs

================================================================================
ROADMAP
================================================================================

Planned Features

- Mobile app (iOS/Android)
- Email notifications for price alerts
- Seller portal for listing cars
- Payment integration
- Advanced admin dashboard
- Image upload functionality
- Multi-language support
- Social sharing features

================================================================================
PROJECT STATUS
================================================================================

Component: Backend API
Status: Complete

Component: Frontend UI
Status: Complete

Component: Authentication
Status: Complete

Component: Car Listings
Status: Complete

Component: Advanced Search
Status: Complete

Component: AI Chatbot
Status: Complete

Component: Recommendations
Status: Complete

Component: Reviews System
Status: Complete

Component: MCP Server
Status: Complete

Component: Testing
Status: Ongoing

Component: Deployment
Status: Planned

================================================================================

Last Updated: January 2026
Version: 1.0.0
Maintainer: CarGenie Development Team

Built with FastAPI, OpenAI, and modern web technologies
