"""
Recommendations Tool for MCP Server
"""

import logging
from typing import Any, Dict

import httpx

logger = logging.getLogger(__name__)


async def get_recommendations_tool(
    client: httpx.AsyncClient,
    api_base: str,
    arguments: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Get personalized car recommendations.

    Expected arguments:
      - n_results: int (optional, default 10)
      - user_token: str (optional)  # forwarded as Authorization header if provided
    """
    n_results = arguments.get("n_results", 10)
    try:
        n_results_int = int(n_results)
    except (TypeError, ValueError):
        n_results_int = 10

    headers: Dict[str, str] = {}
    user_token = arguments.get("user_token")
    if isinstance(user_token, str) and user_token.strip():
        headers["Authorization"] = f"Bearer {user_token.strip()}"

    url = f"{api_base}/recommendations"
    params = {"n_results": n_results_int}
    logger.info(f"Fetching recommendations: n_results={n_results_int}, auth={'yes' if headers else 'no'}")

    try:
        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return {"success": True, "data": response.json()}
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error getting recommendations: {e}")
        return {
            "success": False,
            "error": f"HTTP {e.response.status_code}: {e.response.text}",
        }
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}", exc_info=True)
        return {"success": False, "error": str(e)}

