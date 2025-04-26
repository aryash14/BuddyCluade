#
from mcp.server.fastmcp import FastMCP
from typing import List, Dict
# from schema import *
from client import *

# Create MCP server
mcp = FastMCP("Demo")

@mcp.tool()
def get_list_of_activities() -> List[str]:
    """Options for wellbeing activities"""
    return ["Drink Water", "Sleep Better", "Go outside"]
@mcp.tool()
def get_availability_time() -> str:
    """Get free timeslots availability from your calendar"""
    return get_free_slots()

@mcp.tool()
def tool3() -> Dict:
    """Tool 3"""
    pass
