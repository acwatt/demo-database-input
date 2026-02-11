"""
Pydantic models for API request/response validation.
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class ProjectBase(BaseModel):
    """Base project model with core fields."""

    project_name: str = Field(..., min_length=1, max_length=200, description="Project name")
    description: str = Field(..., min_length=1, max_length=2000, description="Project description")
    industry: Optional[str] = Field(None, max_length=100, description="Industry sector")
    start_date: Optional[date] = Field(None, description="Project start date")
    end_date: Optional[date] = Field(None, description="Project end date")
    tools_used: Optional[str] = Field(None, max_length=500, description="Comma-separated tools/technologies")
    role: Optional[str] = Field(None, max_length=100, description="Role/position")
    client_organization: Optional[str] = Field(None, max_length=200, description="Client organization name")
    client_description: Optional[str] = Field(None, max_length=1000, description="Client description")

    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v, info):
        """Ensure end_date is not before start_date."""
        start_date = info.data.get('start_date')
        if v and start_date and v < start_date:
            raise ValueError('end_date cannot be before start_date')
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "project_name": "CleanEcon Rate Detection",
                "description": "Automated utility rate change detection system",
                "industry": "Energy",
                "start_date": "2024-01-15",
                "end_date": "2024-06-30",
                "tools_used": "Python, Pandas, FastAPI, SQLite",
                "role": "Lead Developer",
                "client_organization": "CleanEcon",
                "client_description": "Energy efficiency consulting firm"
            }
        }
    }


class ProjectCreate(ProjectBase):
    """Model for creating a new project."""
    pass


class ProjectUpdate(BaseModel):
    """Model for updating an existing project. All fields optional."""

    project_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=2000)
    industry: Optional[str] = Field(None, max_length=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    tools_used: Optional[str] = Field(None, max_length=500)
    role: Optional[str] = Field(None, max_length=100)
    client_organization: Optional[str] = Field(None, max_length=200)
    client_description: Optional[str] = Field(None, max_length=1000)

    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v, info):
        """Ensure end_date is not before start_date."""
        start_date = info.data.get('start_date')
        if v and start_date and v < start_date:
            raise ValueError('end_date cannot be before start_date')
        return v


class ProjectResponse(ProjectBase):
    """Model for API responses including database fields."""

    id: int = Field(..., description="Unique project ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "project_name": "CleanEcon Rate Detection",
                "description": "Automated utility rate change detection system",
                "industry": "Energy",
                "start_date": "2024-01-15",
                "end_date": "2024-06-30",
                "tools_used": "Python, Pandas, FastAPI, SQLite",
                "role": "Lead Developer",
                "client_organization": "CleanEcon",
                "client_description": "Energy efficiency consulting firm",
                "created_at": "2024-01-15T10:30:00",
                "updated_at": "2024-01-15T10:30:00"
            }
        }
    }


class FilterOptions(BaseModel):
    """Model for available filter values."""

    industries: list[str] = Field(..., description="Unique industries")
    clients: list[str] = Field(..., description="Unique client organizations")
    tools: list[str] = Field(..., description="Unique tools/technologies")

    model_config = {
        "json_schema_extra": {
            "example": {
                "industries": ["Energy", "Technology", "Healthcare"],
                "clients": ["CleanEcon", "TechCorp", "HealthPlus"],
                "tools": ["Python", "FastAPI", "React", "PostgreSQL"]
            }
        }
    }
