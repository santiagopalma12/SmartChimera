"""
SmartChimera - GitHub Real Data Ingestor
=========================================
Ingesta datos REALES de proyectos open-source de GitHub.
Extrae: developers, skills (basados en archivos), colaboraciones (PRs compartidos).

Uso:
    python github_real_data_ingestor.py --repos facebook/react microsoft/vscode --max-contributors 500
"""

import os
import sys
import time
import json
import argparse
import requests
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Optional

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from neo4j import GraphDatabase
except ImportError:
    print("ERROR: neo4j package not installed. Run: pip install neo4j")
    sys.exit(1)

# ============================================================================
# CONFIGURATION
# ============================================================================

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
if not GITHUB_TOKEN:
    print("WARNING: GITHUB_TOKEN not set. Rate limit will be 60 req/hour (very slow).")
    print("Set it with: $env:GITHUB_TOKEN = 'your_token_here'")

HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'} if GITHUB_TOKEN else {}
HEADERS['Accept'] = 'application/vnd.github.v3+json'

# Neo4j connection
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASSWORD")

if not NEO4J_PASS:
    print("ERROR: NEO4J_PASSWORD environment variable is required")
    print("Set it with: $env:NEO4J_PASSWORD = 'your_password'")
    sys.exit(1)

# File extension to skill mapping (expanded)
EXTENSION_SKILL_MAP = {
    # Languages
    '.py': 'Python',
    '.js': 'JavaScript',
    '.jsx': 'JavaScript',
    '.ts': 'TypeScript',
    '.tsx': 'TypeScript',
    '.java': 'Java',
    '.go': 'Go',
    '.rs': 'Rust',
    '.rb': 'Ruby',
    '.php': 'PHP',
    '.cs': 'C#',
    '.cpp': 'C++',
    '.c': 'C',
    '.swift': 'Swift',
    '.kt': 'Kotlin',
    '.scala': 'Scala',
    '.r': 'R',
    '.R': 'R',
    # Web
    '.html': 'HTML',
    '.css': 'CSS',
    '.scss': 'CSS',
    '.sass': 'CSS',
    '.less': 'CSS',
    '.vue': 'Vue.js',
    '.svelte': 'Svelte',
    # DevOps
    '.yml': 'YAML',
    '.yaml': 'YAML',
    '.tf': 'Terraform',
    '.sh': 'Shell',
    '.bash': 'Shell',
    'Dockerfile': 'Docker',
    '.docker': 'Docker',
    # Data
    '.sql': 'SQL',
    '.json': 'JSON',
    '.graphql': 'GraphQL',
    # Docs
    '.md': 'Documentation',
}

# ============================================================================
# GITHUB API HELPERS
# ============================================================================

def github_get(url: str, params: dict = None) -> Optional[dict]:
    """Make a GET request to GitHub API with rate limit handling."""
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
        
        # Check rate limit
        remaining = int(resp.headers.get('X-RateLimit-Remaining', 1))
        if remaining < 10:
            reset_time = int(resp.headers.get('X-RateLimit-Reset', 0))
            wait_seconds = max(0, reset_time - int(time.time())) + 5
            print(f"⚠️  Rate limit low ({remaining} remaining). Waiting {wait_seconds}s...")
            time.sleep(wait_seconds)
        
        if resp.status_code == 403 and 'rate limit' in resp.text.lower():
            print("❌ Rate limit exceeded. Waiting 60s...")
            time.sleep(60)
            return github_get(url, params)  # Retry
        
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ API Error: {e}")
        return None

def get_contributors(repo: str, max_count: int = 100) -> List[dict]:
    """Get top contributors for a repository."""
    print(f"  📥 Fetching contributors from {repo}...")
    contributors = []
    page = 1
    per_page = min(100, max_count)
    
    while len(contributors) < max_count:
        url = f"https://api.github.com/repos/{repo}/contributors"
        data = github_get(url, {'page': page, 'per_page': per_page, 'anon': 'false'})
        
        if not data or len(data) == 0:
            break
        
        for c in data:
            if c.get('type') == 'User':  # Skip bots
                contributors.append({
                    'login': c['login'],
                    'contributions': c.get('contributions', 0),
                    'avatar_url': c.get('avatar_url', ''),
                    'html_url': c.get('html_url', ''),
                })
        
        if len(data) < per_page:
            break
        page += 1
    
    print(f"    ✅ Found {len(contributors[:max_count])} contributors")
    return contributors[:max_count]

def get_contributor_commits(repo: str, login: str, max_commits: int = 30) -> List[dict]:
    """Get recent commits by a contributor to extract skills."""
    url = f"https://api.github.com/repos/{repo}/commits"
    commits = []
    page = 1
    
    while len(commits) < max_commits:
        data = github_get(url, {'author': login, 'page': page, 'per_page': min(30, max_commits)})
        
        if not data or len(data) == 0:
            break
        
        for c in data:
            commits.append({
                'sha': c['sha'],
                'message': c['commit']['message'][:100] if c.get('commit') else '',
                'date': c['commit']['committer']['date'] if c.get('commit') else None,
            })
        
        if len(data) < 30:
            break
        page += 1
    
    return commits[:max_commits]

def get_commit_files(repo: str, sha: str) -> List[str]:
    """Get files modified in a commit."""
    url = f"https://api.github.com/repos/{repo}/commits/{sha}"
    data = github_get(url)
    
    if not data:
        return []
    
    files = data.get('files', [])
    return [f.get('filename', '') for f in files]

def extract_skills_from_files(files: List[str]) -> Set[str]:
    """Extract skills from file extensions."""
    skills = set()
    for f in files:
        fname = os.path.basename(f)
        for ext, skill in EXTENSION_SKILL_MAP.items():
            if fname.endswith(ext) or (ext == 'Dockerfile' and 'Dockerfile' in fname):
                skills.add(skill)
    return skills

def get_pull_requests(repo: str, max_prs: int = 100) -> List[dict]:
    """Get merged PRs to detect collaborations."""
    print(f"  📥 Fetching PRs from {repo}...")
    url = f"https://api.github.com/repos/{repo}/pulls"
    prs = []
    page = 1
    
    while len(prs) < max_prs:
        data = github_get(url, {'state': 'closed', 'page': page, 'per_page': 30})
        
        if not data or len(data) == 0:
            break
        
        for pr in data:
            if pr.get('merged_at'):  # Only merged PRs
                prs.append({
                    'number': pr['number'],
                    'author': pr['user']['login'] if pr.get('user') else None,
                    'merged_by': pr.get('merged_by', {}).get('login') if pr.get('merged_by') else None,
                    'title': pr['title'][:80],
                })
        
        if len(data) < 30:
            break
        page += 1
    
    print(f"    ✅ Found {len(prs[:max_prs])} merged PRs")
    return prs[:max_prs]

# ============================================================================
# NEO4J INGESTION
# ============================================================================

def connect_neo4j():
    """Connect to Neo4j database."""
    print(f"🔌 Connecting to Neo4j at {NEO4J_URI}...")
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
        driver.verify_connectivity()
        print("   ✅ Connected!")
        return driver
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        sys.exit(1)

def ingest_developers(driver, developers: List[dict], source_repo: str):
    """Insert developers into Neo4j."""
    with driver.session() as session:
        for dev in developers:
            session.run("""
                MERGE (e:Empleado {id: $id})
                SET e.nombre = $nombre,
                    e.github_url = $github_url,
                    e.avatar_url = $avatar_url,
                    e.contributions = $contributions,
                    e.source_repo = $source_repo,
                    e.ingested_at = datetime()
            """, 
                id=dev['login'],
                nombre=dev['login'],
                github_url=dev.get('html_url', ''),
                avatar_url=dev.get('avatar_url', ''),
                contributions=dev.get('contributions', 0),
                source_repo=source_repo
            )

def ingest_skills(driver, developer_skills: Dict[str, Set[str]]):
    """Insert skills and competencies into Neo4j."""
    with driver.session() as session:
        for dev_id, skills in developer_skills.items():
            for skill in skills:
                # Create skill if not exists
                session.run("MERGE (s:Skill {name: $name})", name=skill)
                
                # Create competency relationship
                session.run("""
                    MATCH (e:Empleado {id: $eid})
                    MATCH (s:Skill {name: $skill})
                    MERGE (e)-[r:DEMUESTRA_COMPETENCIA]->(s)
                    SET r.nivel = COALESCE(r.nivel, 0) + 0.1,
                        r.last_validated = datetime()
                """, eid=dev_id, skill=skill)

def ingest_collaborations(driver, collaborations: List[Tuple[str, str, str]]):
    """Insert collaboration relationships based on PRs."""
    with driver.session() as session:
        for author, reviewer, repo in collaborations:
            if author and reviewer and author != reviewer:
                session.run("""
                    MATCH (a:Empleado {id: $author})
                    MATCH (b:Empleado {id: $reviewer})
                    MERGE (a)-[r:TRABAJO_CON]->(b)
                    SET r.projects = COALESCE(r.projects, 0) + 1,
                        r.frequency = COALESCE(r.frequency, 0) + 1,
                        r.last_collaboration = datetime()
                """, author=author, reviewer=reviewer)

# ============================================================================
# MAIN INGESTION LOGIC
# ============================================================================

def ingest_repository(driver, repo: str, max_contributors: int = 100, max_commits_per_dev: int = 10):
    """Full ingestion for a single repository."""
    print(f"\n{'='*60}")
    print(f"🚀 INGESTING: {repo}")
    print(f"{'='*60}")
    
    # 1. Get contributors
    contributors = get_contributors(repo, max_contributors)
    if not contributors:
        print(f"❌ No contributors found for {repo}")
        return 0
    
    # 2. Insert developers
    print(f"  💾 Inserting {len(contributors)} developers into Neo4j...")
    ingest_developers(driver, contributors, repo)
    
    # 3. Extract skills from commits
    print(f"  🔍 Extracting skills from commits...")
    developer_skills: Dict[str, Set[str]] = defaultdict(set)
    
    for i, dev in enumerate(contributors[:50]):  # Limit to 50 for speed
        login = dev['login']
        commits = get_contributor_commits(repo, login, max_commits_per_dev)
        
        for commit in commits[:5]:  # Sample 5 commits per dev
            files = get_commit_files(repo, commit['sha'])
            skills = extract_skills_from_files(files)
            developer_skills[login].update(skills)
        
        if (i + 1) % 10 == 0:
            print(f"    Processed {i+1}/{min(50, len(contributors))} developers...")
    
    # 4. Insert skills
    print(f"  💾 Inserting skills into Neo4j...")
    ingest_skills(driver, developer_skills)
    
    # 5. Extract and insert collaborations
    prs = get_pull_requests(repo, max_prs=100)
    collaborations = [(pr['author'], pr['merged_by'], repo) for pr in prs if pr['author'] and pr['merged_by']]
    
    print(f"  💾 Inserting {len(collaborations)} collaborations...")
    ingest_collaborations(driver, collaborations)
    
    print(f"  ✅ DONE: {repo}")
    return len(contributors)

def main():
    parser = argparse.ArgumentParser(description="Ingest real GitHub data into SmartChimera")
    parser.add_argument('--repos', nargs='+', default=['facebook/react'],
                        help='GitHub repos to ingest (e.g., facebook/react microsoft/vscode)')
    parser.add_argument('--max-contributors', type=int, default=100,
                        help='Max contributors per repo')
    parser.add_argument('--clear-db', action='store_true',
                        help='Clear existing data before ingesting')
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("  🧬 SmartChimera - GitHub Real Data Ingestor")
    print("="*60)
    print(f"  Repos: {args.repos}")
    print(f"  Max contributors per repo: {args.max_contributors}")
    print(f"  Token: {'✅ Set' if GITHUB_TOKEN else '❌ Not set (slow mode)'}")
    print("="*60 + "\n")
    
    # Connect to Neo4j
    driver = connect_neo4j()
    
    # Optionally clear existing data
    if args.clear_db:
        print("🗑️  Clearing existing data...")
        with driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        print("   ✅ Database cleared")
    
    # Ingest each repo
    total_developers = 0
    for repo in args.repos:
        count = ingest_repository(driver, repo, args.max_contributors)
        total_developers += count
    
    # Final stats
    print("\n" + "="*60)
    print("  📊 INGESTION COMPLETE")
    print("="*60)
    
    with driver.session() as session:
        result = session.run("MATCH (e:Empleado) RETURN count(e) as devs")
        dev_count = result.single()['devs']
        
        result = session.run("MATCH (s:Skill) RETURN count(s) as skills")
        skill_count = result.single()['skills']
        
        result = session.run("MATCH ()-[r:TRABAJO_CON]->() RETURN count(r) as collabs")
        collab_count = result.single()['collabs']
        
        result = session.run("MATCH ()-[r:DEMUESTRA_COMPETENCIA]->() RETURN count(r) as comps")
        comp_count = result.single()['comps']
    
    print(f"  Developers:     {dev_count}")
    print(f"  Skills:         {skill_count}")
    print(f"  Collaborations: {collab_count}")
    print(f"  Competencies:   {comp_count}")
    print("="*60 + "\n")
    
    driver.close()

if __name__ == "__main__":
    main()
