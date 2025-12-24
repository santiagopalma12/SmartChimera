"""
Project Chimera - Smart Team Assembly Engine
Main FastAPI application with all Phase 0-6 endpoints.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional
from .db import get_driver
from .schemas import (
    TeamRequest, Dossier, EmployeeListResponse, EmployeeResponse,
    LinchpinEmployee, MissionProfile
)
from .guardian_core import generate_dossiers
from .linchpin_detector import LinchpinDetector
from .mission_profiles import MISSION_PROFILES
from .scoring import recompute_all_skill_levels
from .uid_normalizer_v2 import normalize_all_employees
import uuid

app = FastAPI(
    title="Project Chimera",
    description="Smart Team Assembly Engine - Evidence-based team recommendations",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "message": "Project Chimera API",
        "version": "1.0.0",
        "status": "operational"
    }


# ============================================================================
# GUARDIAN ENDPOINTS (Phase 5-6)
# ============================================================================

@app.post("/api/recommend", response_model=Dict)
def recommend_teams(request: TeamRequest):
    """
    Generate team recommendations based on requirements and mission profile.
    
    Phase 5: Guardian Co-Pilot Mode
    Phase 6: Policy & Governance (mission profiles, overrides)
    """
    try:
        print("=" * 80)
        print("DEBUG: Received request:")
        print(f"  mission_profile: {request.mission_profile}")
        print(f"  k: {request.k}")
        print(f"  requisitos_hard: {request.requisitos_hard}")
        print("=" * 80)
        
        dossiers = generate_dossiers(request.dict())
        
        print(f"✓ Generated {len(dossiers)} dossiers successfully")
        return {
            "request_id": str(uuid.uuid4()),
            "dossiers": [d.dict() for d in dossiers]
        }
    except Exception as e:
        print("=" * 80)
        print("✗ ERROR EN /api/recommend:")
        print(f"  Tipo: {type(e).__name__}")
        print(f"  Mensaje: {str(e)}")
        print("-" * 80)
        import traceback
        traceback.print_exc()
        print("=" * 80)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/linchpins")
def get_linchpins():
    """
    Get list of critical employees (linchpins) with Bus Factor risk.
    
    Phase 5: Guardian Co-Pilot Mode
    """
    try:
        driver = get_driver()
        detector = LinchpinDetector(driver)
        # Assuming get_all_linchpins returns a list of LinchpinReport objects
        linchpin_reports = detector.get_all_linchpins()
        
        return {
            "linchpins": [
                {
                    "id": lp.employee_id,
                    "name": lp.name,
                    "centrality_score": lp.bc_score,
                    "unique_skills": lp.unique_skills,
                    "project_count": lp.project_count,
                    "top_projects": lp.top_projects,
                    "risk_level": lp.risk_level.value,
                    "recommendation": lp.recommendations[0] if lp.recommendations else "No recommendations", # Frontend expects one string 'recommendation' or list?
                    "recommendations": lp.recommendations # Send both for compatibility
                }
                for lp in linchpin_reports
            ],
            "count": len(linchpin_reports)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/mission-profiles")
def get_mission_profiles():
    """
    Get available mission profiles.
    
    Phase 6: Policy & Governance
    """
    profiles = []
    for profile_id, config in MISSION_PROFILES.items():
        profiles.append({
            "id": profile_id,
            "name": config["name"],
            "description": config["description"],
            "strategy_preference": config["strategy_preference"],
            "color": config.get("color", "#4CAF50")
        })
    return {"profiles": profiles}


@app.get("/api/skills")
def get_all_skills():
    """
    Get list of all unique skills in the database.
    Used for autocomplete in frontend.
    """
    try:
        driver = get_driver()
        with driver.session() as session:
            result = session.run("""
                MATCH (s:Skill)
                RETURN DISTINCT s.name AS skill
                UNION
                MATCH (h:Habilidad)
                RETURN DISTINCT h.nombre AS skill
                ORDER BY skill
            """)
            
            skills = [record["skill"] for record in result if record["skill"]]
            return {"skills": skills}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ADMIN ENDPOINTS (Phase 4)
# ============================================================================

@app.post("/admin/recompute-skills")
def recompute_skills():
    """
    Recalculate skill levels for all employees.
    
    Phase 4: Contextual Scoring Engine
    Warning: This can be slow for large datasets.
    """
    try:
        driver = get_driver()
        result = recompute_all_skill_levels(driver)
        return {
            "ok": True,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/admin/normalize")
def normalize_uids():
    """
    Re-normalize all employee UIDs in the graph.
    
    Phase 3: Privacy & Normalization
    Warning: This is a destructive operation. Backup database first.
    """
    try:
        result = normalize_all_employees()
        return {
            "ok": True,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# QUERY ENDPOINTS (Phase 1)
# ============================================================================

@app.get("/employees", response_model=EmployeeListResponse)
def list_employees():
    """
    List all employees in the system.
    
    Phase 1: Graph & Taxonomy
    """
    query = """
    MATCH (e:Empleado)
    RETURN e.id as id, e.nombre as nombre, e.rol as rol
    ORDER BY e.id
    """
    employees = []
    driver = get_driver()
    with driver.session() as session:
        result = session.run(query)
        for record in result:
            employees.append({
                'id': record['id'],
                'nombre': record.get('nombre'),
                'rol': record.get('rol')
            })
    return {"employees": employees}


# ============================================================================
# SHUTDOWN EVENT
# ============================================================================

@app.get("/api/graph")
def get_graph_data():
    """
    Returns graph data (nodes and edges) for visualization.
    Limits to 100 relationships to prevent overloading.
    """
    driver = get_driver()
    with driver.session() as session:
        # Fetch relationships
        result = session.run("""
            MATCH (n)-[r:TRABAJO_CON]->(m)
            RETURN n, r, m
            LIMIT 300
            UNION
            MATCH (n)-[r:DEMUESTRA_COMPETENCIA]->(m)
            RETURN n, r, m
            LIMIT 300
        """)
        
        nodes = {}
        links = []
        
        for record in result:
            source = record["n"]
            target = record["m"]
            rel = record["r"]
            
            # Process Source Node
            source_id = str(source.id)
            if source_id not in nodes:
                nodes[source_id] = {
                    "id": source_id,
                    "labels": list(source.labels),
                    "properties": dict(source)
                }
            
            # Process Target Node
            target_id = str(target.id)
            if target_id not in nodes:
                nodes[target_id] = {
                    "id": target_id,
                    "labels": list(target.labels),
                    "properties": dict(target)
                }
            
            # Process Link
            links.append({
                "source": source_id,
                "target": target_id,
                "type": rel.type,
                "properties": dict(rel)
            })
            
        return {
            "nodes": list(nodes.values()),
            "links": links
        }

@app.on_event("shutdown")
def shutdown_event():
    """Close database connection on shutdown."""
    from .db import close_driver
    close_driver()
