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


class CourseComposite(LessonComponent):
    """Represents a course that can contain multiple content items or other courses."""

    def __init__(self, title: str):
        self.title = title
        self.lessons: list[LessonComponent] = []

    def render(self) -> str:
        """Render the course and its content items."""
        rendered_content = [f"Course Composite: {self.title}"]
        for item in self.lessons:
            rendered_content.append(item.render())
        return "\n".join(rendered_content)