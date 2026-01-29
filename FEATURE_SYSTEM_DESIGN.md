CarGenie - Feature System Design Document

================================================================================
OVERVIEW
================================================================================

This document explains how each feature in CarGenie works in simple terms with diagrams that are compatible with Microsoft Word.

================================================================================
1. USER AUTHENTICATION SYSTEM
================================================================================

What It Does
Allows users to create accounts, log in, and securely access their personalized features.

How It Works - Flow Diagram

+------------------+
|      User        |
|    (Browser)     |
+------------------+
        |
        | Step 1: Enter email and password
        |
        v
+------------------+
|    Frontend      |
|  (login.html)    |
+------------------+
        |
        | Step 2: POST /api/v1/auth/login
        |
        v
+------------------+
|   Backend API    |
|   (auth.py)      |
+------------------+
        |
        | Step 3: Check credentials
        |
        v
+------------------+
|    Database      |
|  (users table)   |
+------------------+
        |
        | Step 4: Verify password hash
        |
        v
+------------------+
|  JWT Token       |
|  Generation      |
+------------------+
        |
        | Step 5: Return token
        |
        v
+------------------+
|    Frontend      |
| Store in         |
| localStorage     |
+------------------+

Components
- Frontend: Login/signup forms (login.html, signup.html)
- Backend: Auth endpoints (/api/v1/auth/login, /api/v1/auth/signup)
- Database: Users table stores encrypted passwords
- Security: Bcrypt password hashing, JWT tokens (30-min expiry)

Data Flow
1. User enters credentials
2. Frontend sends to backend API
3. Backend hashes password and checks database
4. If valid, creates JWT token
5. Token stored in browser's localStorage
6. Token sent with every authenticated request

================================================================================
2. CAR LISTINGS AND BROWSING
================================================================================

What It Does
Displays cars in a searchable, filterable grid with pagination.

How It Works - Flow Diagram

+------------------+
|      User        |
| Opens            |
| listings.html    |
+------------------+
        |
        | Step 1: Page loads
        |
        v
+------------------+
|  Frontend JS     |
| (listings.js)    |
+------------------+
        |
        | Step 2: GET /api/v1/cars?page=1&page_size=12
        |
        v
+------------------+
|   Backend API    |
|   (cars.py)      |
+------------------+
        |
        | Step 3: Query database with filters
        |
        v
+------------------+
|    Database      |
|  (cars table)    |
+------------------+
        |
        | Step 4: Return cars data
        |
        v
+------------------+
|    Frontend      |
| Render car       |
| cards in grid    |
+------------------+

Components
- Frontend: listings.html - Car grid display
- JavaScript: listings.js - Handles API calls and rendering
- Backend: /api/v1/cars endpoint
- Database: Cars table with indexes on make, year, price

Features
- Pagination: 12 cars per page
- Filtering: By make, model, year, price, fuel type, transmission
- Search: Text search in make, model, description
- Sorting: By price, year, mileage, newest

================================================================================
3. SEARCH AND FILTER SYSTEM
================================================================================

What It Does
Helps users find specific cars based on their preferences.

How It Works - Flow Diagram

+------------------+
|      User        |
| Sets Filters     |
| and Searches     |
+------------------+
        |
        | Step 1: User selects filters
        |
        v
+------------------+
|    Frontend      |
| Build Query      |
| String           |
+------------------+
        |
        | Step 2: GET /api/v1/cars?make=Toyota&min_price=20000&max_price=50000
        |
        v
+------------------+
|   Backend API    |
| Process          |
| Filters          |
+------------------+
        |
        | Step 3: Apply SQL filters
        |
        v
+------------------+
|    Database      |
| SQL WHERE        |
| conditions       |
+------------------+
        |
        | Step 4: Return filtered results
        |
        v
+------------------+
|    Frontend      |
| Update car       |
| grid             |
+------------------+

Filter Types
1. Text Filters: Make, model, description search
2. Range Filters: Year (min/max), price (min/max)
3. Category Filters: Fuel type, transmission, condition
4. Combined: Multiple filters work together

Implementation
- Frontend builds query parameters
- Backend validates and applies filters to SQL query
- Database uses indexes for fast filtering
- Results updated instantly without page reload

================================================================================
4. CAR DETAILS PAGE
================================================================================

What It Does
Shows comprehensive information about a single car.

How It Works - Flow Diagram

+------------------+
|      User        |
| Clicks on        |
| Car Card         |
+------------------+
        |
        | Step 1: Navigate to car-detail.html?id=5
        |
        v
+------------------+
|  Frontend JS     |
| (car-detail.js)  |
+------------------+
        |
        | Step 2-4: Multiple GET requests:
        |   - GET /api/v1/cars/5
        |   - GET /api/v1/reviews/car/5
        |   - GET /api/v1/ai/cars/5/similar
        |
        v
+------------------+
|   Backend API    |
| Multiple         |
| Endpoints        |
+------------------+
        |
        | Step 5: Fetch from database
        |
        v
+------------------+
|    Database      |
| cars, reviews,   |
| specs, scores    |
+------------------+
        |
        | Step 6: Return all data
        |
        v
+------------------+
|    Frontend      |
| Display:         |
| - Car info       |
| - Specs          |
| - Reviews        |
| - Similar cars   |
+------------------+

Components Displayed
- Basic Info: Make, model, year, price, mileage
- Specifications: Engine, horsepower, MPG, drivetrain
- Scores: Overall rating, reliability, safety
- Images: Car photo gallery
- Reviews: User reviews with ratings
- Similar Cars: AI-powered recommendations
- Actions: Favorite, compare buttons

================================================================================
5. FAVORITES SYSTEM
================================================================================

What It Does
Allows users to save cars they like for later viewing.

How It Works - Flow Diagram

+------------------+
|      User        |
| Clicks           |
| Heart Icon       |
+------------------+
        |
        | Step 1: POST /api/v1/favorites
        |         { car_id: 5, user_id: 2 }
        |
        v
+------------------+
|   Backend API    |
| (favorites.py)   |
+------------------+
        |
        | Step 2: Check authentication
        | Step 3: Insert into favorites table
        |
        v
+------------------+
|    Database      |
| favorites table  |
| (user_id, car_id)|
+------------------+
        |
        | Step 4: Success response
        |
        v
+------------------+
|    Frontend      |
| Update UI        |
| (Heart filled)   |
+------------------+

Components
- Frontend: Heart icon on car cards
- Backend: /api/v1/favorites endpoints
- Database: Favorites table (user_id, car_id)
- Features: 
  - Add/remove favorites
  - View all favorites on favorites.html
  - Check if car is favorited

Data Structure
favorites table:
- id (PRIMARY KEY)
- user_id (FOREIGN KEY -> users.id)
- car_id (FOREIGN KEY -> cars.id)
- created_at (timestamp)

================================================================================
6. CAR COMPARISON SYSTEM
================================================================================

What It Does
Allows users to compare multiple cars side-by-side.

How It Works - Flow Diagram

+------------------+
|      User        |
| Adds cars        |
| to compare       |
+------------------+
        |
        | Step 1: Click "Compare" button on cars
        |
        v
+------------------+
|  Frontend JS     |
| (compare.js)     |
| Store in         |
| localStorage     |
+------------------+
        |
        | Step 2: Navigate to compare.html
        | Step 3: GET /api/v1/cars/{id} for each car
        |
        v
+------------------+
|   Backend API    |
| Fetch car        |
| details          |
+------------------+
        |
        | Step 4: Get car data
        |
        v
+------------------+
|    Database      |
| cars + specs     |
+------------------+
        |
        | Step 5: Return data
        |
        v
+------------------+
|    Frontend      |
| Display          |
| comparison       |
| table            |
+------------------+

Components
- Frontend: compare.html - Comparison table
- JavaScript: compare.js - Manages comparison list
- Storage: Car IDs stored in localStorage
- Display: Side-by-side comparison of specs, price, features

Comparison Features
- Specifications: Engine, HP, MPG, drivetrain
- Price: Current price comparison
- Features: Key features highlighted
- Pros/Cons: Based on reviews and ratings

================================================================================
7. REVIEWS AND RATINGS SYSTEM
================================================================================

What It Does
Allows users to read and write reviews about cars.

How It Works - Viewing Reviews

+------------------+
|      User        |
| Views car        |
| detail page      |
+------------------+
        |
        | Step 1: GET /api/v1/reviews/car/5
        |
        v
+------------------+
|   Backend API    |
| (reviews.py)     |
+------------------+
        |
        | Step 2: Query reviews table
        |
        v
+------------------+
|    Database      |
| reviews table    |
+------------------+
        |
        | Step 3: Return reviews with user info
        |
        v
+------------------+
|    Frontend      |
| Display reviews  |
| with ratings     |
+------------------+

How It Works - Writing Reviews

+------------------+
|      User        |
| Writes           |
| Review           |
+------------------+
        |
        | Step 1: POST /api/v1/reviews
        |         { car_id, rating, title, content }
        |
        v
+------------------+
|   Backend API    |
| Validate and     |
| Check existing   |
+------------------+
        |
        | Step 2: Check: One review per user per car
        | Step 3: Insert into reviews table
        | Step 4: Trigger AI summary (background)
        |
        v
+------------------+
|    Database      |
| Store review     |
+------------------+
        |
        | Step 5: Background: Generate AI summary
        |
        v
+------------------+
|   OpenAI API     |
| Summarize        |
| all reviews      |
+------------------+
        |
        | Step 6: Update review with ai_summary
        |
        v
+------------------+
|    Database      |
| ai_summary       |
| field updated    |
+------------------+

Components
- Frontend: Review form on car detail page
- Backend: /api/v1/reviews endpoints
- Database: Reviews table with ai_summary field
- Rules: One review per user per car (can edit/delete)

Review Features
- Rating: 1-5 stars
- Title: Optional review title
- Content: Review text
- AI Summary: Auto-generated summary of all reviews
- Edit/Delete: Users can modify their own reviews

================================================================================
8. AI SIMILAR CARS RECOMMENDATION
================================================================================

What It Does
Finds cars similar to the one you're viewing using AI.

How It Works - Similarity Search

+------------------+
|      User        |
| Views car        |
| detail page      |
+------------------+
        |
        | Step 1: GET /api/v1/ai/cars/5/similar
        |
        v
+------------------+
|   Backend API    |
| (ai.py)          |
+------------------+
        |
        | Step 2: Get car embedding from ChromaDB
        |
        v
+------------------+
|   Vector DB      |
| (ChromaDB)       |
| Get car's        |
| embedding        |
+------------------+
        |
        | Step 3: Search for similar embeddings
        |         (cosine similarity)
        |
        v
+------------------+
|   Vector DB      |
| Returns 3        |
| similar car IDs  |
+------------------+
        |
        | Step 4: Fetch car details from database
        |
        v
+------------------+
|    Database      |
| Get car info     |
| for IDs          |
+------------------+
        |
        | Step 5: Return similar cars
        |
        v
+------------------+
|    Frontend      |
| Display          |
| similar cars     |
| section          |
+------------------+

How Embeddings Work - Initial Setup (One-time)

+------------------+
| Admin runs       |
| generate_        |
| embeddings.py    |
+------------------+
        |
        | Step 1: For each car:
        |         - Get car data (make, model, year, description)
        |         - Send to OpenAI API
        |
        v
+------------------+
|   OpenAI API     |
| text-embedding-  |
| 3-small          |
| Returns vector   |
| (1536 numbers)   |
+------------------+
        |
        | Step 2: Store in ChromaDB
        |
        v
+------------------+
|   ChromaDB       |
| Car ID +         |
| Embedding +      |
| Metadata         |
+------------------+

Similarity Search Details
- Vector Comparison: Uses cosine similarity to find similar vectors
- Similarity Score: Lower distance equals more similar
- Metadata Filtering: Can filter by price range, year, etc.
- Results: Returns top 3 most similar cars

Components
- Embedding Generation: generate_embeddings.py script
- Vector Storage: ChromaDB collection
- Similarity Search: ChromaDB query with cosine distance
- API: /api/v1/ai/cars/{car_id}/similar endpoint

================================================================================
9. AI REVIEW SUMMARIZATION
================================================================================

What It Does
Automatically creates a summary of all reviews for a car using AI.

How It Works

+------------------+
| New Review       |
| Submitted        |
+------------------+
        |
        | Step 1: Review saved to database
        | Step 2: Background task triggered
        |
        v
+------------------+
| Backend          |
| Background       |
| Task             |
+------------------+
        |
        | Step 3: Get all reviews for car
        |         (Need at least 2 reviews)
        |
        v
+------------------+
|    Database      |
| reviews table    |
+------------------+
        |
        | Step 4: Combine review texts
        |
        v
+------------------+
|   OpenAI API     |
| gpt-3.5-turbo    |
| Summarize        |
| reviews          |
+------------------+
        |
        | Step 5: Generated summary
        |         (200 words, pros/cons)
        |
        v
+------------------+
|    Database      |
| Update most      |
| recent review's  |
| ai_summary       |
+------------------+

Summary Content
- Common Themes: What reviewers mention most
- Pros: Positive aspects mentioned
- Cons: Negative aspects mentioned
- Overall Sentiment: General feeling about the car

Components
- Trigger: Background task after review submission
- AI Model: OpenAI GPT-3.5-turbo
- Storage: ai_summary field in reviews table
- Display: Shown on car detail page above reviews

================================================================================
10. AI CHATBOT ASSISTANT
================================================================================

What It Does
Provides an AI-powered chatbot that answers questions about cars.

How It Works - Car-Specific Chat

+------------------+
|      User        |
| Asks             |
| Question         |
+------------------+
        |
        | Step 1: POST /api/v1/ai/chat/{car_id}
        |         { message, conversation_history }
        |
        v
+------------------+
|   Backend API    |
| (ai.py)          |
+------------------+
        |
        | Step 2: Get car details from database
        |
        v
+------------------+
|    Database      |
| Car + specs +    |
| reviews          |
+------------------+
        |
        | Step 3: Build context (RAG)
        |         - Car specifications
        |         - Reviews summary
        |         - Features
        |
        v
+------------------+
|   OpenAI API     |
| gpt-3.5-turbo    |
| With context     |
+------------------+
        |
        | Step 4: AI generates response
        |         using car data
        |
        v
+------------------+
|    Frontend      |
| Display          |
| response in      |
| chat UI          |
+------------------+

How It Works - General Chat

+------------------+
|      User        |
| Asks general     |
| question         |
+------------------+
        |
        | Step 1: POST /api/v1/ai/chat/general
        |         { message, conversation_history }
        |
        v
+------------------+
|   Backend API    |
| (ai.py)          |
+------------------+
        |
        | Step 2: No car context needed
        |
        v
+------------------+
|   OpenAI API     |
| gpt-3.5-turbo    |
| General car      |
| advice           |
+------------------+
        |
        | Step 3: AI generates general response
        |
        v
+------------------+
|    Frontend      |
| Display          |
| response         |
+------------------+

Chatbot Features
- Global Widget: Available on all pages (left side)
- Context-Aware: Knows which car you're viewing
- Conversation History: Remembers previous messages
- Quick Suggestions: Pre-defined question buttons
- RAG (Retrieval Augmented Generation): Uses car data to answer questions

Components
- Frontend: Global floating chatbot widget (chatbot.js)
- Backend: /api/v1/ai/chat/{car_id} and /api/v1/ai/chat/general
- AI Model: OpenAI GPT-3.5-turbo
- Context Building: Car data + reviews + specifications

================================================================================
11. PRICE PREDICTIONS
================================================================================

What It Does
Predicts future car prices to help users make informed decisions.

How It Works

+------------------+
|      User        |
| Views price      |
| prediction       |
+------------------+
        |
        | Step 1: GET /api/v1/predictions/car/{car_id}
        |
        v
+------------------+
|   Backend API    |
| (predictions.py) |
+------------------+
        |
        | Step 2: Get car price history
        |
        v
+------------------+
|    Database      |
| price_history    |
| table            |
+------------------+
        |
        | Step 3: Analyze trends
        |         - Current price
        |         - Price changes over time
        |         - Similar cars' prices
        |
        v
+------------------+
| Prediction       |
| Algorithm        |
| (ML model)       |
+------------------+
        |
        | Step 4: Calculate predicted price
        |
        v
+------------------+
|    Frontend      |
| Display          |
| prediction       |
| + chart          |
+------------------+

Prediction Factors
- Current Price: Base price of the car
- Price History: Historical price changes
- Car Age: Depreciation over time
- Mileage: Impact on value
- Market Trends: Overall market conditions
- Similar Cars: Prices of comparable vehicles

================================================================================
12. PRICE ALERTS SYSTEM
================================================================================

What It Does
Notifies users when car prices drop or match their criteria.

How It Works - Creating Alert

+------------------+
|      User        |
| Creates          |
| Alert            |
+------------------+
        |
        | Step 1: POST /api/v1/alerts
        |         { car_id, max_price, criteria }
        |
        v
+------------------+
|   Backend API    |
| (alerts.py)      |
+------------------+
        |
        | Step 2: Store alert in database
        |
        v
+------------------+
|    Database      |
| alerts table     |
+------------------+

How It Works - Checking Alerts (Background Job)

+------------------+
| Scheduler        |
| (Runs every      |
| hour)            |
+------------------+
        |
        | Step 1: Get all active alerts
        |
        v
+------------------+
|    Database      |
| alerts table     |
+------------------+
        |
        | Step 2: For each alert:
        |         - Check car prices
        |         - Compare with criteria
        |
        v
+------------------+
|    Database      |
| Check current    |
| car prices       |
+------------------+
        |
        | Step 3: If price matches criteria:
        |         - Create notification
        |         - Store in alerts
        |
        v
+------------------+
|    Frontend      |
| User sees        |
| alert on         |
| alerts page      |
+------------------+

Alert Types
- Price Drop: Notify when car price drops below threshold
- New Listing: Notify when new car matches criteria
- Custom: User-defined criteria (make, model, price range)

Components
- Frontend: alerts.html - Alert management page
- Backend: /api/v1/alerts endpoints
- Scheduler: Background job runs hourly
- Database: Alerts table stores user criteria

================================================================================
13. PERSONALIZED RECOMMENDATIONS
================================================================================

What It Does
Shows cars on home page that match user preferences.

How It Works

+------------------+
|      User        |
| Opens            |
| home page        |
+------------------+
        |
        | Step 1: GET /api/v1/recommendations
        |
        v
+------------------+
|   Backend API    |
| (recommendations.|
| py)              |
+------------------+
        |
        | Step 2: Analyze user:
        |         - Favorites history
        |         - Viewed cars
        |         - Price preferences
        |
        v
+------------------+
|    Database      |
| Get user         |
| preferences      |
+------------------+
        |
        | Step 3: Find matching cars
        |         - Similar to favorites
        |         - Price range
        |         - Popular cars
        |
        v
+------------------+
|    Database      |
| Return           |
| recommended      |
| cars             |
+------------------+
        |
        | Step 4: Display on home page
        |
        v
+------------------+
|    Frontend      |
| Show             |
| recommendations  |
| section          |
+------------------+

Recommendation Factors
- User Favorites: Similar to saved favorites
- Browsing History: Based on cars viewed
- Price Preferences: Within typical price range
- Popular Cars: Trending/popular listings
- New Listings: Recently added cars

================================================================================
14. ADVANCED SEARCH (FUZZY SEARCH)
================================================================================

What It Does
Provides typo-tolerant search that automatically corrects misspellings and finds cars even with typing errors.

How It Works - Flow Diagram

+------------------+
|      User        |
| Searches:        |
| "tuyata camry"   |
+------------------+
        |
        | Step 1: Try exact search first
        |
        v
+------------------+
|   Backend API    |
| (cars.py)        |
| Exact search     |
+------------------+
        |
        | Step 2: No results found
        |         Trigger fuzzy correction
        |
        v
+------------------+
| Tokenize Search  |
| Split into words:|
| ["tuyata",       |
|  "camry"]        |
+------------------+
        |
        | Step 3: Build vocabulary from database
        |         - All car makes
        |         - All car models
        |         - All description words
        |
        v
+------------------+
| Fuzzy Matching   |
| For each word:   |
| - Compare with   |
|   vocabulary     |
| - Calculate      |
|   similarity     |
| - Find best match|
+------------------+
        |
        | Step 4: Correct "tuyata" to "Toyota" (80% match)
        |         Keep "camry" as "camry" (100% match)
        |
        v
+------------------+
| Rebuild Search   |
| "Toyota camry"   |
+------------------+
        |
        | Step 5: Search again with corrected terms
        |
        v
+------------------+
|    Database      |
| Find results     |
+------------------+
        |
        | Step 6: Return results with correction hint
        |
        v
+------------------+
|    Frontend      |
| Display:         |
| "Showing results |
| for Toyota camry |
| (from 'tuyata    |
| camry')"         |
+------------------+

Search Process Details

Step 1: Exact Search
- User enters search query
- Backend searches database for exact match
- If results found, return them
- If no results, proceed to Step 2

Step 2: Tokenization
- Split search query into individual words
- Example: "tuyata camry" becomes ["tuyata", "camry"]
- Remove punctuation and normalize

Step 3: Vocabulary Building
- Query database for all car makes
- Query database for all car models
- Extract words from all car descriptions
- Build vocabulary set (unique words, minimum 3 characters)

Step 4: Fuzzy Matching
- For each word in search query:
  - Compare with every word in vocabulary
  - Calculate similarity score (0.0 to 1.0)
  - Find best matching word
- Similarity calculation uses Python's difflib.SequenceMatcher
- Normalizes strings (lowercase, no punctuation) before comparison

Step 5: Threshold Check
- Short words (4 characters or less): 74% similarity threshold
  Example: "binz" compared to "benz" = 75% match - Corrected
- Longer words: 72% similarity threshold
  Example: "tuyata" compared to "Toyota" = 80% match - Corrected
- Too different: No correction
  Example: "hzhz" compared to "benz" = 25% match - Not corrected

Step 6: Rebuild and Search
- Reconstruct corrected search string
- Re-run database query with corrected terms
- Return results with correction metadata

Example Searches

User Input: binz
Corrected To: benz
Similarity: 75%
Result: Shows Mercedes-Benz cars

User Input: tuyata
Corrected To: Toyota
Similarity: 80%
Result: Shows Toyota cars

User Input: tuyata camry
Corrected To: Toyota camry
Similarity: 80% and 100%
Result: Shows Toyota Camry cars

User Input: hzhz
Corrected To: (no correction)
Similarity: 25% (below threshold)
Result: No results (too different)

User Input: mercedez
Corrected To: Mercedes
Similarity: 85%
Result: Shows Mercedes-Benz cars

Implementation Details

Backend (backend/app/api/v1/cars.py):
- Tokenizes search query using regex
- Builds vocabulary from all car data (makes, models, descriptions)
- Uses _best_fuzzy_candidate function to find best match
- Uses _similarity function with SequenceMatcher
- Applies dynamic threshold based on word length
- Re-runs search with corrected terms
- Returns original_search, corrected_search, and correction_score

Frontend (frontend/js/listings.js):
- Displays searchHint element when correction occurs
- Shows message: "Showing results for [corrected] (from '[original]')"
- Updates search input with corrected term (optional)

================================================================================
SUMMARY: SYSTEM INTEGRATION
================================================================================

All features work together in a layered architecture:

Layer 1: User Interface
+------------------------------------------+
|         User Interface                   |
|  (HTML/CSS/JavaScript)                   |
+------------------------------------------+
                  |
                  | HTTP/REST API
                  |
                  v
Layer 2: Backend API Layer
+------------------------------------------+
|         Backend API Layer                |
|  (FastAPI - Python)                      |
|  Auth, Cars, Reviews, AI,               |
|  Recommendations, Favorites, Predictions |
+------------------------------------------+
        |                      |
        |                      |
        v                      v
Layer 3: Database Layer
+------------------+  +------------------+
|  SQLite/         |  |   ChromaDB        |
|  PostgreSQL      |  |   (Vector DB)     |
|  (Relational)    |  |                   |
|                  |  |  Car embeddings   |
|  Users           |  |  Similarity       |
|  Cars            |  |  search           |
|  Reviews         |  |                   |
|  Favorites       |  |                   |
|  Alerts          |  |                   |
+------------------+  +------------------+
                  |
                  |
                  v
Layer 4: External Services
+------------------+
|   OpenAI API     |
|                  |
|  Embeddings      |
|  Chatbot         |
|  Summarization   |
+------------------+

Communication Flow
- User Interface communicates with Backend API via HTTP/REST API
- Backend API communicates with databases (SQLite/PostgreSQL and ChromaDB)
- Backend API communicates with OpenAI API for AI features

================================================================================
KEY DESIGN PRINCIPLES
================================================================================

1. Separation of Concerns: Frontend, backend, and database are separate
2. RESTful API: Standard HTTP methods and status codes
3. Stateless: Each request is independent (except auth tokens)
4. Scalable: Can handle multiple users and requests
5. Secure: Password hashing, JWT tokens, input validation
6. AI-Enhanced: Uses AI for recommendations, summaries, and assistance

================================================================================
TECHNOLOGY STACK SUMMARY
================================================================================

Frontend: HTML, CSS, JavaScript (vanilla)
Backend: FastAPI (Python)
Database: SQLite (dev) / PostgreSQL (production)
Vector DB: ChromaDB
AI Services: OpenAI API
Authentication: JWT tokens
API Style: RESTful

================================================================================

Document Version: 1.0
Last Updated: January 2026
