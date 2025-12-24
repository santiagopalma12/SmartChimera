import { useState, FC, FormEvent } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { TeamRequest } from '@/types/api';
import { Search, Plus, X, Loader2 } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import SkillAutocomplete from '@/components/dossier/SkillAutocomplete';
import MissionSelector from '@/components/mission/MissionSelector';

interface RequirementsFormProps {
    onSubmit: (request: TeamRequest) => void;
    isLoading?: boolean;
}

const RequirementsForm: FC<RequirementsFormProps> = ({ onSubmit, isLoading }) => {
    const [skills, setSkills] = useState<string[]>([]);
    const [currentSkill, setCurrentSkill] = useState('');
    const [teamSize, setTeamSize] = useState(3);
    const [missionProfile, setMissionProfile] = useState('mantenimiento');
    const [minHours, setMinHours] = useState(20);

    const handleAddSkill = () => {
        if (currentSkill.trim() && !skills.includes(currentSkill.trim())) {
            setSkills([...skills, currentSkill.trim()]);
            setCurrentSkill('');
        }
    };

    const handleRemoveSkill = (skill: string) => {
        setSkills(skills.filter(s => s !== skill));
    };

    const handleSubmit = (e: FormEvent) => {
        e.preventDefault();
        if (skills.length === 0) {
            alert('Please add at least one skill');
            return;
        }
        onSubmit({
            requisitos_hard: { skills: skills },
            k: teamSize,
            mission_profile: missionProfile,
            min_hours: minHours,
            force_include: [],
            force_exclude: []
        });
    };

    return (
        <Card className="w-full">
            <CardHeader>
                <CardTitle>Team Requirements</CardTitle>
            </CardHeader>
            <CardContent>
                <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Mission Profile Selector */}
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Mission Profile</label>
                        <MissionSelector
                            selectedProfileId={missionProfile}
                            onSelect={setMissionProfile}
                        />
                    </div>

                    {/* Skills Input */}
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Required Skills</label>
                        <div className="flex gap-2">
                            <SkillAutocomplete
                                value={currentSkill}
                                onChange={setCurrentSkill}
                                onSelect={(skill) => {
                                    if (!skills.includes(skill)) {
                                        setSkills([...skills, skill]);
                                    }
                                }}
                                placeholder="Type to search skills (e.g. P → Python)"
                            />
                            <Button type="button" onClick={handleAddSkill} variant="secondary">
                                <Plus className="h-4 w-4" />
                            </Button>
                        </div>
                        <div className="flex flex-wrap gap-2 mt-2">
                            {skills.map(skill => (
                                <Badge key={skill} variant="secondary" className="px-3 py-1">
                                    {skill}
                                    <button
                                        type="button"
                                        onClick={() => handleRemoveSkill(skill)}
                                        className="ml-2 hover:text-destructive"
                                    >
                                        <X className="h-3 w-3" />
                                    </button>
                                </Badge>
                            ))}
                        </div>
                    </div>

                    {/* Team Size & Hours */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Team Size (k)</label>
                            <Input
                                type="number"
                                min={1}
                                max={10}
                                value={teamSize}
                                onChange={(e) => setTeamSize(parseInt(e.target.value))}
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Min. Hours/Week</label>
                            <Input
                                type="number"
                                min={0}
                                max={40}
                                value={minHours}
                                onChange={(e) => setMinHours(parseInt(e.target.value))}
                            />
                        </div>
                    </div>

                    <Button type="submit" disabled={isLoading} className="w-full">
                        {isLoading ? (
                            <>
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                Generating Recommendations...
                            </>
                        ) : (
                            <>
                                <Search className="mr-2 h-4 w-4" />
                                Find Optimal Team
                            </>
                        )}
                    </Button>
                </form>
            </CardContent>
        </Card>
    );
};

export default RequirementsForm;
