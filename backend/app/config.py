"""
Configuration management for Project Chimera.
Loads environment variables and provides application settings.
"""
import os


class Settings:
    """Application settings loaded from environment variables."""
    
    def __init__(self):
        # Neo4j Configuration
        # Note: In production, ensure these are set via environment variables
        self.neo4j_uri = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
        self.neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        self.neo4j_pass = os.getenv("NEO4J_PASSWORD", "")
        
        if not self.neo4j_pass:
            import warnings
            warnings.warn(
                "NEO4J_PASSWORD not set. Set this environment variable for database access.",
                UserWarning
            )
        
        # GitHub Configuration (optional)
        self.github_token = os.getenv("GITHUB_TOKEN", "")
        
        # Jira Configuration (optional)
        self.jira_base = os.getenv("JIRA_BASE", "")
        self.jira_user = os.getenv("JIRA_USER", "")
        self.jira_token = os.getenv("JIRA_TOKEN", "")
        
        # Privacy Configuration
        self.hash_actor_ids = os.getenv("HASH_ACTOR_IDS", "false").lower() == "true"
        self.privacy_salt = os.getenv("PRIVACY_SALT", "")
        
        if not self.privacy_salt or self.privacy_salt == "INSECURE_DEFAULT_CHANGE_ME":
            import warnings
            warnings.warn(
                "PRIVACY_SALT not set or using insecure default. Set a secure random string in production.",
                UserWarning
            )


settings = Settings()
