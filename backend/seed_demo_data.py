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
    NUM_EMPLOYEES = 150  # Scaled up for "Realism"
    
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

    employees = []
    
    print(f"Generating {NUM_EMPLOYEES} employees with Multi-Source Evidence Personas...")
    
    for i in range(NUM_EMPLOYEES):
        emp_id = f"emp_{i+1:03d}"
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        role = random.choice(roles)
        
        # Assign Persona
        dice = random.random()
        if dice < 0.15:
            persona = "EXPERT" # 15% - Both
        elif dice < 0.50:
            persona = "PRACTITIONER" # 35% - GitHub only
        elif dice < 0.80:
            persona = "THEORIST" # 30% - Cert only
        else:
            persona = "NOVICE" # 20% - None
            
        employees.append({
            "id": emp_id,
            "name": name,
            "role": role,
            "email": f"{name.lower().replace(' ', '.')}@smartchimera.com",
            "persona": persona
        })

    with driver.session() as session:
        print("Cleaning up database...")
        session.run("MATCH (n) DETACH DELETE n")
        
        print("Creating Employees...")
        for emp in employees:
            session.run("""
                MERGE (e:Empleado {id: $id})
                SET e.nombre = $name,
                    e.rol = $role,
                    e.email = $email,
                    e.persona = $persona
            """, **emp)

        print("Assigning Skills & Evidence (Multi-Source)...")
        for emp in employees:
            role_skills = skills_map.get(emp["role"], [])
            my_skills = random.sample(role_skills, k=min(len(role_skills), random.randint(3, 5)))
            
            for skill_name in my_skills:
                session.run("MERGE (s:Skill {name: $name})", name=skill_name)
                
                # Create base relationship
                session.run("""
                    MATCH (e:Empleado {id: $eid})
                    MATCH (s:Skill {name: $sname})
                    MERGE (e)-[r:DEMUESTRA_COMPETENCIA]->(s)
                    SET r.last_validated = datetime()
                """, eid=emp["id"], sname=skill_name)
                
                # Generate Evidence based on Persona
                evidences = []
                
                # 1. GitHub Project Evidence (Practical)
                if emp["persona"] in ["EXPERT", "PRACTITIONER"]:
                    evidences.append({
                        "source": "github",
                        "url": f"https://github.com/{emp['name'].replace(' ','')}/repo-{skill_name.lower()}",
                        "type": "commit_history"
                    })
                    
                # 2. LinkedIn Certification Evidence (Theoretical)
                if emp["persona"] in ["EXPERT", "THEORIST"]:
                    evidences.append({
                        "source": "linkedin",
                        "url": f"https://linkedin.com/cert/{skill_name.lower()}-cert-123",
                        "type": "certification"
                    })
                
                # Insert Evidence Nodes
                for ev in evidences:
                    session.run("""
                        MATCH (e:Empleado {id: $eid})
                        MATCH (s:Skill {name: $sname})
                        CREATE (v:Evidence {
                            id: randomUUID(),
                            source: $source,
                            url: $url,
                            type: $type,
                            date: datetime()
                        })
                        MERGE (e)-[:HAS_EVIDENCE]->(v)
                        MERGE (v)-[:ABOUT]->(s)
                    """, eid=emp["id"], sname=skill_name, **ev)

        # ====================================================================
        # ENGINEER LINCHPINS (Critical Employees)
        # ====================================================================
        print("Engineering Hub Linchpin...")
        hub_emp = employees[0] # Assume emp_001 is a charismatic leader
        other_ids = [e["id"] for e in employees if e["id"] != hub_emp["id"]]
        connections = random.sample(other_ids, k=int(NUM_EMPLOYEES * 0.4))
        
        for other_id in connections:
            session.run("""
                MATCH (a:Empleado {id: $id1}), (b:Empleado {id: $id2})
                MERGE (a)-[r:TRABAJO_CON]->(b)
                SET r.projects = 5
            """, id1=hub_emp["id"], id2=other_id)

        # General Connectivity
        print("Creating general connectivity...")
        for emp in employees:
            if emp["id"] == hub_emp["id"]: continue
            others = random.sample([e for e in employees if e["id"] != emp["id"]], k=random.randint(1, 3))
            for other in others:
                session.run("""
                    MATCH (a:Empleado {id: $id1}), (b:Empleado {id: $id2})
                    MERGE (a)-[r:TRABAJO_CON]->(b)
                """, id1=emp["id"], id2=other["id"])
                
        # Availability
        current_week = datetime.now().strftime("%Y-W%U")
        for emp in employees:
            hours = random.choice([0, 10, 40, 40, 40]) # Mostly full time
            session.run("""
                MATCH (e:Empleado {id: $eid})
                MERGE (a:Availability {week: $week, employee_id: $eid})
                SET a.hours = $hours
                MERGE (e)-[:HAS_AVAILABILITY]->(a)
            """, eid=emp["id"], week=current_week, hours=hours)

        print(f"Successfully seeded {NUM_EMPLOYEES} employees with Multi-Source logic! 🚀")
        
    driver.close()

if __name__ == "__main__":
    seed_demo_data()
