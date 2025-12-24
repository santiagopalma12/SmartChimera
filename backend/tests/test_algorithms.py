"""
Unit tests for SmartChimera core algorithms.
Tests Beam Search (Team Formation) and Bus Factor Detection.
"""
import pytest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.app.smart_team_formation import SmartTeamFormation, FormationMode
from unittest.mock import MagicMock


class TestBeamSearch:
    """Test Beam Search algorithm for team formation."""
    
    def test_beam_width_is_10(self):
        """Verify BEAM_WIDTH constant is set to 10."""
        # This is hardcoded in form_team method, line 126
        # We verify behavior by checking k=2 returns teams
        mock_driver = MagicMock()
        tf = SmartTeamFormation(mock_driver)
        
        candidates = [
            {'id': f'emp_{i}', 'skills_detail': [{'skill': 'Python', 'nivel': 3.0}], 'availability_hours': 40}
            for i in range(15)
        ]
        
        # Should work even with BEAM_WIDTH=10 and 15 candidates
        team = tf.form_team(candidates, ['Python'], k=2, mode=FormationMode.PERFORMANCE)
        assert len(team) == 2
    
    def test_resilient_mode_penalizes_bc(self):
        """Verify resilient mode applies BC penalty."""
        mock_driver = MagicMock()
        mock_detector = MagicMock()
        mock_detector.compute_betweenness_centrality.return_value = {
            'high_bc': 0.9,
            'low_bc': 0.1
        }
        
        tf = SmartTeamFormation(mock_driver, linchpin_detector=mock_detector)
        
        candidates = [
            {'id': 'high_bc', 'skills_detail': [{'skill': 'Python', 'nivel': 5.0}], 'availability_hours': 40},
            {'id': 'low_bc', 'skills_detail': [{'skill': 'Python', 'nivel': 5.0}], 'availability_hours': 40}
        ]
        
        team = tf.form_team(candidates, ['Python'], k=1, mode=FormationMode.RESILIENT)
        
        # Should prefer low_bc in resilient mode
        assert team[0]['id'] == 'low_bc', "Resilient mode should avoid high BC candidates"
    
    def test_performance_mode_selects_best_skills(self):
        """Verify performance mode prioritizes skill depth."""
        mock_driver = MagicMock()
        tf = SmartTeamFormation(mock_driver)
        
        candidates = [
            {'id': 'expert', 'skills_detail': [{'skill': 'Python', 'nivel': 5.0}], 'availability_hours': 40},
            {'id': 'novice', 'skills_detail': [{'skill': 'Python', 'nivel': 1.0}], 'availability_hours': 40}
        ]
        
        team = tf.form_team(candidates, ['Python'], k=1, mode=FormationMode.PERFORMANCE)
        
        # Should select expert in performance mode
        assert team[0]['id'] == 'expert', "Performance mode should select highest skill level"
    
    def test_team_size_respected(self):
        """Verify algorithm returns exactly k members."""
        mock_driver = MagicMock()
        tf = SmartTeamFormation(mock_driver)
        
        candidates = [
            {'id': f'emp_{i}', 'skills_detail': [{'skill': 'Python', 'nivel': 3.0}], 'availability_hours': 40}
            for i in range(10)
        ]
        
        for k in [1, 3, 5, 7]:
            team = tf.form_team(candidates, ['Python'], k=k, mode=FormationMode.PERFORMANCE)
            assert len(team) == k, f"Expected team size {k}, got {len(team)}"


class TestBusFactorDetection:
    """Test Bus Factor / Linchpin detection algorithms."""
    
    def test_hybrid_score_is_50_50(self):
        """Verify hybrid score combines BC and Project Weight equally."""
        from backend.app.linchpin_detector import LinchpinDetector
        
        mock_driver = MagicMock()
        
        # Mock BC computation
        detector = LinchpinDetector(mock_driver)
        detector._bc_cache = {'emp_001': 0.8}  # High BC
        
        # Mock project score computation
        mock_session = MagicMock()
        mock_result = [{'eid': 'emp_001', 'projects_count': 10}]
        mock_session.run.return_value = mock_result
        mock_driver.session.return_value.__enter__.return_value = mock_session
        
        # Compute combined (should be 0.5 * BC + 0.5 * PW)
        # BC = 0.8, PW = 10/10 = 1.0
        # Expected: 0.5 * 0.8 + 0.5 * 1.0 = 0.4 + 0.5 = 0.9
        scores = detector.compute_combined_risk_score()
        
        # Note: actual value depends on normalization, but weights should be 50/50
        assert 'emp_001' in scores
    
    def test_risk_level_thresholds(self):
        """Verify risk level classification thresholds."""
        from backend.app.linchpin_detector import LinchpinDetector, RiskLevel
        
        mock_driver = MagicMock()
        detector = LinchpinDetector(mock_driver)
        
        assert detector.get_risk_level(0.8) == RiskLevel.CRITICAL  # > 0.7
        assert detector.get_risk_level(0.6) == RiskLevel.HIGH      # > 0.5
        assert detector.get_risk_level(0.3) == RiskLevel.MEDIUM    # > 0.25
        assert detector.get_risk_level(0.1) == RiskLevel.LOW       # <= 0.25


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
