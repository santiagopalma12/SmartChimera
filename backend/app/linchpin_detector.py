"""
SmartChimera - LinchpinDetector Module
======================================
INDEPENDENT module for linchpin detection and risk analysis.
Does NOT exclude anyone - only identifies risks and provides recommendations.

Based on:
- Brandes Algorithm for Betweenness Centrality
- Avelino et al. (2016) for Bus Factor methodology
"""

from typing import List, Dict, Set, Tuple
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum

class RiskLevel(Enum):
    CRITICAL = "critical"   # BC > 0.8
    HIGH = "high"           # BC > 0.6
    MEDIUM = "medium"       # BC > 0.4
    LOW = "low"             # BC <= 0.4

@dataclass
class LinchpinReport:
    employee_id: str
    name: str
    bc_score: float
    risk_level: RiskLevel
    skills: List[str]
    unique_skills: List[str]
    project_count: int
    top_projects: List[str]
    recommendations: List[str]

class LinchpinDetector:
    """
    Detects and analyzes organizational linchpins.
    Provides recommendations but does NOT exclude anyone from teams.
    """
    
    def __init__(self, driver):
        self.driver = driver
        self._bc_cache: Dict[str, float] = {}
    
    def compute_betweenness_centrality(self) -> Dict[str, float]:
        """
        Compute Brandes BC using NetworkX, combined with bc_synthetic.
        Uses max(brandes_bc, bc_synthetic) to catch both real and known linchpins.
        Caches result for reuse.
        """
        if self._bc_cache:
            return self._bc_cache
        
        try:
            import networkx as nx
        except ImportError:
            return self._fallback_bc()
        
        G = nx.Graph()
        
        with self.driver.session() as s:
            for r in s.run("MATCH (e:Empleado) RETURN e.id as id"):
                G.add_node(r['id'])
            for r in s.run("MATCH (a:Empleado)-[:TRABAJO_CON]-(b:Empleado) WHERE a.id < b.id RETURN a.id as s, b.id as d"):
                G.add_edge(r['s'], r['d'])
        
        if len(G.nodes) == 0:
            return {}
        
        brandes_bc = nx.betweenness_centrality(G, normalized=True)
        
        # Combine with bc_synthetic (use max of both)
        with self.driver.session() as s:
            for r in s.run("MATCH (e:Empleado) RETURN e.id as id, coalesce(e.bc_synthetic, 0) as bc_syn"):
                eid = r['id']
                bc_syn = r['bc_syn']
                bc_brandes = brandes_bc.get(eid, 0)
                # Use maximum of both values
                self._bc_cache[eid] = max(bc_brandes, bc_syn)
        
        # Store combined BC in Neo4j
        with self.driver.session() as s:
            for eid, bc in self._bc_cache.items():
                s.run("MATCH (e:Empleado {id: $id}) SET e.bc_combined = $bc", id=eid, bc=bc)
        
        return self._bc_cache
    
    def _compute_project_dependency_score(self) -> Dict[str, float]:
        """
        Compute 'Project Weight/Dependency' score requested by user.
        Logic: Use EVIDENCE nodes or implicit Project relationships.
        For now, we simulate this based on the 'Project' nodes created in ingestion.
        """
        scores = defaultdict(float)
        with self.driver.session() as s:
            # Find projects and who worked on them
            # Assuming (:Empleado)-[:CREATED_EVIDENCE {source='github'}]->(:Evidence) or similar
            # If explicit Project nodes exist:
            result = s.run("""
                MATCH (e:Empleado)-[:CREATED_EVIDENCE]->(ev:Evidence)
                WHERE ev.source = 'github'
                RETURN e.id as eid, count(ev) as projects_count
            """)
            
            # Normalize project counts to 0-1 range roughly
            max_proj = 1
            data = []
            for r in result:
                data.append((r['eid'], r['projects_count']))
                max_proj = max(max_proj, r['projects_count'])
                
            for eid, count in data:
                # Simple centrality: More projects = Higher dependency risk
                scores[eid] = count / max_proj
                
        return scores

    def compute_combined_risk_score(self) -> Dict[str, float]:
        """
        Combine Network Centrality (BC) + Project Dependency Score.
        """
        network_bc = self.compute_betweenness_centrality()
        project_scores = self._compute_project_dependency_score()
        
        final_scores = {}
        all_ids = set(network_bc.keys()) | set(project_scores.keys())
        
        for eid in all_ids:
            net_score = network_bc.get(eid, 0.0)
            proj_score = project_scores.get(eid, 0.0)
            
            # Weighted unification: 50% Network, 50% Project Weight (Balanced)
            combined = (net_score * 0.5) + (proj_score * 0.5)
            final_scores[eid] = combined
            
            # Update Neo4j for provenance
            with self.driver.session() as s:
                s.run("MATCH (e:Empleado {id: $id}) SET e.linchpin_score = $score", id=eid, score=combined)
                
        return final_scores
    
    def get_risk_level(self, bc: float) -> RiskLevel:
        """Classify risk based on Combined Score."""
        if bc > 0.7:
            return RiskLevel.CRITICAL
        elif bc > 0.5:
            return RiskLevel.HIGH
        elif bc > 0.25:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW
    
    def get_recommendations(self, risk_level: RiskLevel, skills: List[str]) -> List[str]:
        """Generate actionable recommendations based on risk level."""
        recs = []
        
        if risk_level == RiskLevel.CRITICAL:
            recs.extend([
                "URGENTE: Iniciar cross-training inmediato",
                "Documentar todo el conocimiento crítico",
                "Asignar shadow/backup para cada responsabilidad",
                f"Capacitar a 2+ personas en: {', '.join(skills[:3])}"
            ])
        elif risk_level == RiskLevel.HIGH:
            recs.extend([
                "Implementar pair programming regular",
                "Crear documentación técnica detallada",
                f"Identificar candidatos para cross-training en: {', '.join(skills[:2])}"
            ])
        elif risk_level == RiskLevel.MEDIUM:
            recs.extend([
                "Fomentar knowledge sharing sessions",
                "Incluir en code reviews como reviewer"
            ])
        else:
            recs.append("Riesgo bajo - mantener prácticas actuales")
        
        return recs
    
    def analyze_employee(self, employee_id: str) -> LinchpinReport:
        """Generate full linchpin report for one employee."""
        # FIX: Use Combined Risk (Network + Project)
        bc_scores = self.compute_combined_risk_score()
        bc = bc_scores.get(employee_id, 0.0)
        
        with self.driver.session() as s:
            r = s.run("""
                MATCH (e:Empleado {id: $id})
                OPTIONAL MATCH (e)-[:DEMUESTRA_COMPETENCIA]->(sk:Skill)
                RETURN e.nombre as name, collect(sk.name) as skills
            """, id=employee_id).single()
            name = r['name'] if r else employee_id
            skills = r['skills'] if r else []

            # Calculate UNIQUE skills (skills that only this person or very few have)
            # For now, simplistic approximation or random for demo if requested
            # Real query:
            unique_skills = []
            if skills:
                res_unique = s.run("""
                    MATCH (e:Empleado {id: $id})-[:DEMUESTRA_COMPETENCIA]->(sk:Skill)
                    WITH sk, count { (p:Empleado)-[:DEMUESTRA_COMPETENCIA]->(sk) } as num_p
                    WHERE num_p = 1
                    RETURN sk.name as skill
                """, id=employee_id)
                unique_skills = [record['skill'] for record in res_unique]
                
            # Calculate PROJECT context (Count & Names)
            res_proj = s.run("""
                MATCH (e:Empleado {id: $id})-[:CREATED_EVIDENCE]->(ev:Evidence)
                WHERE ev.source = 'github'
                RETURN count(ev) as p_count, collect(ev.url) as p_urls
            """, id=employee_id).single()
            
            project_count = res_proj['p_count'] if res_proj else 0
            # Extract simplistic project names from URLs for display
            # e.g. http://github.com/project/1 -> "Project 1"
            raw_urls = res_proj['p_urls'] if res_proj else []
            top_projects = [url.split('/')[-1] for url in raw_urls[:3]] # Take last part
        
        risk = self.get_risk_level(bc)
        recs = self.get_recommendations(risk, skills)
        
        return LinchpinReport(
            employee_id=employee_id,
            name=name,
            bc_score=bc,
            risk_level=risk,
            skills=skills,
            unique_skills=unique_skills,
            project_count=project_count,
            top_projects=top_projects,
            recommendations=recs
        )
    
    def get_all_linchpins(self, threshold: float = 0.15) -> List[LinchpinReport]:
        """Get all employees above threshold, sorted by risk."""
        bc_scores = self.compute_combined_risk_score()
        
        linchpins = []
        for eid, bc in bc_scores.items():
            if bc >= threshold:
                report = self.analyze_employee(eid)
                linchpins.append(report)
        
        linchpins.sort(key=lambda x: x.bc_score, reverse=True)
        return linchpins
    
    def calculate_team_bus_factor(self, team_ids: List[str], skills: List[str]) -> Tuple[int, List[str]]:
        """
        Calculate Bus Factor for a team.
        Returns (bus_factor, list of critical members).
        """
        required = {s.lower() for s in skills}
        
        # Get skills per team member
        member_skills = {}
        with self.driver.session() as s:
            for tid in team_ids:
                r = s.run("""
                    MATCH (e:Empleado {id: $id})-[:DEMUESTRA_COMPETENCIA]->(sk:Skill)
                    RETURN collect(sk.name) as skills
                """, id=tid).single()
                member_skills[tid] = {sk.lower() for sk in (r['skills'] if r else [])}
        
        # Calculate coverage
        skill_coverage = defaultdict(set)
        for tid, skills_set in member_skills.items():
            for sk in skills_set:
                if sk in required:
                    skill_coverage[sk].add(tid)
        
        # Find bus factor
        removed = set()
        bf = 0
        critical_members = []
        
        for _ in range(len(team_ids)):
            worst, worst_damage = None, 0
            for tid in team_ids:
                if tid in removed:
                    continue
                damage = sum(1 for sk, members in skill_coverage.items() 
                           if len(members - removed - {tid}) == 0)
                if damage > worst_damage:
                    worst_damage = damage
                    worst = tid
            
            if worst is None:
                break
            
            removed.add(worst)
            bf += 1
            critical_members.append(worst)
            
            lost = sum(1 for sk, members in skill_coverage.items() if len(members - removed) == 0)
            if lost > len(required) * 0.5:
                break
        
        return bf, critical_members
