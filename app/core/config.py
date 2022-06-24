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
    SECRET: str = os.environ["SECRET"]
    TWILIO_ACCOUNT_SID: str = os.environ["TWILIO_ACCOUNT_SID"]
    TWILIO_AUTH_TOKEN: str = os.environ["TWILIO_AUTH_TOKEN"]
    TWILIO_NUMBER: str = os.environ["TWILIO_NUMBER"]

    class Config:
        env_file = '/Users/santosh/mum_mum-idlis/.env'
settings = Settings()
