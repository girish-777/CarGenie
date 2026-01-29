# CarGenie - AI-Powered Automobile Marketplace

An intelligent car marketplace platform that combines traditional e-commerce features with AI capabilities to help users discover, compare, and make informed decisions about cars.

## Key Features

- **AI Chatbot Assistant**: Global chatbot available on all pages for car-related queries
- **Advanced Search**: Typo-tolerant fuzzy search that finds cars even with misspellings
- **Personalized Recommendations**: AI-powered car suggestions based on user preferences
- **Smart Comparisons**: Side-by-side comparison of multiple cars
- **Review System**: User reviews with AI-generated summaries
- **Price Predictions**: Future price forecasting for informed decisions
- **Favorites**: Save cars for later viewing


## Tech Stack

- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Backend**: FastAPI (Python)
- **Database**: SQLite (dev) / PostgreSQL (production)
- **Vector DB**: ChromaDB for similarity search
- **AI Services**: OpenAI API (GPT-3.5-turbo, embeddings)

## Quick Start

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables (see `.env.example`)
4. Run backend: `cd backend && python -m uvicorn app.main:app --reload`
5. Open `frontend/index.html` in your browser

