# CarGenie - Feature System Design Document

## Overview
This document explains how each feature in CarGenie works in simple terms with diagrams.

---

## 1. User Authentication System

### What It Does
Allows users to create accounts, log in, and securely access their personalized features.

### How It Works

```
┌──────────────┐
│   User       │
│  (Browser)   │
└──────┬───────┘
       │
       │ 1. Enter email & password
       ▼
┌─────────────────┐
│  Frontend       │
│  (login.html)   │
└──────┬──────────┘
       │
       │ 2. POST /api/v1/auth/login
       ▼
┌─────────────────┐
│  Backend API    │
│  (auth.py)      │
└──────┬──────────┘
       │
       │ 3. Check credentials
       ▼
┌─────────────────┐
│  Database       │
│  (users table)  │
└──────┬──────────┘
       │
       │ 4. Verify password hash
       ▼
┌─────────────────┐
│  JWT Token      │
│  Generation     │
└──────┬──────────┘
       │
       │ 5. Return token
       ▼
┌─────────────────┐
│  Frontend       │
│  Store in       │
│  localStorage   │
└─────────────────┘
```

### Components
- **Frontend**: Login/signup forms (`login.html`, `signup.html`)
- **Backend**: Auth endpoints (`/api/v1/auth/login`, `/api/v1/auth/signup`)
- **Database**: Users table stores encrypted passwords
- **Security**: Bcrypt password hashing, JWT tokens (30-min expiry)

### Data Flow
1. User enters credentials
2. Frontend sends to backend API
3. Backend hashes password and checks database
4. If valid, creates JWT token
5. Token stored in browser's localStorage
6. Token sent with every authenticated request

---

## 2. Car Listings & Browsing

### What It Does
Displays cars in a searchable, filterable grid with pagination.

### How It Works

```
┌──────────────┐
│   User       │
│  Opens       │
│  listings.html│
└──────┬───────┘
       │
       │ 1. Page loads
       ▼
┌─────────────────┐
│  Frontend JS    │
│  (listings.js)  │
└──────┬──────────┘
       │
       │ 2. GET /api/v1/cars?page=1&page_size=12
       ▼
┌─────────────────┐
│  Backend API    │
│  (cars.py)      │
└──────┬──────────┘
       │
       │ 3. Query database with filters
       ▼
┌─────────────────┐
│  Database       │
│  (cars table)   │
└──────┬──────────┘
       │
       │ 4. Return cars data
       ▼
┌─────────────────┐
│  Frontend       │
│  Render car     │
│  cards in grid  │
└─────────────────┘
```

### Components
- **Frontend**: `listings.html` - Car grid display
- **JavaScript**: `listings.js` - Handles API calls and rendering
- **Backend**: `/api/v1/cars` endpoint
- **Database**: Cars table with indexes on make, year, price

### Features
- **Pagination**: 12 cars per page
- **Filtering**: By make, model, year, price, fuel type, transmission
- **Search**: Text search in make, model, description
- **Sorting**: By price, year, mileage, newest

---

## 3. Search & Filter System

### What It Does
Helps users find specific cars based on their preferences.

### How It Works

```
┌──────────────┐
│   User       │
│  Sets Filters│
│  & Searches  │
└──────┬───────┘
       │
       │ 1. User selects filters
       ▼
┌─────────────────┐
│  Frontend       │
│  Build Query    │
│  String         │
└──────┬──────────┘
       │
       │ 2. GET /api/v1/cars?make=Toyota&min_price=20000&max_price=50000
       ▼
┌─────────────────┐
│  Backend API    │
│  Process        │
│  Filters        │
└──────┬──────────┘
       │
       │ 3. Apply SQL filters
       ▼
┌─────────────────┐
│  Database       │
│  SQL WHERE      │
│  conditions     │
└──────┬──────────┘
       │
       │ 4. Return filtered results
       ▼
┌─────────────────┐
│  Frontend       │
│  Update car     │
│  grid           │
└─────────────────┘
```

### Filter Types
1. **Text Filters**: Make, model, description search
2. **Range Filters**: Year (min/max), price (min/max)
3. **Category Filters**: Fuel type, transmission, condition
4. **Combined**: Multiple filters work together

### Implementation
- Frontend builds query parameters
- Backend validates and applies filters to SQL query
- Database uses indexes for fast filtering
- Results updated instantly without page reload

---

## 4. Car Details Page

### What It Does
Shows comprehensive information about a single car.

### How It Works

```
┌──────────────┐
│   User       │
│  Clicks on   │
│  Car Card    │
└──────┬───────┘
       │
       │ 1. Navigate to car-detail.html?id=5
       ▼
┌─────────────────┐
│  Frontend JS    │
│  (car-detail.js)│
└──────┬──────────┘
       │
       │ 2. GET /api/v1/cars/5
       │ 3. GET /api/v1/reviews/car/5
       │ 4. GET /api/v1/ai/cars/5/similar
       ▼
┌─────────────────┐
│  Backend API    │
│  Multiple       │
│  Endpoints      │
└──────┬──────────┘
       │
       │ 5. Fetch from database
       ▼
┌─────────────────┐
│  Database       │
│  cars, reviews, │
│  specs, scores  │
└──────┬──────────┘
       │
       │ 6. Return all data
       ▼
┌─────────────────┐
│  Frontend       │
│  Display:       │
│  - Car info     │
│  - Specs        │
│  - Reviews      │
│  - Similar cars │
└─────────────────┘
```

### Components Displayed
- **Basic Info**: Make, model, year, price, mileage
- **Specifications**: Engine, horsepower, MPG, drivetrain
- **Scores**: Overall rating, reliability, safety
- **Images**: Car photo gallery
- **Reviews**: User reviews with ratings
- **Similar Cars**: AI-powered recommendations
- **Actions**: Favorite, compare buttons

---

## 5. Favorites System

### What It Does
Allows users to save cars they like for later viewing.

### How It Works

```
┌──────────────┐
│   User       │
│  Clicks      │
│  Heart Icon  │
└──────┬───────┘
       │
       │ 1. POST /api/v1/favorites
       │    { car_id: 5, user_id: 2 }
       ▼
┌─────────────────┐
│  Backend API    │
│  (favorites.py) │
└──────┬──────────┘
       │
       │ 2. Check authentication
       │ 3. Insert into favorites table
       ▼
┌─────────────────┐
│  Database       │
│  favorites table│
│  (user_id, car_id)│
└──────┬──────────┘
       │
       │ 4. Success response
       ▼
┌─────────────────┐
│  Frontend       │
│  Update UI      │
│  (Heart filled) │
└─────────────────┘
```

### Components
- **Frontend**: Heart icon on car cards
- **Backend**: `/api/v1/favorites` endpoints
- **Database**: Favorites table (user_id, car_id)
- **Features**: 
  - Add/remove favorites
  - View all favorites on favorites.html
  - Check if car is favorited

### Data Structure
```sql
favorites (
    id PRIMARY KEY,
    user_id FOREIGN KEY -> users.id,
    car_id FOREIGN KEY -> cars.id,
    created_at
)
```

---

## 6. Car Comparison System

### What It Does
Allows users to compare multiple cars side-by-side.

### How It Works

```
┌──────────────┐
│   User       │
│  Adds cars   │
│  to compare  │
└──────┬───────┘
       │
       │ 1. Click "Compare" button on cars
       ▼
┌─────────────────┐
│  Frontend JS    │
│  (compare.js)   │
│  Store in       │
│  session/localStorage│
└──────┬──────────┘
       │
       │ 2. Navigate to compare.html
       │ 3. GET /api/v1/cars/{id} for each car
       ▼
┌─────────────────┐
│  Backend API    │
│  Fetch car      │
│  details        │
└──────┬──────────┘
       │
       │ 4. Get car data
       ▼
┌─────────────────┐
│  Database       │
│  cars + specs   │
└──────┬──────────┘
       │
       │ 5. Return data
       ▼
┌─────────────────┐
│  Frontend       │
│  Display        │
│  comparison     │
│  table          │
└─────────────────┘
```

### Components
- **Frontend**: `compare.html` - Comparison table
- **JavaScript**: `compare.js` - Manages comparison list
- **Storage**: Car IDs stored in localStorage
- **Display**: Side-by-side comparison of specs, price, features

### Comparison Features
- **Specifications**: Engine, HP, MPG, drivetrain
- **Price**: Current price comparison
- **Features**: Key features highlighted
- **Pros/Cons**: Based on reviews and ratings

---

## 7. Reviews & Ratings System

### What It Does
Allows users to read and write reviews about cars.

### How It Works

#### Viewing Reviews
```
┌──────────────┐
│   User       │
│  Views car   │
│  detail page │
└──────┬───────┘
       │
       │ 1. GET /api/v1/reviews/car/5
       ▼
┌─────────────────┐
│  Backend API    │
│  (reviews.py)   │
└──────┬──────────┘
       │
       │ 2. Query reviews table
       ▼
┌─────────────────┐
│  Database       │
│  reviews table  │
└──────┬──────────┘
       │
       │ 3. Return reviews with user info
       ▼
┌─────────────────┐
│  Frontend       │
│  Display reviews│
│  with ratings   │
└─────────────────┘
```

#### Writing Reviews
```
┌──────────────┐
│   User       │
│  Writes      │
│  Review      │
└──────┬───────┘
       │
       │ 1. POST /api/v1/reviews
       │    { car_id, rating, title, content }
       ▼
┌─────────────────┐
│  Backend API    │
│  Validate &     │
│  Check existing │
└──────┬──────────┘
       │
       │ 2. Check: One review per user per car
       │ 3. Insert into reviews table
       │ 4. Trigger AI summary (background)
       ▼
┌─────────────────┐
│  Database       │
│  Store review   │
└──────┬──────────┘
       │
       │ 5. Background: Generate AI summary
       ▼
┌─────────────────┐
│  OpenAI API     │
│  Summarize      │
│  all reviews    │
└──────┬──────────┘
       │
       │ 6. Update review with ai_summary
       ▼
┌─────────────────┐
│  Database       │
│  ai_summary     │
│  field updated  │
└─────────────────┘
```

### Components
- **Frontend**: Review form on car detail page
- **Backend**: `/api/v1/reviews` endpoints
- **Database**: Reviews table with ai_summary field
- **Rules**: One review per user per car (can edit/delete)

### Review Features
- **Rating**: 1-5 stars
- **Title**: Optional review title
- **Content**: Review text
- **AI Summary**: Auto-generated summary of all reviews
- **Edit/Delete**: Users can modify their own reviews

---

## 8. AI Similar Cars Recommendation

### What It Does
Finds cars similar to the one you're viewing using AI.

### How It Works

```
┌──────────────┐
│   User       │
│  Views car   │
│  detail page │
└──────┬───────┘
       │
       │ 1. GET /api/v1/ai/cars/5/similar
       ▼
┌─────────────────┐
│  Backend API    │
│  (ai.py)        │
└──────┬──────────┘
       │
       │ 2. Get car embedding from ChromaDB
       ▼
┌─────────────────┐
│  Vector DB      │
│  (ChromaDB)     │
│  Get car's      │
│  embedding      │
└──────┬──────────┘
       │
       │ 3. Search for similar embeddings
       │    (cosine similarity)
       ▼
┌─────────────────┐
│  Vector DB      │
│  Returns 3      │
│  similar car IDs│
└──────┬──────────┘
       │
       │ 4. Fetch car details from database
       ▼
┌─────────────────┐
│  Database       │
│  Get car info   │
│  for IDs        │
└──────┬──────────┘
       │
       │ 5. Return similar cars
       ▼
┌─────────────────┐
│  Frontend       │
│  Display        │
│  similar cars   │
│  section        │
└─────────────────┘
```

### How Embeddings Work

#### Initial Setup (One-time)
```
┌─────────────────┐
│  Admin runs     │
│  generate_embeddings.py │
└──────┬──────────┘
       │
       │ 1. For each car:
       │    - Get car data (make, model, year, description)
       │    - Send to OpenAI API
       ▼
┌─────────────────┐
│  OpenAI API     │
│  text-embedding-3-small│
│  Returns vector │
│  (1536 numbers) │
└──────┬──────────┘
       │
       │ 2. Store in ChromaDB
       ▼
┌─────────────────┐
│  ChromaDB       │
│  Car ID +       │
│  Embedding +    │
│  Metadata       │
└─────────────────┘
```

#### Similarity Search
- **Vector Comparison**: Uses cosine similarity to find similar vectors
- **Similarity Score**: Lower distance = more similar
- **Metadata Filtering**: Can filter by price range, year, etc.
- **Results**: Returns top 3 most similar cars

### Components
- **Embedding Generation**: `generate_embeddings.py` script
- **Vector Storage**: ChromaDB collection
- **Similarity Search**: ChromaDB query with cosine distance
- **API**: `/api/v1/ai/cars/{car_id}/similar` endpoint

---

## 9. AI Review Summarization

### What It Does
Automatically creates a summary of all reviews for a car using AI.

### How It Works

```
┌──────────────┐
│  New Review  │
│  Submitted   │
└──────┬───────┘
       │
       │ 1. Review saved to database
       │ 2. Background task triggered
       ▼
┌─────────────────┐
│  Backend        │
│  Background     │
│  Task           │
└──────┬──────────┘
       │
       │ 3. Get all reviews for car
       │    (Need at least 2 reviews)
       ▼
┌─────────────────┐
│  Database       │
│  reviews table  │
└──────┬──────────┘
       │
       │ 4. Combine review texts
       ▼
┌─────────────────┐
│  OpenAI API     │
│  gpt-3.5-turbo  │
│  Summarize      │
│  reviews        │
└──────┬──────────┘
       │
       │ 5. Generated summary
       │    (200 words, pros/cons)
       ▼
┌─────────────────┐
│  Database       │
│  Update most    │
│  recent review's│
│  ai_summary     │
└─────────────────┘
```

### Summary Content
- **Common Themes**: What reviewers mention most
- **Pros**: Positive aspects mentioned
- **Cons**: Negative aspects mentioned
- **Overall Sentiment**: General feeling about the car

### Components
- **Trigger**: Background task after review submission
- **AI Model**: OpenAI GPT-3.5-turbo
- **Storage**: ai_summary field in reviews table
- **Display**: Shown on car detail page above reviews

---

## 10. AI Chatbot Assistant

### What It Does
Provides an AI-powered chatbot that answers questions about cars.

### How It Works

#### Car-Specific Chat
```
┌──────────────┐
│   User       │
│  Asks        │
│  Question    │
└──────┬───────┘
       │
       │ 1. POST /api/v1/ai/chat/{car_id}
       │    { message, conversation_history }
       ▼
┌─────────────────┐
│  Backend API    │
│  (ai.py)        │
└──────┬──────────┘
       │
       │ 2. Get car details from database
       ▼
┌─────────────────┐
│  Database       │
│  Car + specs +  │
│  reviews        │
└──────┬──────────┘
       │
       │ 3. Build context (RAG)
       │    - Car specifications
       │    - Reviews summary
       │    - Features
       ▼
┌─────────────────┐
│  OpenAI API     │
│  gpt-3.5-turbo  │
│  With context   │
└──────┬──────────┘
       │
       │ 4. AI generates response
       │    using car data
       ▼
┌─────────────────┐
│  Frontend       │
│  Display        │
│  response in    │
│  chat UI        │
└─────────────────┘
```

#### General Chat
```
┌──────────────┐
│   User       │
│  Asks general│
│  question    │
└──────┬───────┘
       │
       │ 1. POST /api/v1/ai/chat/general
       │    { message, conversation_history }
       ▼
┌─────────────────┐
│  Backend API    │
│  (ai.py)        │
└──────┬──────────┘
       │
       │ 2. No car context needed
       ▼
┌─────────────────┐
│  OpenAI API     │
│  gpt-3.5-turbo  │
│  General car    │
│  advice         │
└──────┬──────────┘
       │
       │ 3. AI generates general response
       ▼
┌─────────────────┐
│  Frontend       │
│  Display        │
│  response       │
└─────────────────┘
```

### Chatbot Features
- **Global Widget**: Available on all pages (left side)
- **Context-Aware**: Knows which car you're viewing
- **Conversation History**: Remembers previous messages
- **Quick Suggestions**: Pre-defined question buttons
- **RAG (Retrieval Augmented Generation)**: Uses car data to answer questions

### Components
- **Frontend**: Global floating chatbot widget (`chatbot.js`)
- **Backend**: `/api/v1/ai/chat/{car_id}` and `/api/v1/ai/chat/general`
- **AI Model**: OpenAI GPT-3.5-turbo
- **Context Building**: Car data + reviews + specifications

---

## 11. Price Predictions

### What It Does
Predicts future car prices to help users make informed decisions.

### How It Works

```
┌──────────────┐
│   User       │
│  Views price │
│  prediction  │
└──────┬───────┘
       │
       │ 1. GET /api/v1/predictions/car/{car_id}
       ▼
┌─────────────────┐
│  Backend API    │
│  (predictions.py)│
└──────┬──────────┘
       │
       │ 2. Get car price history
       ▼
┌─────────────────┐
│  Database       │
│  price_history  │
│  table          │
└──────┬──────────┘
       │
       │ 3. Analyze trends
       │    - Current price
       │    - Price changes over time
       │    - Similar cars' prices
       ▼
┌─────────────────┐
│  Prediction     │
│  Algorithm      │
│  (ML model)     │
└──────┬──────────┘
       │
       │ 4. Calculate predicted price
       ▼
┌─────────────────┐
│  Frontend       │
│  Display        │
│  prediction     │
│  + chart        │
└─────────────────┘
```

### Prediction Factors
- **Current Price**: Base price of the car
- **Price History**: Historical price changes
- **Car Age**: Depreciation over time
- **Mileage**: Impact on value
- **Market Trends**: Overall market conditions
- **Similar Cars**: Prices of comparable vehicles

---

## 12. Price Alerts System

### What It Does
Notifies users when car prices drop or match their criteria.

### How It Works

#### Creating Alert
```
┌──────────────┐
│   User       │
│  Creates     │
│  Alert       │
└──────┬───────┘
       │
       │ 1. POST /api/v1/alerts
       │    { car_id, max_price, criteria }
       ▼
┌─────────────────┐
│  Backend API    │
│  (alerts.py)    │
└──────┬──────────┘
       │
       │ 2. Store alert in database
       ▼
┌─────────────────┐
│  Database       │
│  alerts table   │
└─────────────────┘
```

#### Checking Alerts (Background Job)
```
┌─────────────────┐
│  Scheduler      │
│  (Runs every    │
│   hour)         │
└──────┬──────────┘
       │
       │ 1. Get all active alerts
       ▼
┌─────────────────┐
│  Database       │
│  alerts table   │
└──────┬──────────┘
       │
       │ 2. For each alert:
       │    - Check car prices
       │    - Compare with criteria
       ▼
┌─────────────────┐
│  Database       │
│  Check current  │
│  car prices     │
└──────┬──────────┘
       │
       │ 3. If price matches criteria:
       │    - Create notification
       │    - Store in alerts
       ▼
┌─────────────────┐
│  Frontend       │
│  User sees      │
│  alert on       │
│  alerts page    │
└─────────────────┘
```

### Alert Types
- **Price Drop**: Notify when car price drops below threshold
- **New Listing**: Notify when new car matches criteria
- **Custom**: User-defined criteria (make, model, price range)

### Components
- **Frontend**: `alerts.html` - Alert management page
- **Backend**: `/api/v1/alerts` endpoints
- **Scheduler**: Background job runs hourly
- **Database**: Alerts table stores user criteria

---

## 13. Personalized Recommendations

### What It Does
Shows cars on home page that match user preferences.

### How It Works

```
┌──────────────┐
│   User       │
│  Opens       │
│  home page   │
└──────┬───────┘
       │
       │ 1. GET /api/v1/recommendations
       ▼
┌─────────────────┐
│  Backend API    │
│  (recommendations.py)│
└──────┬──────────┘
       │
       │ 2. Analyze user:
       │    - Favorites history
       │    - Viewed cars
       │    - Price preferences
       ▼
┌─────────────────┐
│  Database       │
│  Get user       │
│  preferences    │
└──────┬──────────┘
       │
       │ 3. Find matching cars
       │    - Similar to favorites
       │    - Price range
       │    - Popular cars
       ▼
┌─────────────────┐
│  Database       │
│  Return         │
│  recommended    │
│  cars           │
└──────┬──────────┘
       │
       │ 4. Display on home page
       ▼
┌─────────────────┐
│  Frontend       │
│  Show           │
│  recommendations│
│  section        │
└─────────────────┘
```

### Recommendation Factors
- **User Favorites**: Similar to saved favorites
- **Browsing History**: Based on cars viewed
- **Price Preferences**: Within typical price range
- **Popular Cars**: Trending/popular listings
- **New Listings**: Recently added cars

---

## Summary: System Integration

All features work together:

```
┌─────────────────────────────────────────┐
│            User Interface               │
│  (HTML/CSS/JavaScript)                  │
└─────────────────┬───────────────────────┘
                  │
                  │ HTTP/REST API
                  ▼
┌─────────────────────────────────────────┐
│         Backend API Layer               │
│  (FastAPI - Python)                     │
│  • Auth • Cars • Reviews • AI • etc.    │
└──────┬──────────────────┬───────────────┘
       │                  │
       ▼                  ▼
┌──────────────┐  ┌──────────────────┐
│  SQLite/     │  │   ChromaDB       │
│  PostgreSQL  │  │   (Vector DB)    │
│  (Relational)│  │                  │
│              │  │  • Car embeddings│
│  • Users     │  │  • Similarity    │
│  • Cars      │  │    search        │
│  • Reviews   │  │                  │
│  • Favorites │  │                  │
│  • Alerts    │  │                  │
└──────────────┘  └──────────────────┘
                  │
                  ▼
         ┌─────────────────┐
         │   OpenAI API    │
         │                 │
         │  • Embeddings   │
         │  • Chatbot      │
         │  • Summarization│
         └─────────────────┘
```

---

## Key Design Principles

1. **Separation of Concerns**: Frontend, backend, and database are separate
2. **RESTful API**: Standard HTTP methods and status codes
3. **Stateless**: Each request is independent (except auth tokens)
4. **Scalable**: Can handle multiple users and requests
5. **Secure**: Password hashing, JWT tokens, input validation
6. **AI-Enhanced**: Uses AI for recommendations, summaries, and assistance

---

## Technology Stack Summary

- **Frontend**: HTML, CSS, JavaScript (vanilla)
- **Backend**: FastAPI (Python)
- **Database**: SQLite (dev) / PostgreSQL (production)
- **Vector DB**: ChromaDB
- **AI Services**: OpenAI API
- **Authentication**: JWT tokens
- **API Style**: RESTful

---

**Document Version**: 1.0  
**Last Updated**: 2024

