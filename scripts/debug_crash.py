
import sys
import os
import traceback

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    print("Importing guardian_core...")
    from backend.app.guardian_core import generate_dossiers
    print("Successfully imported generate_dossiers")
except Exception as e:
    print(f"CRASH ON IMPORT: {e}")
    traceback.print_exc()
    sys.exit(1)

mock_request = {
    'requisitos_hard': {'skills': ['Python', 'React']},
    'k': 5,
    'mission_profile': 'innovacion',
    'formation_mode': 'performance'
}

try:
    print("Attempting to generate dossiers (this triggers lazy imports)...")
    dossiers = generate_dossiers(mock_request)
    print(f"Success! Generated {len(dossiers)} dossiers.")
except Exception as e:
    print(f"CRASH ON EXECUTION: {e}")
    traceback.print_exc()
