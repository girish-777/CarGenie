"""
ChromaDB vector database integration for car embeddings
"""
import logging
import chromadb
from chromadb.config import Settings
from typing import List, Optional, Dict, Any
import os

logger = logging.getLogger(__name__)

# Get project root directory
_base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_project_root = os.path.dirname(_base_dir)
_chroma_db_path = os.path.join(_project_root, 'db_deploy', 'chroma_db').replace('\\', '/')


class VectorDB:
    """ChromaDB client for storing and querying car embeddings"""
    
    def __init__(self, collection_name: str = "cars"):
        """Initialize ChromaDB client"""
        try:
            # Create persistent client
            self.client = chromadb.PersistentClient(
                path=_chroma_db_path,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"description": "Car embeddings for semantic search"}
            )
            
            logger.info(f"[VectorDB] Initialized ChromaDB at {_chroma_db_path}")
            logger.info(f"[VectorDB] Collection '{collection_name}' ready")
        except Exception as e:
            logger.error(f"[VectorDB] Failed to initialize: {e}")
            raise
    
    def add_car_embedding(
        self,
        car_id: int,
        embedding: List[float],
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Add or update car embedding
        
        Args:
            car_id: Car database ID
            embedding: Vector embedding (list of floats)
            metadata: Car metadata (make, model, year, description, etc.)
        
        Returns:
            True if successful
        """
        try:
            # Use car_id as document ID
            doc_id = str(car_id)
            
            # Prepare metadata (ChromaDB requires string values)
            chroma_metadata = {
                "car_id": str(car_id),
                "make": str(metadata.get("make", "")),
                "model": str(metadata.get("model", "")),
                "year": str(metadata.get("year", "")),
                "price": str(metadata.get("price", "")),
                "fuel_type": str(metadata.get("fuel_type", "")),
                "transmission": str(metadata.get("transmission", "")),
            }
            
            # Add description if available
            if "description" in metadata:
                chroma_metadata["description"] = str(metadata["description"])[:1000]  # Limit length
            
            # Upsert (update if exists, insert if not)
            self.collection.upsert(
                ids=[doc_id],
                embeddings=[embedding],
                metadatas=[chroma_metadata]
            )
            
            logger.info(f"[VectorDB] Added/updated embedding for car {car_id}")
            return True
        except Exception as e:
            logger.error(f"[VectorDB] Failed to add embedding for car {car_id}: {e}")
            return False
    
    def get_car_embedding(self, car_id: int) -> Optional[List[float]]:
        """Get embedding for a specific car"""
        try:
            result = self.collection.get(ids=[str(car_id)])
            if result['embeddings'] and len(result['embeddings']) > 0:
                return result['embeddings'][0]
            return None
        except Exception as e:
            logger.error(f"[VectorDB] Failed to get embedding for car {car_id}: {e}")
            return None
    
    def search_similar_cars(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar cars using vector similarity
        
        Args:
            query_embedding: Query vector embedding
            n_results: Number of results to return
            filters: Optional metadata filters (e.g., {"make": "Toyota"})
        
        Returns:
            List of similar cars with similarity scores
        """
        try:
            where_clause = None
            if filters:
                where_clause = {}
                for key, value in filters.items():
                    where_clause[key] = str(value)
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_clause
            )
            
            # Format results
            similar_cars = []
            if results['ids'] and len(results['ids']) > 0:
                for i in range(len(results['ids'][0])):
                    similar_cars.append({
                        "car_id": int(results['ids'][0][i]),
                        "distance": results['distances'][0][i] if 'distances' in results else None,
                        "metadata": results['metadatas'][0][i] if 'metadatas' in results else {}
                    })
            
            logger.info(f"[VectorDB] Found {len(similar_cars)} similar cars")
            return similar_cars
        except Exception as e:
            logger.error(f"[VectorDB] Failed to search similar cars: {e}")
            return []
    
    def delete_car_embedding(self, car_id: int) -> bool:
        """Delete embedding for a car"""
        try:
            self.collection.delete(ids=[str(car_id)])
            logger.info(f"[VectorDB] Deleted embedding for car {car_id}")
            return True
        except Exception as e:
            logger.error(f"[VectorDB] Failed to delete embedding for car {car_id}: {e}")
            return False
    
    def get_collection_count(self) -> int:
        """Get total number of embeddings in collection"""
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"[VectorDB] Failed to get collection count: {e}")
            return 0

