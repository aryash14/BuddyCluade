# @mcp.tool()
# def get_positive_emotions_activities() -> ActivitiesResponse:
#     """Get activities that generate positive feelings such as joy, gratitude, contentment, hope, and love."""
#     category_data = PERMAV_DATA.get("P", {})
#     activities = []
#     for name, details in category_data.get("activities", {}).items():
#         activities.append(Activity(
#             name=name,
#             description=details.get("description", ""),
#             benefits=details.get("benefits", []),
#             frequency=details.get("frequency", ""),
#             duration_min=details.get("duration_min", "")
#         ))
#     return ActivitiesResponse(activities=activities)

# @mcp.tool()
# def get_engagement_activities() -> ActivitiesResponse:
#     """Get activities that create a state of flow where one is completely absorbed and focused."""
#     category_data = PERMAV_DATA.get("E", {})
#     activities = []
#     for name, details in category_data.get("activities", {}).items():
#         activities.append(Activity(
#             name=name,
#             description=details.get("description", ""),
#             benefits=details.get("benefits", []),
#             frequency=details.get("frequency", ""),
#             duration_min=details.get("duration_min", "")
#         ))
#     return ActivitiesResponse(activities=activities)

# @mcp.tool()
# def get_relationships_activities() -> ActivitiesResponse:
#     """Get activities that build and strengthen positive connections with others."""
#     category_data = PERMAV_DATA.get("R", {})
#     activities = []
#     for name, details in category_data.get("activities", {}).items():
#         activities.append(Activity(
#             name=name,
#             description=details.get("description", ""),
#             benefits=details.get("benefits", []),
#             frequency=details.get("frequency", ""),
#             duration_min=details.get("duration_min", "")
#         ))
#     return ActivitiesResponse(activities=activities)

# @mcp.tool()
# def get_meaning_activities() -> ActivitiesResponse:
#     """Get activities that provide a sense of purpose and connection to something larger than oneself."""
#     category_data = PERMAV_DATA.get("M", {})
#     activities = []
#     for name, details in category_data.get("activities", {}).items():
#         activities.append(Activity(
#             name=name,
#             description=details.get("description", ""),
#             benefits=details.get("benefits", []),
#             frequency=details.get("frequency", ""),
#             duration_min=details.get("duration_min", "")
#         ))
#     return ActivitiesResponse(activities=activities)

# @mcp.tool()
# def get_accomplishment_activities() -> ActivitiesResponse:
#     """Get activities that provide a sense of achievement, progress, and mastery."""
#     category_data = PERMAV_DATA.get("A", {})
#     activities = []
#     for name, details in category_data.get("activities", {}).items():
#         activities.append(Activity(
#             name=name,
#             description=details.get("description", ""),
#             benefits=details.get("benefits", []),
#             frequency=details.get("frequency", ""),
#             duration_min=details.get("duration_min", "")
#         ))
#     return ActivitiesResponse(activities=activities)

# @mcp.tool()
# def search_activities(query: str) -> ActivitySearchResponse:
#     """Search for activities by keyword"""
#     results = []
#     query = query.lower()
    
#     for category_key, category in PERMAV_DATA.items():
#         for name, details in category.get("activities", {}).items():
#             if (query in name.lower() or 
#                 query in details.get("description", "").lower() or
#                 any(query in benefit.lower() for benefit in details.get("benefits", []))):
                
#                 results.append(CategoryActivity(
#                     name=name,
#                     description=details.get("description", ""),
#                     category=category.get("name", ""),
#                     benefits=details.get("benefits", []),
#                     frequency=details.get("frequency", ""),
#                     duration_min=details.get("duration_min", "")
#                 ))
    
#     return ActivitySearchResponse(results=results, count=len(results))
    


# @mcp.tool()
# def get_activity_details(activity_name: str) -> ActivityDetail:
#     """Get detailed information about a specific activity by name"""
#     for category_key, category in PERMAV_DATA.items():
#         activities = category.get("activities", {})
#         if activity_name in activities:
#             activity = activities[activity_name]
#             return ActivityDetail(
#                 name=activity_name,
#                 description=activity.get("description", ""),
#                 benefits=activity.get("benefits", []),
#                 frequency=activity.get("frequency", ""),
#                 duration_min=activity.get("duration_min", ""),
#                 category=category.get("name", "")
#             )
#     return ErrorResponse(error=f"Activity '{activity_name}' not found")