import { FC } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Candidate } from '@/types/api';
import { User, Clock, AlertTriangle, ShieldAlert } from 'lucide-react';
import { usePrivacy } from '@/context/PrivacyContext';

interface TeamMemberCardProps {
    member: Candidate;
}

const TeamMemberCard: FC<TeamMemberCardProps> = ({ member }) => {
    const { isPrivacyMode } = usePrivacy();

    return (
        <Card>
            <CardContent className="p-4">
                <div className="flex items-center gap-3 mb-3">
                    <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                        <User className="h-5 w-5 text-primary" />
                    </div>
                    <div className="flex-1">
                        <h4 className="font-semibold text-sm">
                            {isPrivacyMode ? `Candidate ${member.id.substring(0, 4)}` : member.id}
                        </h4>
                        <div className="flex items-center text-xs text-muted-foreground">
                            <Clock className="mr-1 h-3 w-3" />
                            {member.availability_hours || 0}h / week
                        </div>
                    </div>
                    <div className="text-right">
                        <span className="text-lg font-bold text-primary">{member.score.toFixed(1)}</span>
                        <div className="text-[10px] text-muted-foreground">SCORE</div>
                    </div>
                </div>

                <div className="mt-3 space-y-2">
                    {/* Skills */}
                    <div className="flex flex-wrap gap-1">
                        {member.skills_matched.slice(0, 3).map(skill => (
                            <Badge key={skill} variant="secondary" className="text-[10px] px-1.5 py-0">
                                {skill}
                            </Badge>
                        ))}
                        {member.skills_matched.length > 3 && (
                            <Badge variant="outline" className="text-[10px] px-1.5 py-0">
                                +{member.skills_matched.length - 3}
                            </Badge>
                        )}
                    </div>

                    {/* Risks */}
                    <div className="flex gap-2 pt-1">
                        {member.conflict_risk && (
                            <Badge variant="destructive" className="text-[10px] px-1.5 py-0">
                                <AlertTriangle className="mr-1 h-3 w-3" /> Conflict
                            </Badge>
                        )}
                        {member.linchpin_risk && (
                            <Badge
                                variant={member.linchpin_risk.toLowerCase() as any}
                                className="text-[10px] px-1.5 py-0"
                            >
                                <ShieldAlert className="mr-1 h-3 w-3" /> {member.linchpin_risk} Risk
                            </Badge>
                        )}
                    </div>
                </div>
            </CardContent>
        </Card>
    );
};

export default TeamMemberCard;
