from app.core.config import settings
from neo4j import GraphDatabase

graph = GraphDatabase(settings.NEO4J_URI, auth=(settings.NEO4J_UNAME, settings.NEO4J_PASS), routing=True)