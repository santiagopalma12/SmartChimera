"""
Guardian Core: The Advisor Engine

This module implements the core recommendation logic for Project Chimera.
Philosophy: Constraint Satisfaction First, Optimization Second.

Key Functions:
- find_candidates: Query employees with required skills
- filter_availability: Hard filter by time availability
- filter_conflicts: Hard filter by HR constraints
- generate_dossiers: Main entry point - produces 3 strategic options
"""

from typing import List, Dict, Any, Set
from .db import get_driver
from .schemas import Dossier, Candidate, ExecutiveSummary
import uuid
import statistics


def find_candidates(skills_required: List[str]) -> List[Dict[str, Any]]:
    """
    Find all employees who have ALL required skills.
    
    Args:
        skills_required: List of skill names (e.g., ['Python', 'Docker'])
    
    Returns:
        List of employee dicts with id, nombre, and matched skills
    """
    driver = get_driver()
    # Support both DEMUESTRA_COMPETENCIA->Skill and POSEE_HABILIDAD->Habilidad
    query = """
    MATCH (e:Empleado)
    WHERE ALL(skill IN $skills WHERE EXISTS {
        MATCH (e)-[:DEMUESTRA_COMPETENCIA]->(s:Skill)
        WHERE toLower(s.name) = toLower(skill)
    } OR EXISTS {
        MATCH (e)-[:POSEE_HABILIDAD]->(h:Habilidad)
        WHERE toLower(h.nombre) = toLower(skill)
    })
    OPTIONAL MATCH (e)-[r:DEMUESTRA_COMPETENCIA]->(s:Skill)
    WHERE toLower(s.name) IN [x IN $skills | toLower(x)]
    OPTIONAL MATCH (e)-[rh:POSEE_HABILIDAD]->(h:Habilidad)
    WHERE toLower(h.nombre) IN [x IN $skills | toLower(x)]
    WITH e, 
         collect(DISTINCT {skill: s.name, nivel: r.nivel}) + collect(DISTINCT {skill: h.nombre, nivel: rh.nivel}) AS all_skills
    RETURN e.id AS id, 
           e.nombre AS nombre,
           coalesce(e.disponibilidad_horas, 30) AS availability_hours,
           [s IN all_skills WHERE s.skill IS NOT NULL] AS skills_detail
    """
    
    with driver.session() as session:
        result = session.run(query, skills=skills_required)
        candidates = []
        for record in result:
            candidates.append({
                'id': record['id'],
                'nombre': record.get('nombre', record['id']),
                'availability_hours': record.get('availability_hours', 40),
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
    # If availability_hours already set from query, just filter by min_hours
    filtered = []
    for candidate in candidates:
        hours = candidate.get('availability_hours', 40)
        if hours >= min_hours:
            candidate['availability_hours'] = hours
            filtered.append(candidate)
    
    return filtered


# ============================================================================
# PHASE 6: OVERRIDE MECHANISM
# ============================================================================

def apply_overrides(candidates: List[Dict], force_include: List[str], force_exclude: List[str]) -> List[Dict]:
    """
    Apply manager overrides (Phase 6: Policy & Governance).
    
    Managers can:
    - Force-include specific employees (even if they don't meet criteria)
    - Force-exclude specific employees (e.g., on vacation, conflicts)
    
    Args:
        candidates: List of candidate dicts
        force_include: Employee IDs that MUST be included
        force_exclude: Employee IDs that MUST be excluded
    
    Returns:
        Filtered candidates + forced includes
    """
    # Step 1: Remove excluded employees
    filtered = [c for c in candidates if c['id'] not in force_exclude]
    
    # Step 2: Add forced includes (even if they don't meet normal criteria)
    if force_include:
        # Filter out IDs already in candidates (avoid duplicates)
        existing_ids = {c['id'] for c in filtered}
        ids_to_fetch = [eid for eid in force_include if eid not in existing_ids]
        
        if ids_to_fetch:
            driver = get_driver()
            # OPTIMIZED: Single bulk query instead of N queries
            query = """
            UNWIND $emp_ids AS eid
            MATCH (e:Empleado {id: eid})
            OPTIONAL MATCH (e)-[r:DEMUESTRA_COMPETENCIA]->(s:Skill)
            RETURN e.id AS id, 
                   e.nombre AS nombre,
                   collect({skill: s.name, nivel: r.nivel}) AS skills_detail
            """
            
            with driver.session() as session:
                result = session.run(query, emp_ids=ids_to_fetch)
                for record in result:
                    # Add to candidates with special flag
                    filtered.append({
                        'id': record['id'],
                        'nombre': record.get('nombre', record['id']),
                        'skills_detail': record['skills_detail'],
                        'forced_include': True,  # Mark as manager override
                        'availability_hours': 40  # Assume full availability
                    })
    
    return filtered


def filter_conflicts(team_ids: List[str]) -> bool:
    """
    Check if proposed team has any pairwise conflicts.
    
    Phase 5: Now checks BOTH:
    - CONFLICT_WITH edges (existing)
    - MANUAL_CONSTRAINT edges (HR overrides)
    
    Args:
        team_ids: List of employee IDs
    
    Returns:
        True if team is VALID (no conflicts), False if conflicts exist
    """
    if len(team_ids) < 2:
        return True  # No conflicts possible
    
    driver = get_driver()
    query = """
    UNWIND $ids AS id1
    MATCH (a:Empleado {id: id1})-[r]-(b:Empleado)
    WHERE b.id IN $ids AND id1 < b.id
      AND (type(r) = 'CONFLICT_WITH' OR type(r) = 'MANUAL_CONSTRAINT')
    RETURN a.id AS person1, b.id AS person2, type(r) AS conflict_type
    LIMIT 1
    """
    
    with driver.session() as session:
        result = session.run(query, ids=team_ids)
        conflicts = list(result)
        return len(conflicts) == 0  # True if no conflicts found


def _calculate_candidate_score(candidate: Dict, skills_required: List[str], weights: Dict = None) -> float:
    """
    Calculate overall score for a candidate based on skill levels and mission profile weights.
    
    Args:
        candidate: Candidate dict with 'skills_detail' field
        skills_required: List of required skills
        weights: Mission profile weights (skill_level, availability, collaboration)
    
    Returns:
        Score (0.0 to 5.0+)
    """
    if weights is None:
        weights = {'skill_level': 1.0, 'availability': 1.0, 'collaboration': 1.0}
    
    skills_detail = candidate.get('skills_detail', [])
    if not skills_detail:
        return 1.0  # Minimum score
    
    # Case-insensitive matching
    req_lower = [s.lower() for s in skills_required]
    
    total_nivel = 0.0
    matched_count = 0
    
    for s in skills_detail:
        skill_name = s.get('skill', '').lower()
        if skill_name in req_lower:
            nivel = s.get('nivel')
            if nivel is None:
                nivel = 1.0
            total_nivel += float(nivel)
            matched_count += 1
    
    # Base score from skills
    avg_nivel = total_nivel / len(skills_required) if skills_required else 1.0
    skill_score = avg_nivel * weights.get('skill_level', 1.0)
    
    # Availability bonus
    availability_hours = candidate.get('availability_hours', 30)
    availability_score = (availability_hours / 40.0) * weights.get('availability', 1.0)
    
    # Final weighted score
    final_score = skill_score + availability_score
    
    return round(final_score, 2)


# ============================================================================
# PHASE 5: EXECUTIVE SUMMARY GENERATION
# ============================================================================

# ============================================================================
# PHASE 5: RICH EXECUTIVE SUMMARY GENERATION (40+ Strategies)
# ============================================================================

# ============================================================================
# PHASE 5: RICH EXECUTIVE SUMMARY GENERATION (Universal Logic)
# ============================================================================

def _generate_executive_summary(team: List[Candidate], strategy: str) -> ExecutiveSummary:
    """
    Generate Deep Insight Executive Summary.
    Uses universal content-based logic. 
    """
    if not team:
        return ExecutiveSummary(pros=[], cons=[], recommendation="REJECT")

    # 1. METRICS EXTRACTION
    avg_score = statistics.mean([c.score for c in team])
    min_avail = min([c.availability_hours for c in team])
    linchpins = [c for c in team if c.linchpin_risk in ['CRITICAL', 'HIGH']]
    experts = [c for c in team if c.score >= 4.5]
    novices = [c for c in team if c.score <= 2.5]
    
    # 2. PROS LIBRARY (Universal)
    possible_pros = []
    
    # Skill & Competence
    if avg_score >= 4.8: possible_pros.append("✅ World-Class Expertise (Top 1%)")
    elif avg_score >= 4.5: possible_pros.append("✅ Elite Technical Density (Top 5%)")
    elif avg_score >= 4.0: possible_pros.append("✅ Very High Competence Level")
    elif avg_score >= 3.5: possible_pros.append("✅ Solid, Reliable Skill Base")
    else: possible_pros.append("✅ Functional Skill Coverage")
    
    # Mentorship & Composition
    if len(experts) >= 1 and len(novices) >= 1: 
        possible_pros.append("✅ Natural Mentorship Ecosystem")
        possible_pros.append("✅ Cost-Effective Skill Transfer")
    
    if len(experts) == len(team): possible_pros.append("✅ Unmatched Problem-Solving Power")
    
    # Availability
    if min_avail >= 35: possible_pros.append("✅ Dedicated Squad (>35h/wk)")
    elif min_avail >= 25: possible_pros.append("✅ Sprint-Ready Availability")
    
    # Risk Profile
    if not linchpins: possible_pros.append("✅ Low Bus Factor (No Linchpins)")
    if len(linchpins) == 0 and avg_score > 3.5: possible_pros.append("✅ Highly Resilient Architecture")
    
    # Strategy Specific (Only added if strictly relevant)
    if strategy == 'safe_bet': possible_pros.append("✅ Maximized Stability (Conservative)")
    if strategy == 'growth': possible_pros.append("✅ Maximized Ceiling (Performance)")

    # 3. CONS LIBRARY (Universal - applied to ALL strategies)
    possible_cons = []
    
    # "Too Many Chiefs" Risk (Universal)
    if len(experts) == len(team) and len(team) > 1:
         possible_cons.append("⚠️ Retention Risk: Too many chiefs, no indians")
         possible_cons.append("⚠️ Potential Ego Conflicts")

    # Dependency Risk
    if len(linchpins) >= 2: 
        possible_cons.append(f"🚨 EXTREME Bus Factor ({len(linchpins)} Linchpins)")
        possible_cons.append("🚨 Critical Dependency Chain")
    elif len(linchpins) == 1: 
        possible_cons.append(f"⚠️ Single Point of Failure Possible")
    
    # Skill Gaps
    if avg_score < 2.5: possible_cons.append("🚨 Significant Skill Deficiencies")
    if len(experts) == 0: possible_cons.append("⚠️ Lack of Senior Guiding Force")
    if len(novices) == len(team): possible_cons.append("⚠️ Junior-Only Team (High Oversight Needed)")
    
    # Availability
    if min_avail < 15: possible_cons.append("🚨 Distracted Members (<15h/wk)")
    
    # 4. RECOMMENDATION LIBRARY (40+ Options)
    # Logic: Risk + Score + Balance -> Specific Output
    rec_text = "APPROVE"
    
    # A. High Risk Scenarios
    if len(linchpins) >= 2:
        rec_text = "REJECT: Critical Bus Factor Risk (2+ Linchpins)."
    elif len(linchpins) == 1 and avg_score < 3.0:
        rec_text = "REVIEW: Reliance on single expert with weak support."
        
    # B. All Expert Teams (Growth/DeepTech)
    elif len(experts) == len(team):
        if strategy == 'mission_aligned' or strategy == 'growth':
            rec_text = "APPROVE: High Octane Team (Monitor Burnout/Retention)."
        else:
            rec_text = "CAUTION: Overqualified. Expensive & Risk of boredem."
            
    # C. Mentor Teams (Mixed)
    elif len(experts) >= 1 and len(novices) >= 1:
        rec_text = "APPROVE: Excellent Training Configuration."
        
    # D. Junior Teams (Enablement)
    elif len(novices) >= len(team) / 2:
        if avg_score > 2.0:
             rec_text = "APPROVE: Good for Enablement/Maintenance tasks."
        else:
             rec_text = "REVIEW: Skill level may be too low for autonomy."
             
    # E. Solid Middle
    elif avg_score >= 3.5:
        rec_text = "APPROVE: Strong, balanced configuration."
    else:
        rec_text = "APPROVE: Meets baseline requirements."

    # Select top distinct Pros/Cons
    final_pros = list(dict.fromkeys(possible_pros))[:4]
    final_cons = list(dict.fromkeys(possible_cons))[:4]

    return ExecutiveSummary(
        pros=final_pros if final_pros else ["Standard Configuration"],
        cons=final_cons if final_cons else ["No major risks detected"],
        recommendation=rec_text
    )



def generate_dossiers(request: Dict[str, Any]) -> List[Dossier]:
    """
    Main entry point: Generate strategic team options.
    
    Args:
        request: TeamRequest dict with:
            - requisitos_hard: {'skills': [...], ...}
            - k: team size
            - week: optional ISO week for availability
            - min_hours: optional minimum hours required
            - mission_profile: optional mission context (Phase 6)
            - formation_mode: 'resilient' or 'performance' (default)
            - force_include: optional list of IDs to force-include (Phase 6)
            - force_exclude: optional list of IDs to force-exclude (Phase 6)
    
    Returns:
        List of Dossier objects
    """
    hard_reqs = request.get('requisitos_hard', {})
    skills_required = hard_reqs.get('skills', [])
    k = request.get('k', 5)
    week = request.get('week')
    min_hours = request.get('min_hours', 20)  # Default: 20 hours/week
    
    # Phase 6: Get mission profile and overrides
    mission_profile = request.get('mission_profile', 'mantenimiento')
    formation_mode = request.get('formation_mode', 'performance')  # NEW: resilient or performance
    force_include = request.get('force_include', [])
    force_exclude = request.get('force_exclude', [])
    
    # Step 1: Find candidates with required skills
    candidates = find_candidates(skills_required)
    
    if not candidates:
        # No candidates found - return empty dossiers
        return []
    
    # Step 2: Filter by availability (HARD CONSTRAINT)
    candidates = filter_availability(candidates, week, min_hours)
    
    if not candidates:
        # No one available
        return []
    
    # Phase 6: Step 3: Apply manager overrides
    if force_include or force_exclude:
        candidates = apply_overrides(candidates, force_include, force_exclude)
    
    # Phase 6: Step 4: Get mission profile configuration
    from .mission_profiles import get_mission_profile
    profile_config = get_mission_profile(mission_profile)
    weights = profile_config.get('weights', {})
    preferred_strategy = profile_config.get('strategy_preference', 'safe_bet')
    
    # Step 5: Initialize Smart Team Formation Engine
    from .smart_team_formation import SmartTeamFormation, FormationMode
    from .linchpin_detector import LinchpinDetector
    
    driver = get_driver()
    detector = LinchpinDetector(driver)
    tf = SmartTeamFormation(driver, linchpin_detector=detector)
    
    # Define strategy configurations
    # Define BASELINE weights for the anchors (independent of selected mission)
    # This guarantees that Option 1 and 2 are always stable comparisons
    
    # Baseline Resilient (Safe Bet)
    weights_resilient = {
        'skill_coverage': 2.0,
        'skill_depth': 1.0,
        'collaboration': 2.0,
        'redundancy': 3.0,
        'availability': 2.0,
        'bc_penalty': 20.0
    }
    
    # Baseline Performance (Growth)
    weights_performance = {
        'skill_coverage': 1.0,
        'skill_depth': 3.0,
        'collaboration': 1.0,
        'redundancy': 1.0,
        'availability': 1.0,
        'bc_penalty': 0.0
    }

    strategies_config = [
        {
            'id': 'safe_bet',
            'title': 'The Safe Bet (Reference)',
            'description': 'Standard high-stability team (Baseline).',
            'mode': FormationMode.RESILIENT,
            'custom_weights': weights_resilient # FIXED: Independent of selection
        },
        {
            'id': 'growth',
            'title': 'The Growth Team (Reference)',
            'description': 'Standard high-performance team (Baseline).',
            'mode': FormationMode.PERFORMANCE,
            'custom_weights': weights_performance # FIXED: Independent of selection
        },
        {
            # OPTION 3: STRICTLY ADHERES TO THE USER'S SELECTED MISSION
            'id': 'mission_aligned',
            'title': f"{profile_config.get('name', 'Mission Aligned')} (Target)",
            'description': profile_config.get('description', 'Optimized for specific mission requirements.'),
            'mode': FormationMode.RESILIENT if profile_config.get('strategy_preference') == 'resilient' else FormationMode.PERFORMANCE,
            'custom_weights': weights # PASS RAW WEIGHTS - NO OVERRIDES
        }
    ]
    
    # If user specifically requested 'resilient' mode, ALL strategies should be resilient
    if formation_mode == 'resilient':
        for strat in strategies_config:
            strat['mode'] = FormationMode.RESILIENT
            strat['custom_weights']['bc_penalty'] = 20.0
            strat['title'] += " [Resilient]"

    dossiers = []
    
    for strategy in strategies_config:
        # Form team using Smart Engine
        team = tf.form_team(
            candidates, 
            skills_required, 
            k, 
            mode=strategy['mode'],
            custom_weights=strategy['custom_weights']
        )
        
        if not team:
            continue

        # Convert to Candidate objects for response
        team_candidates = []
        total_score = 0
        
        for c in team:
            # Calculate simple display score (Use pre-calculated normalized score if available)
            if 'score' in c:
                display_score = c['score']
            else:
                # Fallback: Calculate using the STRATEGY specific weights, not the selected profile weights
                display_score = _calculate_candidate_score(c, skills_required, strategy['custom_weights'])
            
            # Analyze Linchpin Risk
            report = detector.analyze_employee(c['id'])
            linchpin_risk = report.risk_level.value.upper() if report else 'LOW'
            
            candidate = Candidate(
                id=c['id'],
                skills_matched=[s['skill'] for s in c.get('skills_detail', []) if s.get('skill')],
                score=display_score,
                availability_hours=c.get('availability_hours', 40),
                conflict_risk=False,
                linchpin_risk=linchpin_risk
            )
            team_candidates.append(candidate)
            total_score += display_score
            
        # Generate Executive Summary
        exec_summary = _generate_executive_summary(team_candidates, strategy['id'])
        
        # Create Dossier
        d = Dossier(
            title=strategy['title'],
            description=strategy['description'],
            executive_summary=exec_summary,
            team=team_candidates,
            total_score=round(total_score, 2),
            risk_analysis=_generate_risk_analysis(team_candidates, strategy['mode']),
            rationale=exec_summary.recommendation # Use the rich recommendation as the rationale
        )
        dossiers.append(d)
        
    return dossiers


def _generate_risk_analysis(team: List[Candidate], mode) -> List[str]:
    """Generate risk analysis bullet points."""
    risks = []
    avg_score = statistics.mean([m.score for m in team]) if team else 0
    critical_linchpins = [m for m in team if m.linchpin_risk == 'CRITICAL']
    
    if avg_score > 4.0:
        risks.append("✅ High technical competence")
    if not critical_linchpins:
        risks.append("✅ Low 'Bus Factor' risk")
    else:
        risks.append(f"⚠️ Contains {len(critical_linchpins)} critical linchpin(s)")
        
    if mode.value == 'resilient':
        risks.append("✅ Optimized for long-term stability")
    else:
        risks.append("ℹ️ Performance-focused formation")
        
    return risks
