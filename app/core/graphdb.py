from app.core.config import settings
from py2neo import Graph

graph = Graph(settings.NEO4J_URI, auth=(settings.NEO4J_UNAME, settings.NEO4J_PASS), routing=True)