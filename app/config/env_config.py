from dotenv import load_dotenv
import os

# Load .env variables into environment
_ = load_dotenv()


def must_getenv(key: str) -> str:
    value = os.getenv(key)
    if value is None:
        raise EnvironmentError(f"Missing required env var: {key}")
    return value

class Config:
    PORT: str = must_getenv("PORT")
    MONGODB_URL: str = must_getenv("MONGODB_URL")
    MONGODB_DB_NAME: str = must_getenv("MONGODB_DB_NAME")
    JWT_SECRET: str = must_getenv("JWT_SECRET")
    SHOPIFY_ACCESS_TOKEN: str = must_getenv("SHOPIFY_ACCESS_TOKEN")
    SHOPIFY_STORE_NAME: str = must_getenv("SHOPIFY_STORE_NAME")
