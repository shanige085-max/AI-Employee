"""Template management for supported puzzle book formats."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class TemplateKey(StrEnum):
    """Canonical template identifiers supported by Module 3."""

    KIDS_MAZE = "kids_maze"
    KIDS_WORD_SEARCH = "kids_word_search"
    KIDS_CROSSWORD = "kids_crossword"
    ADULTS_MAZE = "adults_maze"
    ADULTS_WORD_SEARCH = "adults_word_search"
    ADULTS_CROSSWORD = "adults_crossword"


@dataclass(frozen=True, slots=True)
class PuzzleTemplate:
    """Describes a puzzle book template without rendering it yet."""

    key: TemplateKey
    display_name: str
    age_group: str
    puzzle_type: str
    default_difficulty: str


class TemplateManager:
    """Registry and lookup service for puzzle templates."""

    def __init__(self, templates: tuple[PuzzleTemplate, ...] | None = None) -> None:
        self._templates = {template.key: template for template in (templates or self.defaults())}

    @staticmethod
    def defaults() -> tuple[PuzzleTemplate, ...]:
        """Return all built-in templates required by Module 3."""

        return (
            PuzzleTemplate(TemplateKey.KIDS_MAZE, "Kids Maze", "kids", "maze", "easy"),
            PuzzleTemplate(TemplateKey.KIDS_WORD_SEARCH, "Kids Word Search", "kids", "word_search", "easy"),
            PuzzleTemplate(TemplateKey.KIDS_CROSSWORD, "Kids Crossword", "kids", "crossword", "easy"),
            PuzzleTemplate(TemplateKey.ADULTS_MAZE, "Adults Maze", "adults", "maze", "medium"),
            PuzzleTemplate(TemplateKey.ADULTS_WORD_SEARCH, "Adults Word Search", "adults", "word_search", "medium"),
            PuzzleTemplate(TemplateKey.ADULTS_CROSSWORD, "Adults Crossword", "adults", "crossword", "medium"),
        )

    def get(self, key: TemplateKey | str) -> PuzzleTemplate:
        """Return a template by key."""

        normalized = TemplateKey(key)
        return self._templates[normalized]

    def list_templates(self) -> tuple[PuzzleTemplate, ...]:
        """List all registered templates."""

        return tuple(self._templates.values())
