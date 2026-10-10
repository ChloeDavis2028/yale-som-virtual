"""AI avatars of Yale SOM professors. Each one is a cached PydanticAI agent.

To add an avatar: write backend/prompts/<id>.md, add a Person to PEOPLE, add an entry to
PEOPLE_INFO in src/talk.js, and put a Professor preset in a classroom (src/Faculty.jsx).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

os.environ.setdefault("PYDANTIC_AI_NO_BANNER", "1")

from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider

import courses

HERE = Path(__file__).resolve().parent
# .env may live in backend/, the game folder, or one or two folders up. Load them all.
for env in (HERE / ".env", HERE.parent / ".env", HERE.parent.parent / ".env", HERE.parent.parent.parent / ".env"):
    load_dotenv(env)

PORTKEY_BASE_URL = "https://api.portkey.ai/v1"
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-6-luna")


@dataclass(frozen=True)
class Person:
    id: str
    name: str
    title: str
    room: str
    course_number: str
    prompt_file: str


PEOPLE: dict[str, Person] = {
    "zaman": Person(
        id="zaman", name="Tauhid Zaman", title="Professor", room="2200",
        course_number="MGT 409", prompt_file="zaman.md",
    ),
}


def make_model() -> OpenAIResponsesModel:
    api_key = os.getenv("PORTKEY_API_KEY")
    if not api_key:
        raise RuntimeError("PORTKEY_API_KEY is not set. Put it in backend/.env (or one or two folders up).")
    # gpt-6-luna on Portkey only takes function tools through the Responses API
    return OpenAIResponsesModel(MODEL_NAME, provider=OpenAIProvider(base_url=PORTKEY_BASE_URL, api_key=api_key))


@lru_cache(maxsize=None)
def agent_for(person_id: str) -> Agent:
    person = PEOPLE[person_id]
    persona = (HERE / "prompts" / person.prompt_file).read_text(encoding="utf-8")
    instructions = (
        f"{persona}\n\n## Course facts (from the Yale SOM catalog)\n{courses.course_brief(person.course_number)}"
    )
    agent = Agent(make_model(), instructions=instructions)

    @agent.tool_plain
    def search_courses(keyword: str) -> list[dict]:
        """Find MBA courses whose number, title, description, or instructor matches the keyword."""
        return courses.search_courses(keyword)

    @agent.tool_plain
    def course_info(course_number: str) -> list[dict]:
        """Every section of one course (e.g. 'MGT 409'): description, instructor, days/times, room."""
        return courses.course_sections(course_number)

    @agent.tool_plain
    def search_course_material(question: str) -> list[dict]:
        """Look up course questions and answers (statistics, regression, central limit theorem, variance,
        confidence intervals, hypothesis tests, AI agents, PydanticAI). Use before explaining a concept."""
        return courses.search_material(question)

    @agent.tool_plain
    def course_material_topics() -> list[str]:
        """List every topic in the course question-and-answer database."""
        return courses.material_topics()

    return agent
