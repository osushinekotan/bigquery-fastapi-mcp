from datetime import datetime

from pydantic import BaseModel, Field


class ThoughtBase(BaseModel):
    """Base model for sequential thinking thoughts"""

    thought: str = Field(..., description="Your current thinking step")
    next_thought_needed: bool = Field(..., description="Whether another thought step is needed")
    thought_number: int = Field(..., description="Current thought number", gt=0)
    total_thoughts: int = Field(..., description="Estimated total thoughts needed", gt=0)
    is_revision: bool | None = Field(None, description="Whether this revises previous thinking")
    revises_thought: int | None = Field(None, description="Which thought is being reconsidered")
    branch_from_thought: int | None = Field(None, description="Branching point thought number")
    branch_id: str | None = Field(None, description="Branch identifier")
    needs_more_thoughts: bool | None = Field(None, description="If more thoughts are needed")


class ThoughtResponse(BaseModel):
    """Response model for sequential thinking endpoint"""

    thought_id: str = Field(..., description="Unique identifier for this thought")
    thought_number: int = Field(..., description="Current thought number")
    total_thoughts: int = Field(..., description="Current estimate of thoughts needed")
    next_thought_needed: bool = Field(..., description="Whether another thought step is needed")
    branches: list[str] = Field(default_factory=list, description="Available branch identifiers")
    thought_history_length: int = Field(..., description="Number of thoughts recorded so far")
    timestamp: datetime = Field(..., description="Timestamp when this thought was processed")


class ThoughtHistory(BaseModel):
    """Model for representing a stored thought"""

    id: str = Field(..., description="Unique identifier for this thought")
    thought: str = Field(..., description="The thinking step content")
    thought_number: int = Field(..., description="Number in thinking sequence")
    total_thoughts: int = Field(..., description="Total thoughts estimated")
    next_thought_needed: bool = Field(..., description="Whether another thought is needed")
    is_revision: bool | None = Field(None, description="Whether this revises previous thinking")
    revises_thought: int | None = Field(None, description="Which thought is being reconsidered")
    branch_from_thought: int | None = Field(None, description="Branching point thought number")
    branch_id: str | None = Field(None, description="Branch identifier")
    needs_more_thoughts: bool | None = Field(None, description="If more thoughts are needed")
    timestamp: datetime = Field(..., description="When this thought was recorded")


class BranchDetails(BaseModel):
    """Model for branch information"""

    id: str = Field(..., description="Branch identifier")
    thoughts: list[str] = Field(default_factory=list, description="Thought IDs in this branch")
