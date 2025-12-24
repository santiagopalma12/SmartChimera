"""
SmartChimera - Mission Profiles
===============================
Defines strategic profiles for team formation with specific weight configurations.
Weights are optimized via Grid Search and validated empirically.
"""

from typing import Dict, Any

MISSION_PROFILES = {
    "mantenimiento": {
        "name": "Mantenimiento Crítico (Resilient)",
        "description": "Estabilidad máxima. Penaliza riesgo (Bus Factor) y exige redundancia.",
        "strategy_preference": "resilient",
        "weights": {
            "skill_coverage": 2.0,
            "skill_depth": 1.0,      # Stability > Brilliance
            "collaboration": 2.0,
            "redundancy": 5.0,       # CRITICAL: Must have backups
            "availability": 3.0,
            "bc_penalty": 20.0       # VETO: No Linchpins allowed
        }
    },
    "innovacion": {
        "name": "I+D / Deep Tech (Growth)",
        "description": "Prioriza genios técnicos (Score 5.0). Acepta riesgo de Bus Factor.",
        "strategy_preference": "performance",
        "weights": {
            "skill_coverage": 1.0,
            "skill_depth": 10.0,     # CRITICAL: Only experts
            "collaboration": 0.5,
            "redundancy": 0.0,
            "availability": 1.0,
            "bc_penalty": -5.0       # BONUS: We connect disconnected experts
        }
    },
    "entrega_rapida": {
        "name": "Speed Squad (Agile)",
        "description": "Equipos que ya se conocen. Maximiza colaboración previa.",
        "strategy_preference": "speed",
        "weights": {
            "skill_coverage": 2.0,
            "skill_depth": 1.0,
            "collaboration": 10.0,   # CRITICAL: Must have worked together
            "redundancy": 1.0,
            "availability": 4.0,     # Must be free NOW
            "bc_penalty": 0.0
        }
    },
    "legacy_rescue": {
        "name": "Legacy Rescue (SRE)",
        "description": "Coverage agresivo. Para sistemas viejos y no documentados.",
        "strategy_preference": "resilient",
        "weights": {
            "skill_coverage": 10.0,  # CRITICAL: Cover ALL the weird skills
            "skill_depth": 2.0,
            "collaboration": 2.0,
            "redundancy": 3.0,
            "availability": 5.0,     # Firefighting mode
            "bc_penalty": 10.0
        }
    },
    "junior_training": {
        "name": "Junior Squad / Semillero",
        "description": "Reduce Bus Factor usando Amateurs. Evita Linchpins (Seniors) para tareas monótonas.",
        "strategy_preference": "resilient",
        "weights": {
            "skill_coverage": 2.0,
            "skill_depth": 0.5,      # We don't need experts
            "collaboration": 5.0,    # Need them to talk to each other
            "redundancy": 5.0,       # Safety in numbers
            "availability": 5.0,     # Juniors have time
            "bc_penalty": 50.0       # EXTREME VETO: Ban Seniors/Linchpins to force Junior selection
        }
    },
    "crisis_response": {
        "name": "Crisis / Firefighting",
        "description": "Resolución inmediata de incidentes. Disponibilidad total requerida.",
        "strategy_preference": "speed",
        "weights": {
            "skill_coverage": 5.0,
            "skill_depth": 2.0,
            "collaboration": 2.0,
            "redundancy": 1.0,
            "availability": 20.0,    # CRITICAL: Must be free NOW
            "bc_penalty": 0.0
        }
    },
    "architecture_review": {
        "name": "Architecture Review",
        "description": "Los mejores y más conectados (Linchpins) para definir el futuro.",
        "strategy_preference": "performance", # Growth
        "weights": {
            "skill_coverage": 3.0,
            "skill_depth": 10.0,     # Max Expertise
            "collaboration": 1.0,
            "redundancy": 0.0,
            "availability": 0.5,     # They are busy, we wait
            "bc_penalty": -10.0      # BONUS: We WANT Linchpins here
        }
    },
    "security_audit": {
        "name": "Security & Compliance",
        "description": "Paranoia máxima. Redundancia extrema para no perder detalles.",
        "strategy_preference": "resilient",
        "weights": {
            "skill_coverage": 5.0,
            "skill_depth": 5.0,
            "collaboration": 0.0,    # Independence is good for audit
            "redundancy": 10.0,      # Two sets of eyes on everything
            "availability": 2.0,
            "bc_penalty": 5.0
        }
    },
    "cloud_migration": {
        "name": "Cloud Migration",
        "description": "Cobertura amplia de tecnologías (AWS/Azure/Docker).",
        "strategy_preference": "performance",
        "weights": {
            "skill_coverage": 15.0,  # CRITICAL: Must know ALL the tools
            "skill_depth": 2.0,
            "collaboration": 3.0,
            "redundancy": 2.0,
            "availability": 2.0,
            "bc_penalty": 5.0
        }
    }
}

def get_mission_profile(profile_id: str) -> Dict[str, Any]:
    """Get profile config by ID, defaulting to 'innovacion' if not found."""
    return MISSION_PROFILES.get(profile_id, MISSION_PROFILES["innovacion"])
