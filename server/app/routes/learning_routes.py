"""
Dynamic Learning Path Generator API routes.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.learning_path_service import generate_learning_path

router = APIRouter(prefix="/api", tags=["Learning Path"])


class LearningPathRequest(BaseModel):
    """Request body for POST /api/learning-path."""

    topic: str = Field(..., description="Topic for the learning roadmap", min_length=1)


class LearningPathRoadmap(BaseModel):
    """Nested roadmap structure."""

    beginner: list[str] = Field(default_factory=list, description="Beginner phase items")
    intermediate: list[str] = Field(default_factory=list, description="Intermediate phase items")
    advanced: list[str] = Field(default_factory=list, description="Advanced phase items")
    resources: list[str] = Field(default_factory=list, description="Recommended resources")
    timeline: str = Field(default="", description="Estimated learning timeline")


class LearningPathResponse(BaseModel):
    """Response for POST /api/learning-path."""

    roadmap: LearningPathRoadmap = Field(..., description="Structured learning roadmap")


@router.post("/learning-path", response_model=LearningPathResponse)
def api_learning_path(request: LearningPathRequest):
    """
    Generate a structured learning roadmap for the given topic.
    Returns beginner, intermediate, advanced phases, resources, and estimated timeline.
    """
    try:
        result = generate_learning_path(request.topic)
        roadmap = result["roadmap"]
        return LearningPathResponse(
            roadmap=LearningPathRoadmap(
                beginner=roadmap.get("beginner", []),
                intermediate=roadmap.get("intermediate", []),
                advanced=roadmap.get("advanced", []),
                resources=roadmap.get("resources", []),
                timeline=roadmap.get("timeline", ""),
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Learning path generation failed: {str(e)}")
