export interface Candidate {
    id: string;
    skills_matched: string[];
    score: number;
    availability_hours?: number;
    conflict_risk: boolean;
    linchpin_risk?: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
}

export interface ExecutiveSummary {
    pros: string[];
    cons: string[];
    recommendation: 'APPROVE' | 'REVIEW' | 'REJECT';
}

export interface Dossier {
    title: string;
    description: string;
    executive_summary: ExecutiveSummary;
    team: Candidate[];
    total_score: number;
    risk_analysis: string[];
    rationale: string;
}

export interface TeamRequest {
    requisitos_hard: { skills: string[] };
    k: number;
    mission_profile?: string;
    formation_mode?: 'resilient' | 'performance';
    week?: string;
    min_hours?: number;
    force_include?: string[];
    force_exclude?: string[];
}

export interface MissionProfile {
    id: string;
    name: string;
    description: string;
    strategy_preference: string;
    color: string;
}

export interface LinchpinEmployee {
    id: string;
    centrality_score: number;
    unique_skills: string[];
    risk_level: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
    recommendation: string;
}

export interface Employee {
    id: string;
    nombre?: string;
    rol?: string;
}
