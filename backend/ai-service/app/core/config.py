from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import List

load_dotenv()

class Settings(BaseSettings):

    # API
    openai_api_key: str

    # Database
    user: str
    password: str
    host: str
    port: str
    dbname: str

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}?sslmode=disable"

    # Debug
    DEBUG_SQL: bool = False

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False
    }

settings = Settings() 