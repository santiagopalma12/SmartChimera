import { FC } from 'react';
import { Dossier } from '@/types/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface ComparisonChartProps {
    dossiers: Dossier[];
}

const ComparisonChart: FC<ComparisonChartProps> = ({ dossiers }) => {
    const data = dossiers.map((d, i) => ({
        name: `Option ${i + 1}`,
        score: d.total_score,
        title: d.title,
    }));

    const colors = ['#2563eb', '#7c3aed', '#f59e0b']; // Blue, Purple, Amber

    return (
        <Card>
            <CardHeader>
                <CardTitle>Score Comparison</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="h-[300px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} />
                            <XAxis dataKey="name" />
                            <YAxis domain={[0, 5]} />
                            <Tooltip
                                cursor={{ fill: 'transparent' }}
                                content={({ active, payload }) => {
                                    if (active && payload && payload.length) {
                                        const data = payload[0].payload;
                                        return (
                                            <div className="rounded-lg border bg-background p-2 shadow-sm">
                                                <div className="font-bold">{data.name}</div>
                                                <div className="text-xs text-muted-foreground">{data.title}</div>
                                                <div className="font-mono text-primary">Score: {data.score.toFixed(2)}</div>
                                            </div>
                                        );
                                    }
                                    return null;
                                }}
                            />
                            <Bar dataKey="score" radius={[4, 4, 0, 0]}>
                                {data.map((_, index) => (
                                    <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </CardContent>
        </Card>
    );
};

export default ComparisonChart;
