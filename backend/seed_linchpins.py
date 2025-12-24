import sys
import os

# Add parent directory to path to allow importing 'app'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db import get_driver, close_driver
from app.linchpin_detector import LinchpinDetector
from app.config import settings

def seed_linchpins():
    print("Initializing Linchpin Seeder...")
    
    # Ensure driver is connected
    driver = get_driver()
    
    try:
        print("verifying connection...")
        driver.verify_connectivity()
        
        detector = LinchpinDetector(driver)
        
        print("Computing Network Centrality & Risk Scores...")
        # This method automatically updates the 'linchpin_score' property on Employee nodes
        scores = detector.compute_combined_risk_score()
        
        count = len(scores)
        print(f"✓ Computed scores for {count} employees.")
        
        print("Retrieving Top Linchpins...")
        linchpins = detector.get_all_linchpins(threshold=0.1) # Lower threshold to see more results
        
        print("\n" + "="*50)
        print(f"TOP {min(5, len(linchpins))} DETECTED LINCHPINS")
        print("="*50)
        
        for i, lp in enumerate(linchpins[:5]):
            print(f"{i+1}. {lp.name} (ID: {lp.employee_id})")
            print(f"   Score: {lp.bc_score:.4f} | Risk: {lp.risk_level.value}")
            print(f"   Projects: {lp.project_count}")
            print("-" * 30)
            
        print(f"\nTotal High Risk Employees: {len(linchpins)}")
        print("Success! Data persisted to Neo4j.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        close_driver()

if __name__ == "__main__":
    seed_linchpins()
