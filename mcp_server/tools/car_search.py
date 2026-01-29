"""
Car Search Tool for MCP Server
"""
import logging
from typing import Any, Dict, Optional
import httpx

logger = logging.getLogger(__name__)


async def search_cars_tool(
    client: httpx.AsyncClient,
    api_base: str,
    arguments: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Search for cars with various filters
    
    Args:
        client: HTTP client
        api_base: Base URL for API
        arguments: Tool arguments containing search filters
    
    Returns:
        Dictionary with search results
    """
    try:
        # Build query parameters
        params = {}
        
        if "make" in arguments:
            params["make"] = arguments["make"]
        if "model" in arguments:
            params["model"] = arguments["model"]
        if "min_year" in arguments:
            params["min_year"] = arguments["min_year"]
        if "max_year" in arguments:
            params["max_year"] = arguments["max_year"]
        if "min_price" in arguments:
            params["min_price"] = arguments["min_price"]
        if "max_price" in arguments:
            params["max_price"] = arguments["max_price"]
        if "fuel_type" in arguments:
            params["fuel_type"] = arguments["fuel_type"]
        if "transmission" in arguments:
            params["transmission"] = arguments["transmission"]
        if "search" in arguments:
            params["search"] = arguments["search"]
        if "page" in arguments:
            params["page"] = arguments["page"]
        if "page_size" in arguments:
            params["page_size"] = arguments["page_size"]
        
        # Make API request
        url = f"{api_base}/cars/"
        logger.info(f"Searching cars with params: {params}")
        
        response = await client.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        return {
            "success": True,
            "total": data.get("total", 0),
            "page": data.get("page", 1),
            "page_size": data.get("page_size", 12),
            "total_pages": data.get("total_pages", 1),
            "cars": data.get("cars", []),
        }
    
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error searching cars: {e}")
        return {
            "success": False,
            "error": f"HTTP {e.response.status_code}: {e.response.text}",
        }
    except Exception as e:
        logger.error(f"Error searching cars: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
        }
