import { FC, useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { getLinchpins } from '@/services/api';
import { AlertTriangle, ShieldAlert, Info } from 'lucide-react';

interface Linchpin {
    id: string;
    name: string; // Added Name
    centrality_score: number;
    unique_skills: string[];
    project_count: number; // Added Project Count
    risk_level: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
    recommendation: string;
}

const Linchpins: FC = () => {
    const [linchpins, setLinchpins] = useState<Linchpin[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const data = await getLinchpins();
                setLinchpins(data);
            } catch (error) {
                console.error("Failed to fetch linchpins", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    const getRiskColor = (level: string) => {
        switch (level) {
            case 'CRITICAL': return 'bg-red-500/15 text-red-500 border-red-500/20';
            case 'HIGH': return 'bg-orange-500/15 text-orange-500 border-orange-500/20';
            case 'MEDIUM': return 'bg-yellow-500/15 text-yellow-500 border-yellow-500/20';
            default: return 'bg-blue-500/15 text-blue-500 border-blue-500/20';
        }
    };

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-3xl font-bold tracking-tight">Linchpin Analysis</h2>
                <p className="text-muted-foreground">
                    Identify critical employees with high "Bus Factor" risk.
                </p>
            </div>

            {loading ? (
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                    {[1, 2, 3].map((i) => (
                        <div key={i} className="h-[200px] w-full animate-pulse rounded-lg bg-muted" />
                    ))}
                </div>
            ) : (
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                    {linchpins.length === 0 ? (
                        <div className="col-span-full flex h-[200px] items-center justify-center rounded-lg border border-dashed bg-muted/50">
                            <div className="flex flex-col items-center text-center text-muted-foreground">
                                <ShieldAlert className="h-8 w-8 mb-2 opacity-50" />
                                <p>No critical linchpins detected.</p>
                                <p className="text-sm">Your team knowledge distribution is healthy.</p>
                            </div>
                        </div>
                    ) : (
                        linchpins.map((employee) => (
                            <Card key={employee.id} className="border-slate-700 bg-slate-800/50">
                                <CardHeader className="pb-2">
                                    <div className="flex items-start justify-between">
                                        <div>
                                            <CardTitle className="text-lg font-semibold text-white">
                                                {employee.name || employee.id}
                                            </CardTitle>
                                            <CardDescription className="text-xs font-mono mt-1 text-slate-400">
                                                ID: {employee.id} • Score: {(employee.centrality_score || 0).toFixed(3)}
                                            </CardDescription>
                                        </div>
                                        <Badge variant="outline" className={getRiskColor(employee.risk_level)}>
                                            {employee.risk_level} RISK
                                        </Badge>
                                    </div>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    {/* Valid Project Weight Section */}
                                    {(employee.project_count || 0) > 5 && (
                                        <div className="rounded-md bg-purple-500/10 p-2 border border-purple-500/20">
                                            <p className="text-xs font-semibold text-purple-400 uppercase tracking-wider mb-1">
                                                Project Weight
                                            </p>
                                            <p className="text-sm text-slate-200">
                                                Critical contributor in <span className="font-bold text-white">{employee.project_count}</span> projects.
                                            </p>
                                        </div>
                                    )}

                                    {(employee.unique_skills || []).length > 0 && (
                                        <div className="space-y-2">
                                            <div className="text-xs font-medium text-slate-400 uppercase tracking-wider flex items-center gap-1">
                                                <AlertTriangle className="h-3 w-3 text-yellow-500" />
                                                Unique Knowledge
                                            </div>
                                            <div className="flex flex-wrap gap-1">
                                                {employee.unique_skills.map(skill => (
                                                    <Badge key={skill} variant="secondary" className="text-[10px] px-1.5 py-0 h-5 bg-yellow-500/10 text-yellow-500 hover:bg-yellow-500/20">
                                                        {skill}
                                                    </Badge>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    <div className="rounded-md bg-slate-900/50 p-3 text-sm text-slate-300 border border-slate-700/50">
                                        <div className="flex items-start gap-2">
                                            <Info className="h-4 w-4 mt-0.5 text-blue-400 shrink-0" />
                                            {employee.recommendation}
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        ))
                    )}
                </div>
            )}
        </div>
    );
};

export default Linchpins;
