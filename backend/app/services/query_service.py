"""
Query Service: Database operations for finding and filtering candidates.

Extracted from guardian_core.py to improve modularity.
Contains all Neo4j queries for employee/skill matching.
"""

from typing import List, Dict, Any
from ..db import get_driver


def find_candidates(skills_required: List[str]) -> List[Dict[str, Any]]:
    """
    Find all employees who have ALL required skills.
    
    Args:
        skills_required: List of skill names (e.g., ['Python', 'Docker'])
    
    Returns:
        List of employee dicts with id, nombre, and matched skills
    """
    driver = get_driver()
    query = """
    MATCH (e:Empleado)
    WHERE ALL(skill IN $skills WHERE EXISTS {
        MATCH (e)-[:DEMUESTRA_COMPETENCIA]->(s:Skill)
        WHERE toLower(s.name) = toLower(skill)
    })
    OPTIONAL MATCH (e)-[r:DEMUESTRA_COMPETENCIA]->(s:Skill)
    WHERE toLower(s.name) IN [x IN $skills | toLower(x)]
    RETURN e.id AS id, 
           e.nombre AS nombre,
           collect({skill: s.name, nivel: r.nivel}) AS skills_detail
    """
    
    with driver.session() as session:
        result = session.run(query, skills=skills_required)
        candidates = []
        for record in result:
            candidates.append({
                'id': record['id'],
                'nombre': record.get('nombre', record['id']),
                'skills_detail': record['skills_detail']
            })
        return candidates


def filter_availability(candidates: List[Dict], week: str, min_hours: int) -> List[Dict]:
    """
    HARD FILTER: Exclude candidates with insufficient availability.
    
    Args:
        candidates: List of candidate dicts with 'id' field
        week: ISO week string (e.g., '2025-W01')
        min_hours: Minimum required hours
    
    Returns:
        Filtered list with availability_hours added to each candidate
    """
    if not week or min_hours is None:
        # If no availability requirements, return all with default hours
        for c in candidates:
            c['availability_hours'] = 40  # Default assumption
        return candidates
    
    driver = get_driver()
    candidate_ids = [c['id'] for c in candidates]
    
    query = """
    UNWIND $ids AS eid
    MATCH (e:Empleado {id: eid})
    OPTIONAL MATCH (e)-[:HAS_AVAILABILITY]->(a:Availability {week: $week})
    RETURN e.id AS id, coalesce(a.hours, 0) AS hours
    """
    
    with driver.session() as session:
        result = session.run(query, ids=candidate_ids, week=week)
        availability_map = {r['id']: r['hours'] for r in result}
    
    # Filter and enrich
    filtered = []
    for candidate in candidates:
        hours = availability_map.get(candidate['id'], 0)
        if hours >= min_hours:
            candidate['availability_hours'] = hours
            filtered.append(candidate)
    
    return filtered


def fetch_forced_employees(emp_ids: List[str]) -> List[Dict]:
    """
    Fetch employee data for forced includes in bulk (optimized query).
    
    Args:
        emp_ids: List of employee IDs to fetch
    
    Returns:
        List of employee dicts with skills
    """
    if not emp_ids:
        return []
    
    driver = get_driver()
    query = """
    UNWIND $emp_ids AS eid
    MATCH (e:Empleado {id: eid})
    OPTIONAL MATCH (e)-[r:DEMUESTRA_COMPETENCIA]->(s:Skill)
    RETURN e.id AS id, 
           e.nombre AS nombre,
           collect({skill: s.name, nivel: r.nivel}) AS skills_detail
    """
    
    with driver.session() as session:
        result = session.run(query, emp_ids=emp_ids)
        return [{
            'id': record['id'],
            'nombre': record.get('nombre', record['id']),
            'skills_detail': record['skills_detail'],
            'forced_include': True,
            'availability_hours': 40
        } for record in result]
