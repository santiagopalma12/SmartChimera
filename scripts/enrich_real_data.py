"""
SmartChimera - Data Enrichment Script
======================================
Enriches real GitHub data with plausible synthetic attributes:
- Roles (inferred from skills)
- Emails (generated from usernames)
- Availability (randomized realistic distribution)
- Skill Levels (normalized)
- Implied Skills (e.g. React -> JavaScript)

Usage:
    python enrich_real_data.py
"""

import os
import sys
import random
from collections import Counter

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from neo4j import GraphDatabase
except ImportError:
    print("ERROR: neo4j package not installed. Run: pip install neo4j")
    sys.exit(1)

# Configuration
# Use 127.0.0.1 to avoid localhost resolution issues
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD")

if not NEO4J_PASS:
    print("ERROR: NEO4J_PASSWORD environment variable is required")
    print("Set it with: $env:NEO4J_PASSWORD = 'your_password'")
    sys.exit(1)

ROLE_RULES = {
    'Frontend Developer': {'JavaScript', 'TypeScript', 'HTML', 'CSS', 'Vue.js', 'Svelte', 'React'},
    'Backend Engineer': {'Python', 'Java', 'Go', 'Rust', 'Ruby', 'PHP', 'C#', 'SQL'},
    'Systems Engineer': {'C', 'C++', 'Rust', 'Shell', 'Assembly'},
    'DevOps Engineer': {'Docker', 'Kubernetes', 'Terraform', 'YAML', 'Shell', 'AWS'},
    'Data Scientist': {'Python', 'R', 'Jupyter', 'SQL', 'Pandas'},
}

IMPLIED_SKILLS = {
    'TypeScript': 'JavaScript',
    'React': 'JavaScript',
    'Vue.js': 'JavaScript',
    'Django': 'Python',
    'Flask': 'Python',
    'Spring Boot': 'Java',
}

def connect_neo4j():
    try:
        return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        sys.exit(1)

def infer_role(skills):
    """Infer likely role based on skills set."""
    if not skills:
        return "Software Developer"
    
    skill_set = set(skills)
    scores = Counter()
    
    for role, criteria in ROLE_RULES.items():
        matches = len(skill_set.intersection(criteria))
        if matches > 0:
            scores[role] = matches
            
    if not scores:
        return "Open Source Contributor"
        
    # Check for Full Stack
    if scores['Frontend Developer'] > 0 and scores['Backend Engineer'] > 0:
        return "Full Stack Developer"
        
    return scores.most_common(1)[0][0]

def enrich_data():
    driver = connect_neo4j()
    print(f"🔌 Connected to Neo4j at {NEO4J_URI}. Enriching data...")

    with driver.session() as session:
        # 1. Fetch all employees and their skills
        result = session.run("""
            MATCH (e:Empleado)
            OPTIONAL MATCH (e)-[:DEMUESTRA_COMPETENCIA]->(s:Skill)
            RETURN e.id as id, collect(s.name) as skills
        """)
        
        employees = [{"id": r["id"], "skills": r["skills"]} for r in result]
        print(f"👥 Processing {len(employees)} employees...")
        
        count = 0
        for emp in employees:
            e_id = emp["id"]
            skills = [s for s in emp["skills"] if s] # Filter None
            
            # 0. Add Implied Skills (e.g. TypeScript -> JavaScript)
            original_skills = set(skills)
            for s in original_skills:
                if s in IMPLIED_SKILLS:
                    implied = IMPLIED_SKILLS[s]
                    if implied not in skills:
                        skills.append(implied)
                        # Add to graph
                        session.run("MERGE (s:Skill {name: $name})", name=implied)
                        session.run("""
                            MATCH (e:Empleado {id: $id})
                            MATCH (s:Skill {name: $name})
                            MERGE (e)-[r:DEMUESTRA_COMPETENCIA]->(s)
                            SET r.nivel = 0.5, r.inferred = true, r.last_validated = datetime()
                        """, id=e_id, name=implied)

            # 1. Infer Role
            role = infer_role(skills)
            
            # 2. Generate Email
            email = f"{e_id.lower()}@github.contributor.org"
            
            # 3. Generate Availability (weighted towards full-time or distinct part-time)
            # 40h (30%), 20h (30%), 10h (20%), 0h (20%)
            availability_hours = random.choices([40, 30, 20, 10, 0], weights=[0.3, 0.1, 0.3, 0.2, 0.1], k=1)[0]
            
            # Update Node
            session.run("""
                MATCH (e:Empleado {id: $id})
                SET e.rol = $role,
                    e.email = $email,
                    e.enriched = true
                
                WITH e
                MERGE (a:Availability {employee_id: $id, week: $week})
                SET a.hours = $hours
                MERGE (e)-[:HAS_AVAILABILITY]->(a)
            """, id=e_id, role=role, email=email, week="2025-W49", hours=availability_hours)
            
            count += 1
            if count % 50 == 0:
                print(f"   Processed {count}...")

        # 4. Normalize Skill Levels (Cap at 1.0, currently stored as raw counts 0.1 per commit)
        print("⚖️  Normalizing skill levels...")
        session.run("""
            MATCH ()-[r:DEMUESTRA_COMPETENCIA]->()
            WHERE r.nivel > 1.0
            SET r.nivel = 1.0
        """)
        
        # 5. Ensure everyone has at least one basic skill if they had none (rare but possible)
        print("🧹 Cleaning up stragglers...")
        session.run("""
            MATCH (e:Empleado)
            WHERE NOT (e)-[:DEMUESTRA_COMPETENCIA]->()
            MATCH (s:Skill {name: 'Documentation'})
            MERGE (e)-[:DEMUESTRA_COMPETENCIA {nivel: 0.5}]->(s)
            SET e.rol = 'Contributor'
        """)

    driver.close()
    print("✅ Enrichment Complete!")

if __name__ == "__main__":
    enrich_data()
