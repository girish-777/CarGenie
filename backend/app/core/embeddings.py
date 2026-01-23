"""
OpenAI embeddings service for generating car and text embeddings
"""
import logging
from typing import List, Optional
from openai import OpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingsService:
    """Service for generating embeddings using OpenAI"""
    
    def __init__(self):
        """Initialize OpenAI client"""
        if not settings.OPENAI_API_KEY:
            logger.warning("[Embeddings] OpenAI API key not set. Embeddings will not work.")
            self.client = None
        else:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info("[Embeddings] OpenAI client initialized")
    
    def generate_car_embedding(
        self,
        make: str,
        model: str,
        year: int,
        description: Optional[str] = None,
        fuel_type: Optional[str] = None,
        transmission: Optional[str] = None
    ) -> Optional[List[float]]:
        """
        Generate embedding for a car based on its attributes
        
        Args:
            make: Car make (e.g., "Toyota")
            model: Car model (e.g., "Camry")
            year: Car year
            description: Car description
            fuel_type: Fuel type
            transmission: Transmission type
        
        Returns:
            Embedding vector or None if failed
        """
        if not self.client:
            logger.error("[Embeddings] OpenAI client not available")
            return None
        
        try:
            # Create text representation of car
            car_text = f"{year} {make} {model}"
            
            if fuel_type:
                car_text += f" {fuel_type}"
            if transmission:
                car_text += f" {transmission}"
            if description:
                car_text += f". {description}"
            
            # Generate embedding
            response = self.client.embeddings.create(
                model="text-embedding-3-small",  # Using small model for cost efficiency
                input=car_text
            )
            
            embedding = response.data[0].embedding
            logger.info(f"[Embeddings] Generated embedding for {car_text}")
            return embedding
        except Exception as e:
            logger.error(f"[Embeddings] Failed to generate car embedding: {e}")
            return None
    
    def generate_text_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for arbitrary text
        
        Args:
            text: Text to embed
        
        Returns:
            Embedding vector or None if failed
        """
        if not self.client:
            logger.error("[Embeddings] OpenAI client not available")
            return None
        
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            
            embedding = response.data[0].embedding
            logger.info(f"[Embeddings] Generated text embedding (length: {len(text)} chars)")
            return embedding
        except Exception as e:
            logger.error(f"[Embeddings] Failed to generate text embedding: {e}")
            return None
    
    def summarize_reviews(self, reviews: List[str], max_length: int = 200) -> Optional[str]:
        """
        Summarize multiple reviews using OpenAI
        
        Args:
            reviews: List of review texts
            max_length: Maximum length of summary
        
        Returns:
            Summary text or None if failed
        """
        if not self.client:
            logger.error("[Embeddings] OpenAI client not available")
            return None
        
        if not reviews:
            return None
        
        try:
            # Combine reviews
            combined_reviews = "\n\n".join(reviews)
            
            # Limit total length to avoid token limits
            if len(combined_reviews) > 3000:
                combined_reviews = combined_reviews[:3000] + "..."
            
            # Create prompt
            prompt = f"""Summarize the following car reviews in a concise way. 
Focus on common themes, pros, cons, and overall sentiment.
Keep the summary under {max_length} words.

IMPORTANT: Do NOT mention:
- Individual ratings (like "5/5", "4 stars", etc.)
- Number of reviewers
- Individual reviewer opinions (like "one reviewer said", "another user gave")
- Rating statistics (like "both reviewers gave it 5/5")
- Any specific rating numbers

Just provide a clean, general summary of the reviews focusing on the car's features, performance, and overall experience.

Reviews:
{combined_reviews}

Summary:"""
            
            # Generate summary
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes car reviews. You provide clean, general summaries without mentioning individual ratings, reviewer counts, or specific rating numbers."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_length * 2,  # Rough estimate
                temperature=0.7
            )
            
            summary = response.choices[0].message.content.strip()
            logger.info(f"[Embeddings] Generated review summary ({len(summary)} chars)")
            return summary
        except Exception as e:
            logger.error(f"[Embeddings] Failed to summarize reviews: {e}")
            return None

