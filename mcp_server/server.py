"""
MCP Server for CarGenie
Model Context Protocol server that provides tools for AI agents to interact with CarGenie
"""
import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional
import httpx

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from mcp_server.tools.car_search import search_cars_tool
from mcp_server.tools.car_details import get_car_details_tool
from mcp_server.tools.recommendations import get_recommendations_tool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BACKEND_URL = os.environ.get("CARGENIE_BACKEND_URL", "http://localhost:8000")
API_BASE = f"{BACKEND_URL}/api/v1"


class MCPServer:
    """MCP Server implementation for CarGenie"""
    
    def __init__(self):
        self.tools = {
            "search_cars": search_cars_tool,
            "get_car_details": get_car_details_tool,
            "get_recommendations": get_recommendations_tool,
        }
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools"""
        return [
            {
                "name": "search_cars",
                "description": "Search for cars with various filters (make, model, year, price, fuel type, etc.)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "make": {"type": "string", "description": "Car make (e.g., Toyota, BMW)"},
                        "model": {"type": "string", "description": "Car model"},
                        "min_year": {"type": "integer", "description": "Minimum year"},
                        "max_year": {"type": "integer", "description": "Maximum year"},
                        "min_price": {"type": "number", "description": "Minimum price"},
                        "max_price": {"type": "number", "description": "Maximum price"},
                        "fuel_type": {"type": "string", "description": "Fuel type (gasoline, diesel, electric, hybrid)"},
                        "transmission": {"type": "string", "description": "Transmission type (manual, automatic, CVT)"},
                        "search": {"type": "string", "description": "Text search in make, model, description"},
                        "page": {"type": "integer", "description": "Page number (default: 1)"},
                        "page_size": {"type": "integer", "description": "Items per page (default: 12, max: 100)"},
                    },
                },
            },
            {
                "name": "get_car_details",
                "description": "Get detailed information about a specific car by ID",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "car_id": {"type": "integer", "description": "Car ID"},
                    },
                    "required": ["car_id"],
                },
            },
            {
                "name": "get_recommendations",
                "description": "Get personalized car recommendations (optionally for a specific user)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "n_results": {"type": "integer", "description": "Number of recommendations (default: 10, max: 20)"},
                        "user_token": {"type": "string", "description": "Optional JWT token for personalized recommendations"},
                    },
                },
            },
        ]
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool by name with arguments"""
        if name not in self.tools:
            return {
                "error": f"Tool '{name}' not found",
                "available_tools": list(self.tools.keys()),
            }
        
        try:
            tool_func = self.tools[name]
            result = await tool_func(self.client, API_BASE, arguments)
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
        except Exception as e:
            logger.error(f"Error calling tool {name}: {e}", exc_info=True)
            return {
                "error": str(e),
                "tool": name,
            }
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


async def handle_request(server: MCPServer, request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle an MCP request"""
    method = request.get("method")
    params = request.get("params", {})
    
    if method == "tools/list":
        tools = await server.list_tools()
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {"tools": tools},
        }
    
    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        result = await server.call_tool(tool_name, arguments)
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": result,
        }
    
    else:
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }


async def main():
    """Main server loop"""
    server = MCPServer()
    
    try:
        logger.info("CarGenie MCP Server starting...")
        logger.info(f"Backend URL: {BACKEND_URL}")
        
        # Read from stdin (MCP protocol)
        while True:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            
            line = line.strip()
            if not line:
                continue
            
            try:
                request = json.loads(line)
                response = await handle_request(server, request)
                print(json.dumps(response))
                sys.stdout.flush()
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": "Parse error"},
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
            except Exception as e:
                logger.error(f"Error handling request: {e}", exc_info=True)
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id") if 'request' in locals() else None,
                    "error": {"code": -32603, "message": str(e)},
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
    
    finally:
        await server.close()
        logger.info("CarGenie MCP Server stopped")


if __name__ == "__main__":
    asyncio.run(main())
