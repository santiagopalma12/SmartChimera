"""
===============================================================================
SMARTCHIMERA - FULL PROFILE VALIDATION FOR IEEE WCCI 2026
===============================================================================
Tests ALL 9 mission profiles to show the full range of configurability.
===============================================================================
"""

import numpy as np
import networkx as nx
from scipy import stats
import json
from datetime import datetime
import functools
import random

print = functools.partial(print, flush=True)

# =============================================================================
# CONFIGURATION
# =============================================================================
CONFIG = {
    'n_simulations': 50,  # Reduced for speed
    'team_size': 5,
    'n_candidates': 80,
    'n_skills_required': 3,
    'beam_width': 10,
    'random_seed': 42,
    'all_skills': ['Python', 'React', 'Docker', 'AWS', 'Kubernetes', 
                   'PostgreSQL', 'MongoDB', 'TypeScript', 'Java', 'Go',
                   'ML', 'DevOps', 'Security', 'Testing', 'Agile']
}

np.random.seed(CONFIG['random_seed'])
random.seed(CONFIG['random_seed'])

# =============================================================================
# ALL 9 MISSION PROFILES (from mission_profiles.py)
# =============================================================================
MISSION_PROFILES = {
    "mantenimiento": {
        "name": "Mantenimiento Crítico",
        "weights": {
            "skill_coverage": 2.0, "skill_depth": 1.0, "collaboration": 2.0,
            "redundancy": 5.0, "bc_penalty": 20.0  # VETO linchpins
        }
    },
    "junior_training": {
        "name": "Junior Squad",
        "weights": {
            "skill_coverage": 2.0, "skill_depth": 0.5, "collaboration": 5.0,
            "redundancy": 5.0, "bc_penalty": 50.0  # EXTREME VETO
        }
    },
    "legacy_rescue": {
        "name": "Legacy Rescue",
        "weights": {
            "skill_coverage": 10.0, "skill_depth": 2.0, "collaboration": 2.0,
            "redundancy": 3.0, "bc_penalty": 10.0
        }
    },
    "security_audit": {
        "name": "Security Audit",
        "weights": {
            "skill_coverage": 5.0, "skill_depth": 5.0, "collaboration": 0.0,
            "redundancy": 10.0, "bc_penalty": 5.0
        }
    },
    "cloud_migration": {
        "name": "Cloud Migration",
        "weights": {
            "skill_coverage": 15.0, "skill_depth": 2.0, "collaboration": 3.0,
            "redundancy": 2.0, "bc_penalty": 5.0
        }
    },
    "entrega_rapida": {
        "name": "Speed Squad",
        "weights": {
            "skill_coverage": 2.0, "skill_depth": 1.0, "collaboration": 10.0,
            "redundancy": 1.0, "bc_penalty": 0.0  # Neutral
        }
    },
    "crisis_response": {
        "name": "Crisis Response",
        "weights": {
            "skill_coverage": 5.0, "skill_depth": 2.0, "collaboration": 2.0,
            "redundancy": 1.0, "bc_penalty": 0.0  # Neutral
        }
    },
    "innovacion": {
        "name": "I+D / Deep Tech",
        "weights": {
            "skill_coverage": 1.0, "skill_depth": 10.0, "collaboration": 0.5,
            "redundancy": 0.0, "bc_penalty": -5.0  # BONUS linchpins
        }
    },
    "architecture_review": {
        "name": "Architecture Review",
        "weights": {
            "skill_coverage": 3.0, "skill_depth": 10.0, "collaboration": 1.0,
            "redundancy": 0.0, "bc_penalty": -10.0  # STRONG BONUS
        }
    }
}

print("=" * 80)
print("SMARTCHIMERA - FULL 9-PROFILE VALIDATION")
print("=" * 80)
print()

# =============================================================================
# DATA GENERATION
# =============================================================================
def generate_organization(n_candidates, all_skills):
    G = nx.Graph()
    candidates = []
    
    for i in range(n_candidates):
        n_skills = np.random.randint(2, 5)
        emp_skills = list(np.random.choice(all_skills, size=n_skills, replace=False))
        
        skills_detail = []
        for skill in emp_skills:
            level = np.clip(np.random.beta(2, 2) * 4 + 1, 1, 5)
            skills_detail.append({'skill': skill, 'nivel': level})
        
        cand = {
            'id': f'emp_{i:03d}',
            'skills_detail': skills_detail,
            'skills_set': set(emp_skills)
        }
        candidates.append(cand)
        G.add_node(cand['id'])
    
    for i, c1 in enumerate(candidates):
        for j, c2 in enumerate(candidates[i+1:], i+1):
            overlap = c1['skills_set'] & c2['skills_set']
            if overlap:
                G.add_edge(c1['id'], c2['id'], weight=len(overlap))
    
    if G.number_of_edges() > 0:
        bc_dict = nx.betweenness_centrality(G, normalized=True)
    else:
        bc_dict = {c['id']: 0.0 for c in candidates}
    
    for c in candidates:
        c['bc_score'] = bc_dict.get(c['id'], 0.0)
    
    return candidates, bc_dict, G


# =============================================================================
# ALGORITHMS
# =============================================================================
def get_skills(candidate):
    return {s['skill'].lower() for s in candidate.get('skills_detail', []) if s.get('skill')}


def smartchimera_with_profile(candidates, required_skills, k, bc_dict, profile_name, beam_width=10):
    weights = MISSION_PROFILES[profile_name]['weights']
    required = {s.lower() for s in required_skills}
    
    def get_depth(c, required):
        levels = [s.get('nivel', 2.5) for s in c.get('skills_detail', []) 
                  if s.get('skill', '').lower() in required]
        return np.mean(levels) if levels else 0.0
    
    beam = [([], set(), set(), 0.0)]
    
    for step in range(k):
        candidates_pool = []
        
        for (curr_team, curr_ids, curr_covered, curr_score) in beam:
            for c in candidates:
                if c['id'] in curr_ids:
                    continue
                
                c_skills = get_skills(c)
                new_skills = c_skills & required - curr_covered
                coverage_score = len(new_skills) * weights['skill_coverage']
                depth_score = get_depth(c, required) * weights['skill_depth']
                overlap = c_skills & curr_covered
                redundancy_score = len(overlap) * weights.get('redundancy', 0)
                
                bc = bc_dict.get(c['id'], 0.0)
                bc_effect = bc * weights['bc_penalty'] * 10
                
                raw_gain = coverage_score + depth_score + redundancy_score - bc_effect
                new_total = curr_score + raw_gain
                
                new_team = curr_team + [c]
                new_ids = curr_ids | {c['id']}
                new_covered = curr_covered | (c_skills & required)
                
                candidates_pool.append((new_team, new_ids, new_covered, new_total))
        
        candidates_pool.sort(key=lambda x: x[3], reverse=True)
        beam = candidates_pool[:beam_width]
    
    return beam[0][0] if beam else []


def greedy_baseline(candidates, required_skills, k):
    required_lower = {s.lower() for s in required_skills}
    scored = []
    for c in candidates:
        total = sum(s.get('nivel', 0) for s in c.get('skills_detail', [])
                    if s.get('skill', '').lower() in required_lower)
        scored.append((c, total))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [c for c, _ in scored[:k]]


# =============================================================================
# METRICS
# =============================================================================
def calculate_skill_coverage(team, required_skills):
    if not required_skills:
        return 1.0
    required_lower = {s.lower() for s in required_skills}
    covered = set()
    for member in team:
        for s in member.get('skills_detail', []):
            covered.add(s['skill'].lower())
    return len(covered & required_lower) / len(required_lower)


def calculate_avg_skill_level(team, required_skills):
    required_lower = {s.lower() for s in required_skills}
    levels = []
    for member in team:
        for s in member.get('skills_detail', []):
            if s['skill'].lower() in required_lower:
                levels.append(s.get('nivel', 2.5))
    return np.mean(levels) if levels else 0.0


def calculate_linchpin_risk(team, bc_dict):
    if not team:
        return 0.0
    return np.mean([bc_dict.get(m['id'], 0) for m in team])


def calculate_redundancy(team, required_skills):
    """Average number of team members covering each required skill."""
    if not required_skills or not team:
        return 0
    required_lower = {s.lower() for s in required_skills}
    coverage_count = {s: 0 for s in required_lower}
    for member in team:
        for s in member.get('skills_detail', []):
            skill_lower = s['skill'].lower()
            if skill_lower in coverage_count:
                coverage_count[skill_lower] += 1
    return np.mean(list(coverage_count.values()))


def jaccard_similarity(team1, team2):
    ids1 = {m['id'] for m in team1}
    ids2 = {m['id'] for m in team2}
    intersection = len(ids1 & ids2)
    union = len(ids1 | ids2)
    return intersection / union if union > 0 else 0.0


# =============================================================================
# RUN ALL PROFILES
# =============================================================================
print("Running all 9 profiles + Greedy baseline...")
print()

all_results = {profile: {'risk': [], 'skill': [], 'coverage': [], 'redundancy': []} 
               for profile in MISSION_PROFILES.keys()}
all_results['greedy'] = {'risk': [], 'skill': [], 'coverage': [], 'redundancy': []}

for sim in range(CONFIG['n_simulations']):
    if (sim + 1) % 10 == 0:
        print(f"  Progress: {sim+1}/{CONFIG['n_simulations']}")
    
    candidates, bc_dict, G = generate_organization(CONFIG['n_candidates'], CONFIG['all_skills'])
    required_skills = list(np.random.choice(CONFIG['all_skills'], 
                                             size=CONFIG['n_skills_required'], 
                                             replace=False))
    
    # Run all profiles
    for profile in MISSION_PROFILES.keys():
        team = smartchimera_with_profile(
            candidates, required_skills, CONFIG['team_size'], 
            bc_dict, profile, CONFIG['beam_width']
        )
        all_results[profile]['risk'].append(calculate_linchpin_risk(team, bc_dict))
        all_results[profile]['skill'].append(calculate_avg_skill_level(team, required_skills))
        all_results[profile]['coverage'].append(calculate_skill_coverage(team, required_skills))
        all_results[profile]['redundancy'].append(calculate_redundancy(team, required_skills))
    
    # Greedy baseline
    team_greedy = greedy_baseline(candidates, required_skills, CONFIG['team_size'])
    all_results['greedy']['risk'].append(calculate_linchpin_risk(team_greedy, bc_dict))
    all_results['greedy']['skill'].append(calculate_avg_skill_level(team_greedy, required_skills))
    all_results['greedy']['coverage'].append(calculate_skill_coverage(team_greedy, required_skills))
    all_results['greedy']['redundancy'].append(calculate_redundancy(team_greedy, required_skills))

# =============================================================================
# RESULTS
# =============================================================================
print()
print("=" * 100)
print("ALL PROFILES COMPARISON")
print("=" * 100)
print()
print(f"{'Profile':<25} {'bc_penalty':>10} {'Risk':>10} {'Skill':>10} {'Coverage':>10} {'Redundancy':>10}")
print("-" * 100)

sorted_profiles = sorted(MISSION_PROFILES.keys(), 
                         key=lambda p: MISSION_PROFILES[p]['weights']['bc_penalty'],
                         reverse=True)

for profile in sorted_profiles:
    weights = MISSION_PROFILES[profile]['weights']
    risk = np.mean(all_results[profile]['risk'])
    skill = np.mean(all_results[profile]['skill'])
    cov = np.mean(all_results[profile]['coverage']) * 100
    red = np.mean(all_results[profile]['redundancy'])
    
    print(f"{profile:<25} {weights['bc_penalty']:>+10.1f} {risk:>10.4f} {skill:>10.2f} {cov:>9.1f}% {red:>10.2f}")

# Greedy
risk = np.mean(all_results['greedy']['risk'])
skill = np.mean(all_results['greedy']['skill'])
cov = np.mean(all_results['greedy']['coverage']) * 100
red = np.mean(all_results['greedy']['redundancy'])
print("-" * 100)
print(f"{'GREEDY (baseline)':<25} {'N/A':>10} {risk:>10.4f} {skill:>10.2f} {cov:>9.1f}% {red:>10.2f}")

# =============================================================================
# KEY COMPARISONS
# =============================================================================
print()
print("=" * 100)
print("KEY INSIGHTS")
print("=" * 100)

# Extreme profiles comparison
jr = all_results['junior_training']
arch = all_results['architecture_review']
greedy = all_results['greedy']

print(f"""
1. LINCHPIN RISK (Lower = Better for stability):
   - Junior Training (bc_penalty=+50):  {np.mean(jr['risk']):.4f}
   - Architecture Review (bc_penalty=-10): {np.mean(arch['risk']):.4f}
   - Greedy (no awareness):             {np.mean(greedy['risk']):.4f}

2. SKILL LEVEL (Higher = Better expertise):
   - Junior Training:    {np.mean(jr['skill']):.2f}
   - Architecture Review: {np.mean(arch['skill']):.2f}
   - Greedy:             {np.mean(greedy['skill']):.2f}

3. COVERAGE (Higher = More skills covered):
   - Junior Training:    {np.mean(jr['coverage'])*100:.1f}%
   - Architecture Review: {np.mean(arch['coverage'])*100:.1f}%
   - Greedy:             {np.mean(greedy['coverage'])*100:.1f}%
""")

# Statistical test: Junior vs Architecture
t_risk, p_risk = stats.ttest_ind(jr['risk'], arch['risk'])
print(f"Statistical Test (Junior vs Architecture Review):")
print(f"  Risk difference: p = {p_risk:.6f}")
if p_risk < 0.001:
    print("  ✅ HIGHLY SIGNIFICANT (p < 0.001)")

# Save results
output = {
    'timestamp': datetime.now().isoformat(),
    'config': CONFIG,
    'results': {
        method: {
            'mean_risk': float(np.mean(data['risk'])),
            'mean_skill': float(np.mean(data['skill'])),
            'mean_coverage': float(np.mean(data['coverage'])),
            'mean_redundancy': float(np.mean(data['redundancy']))
        }
        for method, data in all_results.items()
    }
}

with open('full_profile_results.json', 'w') as f:
    json.dump(output, f, indent=2)

print()
print(f"📁 Results saved to: full_profile_results.json")
print("=" * 100)
