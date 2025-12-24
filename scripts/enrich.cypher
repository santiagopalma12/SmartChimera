// 1. Set Implied Skills (TypeScript -> JavaScript)
MATCH (e:Empleado)-[:DEMUESTRA_COMPETENCIA]->(:Skill {name: 'TypeScript'})
MERGE (js:Skill {name: 'JavaScript'})
MERGE (e)-[:DEMUESTRA_COMPETENCIA {nivel: 0.5, inferred: true}]->(js);

// 2. Set Implied Skills (React -> JavaScript)
MATCH (e:Empleado)-[:DEMUESTRA_COMPETENCIA]->(:Skill {name: 'React'})
MERGE (js:Skill {name: 'JavaScript'})
MERGE (e)-[:DEMUESTRA_COMPETENCIA {nivel: 0.5, inferred: true}]->(js);

// 3. Set Implied Skills (Django -> Python)
MATCH (e:Empleado)-[:DEMUESTRA_COMPETENCIA]->(:Skill {name: 'Django'})
MERGE (py:Skill {name: 'Python'})
MERGE (e)-[:DEMUESTRA_COMPETENCIA {nivel: 0.5, inferred: true}]->(py);

// 4. Default Role and Email
MATCH (e:Empleado)
SET e.rol = 'Software Engineer',
    e.email = toLower(e.id) + '@github.opensource.org';

// 5. Infer Frontend
MATCH (e:Empleado)-[:DEMUESTRA_COMPETENCIA]->(s:Skill)
WHERE s.name IN ['JavaScript', 'TypeScript', 'HTML', 'CSS', 'React', 'Vue.js']
WITH e, count(s) as c
WHERE c >= 1
SET e.rol = 'Frontend Developer';

// 6. Infer Backend
MATCH (e:Empleado)-[:DEMUESTRA_COMPETENCIA]->(s:Skill)
WHERE s.name IN ['Python', 'Java', 'Go', 'Rust', 'Ruby', 'PHP', 'C#', 'SQL', 'C++', 'Django']
WITH e, count(s) as c
WHERE c >= 1
SET e.rol = 'Backend Engineer';

// 7. Infer Full Stack (Intersection)
MATCH (e:Empleado)
WHERE (e)-[:DEMUESTRA_COMPETENCIA]->(:Skill {name: 'JavaScript'})
  AND (e)-[:DEMUESTRA_COMPETENCIA]->(:Skill {name: 'Python'})
SET e.rol = 'Full Stack Developer';

// 8. Infer DevOps
MATCH (e:Empleado)-[:DEMUESTRA_COMPETENCIA]->(s:Skill)
WHERE s.name IN ['Docker', 'Kubernetes', 'Terraform', 'YAML', 'Shell', 'AWS']
WITH e, count(s) as c
WHERE c >= 1
SET e.rol = 'DevOps Engineer';

// 9. Set Availability (Randomized via rand)
MATCH (e:Empleado)
WITH e, toInteger(rand() * 100) as h
WITH e, CASE 
  WHEN h < 30 THEN 40 
  WHEN h < 60 THEN 20 
  WHEN h < 80 THEN 10 
  ELSE 0 
END as hours
MERGE (a:Availability {employee_id: e.id, week: '2025-W49'})
SET a.hours = hours
MERGE (e)-[:HAS_AVAILABILITY]->(a);

// 10. Normalize Levels
MATCH ()-[r:DEMUESTRA_COMPETENCIA]->()
WHERE r.nivel > 1.0
SET r.nivel = 1.0;
