from pydantic import  BaseSettings
import os

class Settings(BaseSettings):
    URL: str = os.environ["URL"]
    TOKEN: str = os.environ["TOKEN"]
    HOST: str = os.environ["HOST"]
    PORT: int = os.environ["PORT"]

settings = Settings()
