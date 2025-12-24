import { useState, useEffect, FC } from 'react';
import { Input } from '@/components/ui/input';

interface SkillAutocompleteProps {
    value: string;
    onChange: (value: string) => void;
    onSelect: (skill: string) => void;
    placeholder?: string;
}

const SkillAutocomplete: FC<SkillAutocompleteProps> = ({ value, onChange, onSelect, placeholder }) => {
    const [skills, setSkills] = useState<string[]>([]);

    // Fetch skills from API on mount
    useEffect(() => {
        const fetchSkills = async () => {
            try {
                const response = await fetch('http://localhost:8000/api/skills');
                const data = await response.json();
                setSkills(data.skills || []);
            } catch (error) {
                console.error('Failed to fetch skills:', error);
                // Fallback to common skills
                setSkills(['Python', 'React', 'Docker', 'AWS', 'TypeScript', 'Node.js', 'PostgreSQL', 'Java', 'Kubernetes', 'Go']);
            }
        };
        fetchSkills();
    }, []);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const newValue = e.target.value;
        onChange(newValue);

        // Auto-select exact match
        const exactMatch = skills.find(s => s.toLowerCase() === newValue.toLowerCase());
        if (exactMatch && exactMatch !== newValue) {
            onSelect(exactMatch);
        }
    };

    return (
        <>
            <Input
                list="skills-datalist"
                placeholder={placeholder || 'Type skill (e.g. P → Python)'}
                value={value}
                onChange={handleChange}
                onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        const match = skills.find(s => s.toLowerCase().startsWith(value.toLowerCase()));
                        if (match) {
                            onSelect(match);
                        } else if (value.trim()) {
                            onSelect(value.trim());
                        }
                    }
                }}
            />
            <datalist id="skills-datalist">
                {skills
                    .filter(skill => skill.toLowerCase().includes(value.toLowerCase()))
                    .slice(0, 20)
                    .map((skill) => (
                        <option key={skill} value={skill} />
                    ))}
            </datalist>
        </>
    );
};

export default SkillAutocomplete;
