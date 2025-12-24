# Mission Profiles Framework
## Adaptive Team Assembly Based on Project Context

### Abstract
SmartChimera implements a **Mission Profile Framework** that adapts team recommendations based on project context and organizational priorities. Each profile applies different weights to candidate scoring dimensions (skill level, availability, collaboration history) to optimize for specific project types.

---

## 1. Mission Profiles Overview

The system provides **9 distinct mission profiles**, each designed for different project contexts:

| Profile | Focus | Strategy Preference | Use Case |
|---------|-------|---------------------|----------|
| **Maintenance** | Stability & Reliability | Safe Bet | Production support, legacy systems |
| **Innovation** | Experimentation | Growth Team | R&D, new product development |
| **Speed** | Fast Delivery | Speed Squad | Urgent deadlines, quick wins |
| **Collaboration** | Team Synergy | Speed Squad | Cross-functional initiatives |
| **Research** | Deep Exploration | Safe Bet | Proof of concepts, technical spikes |
| **Critical** | Zero Tolerance | Safe Bet | Mission-critical systems, compliance |
| **Learning** | Skill Development | Growth Team | Training, capability building |
| **Prototype** | Quick MVP | Speed Squad | Rapid prototyping, iteration |
| **Quality** | Thorough Testing | Safe Bet | QA-focused projects, audits |

---

## 2. Detailed Profile Specifications

### 2.1 Maintenance Profile
**Goal**: Ensure stability and reliability in production systems.

**Weights**:
- Skill Level: **1.5x** (prioritize senior engineers)
- Availability: **1.0x** (standard requirement)
- Collaboration: **0.5x** (less critical)
- Linchpin Penalty: **0.3** (avoid single points of failure)

**Radar Chart Values**:
- Stability: 100/100
- Skills: 90/100
- Innovation: 20/100

**Typical Recommendation**: High-experience teams with proven track records in similar maintenance work.

---

### 2.2 Innovation Profile
**Goal**: Foster creativity and experimental approaches.

**Weights**:
- Skill Level: **0.8x** (accept diverse experience levels)
- Availability: **0.7x** (flexible timelines)
- Collaboration: **1.2x** (knowledge sharing critical)
- Linchpin Penalty: **0.0** (OK to use domain experts)

**Radar Chart Values**:
- Innovation: 100/100
- Collaboration: 90/100
- Skills: 70/100

**Typical Recommendation**: Mixed-level teams with strong collaboration history, including specialists who can introduce novel approaches.

---

### 2.3 Speed Profile
**Goal**: Deliver results rapidly with proven team synergy.

**Weights**:
- Skill Level: **1.0x** (balanced)
- Availability: **1.5x** (must have time)
- Collaboration: **2.0x** (past synergy critical)
- Linchpin Penalty: **0.5** (moderate risk tolerance)

**Radar Chart Values**:
- Speed: 100/100
- Collaboration: 100/100
- Skills: 70/100

**Typical Recommendation**: Teams with prior collaboration history (`TRABAJO_CON` relationships in graph), high availability, and demonstrated ability to work together efficiently.

---

### 2.4 Collaboration Profile
**Goal**: Maximize team synergy and knowledge transfer.

**Weights**:
- Skill Level: **0.9x**
- Availability: **0.8x**
- Collaboration: **2.5x** (highest priority)
- Linchpin Penalty: **0.2**

**Radar Chart Values**:
- Collaboration: 100/100
- Innovation: 70/100
- Speed: 70/100

**Typical Recommendation**: Employees with extensive collaboration networks, proven mentorship capabilities, and cross-functional experience.

---

### 2.5 Research Profile
**Goal**: Deep technical investigation and proof-of-concept development.

**Weights**:
- Skill Level: **1.3x** (need technical depth)
- Availability: **0.6x** (flexible deadlines)
- Collaboration: **0.7x** (mostly independent work)
- Linchpin Penalty: **0.0** (specialists encouraged)

**Radar Chart Values**:
- Skills: 95/100
- Innovation: 90/100
- Stability: 70/100

**Typical Recommendation**: Senior engineers and specialists with deep domain expertise, less emphasis on team dynamics.

---

### 2.6 Critical Profile
**Goal**: Mission-critical systems with zero tolerance for failure.

**Weights**:
- Skill Level: **2.0x** (maximum expertise required)
- Availability: **1.8x** (must be fully committed)
- Collaboration: **1.0x**
- Linchpin Penalty: **0.8** (strongly avoid dependencies)

**Radar Chart Values**:
- Stability: 100/100
- Skills: 100/100
- Speed: 70/100

**Typical Recommendation**: Only the most experienced engineers with perfect availability, explicitly avoiding linchpin employees to prevent bus factor issues.

---

### 2.7 Learning Profile
**Goal**: Team capability building and skill development.

**Weights**:
- Skill Level: **0.5x** (accept juniors/interns)
- Availability: **1.0x**
- Collaboration: **1.5x** (mentorship important)
- Linchpin Penalty: **0.1**

**Radar Chart Values**:
- Collaboration: 95/100
- Innovation: 80/100
- Skills: 40/100

**Typical Recommendation**: Mixed teams with strong senior mentors paired with junior developers for knowledge transfer and growth opportunities.

---

### 2.8 Prototype Profile
**Goal**: Rapid MVP development with iterative approach.

**Weights**:
- Skill Level: **1.1x**
- Availability: **1.3x** (need time to iterate)
- Collaboration: **1.3x** (fast feedback loops)
- Linchpin Penalty: **0.3**

**Radar Chart Values**:
- Speed: 90/100
- Innovation: 85/100
- Collaboration: 80/100

**Typical Recommendation**: Agile teams with quick iteration capabilities, comfortable with ambiguity and changing requirements.

---

### 2.9 Quality Assurance Profile
**Goal**: Thorough testing, validation, and quality standards.

**Weights**:
- Skill Level: **1.4x** (detail-oriented experts)
- Availability: **1.2x**
- Collaboration: **0.9x**
- Linchpin Penalty: **0.4**

**Radar Chart Values**:
- Stability: 95/100
- Skills: 90/100
- Collaboration: 65/100

**Typical Recommendation**: QA specialists, test automation engineers, and detail-oriented developers with systematic approaches.

---

## 3. Implementation Details

### 3.1 Scoring Algorithm
Each candidate receives a composite score:

```python
score = (skill_avg * weight_skill) + (availability / 40 * weight_avail)
```

For Speed Squad strategy, collaboration history is added:
```python
collab_score = (projects_together + frequency * 0.5) * weight_collab
```

### 3.2 Strategy Ordering
The system generates 3 team strategies (Safe Bet, Growth Team, Speed Squad) and reorders them based on:
1. **Preferred strategy** from mission profile (comes first)
2. **Total score** descending (higher scores prioritized)

Example:
- **Maintenance** → Safe Bet first (highest skill emphasis)
- **Speed** → Speed Squad first (highest collaboration emphasis)
- **Learning** → Growth Team first (best mentorship balance)

### 3.3 API Integration
Mission profiles are exposed via REST API:

```bash
GET /api/mission-profiles
```

Response includes all 9 profiles with weights and metadata for frontend visualization.

---

## 4. Research Contribution

This framework represents a novel approach to **context-aware team assembly**. Unlike traditional skill-matching systems, SmartChimera:

1. **Adapts scoring** based on project objectives
2. **Leverages collaboration graphs** to detect synergy
3. **Mitigates bus factor** through linchpin detection
4. **Provides multiple alternatives** ranked by mission context

**Academic Significance**:
- Demonstrates practical application of graph-based workforce analytics
- Introduces weighted multi-objective optimization for team formation
- Validates through 9 distinct real-world project scenarios

---

## 5. Validation Examples

### Example 1: Critical Mission
**Input**: Python + Docker, k=3, min_hours=20, profile=critical

**Output**:
- Safe Bet: **27.0** (APPROVE) ← Highest skill + availability
- Growth Team: 21.46 (REVIEW)
- Speed Squad: 21.46 (REVIEW)

**Analysis**: Critical profile's 2.0x skill weight and 1.8x availability weight heavily favor Safe Bet strategy with senior engineers.

### Example 2: Learning Mission
**Input**: JavaScript + React, k=4, min_hours=15, profile=learning

**Output**:
- Growth Team: **5.18** (APPROVE) ← Best mentorship balance
- Safe Bet: 5.18 (APPROVE)
- Speed Squad: 5.18 (APPROVE)

**Analysis**: Learning profile's 0.5x skill weight and 1.5x collaboration weight favor Growth Team's senior+junior mix.

---

## 6. Future Extensions

Potential enhancements to the framework:

1. **Dynamic weight learning** from historical project outcomes
2. **Custom profiles** allowing managers to define organization-specific contexts
3. **Multi-profile projects** that combine weights from multiple profiles
4. **Temporal adaptation** adjusting weights as project phases change

---

## 7. Conclusion

The Mission Profile Framework transforms team assembly from a one-size-fits-all approach into a **context-aware, adaptive system** that optimizes for specific project needs. By encoding organizational knowledge into 9 distinct profiles, SmartChimera provides intelligent, evidence-based team recommendations that balance multiple competing objectives.

**Key Innovation**: The framework proves that team assembly is not solely about skill matching—it requires understanding project context, organizational priorities, and historical collaboration patterns.
