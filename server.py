#
from mcp.server.fastmcp import FastMCP
from schema import (
    ActivitiesResponse, 
    CategoriesResponse, 
)
from typing import Dict
from PERMAV import get_permav_categories_helper, get_vitality_activities_helper
from client import get_free_slots

# Create MCP server
mcp = FastMCP("BuddyClaude")

@mcp.tool()
def get_permav_categories() -> CategoriesResponse:
    """Get all PERMA-V categories with descriptions"""
    return get_permav_categories_helper()

@mcp.tool()
def get_vitality_activities() -> ActivitiesResponse:
    """Get activities that promote physical health, energy, and overall wellbeing."""
    return get_vitality_activities_helper()

@mcp.tool()
def get_availability_time(date: str = None) -> Dict:
    """Get free timeslots availability from your calendar"""
    return get_free_slots(date)


# Remove or update the placeholder tools
# @mcp.tool()
# def tool2() -> str:
#     """Tool 2"""
#     pass

# @mcp.tool()
# def tool3() -> Dict:
#     """Tool 3"""
#     pass
