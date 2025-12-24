from neo4j import GraphDatabase
import os
import sys

uri = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
user = os.getenv("NEO4J_USER", "neo4j")
password = os.getenv("NEO4J_PASSWORD")

if not password:
    print("ERROR: NEO4J_PASSWORD environment variable is required")
    print("Set it with: $env:NEO4J_PASSWORD = 'your_password'")
    sys.exit(1)

print(f"Connecting to {uri}...")

query = """
    MATCH (n)-[r:TRABAJO_CON]->(m)
    RETURN n, r, m
    LIMIT 300
    UNION
    MATCH (n)-[r:DEMUESTRA_COMPETENCIA]->(m)
    RETURN n, r, m
    LIMIT 300
"""

try:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as s:
        print("Running complex query...")
        result = s.run(query)
        # Consume result
        records = list(result)
        print(f"Query successful. Extracted {len(records)} records.")
        
    driver.close()
    print("SUCCESS")
except Exception as e:
    print("FAILURE")
    import traceback
    traceback.print_exc()
    sys.exit(1)
