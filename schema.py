from pydantic import BaseModel
from typing import List, Dict, Optional

# # Pydantic models
class Activity(BaseModel):
    """Base model for a wellbeing activity"""
    name: str
    description: str
    benefits: List[str]
    frequency: str
    duration_min: str

class CategoryActivity(Activity):
    """Activity with category information"""
    category: str

class Category(BaseModel):
    """PERMA-V category model"""
    category: str  # Single letter code (P, E, R, M, A, V)
    name: str      # Full name (e.g., "Positive Emotions")
    description: str

class ActivityDetail(Activity):
    """Detailed view of an activity including the category it belongs to"""
    category: str

class ActivitiesResponse(BaseModel):
    """Response model for activities list endpoints"""
    activities: List[Activity]

class CategoriesResponse(BaseModel):
    """Response model for categories list endpoint"""
    categories: List[Category]

class ActivitySearchResponse(BaseModel):
    """Response model for activity search endpoint"""
    results: List[CategoryActivity]
    count: int

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str