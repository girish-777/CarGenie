"""
AI-powered features API endpoints
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import Car, Review
from app.models.user import User
from app.core.embeddings import EmbeddingsService
from app.core.vectordb import VectorDB
from app.api.v1.auth import get_current_user, get_current_active_user
from pydantic import BaseModel, Field

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize services
embeddings_service = EmbeddingsService()
vectordb = VectorDB()


class SimilarCarResponse(BaseModel):
    """Response for similar car search"""
    car_id: int
    distance: Optional[float] = None
    metadata: dict


class SimilarCarsResponse(BaseModel):
    """Response for similar cars list"""
    similar_cars: List[SimilarCarResponse]
    total: int


@router.post("/cars/{car_id}/generate-embedding", status_code=status.HTTP_200_OK)
def generate_car_embedding(
    car_id: int,
    db: Session = Depends(get_db)
):
    """
    Generate and store embedding for a specific car
    This is useful for initial setup or updating embeddings
    """
    logger.info(f"[AI] Generating embedding for car {car_id}")
    
    # Get car from database
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car not found"
        )
    
    # Generate embedding
    embedding = embeddings_service.generate_car_embedding(
        make=car.make,
        model=car.model,
        year=car.year,
        description=car.description,
        fuel_type=car.fuel_type,
        transmission=car.transmission
    )
    
    if not embedding:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate embedding. Check OpenAI API key."
        )
    
    # Prepare metadata
    metadata = {
        "make": car.make,
        "model": car.model,
        "year": car.year,
        "price": car.price,
        "fuel_type": car.fuel_type,
        "transmission": car.transmission,
        "description": car.description or ""
    }
    
    # Store in vector DB
    success = vectordb.add_car_embedding(
        car_id=car.id,
        embedding=embedding,
        metadata=metadata
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store embedding"
        )
    
    return {
        "message": "Embedding generated and stored successfully",
        "car_id": car_id,
        "embedding_length": len(embedding)
    }


@router.get("/cars/{car_id}/similar", response_model=SimilarCarsResponse)
def get_similar_cars(
    car_id: int,
    n_results: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """
    Find similar cars using vector similarity search
    """
    logger.info(f"[AI] Finding similar cars for car {car_id}")
    
    # Get car from database
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car not found"
        )
    
    # Get car embedding
    embedding = vectordb.get_car_embedding(car_id)
    
    if not embedding:
        # Generate embedding if not exists
        logger.info(f"[AI] Embedding not found for car {car_id}, generating...")
        embedding = embeddings_service.generate_car_embedding(
            make=car.make,
            model=car.model,
            year=car.year,
            description=car.description,
            fuel_type=car.fuel_type,
            transmission=car.transmission
        )
        
        if embedding:
            metadata = {
                "make": car.make,
                "model": car.model,
                "year": car.year,
                "price": car.price,
                "fuel_type": car.fuel_type,
                "transmission": car.transmission,
                "description": car.description or ""
            }
            vectordb.add_car_embedding(car_id, embedding, metadata)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate embedding"
            )
    
    # Search for similar cars (exclude the car itself)
    similar_results = vectordb.search_similar_cars(
        query_embedding=embedding,
        n_results=n_results + 1  # Get one extra to exclude self
    )
    
    # Filter out the car itself and limit results
    similar_cars = [
        SimilarCarResponse(**result)
        for result in similar_results
        if result["car_id"] != car_id
    ][:n_results]
    
    return SimilarCarsResponse(
        similar_cars=similar_cars,
        total=len(similar_cars)
    )


@router.post("/reviews/{car_id}/summarize", status_code=status.HTTP_200_OK)
def summarize_car_reviews(
    car_id: int,
    db: Session = Depends(get_db)
):
    """
    Generate AI summary for all reviews of a car
    """
    logger.info(f"[AI] Summarizing reviews for car {car_id}")
    
    # Check if car exists
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car not found"
        )
    
    # Get all reviews for the car
    reviews = db.query(Review).filter(Review.car_id == car_id).all()
    
    if not reviews:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No reviews found for this car"
        )
    
    # Extract review texts
    review_texts = [
        f"Rating: {r.rating}/5. {r.title or ''} {r.content}"
        for r in reviews
    ]
    
    # Generate summary
    summary = embeddings_service.summarize_reviews(review_texts)
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate summary. Check OpenAI API key."
        )
    
    # Store summary in the most recent review's ai_summary field
    if reviews:
        latest_review = reviews[-1]
        latest_review.ai_summary = summary
        db.commit()
        logger.info(f"[AI] Stored AI summary for car {car_id} in review {latest_review.id}")
    
    return {
        "car_id": car_id,
        "summary": summary,
        "reviews_count": len(reviews)
    }


@router.get("/embeddings/stats", status_code=status.HTTP_200_OK)
def get_embedding_stats():
    """
    Get statistics about stored embeddings
    """
    count = vectordb.get_collection_count()
    return {
        "total_embeddings": count,
        "status": "active" if embeddings_service.client else "inactive (no API key)"
    }


class ChatMessage(BaseModel):
    """Chat message request"""
    message: str = Field(..., description="User's question about the car")
    conversation_history: Optional[List[dict]] = Field(default=[], description="Previous conversation messages")


class ChatResponse(BaseModel):
    """Chat response"""
    response: str
    car_id: int


@router.post("/chat/general", response_model=ChatResponse, status_code=status.HTTP_200_OK)
def chat_general(
    chat_data: ChatMessage,
    db: Session = Depends(get_db)
):
    """
    General AI Chatbot for car-related questions (not specific to a car)
    """
    logger.info(f"[AI Chat] General question: {chat_data.message[:50]}...")
    
    # Check if OpenAI client is available
    if not embeddings_service.client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI chatbot is not available. OpenAI API key not configured."
        )
    
    try:
        # Build conversation history
        conversation_messages = [
            {
                "role": "system",
                "content": """You are a helpful AI car advisor assistant. You help users with general car-related questions, buying advice, car comparisons, and automotive knowledge.

Instructions:
- Answer questions about cars, buying advice, features, specifications, etc.
- Be friendly, helpful, and concise
- If asked about specific cars, suggest they visit a car's detail page for detailed information
- Provide general automotive knowledge and advice
- Keep responses under 200 words unless more detail is specifically requested"""
            }
        ]
        
        # Add conversation history if provided
        if chat_data.conversation_history:
            for msg in chat_data.conversation_history[-5:]:  # Last 5 messages for context
                if msg.get("role") and msg.get("content"):
                    conversation_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
        
        # Add current user message
        conversation_messages.append({
            "role": "user",
            "content": chat_data.message
        })
        
        # Generate response using OpenAI
        response = embeddings_service.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversation_messages,
            max_tokens=300,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content.strip()
        logger.info(f"[AI Chat] Generated general response")
        
        return ChatResponse(
            response=ai_response,
            car_id=0  # 0 indicates general chat
        )
        
    except Exception as e:
        logger.error(f"[AI Chat] Error generating response: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate chat response: {str(e)}"
        )


def build_car_context(car, db: Session) -> str:
    """
    Build comprehensive context about a car for RAG
    """
    context_parts = []
    
    # Basic car info
    context_parts.append(f"Car: {car.year} {car.make} {car.model}")
    context_parts.append(f"Price: ${car.price:,.0f}")
    context_parts.append(f"Mileage: {car.mileage:,} miles")
    context_parts.append(f"Fuel Type: {car.fuel_type}")
    context_parts.append(f"Transmission: {car.transmission}")
    context_parts.append(f"Condition: {car.condition}")
    context_parts.append(f"Location: {car.location or 'N/A'}")
    
    if car.description:
        context_parts.append(f"Description: {car.description}")
    
    # Specifications
    if car.specs:
        specs = car.specs
        context_parts.append("\nSpecifications:")
        if specs.engine_size:
            context_parts.append(f"- Engine: {specs.engine_size}L")
        if specs.horsepower:
            context_parts.append(f"- Horsepower: {specs.horsepower} HP")
        if specs.torque:
            context_parts.append(f"- Torque: {specs.torque} lb-ft")
        if specs.acceleration_0_60:
            context_parts.append(f"- 0-60 mph: {specs.acceleration_0_60}s")
        if specs.mpg_city and specs.mpg_highway:
            context_parts.append(f"- MPG: {specs.mpg_city}/{specs.mpg_highway} city/highway")
        if specs.drivetrain:
            context_parts.append(f"- Drivetrain: {specs.drivetrain}")
        if specs.seating_capacity:
            context_parts.append(f"- Seating: {specs.seating_capacity} seats")
    
    # Scores
    if car.scores:
        scores = car.scores
        context_parts.append("\nScores & Ratings:")
        if scores.overall_score:
            context_parts.append(f"- Overall Score: {scores.overall_score}/10")
        if scores.reliability_score:
            context_parts.append(f"- Reliability: {scores.reliability_score}/10")
        if scores.safety_score:
            context_parts.append(f"- Safety: {scores.safety_score}/10")
        if scores.crash_test_rating:
            context_parts.append(f"- Crash Test Rating: {scores.crash_test_rating}")
    
    # Reviews summary
    reviews = db.query(Review).filter(Review.car_id == car.id).all()
    if reviews:
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
        context_parts.append(f"\nReviews: {len(reviews)} reviews, Average Rating: {avg_rating:.1f}/5")
        
        # Include AI summary if available
        summary_review = next((r for r in reviews if r.ai_summary), None)
        if summary_review and summary_review.ai_summary:
            context_parts.append(f"Review Summary: {summary_review.ai_summary}")
        elif len(reviews) >= 2:
            # Include a few recent reviews
            recent_reviews = reviews[-3:]  # Last 3 reviews
            context_parts.append("Recent Reviews:")
            for r in recent_reviews:
                context_parts.append(f"- {r.rating}/5: {r.title or ''} {r.content[:100]}...")
    
    return "\n".join(context_parts)


@router.post("/chat/{car_id}", response_model=ChatResponse, status_code=status.HTTP_200_OK)
def chat_about_car(
    car_id: int,
    chat_data: ChatMessage,
    db: Session = Depends(get_db)
):
    """
    AI Chatbot for car questions using RAG (Retrieval Augmented Generation)
    Provides context-aware responses about a specific car
    """
    logger.info(f"[AI Chat] User asking about car {car_id}: {chat_data.message[:50]}...")
    
    # Check if car exists
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car not found"
        )
    
    # Check if OpenAI client is available
    if not embeddings_service.client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI chatbot is not available. OpenAI API key not configured."
        )
    
    try:
        # Build car context for RAG
        car_context = build_car_context(car, db)
        
        # Build conversation history
        conversation_messages = [
            {
                "role": "system",
                "content": f"""You are a helpful AI car advisor assistant. You help users learn about cars by answering their questions.

You have access to the following information about a car:
{car_context}

Instructions:
- Answer questions based ONLY on the provided car information
- If information is not available, say so honestly
- Be friendly, helpful, and concise
- Focus on facts from the car data provided
- If asked about comparisons, use the provided specifications
- If asked about reviews, reference the review summary and ratings provided
- Keep responses under 200 words unless more detail is specifically requested"""
            }
        ]
        
        # Add conversation history if provided
        if chat_data.conversation_history:
            for msg in chat_data.conversation_history[-5:]:  # Last 5 messages for context
                if msg.get("role") and msg.get("content"):
                    conversation_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
        
        # Add current user message
        conversation_messages.append({
            "role": "user",
            "content": chat_data.message
        })
        
        # Generate response using OpenAI
        response = embeddings_service.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversation_messages,
            max_tokens=300,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content.strip()
        logger.info(f"[AI Chat] Generated response for car {car_id}")
        
        return ChatResponse(
            response=ai_response,
            car_id=car_id
        )
        
    except Exception as e:
        logger.error(f"[AI Chat] Error generating response: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate chat response: {str(e)}"
        )

