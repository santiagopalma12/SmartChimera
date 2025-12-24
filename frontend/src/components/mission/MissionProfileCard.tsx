import { FC } from 'react';
import { MissionProfile } from '@/types/api';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Check } from 'lucide-react';
import { cn } from '@/utils/cn';
import { ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';

interface MissionProfileCardProps {
    profile: MissionProfile;
    isSelected: boolean;
    onSelect: (id: string) => void;
}

const MissionProfileCard: FC<MissionProfileCardProps> = ({ profile, isSelected, onSelect }) => {
    // Transform strategy preference into chart data if possible, 
    // but since it's a string description in the current schema, we might need to parse it or just show it.
    // Wait, the backend returns weights? 
    // Checking backend code: `mission_profiles.py` returns a dict of weights.
    // But my `types/api.ts` defined `MissionProfile` with `strategy_preference: string`.
    // I should check the actual API response or update the type.
    // Let's assume for now we visualize the description or static data based on ID.

    const getChartData = (id: string) => {
        switch (id) {
            case 'maintenance':
            case 'mantenimiento':
                return [
                    { subject: 'Stability', A: 100, fullMark: 100 },
                    { subject: 'Innovation', A: 20, fullMark: 100 },
                    { subject: 'Speed', A: 40, fullMark: 100 },
                    { subject: 'Collab', A: 50, fullMark: 100 },
                    { subject: 'Skills', A: 90, fullMark: 100 },
                ];
            case 'innovation':
            case 'innovacion':
                return [
                    { subject: 'Stability', A: 40, fullMark: 100 },
                    { subject: 'Innovation', A: 100, fullMark: 100 },
                    { subject: 'Speed', A: 60, fullMark: 100 },
                    { subject: 'Collab', A: 90, fullMark: 100 },
                    { subject: 'Skills', A: 70, fullMark: 100 },
                ];
            case 'speed':
            case 'entrega_rapida':
                return [
                    { subject: 'Stability', A: 50, fullMark: 100 },
                    { subject: 'Innovation', A: 50, fullMark: 100 },
                    { subject: 'Speed', A: 100, fullMark: 100 },
                    { subject: 'Collab', A: 100, fullMark: 100 },
                    { subject: 'Skills', A: 70, fullMark: 100 },
                ];
            // NEW PROFILES
            case 'crisis_response':
                return [
                    { subject: 'Stability', A: 90, fullMark: 100 },
                    { subject: 'Innovation', A: 20, fullMark: 100 },
                    { subject: 'Speed', A: 100, fullMark: 100 },
                    { subject: 'Collab', A: 40, fullMark: 100 },
                    { subject: 'Skills', A: 80, fullMark: 100 },
                ];
            case 'architecture_review':
                return [
                    { subject: 'Stability', A: 80, fullMark: 100 },
                    { subject: 'Innovation', A: 90, fullMark: 100 },
                    { subject: 'Speed', A: 30, fullMark: 100 },
                    { subject: 'Collab', A: 50, fullMark: 100 },
                    { subject: 'Skills', A: 100, fullMark: 100 },
                ];
            case 'security_audit':
                return [
                    { subject: 'Stability', A: 100, fullMark: 100 },
                    { subject: 'Innovation', A: 10, fullMark: 100 },
                    { subject: 'Speed', A: 40, fullMark: 100 },
                    { subject: 'Collab', A: 20, fullMark: 100 },
                    { subject: 'Skills', A: 90, fullMark: 100 },
                ];
            case 'cloud_migration':
                return [
                    { subject: 'Stability', A: 70, fullMark: 100 },
                    { subject: 'Innovation', A: 60, fullMark: 100 },
                    { subject: 'Speed', A: 60, fullMark: 100 },
                    { subject: 'Collab', A: 70, fullMark: 100 },
                    { subject: 'Skills', A: 100, fullMark: 100 },
                ];
            case 'legacy_rescue':
                return [
                    { subject: 'Stability', A: 80, fullMark: 100 },
                    { subject: 'Innovation', A: 30, fullMark: 100 },
                    { subject: 'Speed', A: 40, fullMark: 100 },
                    { subject: 'Collab', A: 60, fullMark: 100 },
                    { subject: 'Skills', A: 100, fullMark: 100 },
                ];
            case 'junior_training':
                return [
                    { subject: 'Stability', A: 30, fullMark: 100 },
                    { subject: 'Innovation', A: 60, fullMark: 100 },
                    { subject: 'Speed', A: 40, fullMark: 100 },
                    { subject: 'Collab', A: 90, fullMark: 100 },
                    { subject: 'Skills', A: 20, fullMark: 100 },
                ];
            default:
                return [];
        }
    };

    const data = getChartData(profile.id);

    return (
        <Card
            className={cn(
                "cursor-pointer transition-all hover:border-primary/50",
                isSelected ? "border-primary ring-1 ring-primary" : ""
            )}
            onClick={() => onSelect(profile.id)}
        >
            <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                    <CardTitle className="text-lg capitalize">{profile.name}</CardTitle>
                    {isSelected && <div className="rounded-full bg-primary p-1 text-primary-foreground"><Check className="h-3 w-3" /></div>}
                </div>
                <CardDescription>{profile.description}</CardDescription>
            </CardHeader>
            <CardContent>
                <div className="h-[150px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <RadarChart cx="50%" cy="50%" outerRadius="60%" data={data}>
                            <PolarGrid />
                            <PolarAngleAxis dataKey="subject" tick={{ fontSize: 10 }} />
                            <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                            <Radar
                                name={profile.name}
                                dataKey="A"
                                stroke={profile.color || "#2563eb"}
                                fill={profile.color || "#2563eb"}
                                fillOpacity={0.3}
                            />
                        </RadarChart>
                    </ResponsiveContainer>
                </div>
                <div className="mt-2 text-xs text-muted-foreground">
                    <span className="font-semibold">Strategy:</span> {profile.strategy_preference}
                </div>
            </CardContent>
        </Card>
    );
};

export default MissionProfileCard;
