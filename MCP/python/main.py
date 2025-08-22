"""
MCP Server - Python Implementation
"""

import os
import json
import requests
from pathlib import Path
from typing import Annotated
from pydantic import Field
from mcp.server.fastmcp import FastMCP

# Create MCP server instance
mcp = FastMCP("MCP Server")

def get_config():
    """Get configuration from environment or config file."""
    class Config:
        def __init__(self):
            self.base_url = os.getenv("API_BASE_URL")
            self.bearer_token = os.getenv("API_BEARER_TOKEN")
            
            # Try to load from config file if env vars not set
            if not self.base_url or not self.bearer_token:
                config_path = Path.home() / ".api" / "config.json"
                if config_path.exists():
                    with open(config_path, 'r') as f:
                        config_data = json.load(f)
                        self.base_url = self.base_url or config_data.get("baseURL")
                        self.bearer_token = self.bearer_token or config_data.get("bearerToken")
    
    return Config()

# Add configuration resource
@mcp.resource("config://settings")
def get_config_resource() -> str:
    """Get current configuration settings."""
    config = get_config()
    return json.dumps({
        "base_url": config.base_url,
        "bearer_token": "***" if config.bearer_token else None
    }, indent=2)

# Tool functions
@mcp.tool()
def get_query_json(name: Annotated[str, Field(description="A displayable name for the specified place.")], latitude: Annotated[str, Field(description="The latitude of the specified place.")], longitude: Annotated[str, Field(description="The longitude of the specified place.")], sw: Annotated[str, Field(description="Along with ne, forms a bounded box using the longitude and latitude coordinates specified as the southwest corner. The search results are limited to the resulting box. Two float values, separated by a comma `latitude,longitude` <br/> The ne parameter is required to use this parameter.")], query: Annotated[str, Field(description="Search keywords to perform a text search on the fields: web_description, event_name and venue_name. \'AND\' searches can be performed by wrapping query terms in quotes. If you do not specify a query, all results will be returned.")], filter: Annotated[str, Field(description="Filters search results based on the facets provided. For more information on the values you can filter on, see Facets.")], date_range: Annotated[str, Field(description="Start date to end date in the following format- YYYY-MM-DD:YYYY-MM-DD")], sort: Annotated[str, Field(description="Sorts your results on the fields specified. <br/> `sort_value1+[asc | desc],sort_value2+[asc|desc],[...]`<br/> Appending +asc to a facet or response will sort results on that value in ascending order. Appending +desc to a facet or response will sort results in descending order. You can sort on multiple fields. You can sort on any facet. For the list of responses you can sort on, see the Sortable Field column in the Response table. <br/><br/>If you are doing a spatial search with the ll parameter, you can also sort by the distance from the center of the search: dist+[asc | desc] <br/> **Note:** either +asc or +desc is required when using the sort parameter.")], elevation: Annotated[str, Field(description="The elevation of the specified place, in meters.")], facets: Annotated[str, Field(description="When facets is set to 1, a count of all facets will be included in the response.")], limit: Annotated[str, Field(description="Limits the number of results returned")], offset: Annotated[str, Field(description="Sets the starting point of the result set")]) -> str:
    """Geographic API"""
    try:
        config = get_config()
        
        if not config.base_url or not config.bearer_token:
            return "Error: Missing API configuration. Please set API_BASE_URL and API_BEARER_TOKEN environment variables."
        
        # Build request parameters
        params = {}
        if name: params["name"] = name
        if latitude: params["latitude"] = latitude
        if longitude: params["longitude"] = longitude
        if sw: params["sw"] = sw
        if query: params["query"] = query
        if filter: params["filter"] = filter
        if date_range: params["date_range"] = date_range
        if sort: params["sort"] = sort
        if elevation: params["elevation"] = elevation
        if facets: params["facets"] = facets
        if limit: params["limit"] = limit
        if offset: params["offset"] = offset
        
        # Make API call
        url = f"{config.base_url}/api/unknown"
        
        headers = {
            "Authorization": f"Bearer {config.bearer_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        # Handle HTTP errors
        if response.status_code >= 400:
            try:
                error_data = response.json()
                return f"Failed to format JSON: {json.dumps(error_data, indent=2)}"
            except json.JSONDecodeError:
                return f"Failed to format JSON: {response.text}"
        
        # Parse response
        try:
            result = response.json()
            return json.dumps(result, indent=2)
        except json.JSONDecodeError:
            # Fallback to raw text if JSON parsing fails
            return response.text
            
    except requests.exceptions.ConnectionError as e:
        return f"Request failed: Connection error - {str(e)}"
    except requests.exceptions.Timeout as e:
        return f"Request failed: Request timeout - {str(e)}"
    except requests.exceptions.RequestException as e:
        return f"Request failed: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


if __name__ == "__main__":
    mcp.run()
