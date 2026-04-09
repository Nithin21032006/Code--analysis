from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from enum import Enum

class ActionType(str, Enum):
    REVIEW = "review"
    SUGGEST_FIX = "suggest_fix"
    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_CHANGES = "request_changes"

class Severity(str, Enum):
    NITPICK = "nitpick"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class CodeReviewAction(BaseModel):
    """Action space for code review agent"""
    action_type: ActionType
    comment: str = Field(description="Review comment or suggestion", max_length=500)
    line_number: Optional[int] = Field(None, description="Line number being reviewed", ge=1)
    severity: Severity = Field(default=Severity.WARNING)
    suggested_fix: Optional[str] = Field(None, description="Suggested code fix")

class PRFile(BaseModel):
    """A file in the pull request"""
    filename: str
    content: str
    changes: str
    additions: int
    deletions: int

class CodeReviewObservation(BaseModel):
    """Observation space - what the agent sees"""
    pr_title: str
    pr_description: str
    files_changed: List[PRFile]
    current_file_index: int = 0
    task_level: str  # easy, medium, hard
    issues_found_so_far: int = 0
    total_expected_issues: Optional[int] = None
    review_complete: bool = False

class CodeReviewReward(BaseModel):
    """Reward structure"""
    score: float = Field(ge=0.0, le=1.0)
    issues_found: int
    issues_missed: int
    false_positives: int
    suggestion_quality: float = Field(ge=0.0, le=1.0)

class StepResult(BaseModel):
    """Result from step() call"""
    observation: CodeReviewObservation
    reward: float
    done: bool
    info: dict
