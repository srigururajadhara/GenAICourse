import os
import certifi
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()
os.environ.setdefault("SSL_CERT_FILE", certifi.where())


def get_driver():
    required = ("NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD")
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise RuntimeError("Missing Neo4j environment variables: " + ", ".join(missing))

    driver = GraphDatabase.driver(
        os.environ["NEO4J_URI"],
        auth=(os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"]),
        connection_timeout=20,
        max_connection_lifetime=3600,
    )
    driver.verify_connectivity()
    return driver


def get_database():
    return os.getenv("NEO4J_DATABASE", "neo4j")
