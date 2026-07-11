from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "change-this-secret-key-in-production"
)

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30