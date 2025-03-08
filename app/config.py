import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    )  # Set this in your environment
    SQLALCHEMY_TRACK_MODIFICATIONS = False
