"""
SmartChimera - Dual Mode Team Formation
========================================
Two modes for different organizational needs:

1. RESILIENT MODE: Minimizes bus factor risk by penalizing linchpins
   - Use for: Long-term projects, mission-critical systems
   - Trade-off: May sacrifice some expertise f00436676 or stability

2. PERFORMANCE MODE: Maximizes team quality (skills, collaboration)
   - Use for: Urgent projects, short sprints, POCs
   - Trade-off: May include linchpins (alerts will warn)00436676 

LINCHPIN ALERTS: Always active regardless of mode
"""

from typing import List, Dict, Set
from collections import defaultdict
from enum import Enum
import statistics

class FormationMode(Enum):
    RESILIENT = "resilient"      # Minimize risk, avoid linchpins
    PERFORMANCE = "performance"  # Maximize quality, best experts


def get_skills(c: Dict) -> Set[str]:
    return {s['skill'].lower() for s in c.get('skills_detail', []) if s.get('skill')}


def get_depth(c: Dict, required: Set[str]) -> float:
    levels = []
    for s in c.get('skills_detail', []):
        if s.get('skill', '').lower() in required:
            nivel = s.get('nivel')
            # Handle None values: use default 0.5 if nivel is None
            levels.append(float(nivel) if nivel is not None else 0.5)
    return statistics.mean(levels) if levels else 0.0


def get_collab_edges(driver, cid: str, team_ids: Set[str]) -> int:
    if not team_ids:
        return 0
    with driver.session() as s:
        r = s.run("MATCH (a:Empleado {id: $cid})-[:TRABAJO_CON]-(b) WHERE b.id IN $t RETURN count(*) as c",
                  cid=cid, t=list(team_ids)).single()
        return r['c'] if r else 0


class SmartTeamFormation:
    """
    Dual-mode team formation algorithm.
    """
    
    def __init__(self, driver, linchpin_detector=None):
        self.driver = driver
        self.detector = linchpin_detector
        self._bc_cache: Dict[str, float] = {}
    
    def _get_bc(self, candidate_id: str) -> float:
        """Get BC score using detector or database."""
        if candidate_id in self._bc_cache:
            return self._bc_cache[candidate_id]
        
        if self.detector:
            bc_scores = self.detector.compute_betweenness_centrality()
            self._bc_cache = bc_scores
            return bc_scores.get(candidate_id, 0.0)
        
        with self.driver.session() as s:
            r = s.run("""
                MATCH (e:Empleado {id: $id})
                RETURN coalesce(e.bc_combined, e.bc_synthetic, e.bc_brandes, 0) as bc
            """, id=candidate_id).single()
            bc = r['bc'] if r else 0.0
            self._bc_cache[candidate_id] = bc
            return bc
    
    def form_team(self, candidates: List[Dict], skills_required: List[str], k: int,
                  mode: FormationMode = FormationMode.PERFORMANCE,
                  custom_weights: Dict = None) -> List[Dict]:
        """
        Form team with specified mode.
        
        Args:
            candidates: Pool of candidates
            skills_required: Required skills
            k: Team size
            mode: RESILIENT or PERFORMANCE
            custom_weights: Optional custom weights dict (for Grid Search)
            
        Returns:
            List of selected team members
        """
        
        # Use custom weights if provided, otherwise mode-specific defaults
        if custom_weights:
            weights = {
                'skill_coverage': custom_weights.get('skill_coverage', 3.0),
                'skill_depth': custom_weights.get('skill_depth', 2.0),
                'collaboration': custom_weights.get('collaboration', 2.0),
                'redundancy': custom_weights.get('redundancy', 1.5),
                'bc_penalty': custom_weights.get('bc_penalty', 0.0)
            }
        elif mode == FormationMode.RESILIENT:
            weights = {
                'skill_coverage': 3.0,
                'skill_depth': 2.0,
                'collaboration': 2.5,    # Higher: prefer known collaborators
                'redundancy': 2.0,       # Higher: want backup
                'bc_penalty': 15.0       # Penalize linchpins heavily
            }
        else:  # PERFORMANCE
            weights = {
                'skill_coverage': 3.0,
                'skill_depth': 3.0,      # Higher: want best experts
                'collaboration': 2.0,
                'redundancy': 1.5,
                'bc_penalty': 0.0        # No penalty - get the best
            }
        
        required = {s.lower() for s in skills_required}
        
        # BEAM SEARCH IMPLEMENTATION (Precision Mode)
        # --------------------------------------------------------------------------------
        BEAM_WIDTH = 10
        
        # State: list of tuples (current_team_list, current_team_ids_set, covered_skills_set, fit_score)
        # Initialize with one empty team
        beam = [( [], set(), set(), 0.0 )]
        
        # We need to fill teams up to size k
        for _ in range(k):
            candidates_pool = []
            
            # Expand each partial team in the beam
            for (curr_team, curr_ids, curr_covered, curr_score) in beam:
                
                # Try adding every valid candidate to this partial team
                for c in candidates:
                    if c['id'] in curr_ids:
                        continue
                    
                    c_skills = get_skills(c)
                    
                    # --- SCORING LOGIC (Same as before, but wrapped) ---
                    
                    # Skill Coverage
                    new_skills = c_skills & required - curr_covered
                    coverage_score = len(new_skills) * weights['skill_coverage']
                    
                    # Skill Depth
                    depth_score = get_depth(c, required) * weights['skill_depth']
                    
                    # Collaboration
                    # FIX: Global Degree Heuristic for first member still applies here
                    if len(curr_team) == 0:
                        potential_collab = 0
                        if weights['collaboration'] > 5.0: 
                            with self.driver.session() as s:
                                r = s.run("MATCH (e:Empleado {id:$id})-[r:TRABAJO_CON]-() RETURN count(r) as deg", id=c['id']).single()
                                deg = r['deg'] if r else 0
                            potential_collab = (deg / 10.0) * weights['collaboration']
                        collab_score = potential_collab
                    else:
                        edges = get_collab_edges(self.driver, c['id'], curr_ids)
                        collab_score = edges * weights['collaboration']
                    
                    # Redundancy
                    overlap = c_skills & curr_covered
                    redundancy_score = len(overlap) * weights['redundancy']
                    
                    # BC Penalty
                    bc_penalty = 0.0
                    if weights['bc_penalty'] != 0:
                        bc = self._get_bc(c['id'])
                        if weights['bc_penalty'] > 0:
                            if bc > 0.5: bc_penalty = 50.0 
                            else: bc_penalty = bc * 10 * weights['bc_penalty']
                        else:
                            bc_penalty = bc * 10 * weights['bc_penalty']
                    
                    # Availability
                    hours_score = 0
                    if weights.get('availability', 0) > 0:
                        with self.driver.session() as s:
                            r = s.run("MATCH (e:Empleado {id:$id})-[:HAS_AVAILABILITY]->(a) RETURN a.hours as h ORDER BY a.week DESC LIMIT 1", id=c['id']).single()
                            hours = r['h'] if r else 0
                        hours_score = (hours / 40.0) * weights['availability']

                    # Calculate Marginal Gain with this candidate
                    raw_gain = coverage_score + depth_score + collab_score + redundancy_score + hours_score - bc_penalty
                    
                    # New total score for the path
                    new_total_raw = curr_score + raw_gain
                    
                    # Create new state
                    new_team_list = curr_team + [c]
                    new_team_ids = curr_ids | {c['id']}
                    new_covered = curr_covered | (c_skills & required)
                    
                    candidates_pool.append( (new_team_list, new_team_ids, new_covered, new_total_raw) )
            
            # Prune: Keep only top BEAM_WIDTH states
            # Sort by total score descending
            candidates_pool.sort(key=lambda x: x[3], reverse=True)
            beam = candidates_pool[:BEAM_WIDTH]
        
        # Final Selection: Best team from the beam
        if not beam:
            return []
            
        best_team_list, _, _, best_raw_score = beam[0]
        
        # FIX: Dynamic Score Normalization
        # Calculate theoretical max per person based on current weights
        # Max Contribution per person ~= weights['skill_coverage']*5 + weights['skill_depth']*5 + ...
        # We approximate the max possible "marginal gain" a perfect candidate could add
        
        # Max Skill Coverage (approx 1 new skill)
        max_cov = weights.get('skill_coverage', 1.0) * 1.0 
        # Max Depth (Level 5.0)
        max_depth = weights.get('skill_depth', 1.0) * 5.0
        # Max Collab (Assume 5 links or highly connected)
        max_collab = weights.get('collaboration', 1.0) * 5.0 
        # Max Redundancy (Assume covers 1 existing skill)
        max_red = weights.get('redundancy', 1.0) * 1.0
        # Max Availability (40h)
        max_avail = weights.get('availability', 0.0) * 1.0
        
        # Max Penalty (Best case is 0 penalty)
        # If penalty is negative (bonus), it adds to score. 
        # If penalty is positive, best case is 0.
        max_penalty_bonus = 0.0
        if weights.get('bc_penalty', 0) < 0:
            max_penalty_bonus = abs(weights['bc_penalty']) * 1.0 # Bonus for high BC
            
        max_possible_per_person = max_cov + max_depth + max_collab + max_red + max_avail + max_penalty_bonus
        if max_possible_per_person == 0: max_possible_per_person = 1.0
        
        # Total team max
        max_total_team_score = max_possible_per_person * k
        
        normalized_team_score = (best_raw_score / max_total_team_score) * 10.0
        normalized_team_score = max(0.0, min(10.0, normalized_team_score))
        
        for member in best_team_list:
            member['score'] = round(normalized_team_score, 1) 
            
        return best_team_list


# ============================================================================
# BASELINES (unchanged)
# ============================================================================

def greedy_baseline(candidates: List[Dict], skills_required: List[str], k: int) -> List[Dict]:
    required = {s.lower() for s in skills_required}
    scored = []
    for c in candidates:
        total = 0
        for s in c.get('skills_detail', []):
            if s.get('skill', '').lower() in required:
                nivel = s.get('nivel')
                # Handle None values: use default 0.5 if nivel is None
                total += float(nivel) if nivel is not None else 0.5
        scored.append((c, total))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [x[0] for x in scored[:k]]


def lappas_baseline(driver, candidates: List[Dict], skills_required: List[str], k: int) -> List[Dict]:
    required = {s.lower() for s in skills_required}
    freq = defaultdict(int)
    for c in candidates:
        for sk in get_skills(c):
            if sk in required: freq[sk] += 1
    
    team, team_ids, covered = [], set(), set()
    while len(team) < k and len(covered) < len(required):
        best, best_score = None, float('-inf')
        for c in candidates:
            if c['id'] in team_ids: continue
            new = get_skills(c) & required - covered
            if not new: continue
            rarest = min(new, key=lambda s: freq.get(s, 999))
            score = 1.0 / freq.get(rarest, 1) * 10 + get_depth(c, required)
            if score > best_score: best_score, best = score, c
        if best:
            team.append(best)
            team_ids.add(best['id'])
            covered.update(get_skills(best) & required)
        else: break
    
    remaining = sorted([c for c in candidates if c['id'] not in team_ids], 
                       key=lambda c: get_depth(c, required), reverse=True)
    while len(team) < k and remaining:
        team.append(remaining.pop(0))
    return team


def random_baseline(candidates: List[Dict], k: int) -> List[Dict]:
    import random
    return random.sample(candidates, min(k, len(candidates)))
