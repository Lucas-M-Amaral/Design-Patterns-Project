from fastapi import FastAPI

app = FastAPI(
    title="Course Platform API",
    description="API for managing courses, students, and instructors",
    version="0.1.0",
)

@app.get("/")
async def root():
    return {"message": "Course Platform API"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
