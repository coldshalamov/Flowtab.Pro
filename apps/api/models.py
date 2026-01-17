from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime


class Prompt(SQLModel, table=True):
    """Database model for prompts."""

    __tablename__ = "prompts"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="Unique identifier (UUID)"
    )
    
    slug: str = Field(unique=True, index=True, max_length=255)
    
    title: str = Field(max_length=500)
    
    summary: str = Field()
    
    difficulty: str = Field(max_length=20)
    
    # JSON fields for arrays - using SQLAlchemy Column with JSON type
    worksWith: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="List of compatible tools/browsers"
    )
    
    tags: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="List of tags for categorization"
    )
    
    targetSites: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="List of target websites"
    )
    
    promptText: str = Field()
    
    steps: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Step-by-step instructions"
    )
    
    notes: str | None = Field(default=None)
    
    createdAt: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )
    
    updatedAt: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
