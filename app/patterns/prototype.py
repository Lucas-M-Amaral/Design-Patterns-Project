from abc import ABC, abstractmethod
from app.models.courses import Lesson


class Prototype(ABC):
    """Abstract base class for the Prototype pattern."""

    @abstractmethod
    def clone(self):
        """Create a deep copy of the prototype."""
        raise NotImplementedError("Subclasses must implement this method.")


class LessonPrototype(Prototype):
    """Concrete implementation of the Prototype pattern for cloning lessons."""
    def __init__(self, lesson: Lesson, new_course_id: int, new_prerequisite_id: int | None = None):
        self._lesson = lesson
        self._new_course_id = new_course_id
        self._new_prerequisite_id = new_prerequisite_id

    def clone(self) -> Lesson:
        """Create a deep copy of the lesson with updated course and prerequisite IDs."""
        lesson_clone = Lesson(
            title=self._lesson.title,
            description=self._lesson.description,
            lesson_type=self._lesson.lesson_type,
            order=self._lesson.order,
            file_path=self._lesson.file_path,
            quiz_data=self._lesson.quiz_data,
            course_id=self._new_course_id,
            prerequisite_id=self._new_prerequisite_id,
            parent_id=None
        )

        lesson_clone.children = [
            Lesson(
                title=child.title,
                description=child.description,
                lesson_type=child.lesson_type,
                order=child.order,
                file_path=child.file_path,
                quiz_data=child.quiz_data,
                parent_id=child.parent_id,
                prerequisite_id=child.prerequisite_id,
                course_id=self._new_course_id,
            )
            for child in self._lesson.children
        ]

        return lesson_clone
