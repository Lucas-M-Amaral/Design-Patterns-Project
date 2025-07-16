from abc import ABC, abstractmethod
from typing import List, Dict


# ==============================
# SUBJECT (Notification Center)
# ==============================
class Observer(ABC):
    """Interface for all observers (students and instructors)."""

    @abstractmethod
    async def update(self, message: str) -> Dict:
        """Receive a notification update and return structured JSON."""
        pass


class NotificationCenter:
    """
    Subject in the Observer pattern.
    Manages observers (students and instructors) and returns JSON notifications.
    """

    def __init__(self):
        self._observers: List[Observer] = []

    def attach(self, observer: Observer):
        """Attach a new observer."""
        self._observers.append(observer)

    def detach(self, observer: Observer):
        """Detach an observer if needed."""
        if observer in self._observers:
            self._observers.remove(observer)

    async def notify(self, message: str) -> List[Dict]:
        """
        Notify all observers with the given message.
        Returns a list of JSON notifications.
        """
        notifications = []
        for observer in self._observers:
            notifications.append(await observer.update(message))

        self._observers.clear()  # Limpa após notificação
        return notifications


# OBSERVERS (Students / Instructors)
class StudentObserver(Observer):
    """Concrete Observer representing a student."""

    def __init__(self, student_id: int):
        self.student_id = student_id

    async def update(self, message: str) -> Dict:
        return {
            "recipient_type": "student",
            "recipient_id": self.student_id,
            "message": message
        }


class InstructorObserver(Observer):
    """Concrete Observer representing an instructor."""

    def __init__(self, instructor_id: int):
        self.instructor_id = instructor_id

    async def update(self, message: str) -> Dict:
        return {
            "recipient_type": "instructor",
            "recipient_id": self.instructor_id,
            "message": message
        }
