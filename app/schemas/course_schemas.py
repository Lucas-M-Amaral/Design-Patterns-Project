from typing import Generic, TypeVar, List
from pydantic import BaseModel, ConfigDict, Field
from app.models.courses import LessonTypeEnum

T = TypeVar('T')


class LessonCreate(BaseModel):
    """Schema for creating a lesson."""
    title: str = Field(..., max_length=255, description="Title of the lesson")
    description: str | None = Field(None, max_length=1000, description="Detailed description of the lesson content")
    lesson_type: LessonTypeEnum = Field(..., description="Type of the lesson content")
    order: int = Field(..., ge=1, description="Position of the lesson in the course sequence")
    file_path: str | None = Field(None, max_length=255, description="Path to the lesson media file if applicable")
    quiz_data: dict | None = Field(None, description="JSON structure containing quiz questions and answers")
    parent_id: int | None = Field(None, description="ID of the parent module if this is a sub-lesson")
    prerequisite_id: int | None = Field(None, description="ID of the lesson that must be completed before this one")


class LessonUpdate(BaseModel):
    """Schema for updating a lesson."""
    title: str | None = Field(None, max_length=255, description="New title for the lesson")
    description: str | None = Field(None, max_length=1000, description="Updated description of the lesson")
    lesson_type: LessonTypeEnum | None = Field(None, description="Updated lesson type")
    order: int | None = Field(None, ge=1, description="New position in the course sequence")
    file_path: str | None = Field(None, max_length=255, description="Updated path to the lesson media file")
    quiz_data: dict | None = Field(None, description="Updated quiz data structure")

    model_config = ConfigDict(from_attributes=True)


class LessonReadPartial(BaseModel):
    """Schema for reading a lesson not achieved yet."""
    id: int = Field(..., description="Unique identifier for the lesson")
    title: str = Field(..., description="Title of the lesson")
    lesson_type: LessonTypeEnum = Field(..., description="Type of the lesson")
    order: int = Field(..., description="Position in course sequence")
    course_id: int = Field(..., description="ID of the parent course")

    model_config = ConfigDict(from_attributes=True)


class LessonRead(BaseModel, Generic[T]):
    """Schema for reading a lesson."""
    id: int = Field(..., description="Unique identifier for the lesson")
    title: str = Field(..., description="Title of the lesson")
    description: str | None = Field(None, description="Detailed lesson description")
    lesson_type: LessonTypeEnum = Field(..., description="Type of the lesson")
    order: int = Field(..., description="Position in course sequence")
    file_path: str | None = Field(None, description="Path to lesson media file")
    quiz_data: dict | None = Field(None, description="Quiz questions and answers")
    course_id: int = Field(..., description="ID of the parent course")
    parent_id: int | None = Field(None, description="ID of parent module")
    prerequisite_id: int | None = Field(None, description="ID of prerequisite lesson")
    children: List[LessonReadPartial] = Field(default_factory=list, description="List of sub-lessons or modules")

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
    )


class CourseCreate(BaseModel):
    """Schema for creating a course."""
    title: str = Field(..., max_length=255, description="Title of the course")
    description: str | None = Field(None, max_length=2000, description="Detailed course description")
    price: float = Field(..., ge=0, description="Price of the course in USD")
    is_active: bool = Field(True, description="Whether the course is available for enrollment")


class CourseUpdate(BaseModel):
    """Schema for updating a course."""
    title: str | None = Field(None, max_length=255, description="Updated course title")
    description: str | None = Field(None, max_length=2000, description="Updated course description")
    price: float | None = Field(None, ge=0, description="Updated course price")
    is_active: bool | None = Field(None, description="Set course availability status")

    model_config = ConfigDict(from_attributes=True)


class CourseReadPartial(BaseModel):
    """Schema for reading a course not achieved yet."""
    id: int = Field(..., description="Unique course identifier")
    title: str = Field(..., description="Course title")
    description: str | None = Field(None, description="Course description")
    price: float = Field(..., description="Course price")
    is_active: bool = Field(..., description="Course availability status")
    instructor_id: int = Field(..., description="ID of the instructor")
    instructor_name: str = Field(..., description="Name of the instructor")

    model_config = ConfigDict(from_attributes=True)


class CourseRead(BaseModel, Generic[T]):
    """Schema for reading a course."""
    id: int = Field(..., description="Unique course identifier")
    title: str = Field(..., description="Course title")
    description: str | None = Field(None, description="Course description")
    price: float = Field(..., description="Course price")
    is_active: bool = Field(..., description="Course availability status")
    instructor_id: int = Field(..., description="ID of the instructor")
    instructor_name: str = Field(..., description="Name of the instructor")
    lessons: List[T] = Field(default_factory=list, description="List of lessons in this course")

    model_config = ConfigDict(from_attributes=True)


class CoursesTeaching(BaseModel):
    """Schema for reading courses that an instructor is teaching."""
    id: int = Field(..., description="Course ID")
    title: str = Field(..., description="Course title")
    price: float = Field(..., description="Course price")
    is_active: bool = Field(..., description="Course status")
    students_enrolled: int = Field(0, description="Number of students enrolled in this course")

    model_config = ConfigDict(from_attributes=True)


class CourseProgressionRead(BaseModel):
    """Schema for reading course progression."""
    course_id: int = Field(..., description="ID of the course")
    progress_percentage: float = Field(..., ge=0, le=100, description="Percentage of course completed")
    last_lesson_id: int | None = Field(None, description="ID of the last completed lesson")
    last_lesson_title: str | None = Field(None, description="Title of the last completed lesson")

    model_config = ConfigDict(from_attributes=True)