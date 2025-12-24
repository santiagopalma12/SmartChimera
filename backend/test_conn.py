from neo4j import GraphDatabase
import os
import sys

# Force bolt if not set, to match docker-compose
uri = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
user = os.getenv("NEO4J_USER", "neo4j")
password = os.getenv("NEO4J_PASSWORD")

if not password:
    print("ERROR: NEO4J_PASSWORD environment variable is required")
    print("Set it with: $env:NEO4J_PASSWORD = 'your_password'")
    sys.exit(1)

print(f"Connecting to {uri} as {user}...")

try:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    driver.verify_connectivity()
    print("Connectivity verified via driver.verify_connectivity()")

    with driver.session() as s:
        result = s.run("RETURN 1 AS val")
        val = result.single()["val"]
        print(f"Query result: {val}")
        
    print("SUCCESS: Connection and query working!")
    driver.close()
except Exception as e:
    print("FAILURE!")
    print(f"Error type: {type(e).__name__}")
    print(f"Error msg: {e}")
    # Print stack trace just in case
    import traceback
    traceback.print_exc()
    sys.exit(1)
