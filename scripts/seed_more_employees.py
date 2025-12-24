"""
Script para generar más empleados con skills diversas en Neo4j
"""
import os
from neo4j import GraphDatabase
import random

# Conectar directamente a Neo4j
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD")

if not NEO4J_PASS:
    print("ERROR: NEO4J_PASSWORD environment variable is required")
    print("Set it with: $env:NEO4J_PASSWORD = 'your_password'")
    import sys
    sys.exit(1)

def get_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

# Skills técnicas modernas
SKILLS_POOL = [
    "Python", "JavaScript", "TypeScript", "Java", "Go", "Rust",
    "React", "Vue", "Angular", "Node.js", "Express", "FastAPI",
    "Docker", "Kubernetes", "Terraform", "AWS", "Azure", "GCP",
    "PostgreSQL", "MongoDB", "Redis", "MySQL", "DynamoDB",
    "Git", "CI/CD", "Jenkins", "GitHub Actions", "GitLab CI",
    "REST API", "GraphQL", "gRPC", "Microservices",
    "Machine Learning", "TensorFlow", "PyTorch", "Pandas",
    "Agile", "Scrum", "Kanban", "Leadership", "Mentoring"
]

ROLES = [
    "Senior Software Engineer", "Full Stack Developer", "Backend Engineer",
    "Frontend Developer", "DevOps Engineer", "Site Reliability Engineer",
    "Data Engineer", "ML Engineer", "QA Engineer", "Tech Lead",
    "Software Architect", "Platform Engineer", "Security Engineer"
]

FIRST_NAMES = [
    "Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery", "Quinn",
    "Jamie", "Skylar", "Dakota", "Rowan", "Sage", "River", "Phoenix", "Cameron",
    "Blake", "Drew", "Finley", "Harper", "Hayden", "Kai", "Logan", "Mackenzie",
    "Parker", "Peyton", "Reese", "Sam", "Sawyer", "Spencer"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Thompson", "White",
    "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker"
]

def generate_employees(count=100):
    """Genera empleados sintéticos con skills variadas"""
    driver = get_driver()
    
    with driver.session() as session:
        # Primero asegurar que todas las skills existan
        for skill in SKILLS_POOL:
            session.run("""
                MERGE (h:Habilidad {nombre: $skill})
                ON CREATE SET h.categoria = 'Technical'
            """, skill=skill)
        
        print(f"✓ {len(SKILLS_POOL)} skills creadas/verificadas")
        
        # Generar empleados
        existing_count = session.run("MATCH (e:Empleado) RETURN count(e) as cnt").single()["cnt"]
        start_id = existing_count + 1
        
        for i in range(count):
            emp_id = f"emp_{str(start_id + i).zfill(3)}"
            nombre = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
            rol = random.choice(ROLES)
            disponibilidad = random.choice([10, 15, 20, 25, 30, 35, 40])
            
            # Crear empleado
            session.run("""
                MERGE (e:Empleado {id: $emp_id})
                SET e.nombre = $nombre,
                    e.rol = $rol,
                    e.disponibilidad_horas = $disponibilidad
            """, emp_id=emp_id, nombre=nombre, rol=rol, disponibilidad=disponibilidad)
            
            # Asignar 3-8 skills aleatorias
            num_skills = random.randint(3, 8)
            employee_skills = random.sample(SKILLS_POOL, num_skills)
            
            for skill in employee_skills:
                # Nivel entre 2.0 y 5.0
                nivel = round(random.uniform(2.0, 5.0), 1)
                
                session.run("""
                    MATCH (e:Empleado {id: $emp_id})
                    MATCH (h:Habilidad {nombre: $skill})
                    MERGE (e)-[r:POSEE_HABILIDAD]->(h)
                    SET r.nivel = $nivel,
                        r.ultimaDemostracion = date('2024-12-01')
                """, emp_id=emp_id, skill=skill, nivel=nivel)
            
            if (i + 1) % 20 == 0:
                print(f"✓ {i + 1}/{count} empleados creados")
        
        # Resumen final
        total = session.run("MATCH (e:Empleado) RETURN count(e) as cnt").single()["cnt"]
        total_skills = session.run("MATCH (h:Habilidad) RETURN count(h) as cnt").single()["cnt"]
        total_relations = session.run("MATCH (:Empleado)-[r:POSEE_HABILIDAD]->(:Habilidad) RETURN count(r) as cnt").single()["cnt"]
        
        print(f"\n✅ Generación completa:")
        print(f"   📊 Total empleados: {total}")
        print(f"   🎯 Total skills: {total_skills}")
        print(f"   🔗 Total relaciones: {total_relations}")
        
        # Verificar empleados con Python, React, Docker
        result = session.run("""
            MATCH (e:Empleado)-[:POSEE_HABILIDAD]->(h:Habilidad)
            WHERE h.nombre IN ['Python', 'React', 'Docker']
            WITH e, collect(DISTINCT h.nombre) as skills
            WHERE size(skills) >= 2
            RETURN count(e) as cnt
        """).single()["cnt"]
        
        print(f"   ✨ Empleados con 2+ de [Python, React, Docker]: {result}")

if __name__ == "__main__":
    print("🚀 Generando empleados adicionales...\n")
    generate_employees(100)
