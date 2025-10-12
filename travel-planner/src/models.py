"""Data models for travel planner"""

from pydantic import BaseModel, Field, validator
from typing import List, Tuple, Literal, Optional
from datetime import date


class UserInput(BaseModel):
    """User input with validation"""
    
    destination: str = Field(..., min_length=2, description="Destination")
    start_date: date = Field(..., description="Trip start date")
    end_date: date = Field(..., description="Trip end date")
    budget_range: Tuple[float, float] = Field(..., description="Min/max budget in USD")
    pace: Literal["relaxed", "moderate", "packed"] = Field(..., description="Travel pace")
    food_preferences: List[str] = Field(default=[], description="Food preferences")
    activities: List[str] = Field(default=[], description="Activity types")
    content_filter: Literal["family_friendly", "adults_only"] = Field(
        ..., 
        description="Content filtering mode"
    )
    
    @validator("end_date")
    def end_after_start(cls, v, values):
        """Validate end date is after start date"""
        if "start_date" in values and v < values["start_date"]:
            raise ValueError("End date must be after start date")
        return v
    
    @validator("budget_range")
    def valid_budget(cls, v):
        """Validate budget range"""
        if v[0] > v[1]:
            raise ValueError("Min budget must be less than max budget")
        if v[0] < 0:
            raise ValueError("Budget must be positive")
        return v
    
    @property
    def duration_days(self) -> int:
        """Calculate trip duration in days"""
        return (self.end_date - self.start_date).days + 1
    
    def to_prompt_context(self) -> str:
        """Format as context for agents"""
        return f"""
Destination: {self.destination}
Travel Dates: {self.start_date} to {self.end_date} ({self.duration_days} days)
Budget: ${self.budget_range[0]:,.0f} - ${self.budget_range[1]:,.0f}
Pace: {self.pace}
Food Preferences: {', '.join(self.food_preferences) if self.food_preferences else 'No specific preferences'}
Activities: {', '.join(self.activities) if self.activities else 'Open to all'}
Content Filter: {self.content_filter} ← CRITICAL: Apply this filter!
"""


class TravelPlan(BaseModel):
    """Complete travel plan structure"""
    
    places_to_stay: str = Field(..., description="Accommodation recommendations")
    activities: str = Field(..., description="Things to do and attractions")
    transportation: str = Field(..., description="How to get around")
    itinerary: str = Field(..., description="Day-by-day schedule")
    
    def to_markdown(self) -> str:
        """Convert to markdown format"""
        sections = []
        
        sections.append("# Your Travel Plan\n")
        sections.append("## 🏨 Places to Stay\n")
        sections.append(self.places_to_stay)
        sections.append("\n\n---\n\n")
        
        sections.append("## 🎭 Activities\n")
        sections.append(self.activities)
        sections.append("\n\n---\n\n")
        
        sections.append("## 🚗 Transportation\n")
        sections.append(self.transportation)
        sections.append("\n\n---\n\n")
        
        sections.append("## 📅 Day-by-Day Itinerary\n")
        sections.append(self.itinerary)
        
        return "".join(sections)

