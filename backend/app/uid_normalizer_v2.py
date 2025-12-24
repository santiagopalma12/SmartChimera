import re
import json
import os
from typing import Dict, Optional

class UIDNormalizer:
    def __init__(self, mappings_file: str = "app/uid_mappings.json"):
        self.mappings_file = mappings_file
        self.mappings = self._load_mappings()

    def _load_mappings(self) -> Dict[str, str]:
        if os.path.exists(self.mappings_file):
            try:
                with open(self.mappings_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def normalize(self, source_id: str, source_type: str) -> str:
        """
        Normalize an ID from a specific source to a canonical employee ID.
        """
        # Check explicit mappings first
        if source_id in self.mappings:
            return self.mappings[source_id]
        
        # Heuristic: if it looks like an email, extract the part before @
        if '@' in source_id:
            return source_id.split('@')[0]
            
        return source_id

    def add_mapping(self, source_id: str, canonical_id: str):
        self.mappings[source_id] = canonical_id
        self._save_mappings()

    def _save_mappings(self):
        try:
            with open(self.mappings_file, 'w') as f:
                json.dump(self.mappings, f, indent=2)
        except Exception as e:
            print(f"Error saving mappings: {e}")

# Singleton instance
_normalizer = None

def get_uid_normalizer() -> UIDNormalizer:
    global _normalizer
    if _normalizer is None:
        _normalizer = UIDNormalizer()
    return _normalizer

def normalize_uid(source_type: str, source_id: str) -> str:
    return get_uid_normalizer().normalize(source_id, source_type)

def normalize_all_employees():
    from .db import get_driver
    driver = get_driver()
    count = 0
    with driver.session() as session:
        result = session.run("MATCH (e:Empleado) RETURN e.id as id")
        for record in result:
            original_id = record['id']
            new_id = normalize_uid('db', original_id)
            if new_id != original_id:
                session.run("MATCH (e:Empleado {id: $old}) SET e.id = $new", old=original_id, new=new_id)
                count += 1
    return {"updated": count}

# Stubs for pipeline compatibility (Phase 3 logic to be restored)
def fetch_evidence_rows(driver):
    return []

def propose_uid_updates(rows):
    return {}, {}

def apply_updates(driver, updates, blocking_duplicates):
    return 0
