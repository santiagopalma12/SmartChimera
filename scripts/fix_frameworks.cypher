// 1. Assign React skill to facebook/react contributors
MATCH (e:Empleado {source_repo: 'facebook/react'})
MERGE (s:Skill {name: 'React'})
MERGE (e)-[:DEMUESTRA_COMPETENCIA {nivel: 0.8, inferred: true}]->(s);

// 2. Assign Django skill to django/django contributors
MATCH (e:Empleado {source_repo: 'django/django'})
MERGE (s:Skill {name: 'Django'})
MERGE (e)-[:DEMUESTRA_COMPETENCIA {nivel: 0.8, inferred: true}]->(s);

// 3. Assign VSCode skill (as 'TypeScript' expert implies it, but let's add specific domain knowledge)
MATCH (e:Empleado {source_repo: 'microsoft/vscode'})
MERGE (s:Skill {name: 'VSCode API'})
MERGE (e)-[:DEMUESTRA_COMPETENCIA {nivel: 0.8, inferred: true}]->(s);
