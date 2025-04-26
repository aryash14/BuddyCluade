# PERMA-V Wellbeing API

This project provides an API for accessing PERMA-V wellbeing activities through an MCP server.

## What is PERMA-V?

PERMA-V is a wellbeing framework that includes:

- **P**: Positive Emotions
- **E**: Engagement 
- **R**: Relationships
- **M**: Meaning
- **A**: Accomplishment
- **V**: Vitality

Each category contains activities designed to improve wellbeing in that specific area.

## Setup

1. Clone this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the server:

```bash
python -m uvicorn server:mcp.app --reload
```

The API will be available at `http://localhost:8000`.

## API Tools

The MCP server provides the following tools:

- `get_permav_categories()` - Get all PERMA-V categories
- `get_positive_emotions_activities()` - Get activities for the Positive Emotions category
- `get_engagement_activities()` - Get activities for the Engagement category
- `get_relationships_activities()` - Get activities for the Relationships category
- `get_meaning_activities()` - Get activities for the Meaning category
- `get_accomplishment_activities()` - Get activities for the Accomplishment category
- `get_vitality_activities()` - Get activities for the Vitality category
- `get_activity_details(activity_name)` - Get details for a specific activity
- `search_activities(query)` - Search for activities across all categories

## Example Usage

Use the provided MCP client to interact with the API:

```python
from mcp.client import Client

client = Client("http://localhost:8000")

# Get all categories
categories = client.get_permav_categories()
print(categories)

# Get all activities for Positive Emotions
activities = client.get_positive_emotions_activities()
print(activities)

# Search for activities related to "meditation"
results = client.search_activities("meditation")
print(results)
```
