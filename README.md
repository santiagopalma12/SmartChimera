# 🔬 SmartChimera

> Intelligent Team Formation Engine using Graph-Based Algorithms

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.14+-purple.svg)](https://neo4j.com)
[![React](https://img.shields.io/badge/React-18+-cyan.svg)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Overview

SmartChimera is an advanced team formation system that leverages graph algorithms to optimize team composition for software development projects. Using Neo4j graph database and sophisticated algorithms like **Brandes Betweenness Centrality** and **Beam Search optimization**, SmartChimera identifies the best team configurations while minimizing organizational risk.

### Key Features

- 🎯 **Multi-mode Team Formation**: RESILIENT mode (minimizes bus factor) vs PERFORMANCE mode (maximizes expertise)
- 🔍 **Linchpin Detection**: Identifies critical employees using Betweenness Centrality algorithms
- 📊 **Mission Profiles**: Configurable team formation strategies (Speed, Quality, Resilient)
- 🛡️ **Bus Factor Analysis**: Calculates organizational risk and provides mitigation recommendations
- 🔗 **GitHub/Jira Integration**: Automatically ingests collaboration data from real projects
- 📈 **Evidence-Based Skill Scoring**: Multi-source triangulation (GitHub commits + LinkedIn certifications)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React/TS)                     │
│         Team Request Form  │  Results Visualization          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend API (FastAPI)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Guardian  │  │   Linchpin  │  │   Smart Team        │  │
│  │    Core     │  │   Detector  │  │   Formation         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Neo4j Graph Database                     │
│   Employees ──TRABAJO_CON──▶ Collaborations                  │
│   Employees ──DEMUESTRA_COMPETENCIA──▶ Skills                │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/santiagopalma12/SmartChimera.git
   cd SmartChimera
   ```

2. **Configure environment variables**
   ```bash
   # Copy template and configure
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Start with Docker Compose**
   ```powershell
   # Set password environment variable
   $env:NEO4J_PASSWORD = "your_secure_password"
   
   # Start all services
   .\start.ps1
   ```

4. **Access the application**
   - 🌐 Frontend: http://localhost:5173
   - 📚 API Docs: http://localhost:8000/docs
   - 🔗 Neo4j Browser: http://localhost:7474

### Seed Demo Data

```powershell
cd backend
$env:NEO4J_PASSWORD = "your_password"
python seed_demo_data.py
```

## 🧬 Core Algorithms

### Linchpin Detection (Brandes Betweenness Centrality)

Based on [Avelino et al. (2016)](investigacion/Avelino_2016_TruckFactor.pdf) and [Brandes (2001)](investigacion/Brandes_2001_BetweennessCentrality.pdf):

```python
# Identifies employees who are critical communication bridges
detector = LinchpinDetector(driver)
linchpins = detector.get_all_linchpins(threshold=0.15)
```

### Smart Team Formation (Beam Search)

```python
# Form optimal teams with configurable modes
formation = SmartTeamFormation(driver, linchpin_detector)
team = formation.form_team(
    candidates=candidate_pool,
    skills_required=["Python", "React", "Docker"],
    k=5,  # Team size
    mode=FormationMode.RESILIENT
)
```

### Mission Profiles

| Profile | Focus | Use Case |
|---------|-------|----------|
| 🚀 **Speed** | Fast delivery, skill coverage | Tight deadlines, MVPs |
| ⭐ **Quality** | Deep expertise, best performers | Critical features, long-term |
| 🛡️ **Resilient** | Low bus factor, knowledge distribution | Strategic projects |

## 📁 Project Structure

```
SmartChimera/
├── backend/
│   ├── app/
│   │   ├── guardian_core.py      # Main recommendation engine
│   │   ├── linchpin_detector.py  # Betweenness centrality
│   │   ├── smart_team_formation.py # Beam search algorithm
│   │   ├── mission_profiles.py   # Strategy configurations
│   │   ├── scoring.py            # Evidence-based skill levels
│   │   └── main.py               # FastAPI endpoints
│   └── tests/
├── frontend/
│   └── src/
│       ├── components/           # React components
│       └── services/             # API client
├── scripts/                      # Data ingestion utilities
├── experiments/                  # Statistical validation
├── investigacion/                # Research papers (IEEE format)
└── docs/                         # Documentation
```

## 🔬 Research Foundation

SmartChimera is built on peer-reviewed research:

- **Avelino et al. (2016)**: "A Novel Approach for Estimating Truck Factors" - Bus Factor methodology
- **Brandes (2001)**: "A Faster Algorithm for Betweenness Centrality" - BC computation
- **Lappas et al. (2009)**: "Finding a Team of Experts in Social Networks" - Team formation theory
- **MacCormack et al. (2012)**: "Exploring the Structure of Complex Software Designs" - Architecture mirroring

See [investigacion/](investigacion/) for full papers and bibliography.

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/recommend` | Generate team recommendations |
| GET | `/api/linchpins` | List critical employees with risk levels |
| GET | `/api/mission-profiles` | Available team formation strategies |
| GET | `/api/skills` | All skills for autocomplete |
| GET | `/api/graph` | Graph data for visualization |

Full API documentation: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

## 🧪 Testing

```bash
# Run backend tests
cd backend
pytest tests/ -v

# Run statistical validation experiments
cd experiments
python statistical_validation.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Santiago Palma** - *Lead Developer* - [@santiagopalma12](https://github.com/santiagopalma12)

## 🙏 Acknowledgments

- Universidad Nacional de San Agustín (UNSA)
- Neo4j Community
- FastAPI and React ecosystems

---

<p align="center">
  Made with ❤️ for the Feria de Proyectos 2025
</p>
