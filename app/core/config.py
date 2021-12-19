from pydantic import  BaseSettings
import os

class Settings(BaseSettings):
    URL: str = os.getenv("URL")
    TOKEN: str = os.getenv("TOKEN")
    HOST: str = os.getenv("HOST")
    PORT: int = os.getenv("PORT")

settings = Settings()
