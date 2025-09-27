"""Agent workflow and prompt templates for the productivity copilot."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class PromptTemplate:
    name: str
    system_message: str
    user_message: str

    def render(self, **context: str) -> dict[str, str]:
        return {
            "system": self.system_message.format(**context),
            "user": self.user_message.format(**context),
        }


class Agent(Protocol):
    name: str
    description: str
    prompt_template: PromptTemplate

    def run(self, **context: str) -> dict[str, str]:  # pragma: no cover - interface
        raise NotImplementedError


@dataclass
class BaseAgent:
    name: str
    description: str
    prompt_template: PromptTemplate

    def run(self, **context: str) -> dict[str, str]:
        return self.prompt_template.render(**context)


planning_agent = BaseAgent(
    name="Planning Agent",
    description="Decides how to organize tasks into Todoist projects and sub-tasks.",
    prompt_template=PromptTemplate(
        name="planning",
        system_message=(
            "You are a planning specialist who maps a user's goals to Todoist projects, "
            "sections, and parent/child tasks. Respond with a JSON plan that includes "
            "project reuse recommendations and new task breakdowns."
        ),
        user_message=(
            "User request: {user_request}\n\n"
            "Existing projects: {project_summary}\n"
            "Existing tasks: {task_summary}\n"
            "Preferences: {preferences}"
        ),
    ),
)


scheduling_agent = BaseAgent(
    name="Scheduling Agent",
    description="Arranges tasks on the calendar respecting workload and preferences.",
    prompt_template=PromptTemplate(
        name="scheduling",
        system_message=(
            "You are a scheduling specialist. Propose due dates and recurrence patterns "
            "for the provided tasks. Consider workload balance and user availability."
        ),
        user_message=(
            "Tasks to schedule: {tasks}\n"
            "User availability: {availability}\n"
            "Current workload: {workload}\n"
        ),
    ),
)


search_agent = BaseAgent(
    name="Web Search Agent",
    description="Fetches supplemental context from the public web.",
    prompt_template=PromptTemplate(
        name="search",
        system_message=(
            "You are an internet research assistant. Summarize relevant findings and "
            "provide citations when appropriate."
        ),
        user_message="Research topic: {topic}",
    ),
)


@dataclass
class Orchestrator:
    """Composes agents into a multi-step workflow."""

    agents: list[BaseAgent]

    def plan(self, user_request: str, context: dict[str, str]) -> list[dict[str, str]]:
        steps: list[dict[str, str]] = []
        for agent in self.agents:
            prompt = agent.run(user_request=user_request, **context)
            steps.append({"agent": agent.name, "prompt": prompt})
        return steps


copilot_orchestrator = Orchestrator(agents=[planning_agent, scheduling_agent, search_agent])


__all__ = [
    "PromptTemplate",
    "Agent",
    "BaseAgent",
    "planning_agent",
    "scheduling_agent",
    "search_agent",
    "Orchestrator",
    "copilot_orchestrator",
]
