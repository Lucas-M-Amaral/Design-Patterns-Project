import os
import pymongo

from typing_extensions import Annotated
from pydantic import BeforeValidator

# Database connection setup
# ------------------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")
"""str: The URL for the MongoDB database connection."""
MONGO_INITDB_DATABASE = os.getenv("MONGO_INITDB_DATABASE", "database")
"""str: The name of the MongoDB database to connect to."""

client = pymongo.AsyncMongoClient(DATABASE_URL)
"""AsyncMongoClient: The MongoDB client for asynchronous operations."""
db = client.get_database(MONGO_INITDB_DATABASE)
"""Database: The MongoDB database instance."""


async def get_db():
    """Get the database connection."""
    try:
        yield db
    finally:
        # Close the client connection when done
        await client.close()
        print("Database connection closed.")

# Type Aliases
# ------------------------------------------------------------------------------
PyObjectId = Annotated[str, BeforeValidator(str)]
"""PyObjectId: A type alias for a string that represents a MongoDB ObjectId."""


# Collections in the database.
# ------------------------------------------------------------------------------
collections = {
    "users": db.get_collection("users"),
}
"""dict: A dictionary of collections in the database."""
