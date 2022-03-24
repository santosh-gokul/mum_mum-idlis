from pydantic import  BaseSettings
import os

class Settings(BaseSettings):
    HEROKU_URL: str = os.environ["HEROKU_URL"]
    UNIQUE_STRING: str = os.environ["UNIQUE_STRING"]
    NEO4J_URI: str = os.environ["NEO4J_URI"]
    NEO4J_PASS: str = os.environ["NEO4J_PASS"]
    NEO4J_UNAME: str = os.environ["NEO4J_UNAME"]
    HOST: str = os.environ["HOST"]
    PORT: int = os.environ["PORT"]

    class Config:
        env_file = '/Users/santosh/mum_mum-idlis/.env'
settings = Settings()
