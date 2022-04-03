from app.core.config import settings
from neo4j import GraphDatabase

graph = GraphDatabase.driver(settings.NEO4J_URI, auth=(settings.NEO4J_UNAME, settings.NEO4J_PASS))

def get_session():
    return graph.session()