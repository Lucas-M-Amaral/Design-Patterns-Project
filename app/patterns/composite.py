from abc import ABC, abstractmethod


# Composite Pattern for Course Structure
class LessonComponent(ABC):
    """Abstract base class for lesson components in a course structure."""

    @abstractmethod
    def render(self) -> str:
        """Render the content component."""
        raise NotImplementedError("Subclasses must implement this method.")


class LessonLeaf(LessonComponent):
    """Represents a leaf lesson component, such as a video or text content."""

    def __init__(self, title: str, content_type: str, content_path: str | None = None):
        self.title = title
        self.content_type = content_type
        self.content_path = content_path

    def render(self) -> str:
        """Render the content item."""
        return f"Lesson Leaf: {self.title}, Type: {self.content_type}, Path: {self.content_path or 'N/A'}"


class ModuleComposite(LessonComponent):
    """Represents a module composite that can contain other lessons or modules."""

    def __init__(self, title: str, lesson_type: str):
        self.title = title
        self.lesson_type = lesson_type
        self.lessons: list[LessonComponent] = []

    def render(self) -> str:
        """Render the course and its content items."""
        rendered_content = [f"Module Composite: {self.title}, Type: {self.lesson_type}"]
        for item in self.lessons:
            rendered_content.append(item.render())
        return "\n".join(rendered_content)