"""
Car Details Tool for MCP Server
"""

import logging
from typing import Any, Dict

import httpx

logger = logging.getLogger(__name__)


async def get_car_details_tool(
    client: httpx.AsyncClient,
    api_base: str,
    arguments: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Get detailed information about a specific car by ID.

    Expected arguments:
      - car_id: int (required)
      - user_token: str (optional)  # forwarded as Authorization header if provided
    """
    car_id = arguments.get("car_id")
    if car_id is None:
        return {"success": False, "error": "Missing required argument: car_id"}

    try:
        car_id_int = int(car_id)
    except (TypeError, ValueError):
        return {"success": False, "error": "car_id must be an integer"}

    headers: Dict[str, str] = {}
    user_token = arguments.get("user_token")
    if isinstance(user_token, str) and user_token.strip():
        headers["Authorization"] = f"Bearer {user_token.strip()}"

    url = f"{api_base}/cars/{car_id_int}"
    logger.info(f"Fetching car details: car_id={car_id_int}")

    try:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return {"success": True, "car": response.json()}
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error getting car details: {e}")
        return {
            "success": False,
            "error": f"HTTP {e.response.status_code}: {e.response.text}",
            "car_id": car_id_int,
        }
    except Exception as e:
        logger.error(f"Error getting car details: {e}", exc_info=True)
        return {"success": False, "error": str(e), "car_id": car_id_int}

