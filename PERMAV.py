from schema import (
    Activity, 
    ActivitiesResponse, 
    CategoriesResponse, 
    Category
)

import json



# Load PERMA-V activities data
def load_permav_data():
    with open('/Users/aryash/BuddyClaude/permav_activities.json', 'r') as file:
        data = json.load(file)
    return data.get('PERMA-V', {})



def get_permav_categories_helper() -> CategoriesResponse:
    """Get all PERMA-V categories with descriptions"""
    PERMAV_DATA = load_permav_data()
    categories = []
    for key, value in PERMAV_DATA.items():
        categories.append(Category(
            category=key,
            name=value.get("name", ""),
            description=value.get("description", "")
        ))
    return CategoriesResponse(categories=categories)


def get_vitality_activities_helper() -> ActivitiesResponse:
    """Get activities that promote physical health, energy, and overall wellbeing."""
    PERMAV_DATA = load_permav_data()
    category_data = PERMAV_DATA.get("V", {})
    activities = []
    for name, details in category_data.get("activities", {}).items():
        activities.append(Activity(
            name=name,
            description=details.get("description", ""),
            benefits=details.get("benefits", []),
            frequency=details.get("frequency", ""),
            duration_min=details.get("duration_min", "")
        ))
    return ActivitiesResponse(activities=activities)

