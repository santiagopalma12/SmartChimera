"""Quick verification script for ingested data."""
import sys
import os
sys.path.append('../backend')
from neo4j import GraphDatabase

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD")

if not NEO4J_PASS:
    print("ERROR: NEO4J_PASSWORD environment variable is required")
    print("Set it with: $env:NEO4J_PASSWORD = 'your_password'")
    sys.exit(1)

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
session = driver.session()

print("=" * 50)
print("INGESTION RESULTS")
print("=" * 50)

r1 = session.run('MATCH (e:Empleado) RETURN count(e) as total').single()
print(f"  Developers:     {r1['total']}")

r2 = session.run('MATCH (s:Skill) RETURN count(s) as total').single()
print(f"  Skills:         {r2['total']}")

r3 = session.run('MATCH ()-[r:TRABAJO_CON]->() RETURN count(r) as total').single()
print(f"  Collaborations: {r3['total']}")

r4 = session.run('MATCH ()-[r:DEMUESTRA_COMPETENCIA]->() RETURN count(r) as total').single()
print(f"  Competencies:   {r4['total']}")

print("\n" + "=" * 50)
print("TOP 10 DEVELOPERS (by contributions)")
print("=" * 50)
for r in session.run('MATCH (e:Empleado) RETURN e.id as login, e.contributions as contribs ORDER BY e.contributions DESC LIMIT 10'):
    print(f"  {r['login']}: {r['contribs']} contributions")

print("\n" + "=" * 50)
print("SKILLS FOUND")
print("=" * 50)
for r in session.run('MATCH (s:Skill) RETURN s.name as name ORDER BY name'):
    print(f"  - {r['name']}")

print("\n" + "=" * 50)
print("TOP COLLABORATORS (most connections)")
print("=" * 50)
for r in session.run('''
    MATCH (e:Empleado)-[r:TRABAJO_CON]->()
    RETURN e.id as login, count(r) as connections
    ORDER BY connections DESC LIMIT 10
'''):
    print(f"  {r['login']}: {r['connections']} connections")

driver.close()
print("\nVerification complete!")
