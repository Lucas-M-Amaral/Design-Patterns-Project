import os
from dotenv import load_dotenv

from os import getenv

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


load_dotenv("./.env")
DATABASE_URL = os.getenv("DATABASE_URL")
print(DATABASE_URL)