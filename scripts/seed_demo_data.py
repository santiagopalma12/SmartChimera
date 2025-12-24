import sys
import os
import random
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

try:
    from neo4j import GraphDatabase
    # Simple settings class to avoid complex imports if config is tricky
    class Settings:
        NEO4J_URI = os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687")
        NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
        NEO4J_PASS = os.getenv("NEO4J_PASSWORD")
    settings = Settings()
    
    if not settings.NEO4J_PASS:
        print("ERROR: NEO4J_PASSWORD environment variable is required")
        print("Set it with: $env:NEO4J_PASSWORD = 'your_password'")
        sys.exit(1)
except ImportError:
    print("Import Error: Dependencies not found.")
    sys.exit(1)

def seed_demo_data():
    uri = settings.NEO4J_URI
    auth = (settings.NEO4J_USER, settings.NEO4J_PASS)
    
    print(f"Connecting to {uri}...")
    try:
        driver = GraphDatabase.driver(uri, auth=auth)
        driver.verify_connectivity()
    except Exception as e:
        print(f"Failed to connect: {e}")
        return

    # Configuration
    NUM_BG_EMPLOYEES = 138  # Background noise (Total 150 nodes with 12 Linchpins)
    
    first_names = ["Santiago", "Elena", "Marcus", "Sarah", "David", "Ana", "James", "Priya", "Tom", "Lisa", "Carlos", "Emma", "Lucas", "Sofia", "Mateo", "Valentina", "Nicolas", "Isabella", "Daniel", "Camila", "Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery", "Quinn", "Xavier", "Yara", "Zara", "Ben", "Chloe", "Dylan"]
    last_names = ["Perez", "Rodriguez", "Chen", "Johnson", "Kim", "Silva", "Wilson", "Patel", "Baker", "Wong", "Ruiz", "Davis", "Garcia", "Martinez", "Lopez", "Gonzalez", "Hernandez", "Smith", "Brown", "Jones", "Miller", "Davis", "White", "Black", "Green", "Hall", "Young", "King"]
    
    roles = ["Full Stack Developer", "Data Scientist", "Backend Engineer", "Frontend Specialist", "DevOps Engineer", "UX Designer", "Product Manager", "AI Researcher", "Security Engineer", "Mobile Developer", "Database Admin", "QA Engineer"]
    
    skills_map = {
        "Full Stack Developer": ["Python", "React", "TypeScript", "Node.js", "PostgreSQL", "Docker"],
        "Data Scientist": ["Python", "Machine Learning", "TensorFlow", "Pandas", "SQL", "R"],
        "Backend Engineer": ["Java", "Spring Boot", "Kafka", "Microservices", "AWS", "Go"],
        "Frontend Specialist": ["React", "CSS", "HTML", "Figma", "JavaScript", "Tailwind"],
        "DevOps Engineer": ["Docker", "Kubernetes", "Jenkins", "Terraform", "AWS", "Linux"],
        "UX Designer": ["Figma", "User Research", "Prototyping", "CSS", "Adobe XD"],
        "Product Manager": ["Agile", "Jira", "Product Strategy", "Communication", "Scrum"],
        "AI Researcher": ["Python", "PyTorch", "NLP", "Computer Vision", "Mathematics"],
        "Security Engineer": ["Network Security", "Penetration Testing", "Python", "Cryptography", "Cybersecurity"],
        "Mobile Developer": ["Swift", "Kotlin", "React Native", "iOS", "Android"],
        "Database Admin": ["PostgreSQL", "MongoDB", "Redis", "SQL Optimization", "Oracle"],
        "QA Engineer": ["Selenium", "Python", "Test Automation", "Jira", "Cypress"]
    }

    print("Cleaning up database...")
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")

    employees = []
    
    print(f"Generating {NUM_BG_EMPLOYEES} background employees...")
    for i in range(NUM_BG_EMPLOYEES):
        emp_id = f"emp_{i+1:03d}"
        role = random.choice(roles)
        employees.append({
            "id": emp_id,
            "name": f"{random.choice(first_names)} {random.choice(last_names)}",
            "role": role,
            "email": f"emp{i}@smartchimera.com",
            "persona": "PRACTITIONER"
        })

    # ---------------------------------------------------------
    # INJECT CURATED LINCHPINS (12 Archetypes)
    # ---------------------------------------------------------
    linchpins = [
        # CRITICAL RISK (High Project Weight + High Centrality or Unique Skill)
        { "id": "linch_001", "name": "Carlos Ruiz", "role": "Backend Engineer", "risk": "CRITICAL", "desc": "High Project Load", "projects": 45, "unique": "LegacyCoreV1" },
        { "id": "linch_002", "name": "Ana Silva", "role": "Product Manager", "risk": "CRITICAL", "desc": "Social Hub", "projects": 15, "unique": None },
        { "id": "linch_003", "name": "Elena Chen", "role": "Security Engineer", "risk": "CRITICAL", "desc": "Unique Knowledge", "projects": 10, "unique": "QuantumCrypto" },
        { "id": "linch_004", "name": "Marcus Johnson", "role": "DevOps Engineer", "risk": "CRITICAL", "desc": "System Owner", "projects": 35, "unique": "K8s-Custom-Controller" },
        
        # MEDIUM/HIGH RISK
        { "id": "risk_001", "name": "Dr. Sarah Miller", "role": "AI Researcher", "risk": "HIGH", "desc": "Siloed Expert", "projects": 20, "unique": "ProprietaryAI" },
        { "id": "risk_002", "name": "David Wilson", "role": "Full Stack Developer", "risk": "HIGH", "desc": "Cross-Team Link", "projects": 12, "unique": None },
        { "id": "risk_003", "name": "Lisa Wong", "role": "Database Admin", "risk": "MEDIUM", "desc": "Old Guard", "projects": 8, "unique": "Oracle8i" },
        { "id": "risk_004", "name": "Tom Baker", "role": "QA Engineer", "risk": "MEDIUM", "desc": "Gatekeeper", "projects": 18, "unique": None },

        # LOW RISK (High performers but redundant)
        { "id": "star_001", "name": "Fast Coder A", "role": "Frontend Specialist", "risk": "LOW", "desc": "Redundant Skill", "projects": 5, "unique": None },
        { "id": "star_002", "name": "Fast Coder B", "role": "Frontend Specialist", "risk": "LOW", "desc": "Redundant Skill", "projects": 5, "unique": None },
        { "id": "star_003", "name": "Backup Admin", "role": "DevOps Engineer", "risk": "LOW", "desc": "Shadow", "projects": 4, "unique": None },
        { "id": "star_004", "name": "Junior Dev", "role": "Full Stack Developer", "risk": "LOW", "desc": "Learning", "projects": 2, "unique": None },
    ]

    all_users = employees + linchpins

    print("Creating Nodes...")
    with driver.session() as session:
        for u in all_users:
            session.run("""
                MERGE (e:Empleado {id: $id})
                SET e.nombre = $name, e.rol = $role, e.email = $id + '@viz.com'
            """, **u)
    
    print("Assigning Skills and PROJECTS...")
    with driver.session() as session:
        for u in all_users:
            # Assign Standard Skills
            role_s = skills_map.get(u.get("role", "Full Stack Developer"), [])
            if not role_s: role_s = ["Python", "General"]
            
            # Everyone gets some random standard skills
            my_skills = random.sample(role_s, k=min(len(role_s), 3))
            
            # If explicit unique skill
            if u.get("unique"):
                my_skills.append(u.get("unique"))
                
            for sk in my_skills:
                # Skill Evidence
                session.run("""
                    MATCH (e:Empleado {id: $id})
                    MERGE (s:Skill {name: $skill})
                    MERGE (e)-[:DEMUESTRA_COMPETENCIA]->(s)
                """, id=u["id"], skill=sk)

            # PROJECT WEIGHT INJECTION (The "Peso" User asked for)
            # Normal users: 1-5 projects
            # Linchpins: Explicit count
            proj_count = u.get("projects", random.randint(1, 5))
            
            for p in range(proj_count):
                # Create 'Evidence' nodes with source='github' to eventually count as projects
                session.run("""
                    MATCH (e:Empleado {id: $id})
                    CREATE (ev:Evidence {
                        type: 'repository',
                        source: 'github',
                        url: 'http://github.com/project/' + toString($p_idx),
                        description: 'Contribution to critical project'
                    })
                    CREATE (e)-[:CREATED_EVIDENCE]->(ev)
                """, id=u["id"], p_idx=p)
    
    print("Creating Social Network (Collaboration)...")
    # Linchpins need massive connections to trigger BC score
    with driver.session() as session:
        # Connect background people randomly
        for _ in range(300):
            a = random.choice(employees)["id"]
            b = random.choice(employees)["id"]
            if a != b:
                session.run("""
                    MATCH (a:Empleado {id: $id1}), (b:Empleado {id: $id2})
                    MERGE (a)-[:TRABAJO_CON]->(b)
                """, id1=a, id2=b)
        
        # Super-Connect the Critical Linchpins to EVERYONE (Hubs)
        for linch in linchpins:
            if linch["risk"] in ["CRITICAL", "HIGH"]:
                # Connect to 20-30 random people
                targets = random.sample(employees, k=25)
                for t in targets:
                    session.run("""
                        MATCH (a:Empleado {id: $id1}), (b:Empleado {id: $id2})
                        MERGE (a)-[:TRABAJO_CON]->(b)
                    """, id1=linch["id"], id2=t["id"])

    driver.close()
    print("Seeding Complete. Linchpins Ready.")

if __name__ == "__main__":
    seed_demo_data()
