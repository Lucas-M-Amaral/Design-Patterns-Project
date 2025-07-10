from typing import Optional
from abc import ABC, abstractmethod

from app.models.courses import Lesson, LessonProgress


# Chain of Responsibility Pattern for Lesson Progress Handling
class Handler(ABC):
    """Abstract base class for a handler in the chain of responsibility pattern for lesson progress."""

    @abstractmethod
    def handle(self, user_id: int, user_progress: dict[int, LessonProgress]) -> bool:
        """Check if user can access this lesson based on their progress."""
        raise NotImplementedError("Subclasses must implement this method.")


class ConcreteLessonProgressHandler(Handler):
    """Concrete handler that checks if a user can access a lesson based on their progress."""

    def __init__(self, lesson: Lesson):
        self.lesson = lesson
        self._next_handler: Optional[Handler] = None

    def set_next(self, handler: Handler) -> Handler:
        """Set the next handler in the chain."""
        self._next_handler = handler
        return handler

    def handle(self, user_id: int, user_progress: dict[int, LessonProgress]) -> bool:
        """Handle the request to check if the user can access the lesson."""
        if self.can_access_lesson(user_id, user_progress):
            if self._next_handler:
                return self._next_handler.handle(user_id, user_progress)
            return True
        return False

    def can_access_lesson(self, user_id: int, user_progress: dict[int, LessonProgress]) -> bool:
        """Check if the user can access the lesson based on their progress."""
        prerequisite_id = self.lesson.prerequisite_id
        if not prerequisite_id:
            return True

        progress = user_progress.get(prerequisite_id)
        if not progress:
            return False

        return progress.user_id == user_id and progress.completed
