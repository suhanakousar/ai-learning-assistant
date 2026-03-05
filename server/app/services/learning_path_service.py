"""
Dynamic Learning Path Generator service.
Produces structured roadmaps (beginner, intermediate, advanced, resources, timeline).
"""

import json
import re

from app.services.ai_service import get_llm
from app.utils.prompt_templates import LEARNING_PATH_SYSTEM, LEARNING_PATH_USER


def generate_learning_path(topic: str) -> dict:
    """
    Generate a structured learning roadmap for the given topic.
    Returns a dict with keys: beginner, intermediate, advanced, resources, timeline.
    """
    topic = (topic or "").strip()
    if not topic:
        return {
            "roadmap": {
                "beginner": [],
                "intermediate": [],
                "advanced": [],
                "resources": [],
                "timeline": "Provide a topic to generate a roadmap.",
            }
        }

    llm = get_llm()
    from langchain_core.messages import SystemMessage, HumanMessage
    from app.utils.llm_retry import invoke_with_retry
    messages = [
        SystemMessage(content=LEARNING_PATH_SYSTEM),
        HumanMessage(content=LEARNING_PATH_USER.format(topic=topic)),
    ]

    response = invoke_with_retry(llm, messages)
    raw = response.content.strip() if hasattr(response, "content") else str(response).strip()

    # Strip markdown code fences if present
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```\s*$", "", raw)
    raw = raw.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {
            "roadmap": {
                "beginner": [],
                "intermediate": [],
                "advanced": [],
                "resources": [],
                "timeline": "Could not parse roadmap. Please try again.",
            }
        }

    # Normalize to expected keys (allow both camelCase and lowercase from model)
    roadmap = {
        "beginner": data.get("beginner", data.get("Beginner", [])),
        "intermediate": data.get("intermediate", data.get("Intermediate", [])),
        "advanced": data.get("advanced", data.get("Advanced", [])),
        "resources": data.get("resources", data.get("Resources", [])),
        "timeline": data.get("timeline", data.get("Timeline", "Not specified.")),
    }
    if not isinstance(roadmap["beginner"], list):
        roadmap["beginner"] = []
    if not isinstance(roadmap["intermediate"], list):
        roadmap["intermediate"] = []
    if not isinstance(roadmap["advanced"], list):
        roadmap["advanced"] = []
    if not isinstance(roadmap["resources"], list):
        roadmap["resources"] = []

    return {"roadmap": roadmap}
