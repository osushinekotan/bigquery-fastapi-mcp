import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.schemas.sequential_thinking import (
    BranchDetails,
    ThoughtBase,
    ThoughtHistory,
    ThoughtResponse,
)

router = APIRouter()

# In-memory storage for thoughts and branches
thought_history = []
branches = {}  # Dict mapping branch_id to list of thought_ids


def format_thought(thought_data: dict) -> str:
    """Format a thought for console display"""
    prefix = ""
    context = ""

    if thought_data.get("is_revision"):
        prefix = "🔄 Revision"
        context = f" (revising thought {thought_data.get('revises_thought')})"
    elif thought_data.get("branch_from_thought"):
        prefix = "🌿 Branch"
        context = f" (from thought {thought_data.get('branch_from_thought')}, ID: {thought_data.get('branch_id')})"
    else:
        prefix = "💭 Thought"
        context = ""

    header = f"{prefix} {thought_data.get('thought_number')}/{thought_data.get('total_thoughts')}{context}"
    thought_text = thought_data.get("thought")

    border_len = max(len(header), len(thought_text)) + 4
    border = "─" * border_len

    return f"""
┌{border}┐
│ {header.ljust(border_len - 2)} │
├{border}┤
│ {thought_text.ljust(border_len - 2)} │
└{border}┘"""


@router.post("/sequential-thinking", response_model=ThoughtResponse, operation_id="sequential_thinking")
async def process_thought(thought: ThoughtBase):
    """
    Process a sequential thinking step.

    This endpoint implements the sequential thinking tool for dynamic and reflective problem-solving.
    It allows breaking down complex problems into steps, revising previous thoughts, branching into
    alternative paths, and adjusting the total thoughts as needed.

    Parameters explained:
    - thought: Your current thinking step
    - next_thought_needed: True if you need more thinking
    - thought_number: Current number in sequence
    - total_thoughts: Current estimate of thoughts needed
    - is_revision: Whether this revises previous thinking
    - revises_thought: Which thought is being reconsidered
    - branch_from_thought: Branching point thought number
    - branch_id: Identifier for the current branch
    - needs_more_thoughts: If more thoughts are needed than initially estimated

    Returns:
    - Information about the processed thought including its ID, statistics, and available branches
    """
    try:
        # Input validation
        if thought.is_revision and thought.revises_thought is None:
            raise HTTPException(status_code=400, detail="If is_revision is true, revises_thought must be specified")

        if thought.branch_from_thought is not None and thought.branch_id is None:
            raise HTTPException(
                status_code=400, detail="If branch_from_thought is specified, branch_id must be provided"
            )

        # Adjust total_thoughts if needed
        adjusted_total_thoughts = thought.total_thoughts
        if thought.thought_number > thought.total_thoughts:
            adjusted_total_thoughts = thought.thought_number

        # Generate thought ID
        thought_id = str(uuid.uuid4())
        current_time = datetime.now()

        # Create thought record
        thought_record = {
            "id": thought_id,
            "thought": thought.thought,
            "thought_number": thought.thought_number,
            "total_thoughts": adjusted_total_thoughts,
            "next_thought_needed": thought.next_thought_needed,
            "is_revision": thought.is_revision,
            "revises_thought": thought.revises_thought,
            "branch_from_thought": thought.branch_from_thought,
            "branch_id": thought.branch_id,
            "needs_more_thoughts": thought.needs_more_thoughts,
            "timestamp": current_time,
        }

        # Add to thought history
        thought_history.append(thought_record)

        # Handle branch logic
        if thought.branch_id:
            if thought.branch_id not in branches:
                branches[thought.branch_id] = []
            branches[thought.branch_id].append(thought_id)

        # Print formatted thought to console for logging
        print(format_thought(thought_record))

        # Return response
        return ThoughtResponse(
            thought_id=thought_id,
            thought_number=thought.thought_number,
            total_thoughts=adjusted_total_thoughts,
            next_thought_needed=thought.next_thought_needed,
            branches=list(branches.keys()),
            thought_history_length=len(thought_history),
            timestamp=current_time,
        )

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error processing thought: {str(e)}")


@router.get(
    "/history",
    response_model=list[ThoughtHistory],
    operation_id="sequential_thinking_history",
)
async def get_thought_history():
    """
    Get the full history of sequential thoughts processed so far.

    Returns a list of all thoughts in the history, ordered by when they were added.
    """
    return [ThoughtHistory(**record) for record in thought_history]


@router.get(
    "/branch/{branch_id}",
    response_model=BranchDetails,
    operation_id="sequential_thinking_branch",
)
async def get_branch_thoughts(branch_id: str):
    """
    Get details about a specific branch including all thoughts in that branch.

    Args:
        branch_id: The identifier of the branch to retrieve

    Returns:
        Details about the branch and the thought IDs it contains
    """
    if branch_id not in branches:
        raise HTTPException(status_code=404, detail=f"Branch with ID {branch_id} not found")

    return BranchDetails(id=branch_id, thoughts=branches[branch_id])


@router.get("/metadata", operation_id="sequential_thinking_metadata")
async def get_metadata():
    """
    Get metadata about the sequential thinking process.

    Returns information about the number of thoughts, branches, and other statistics.
    """
    return {
        "total_thoughts": len(thought_history),
        "total_branches": len(branches),
        "branches": [{"id": b_id, "thought_count": len(thoughts)} for b_id, thoughts in branches.items()],
    }
