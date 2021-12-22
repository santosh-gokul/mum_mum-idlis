#!/usr/bin/env python3

from app.core.config import settings
from app.main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host = settings.HOST, port = settings.PORT)