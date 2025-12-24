import { useEffect, useState, FC } from 'react';
import { getMissionProfiles } from '@/services/api';
import { MissionProfile } from '@/types/api';
import MissionProfileCard from './MissionProfileCard';
import { Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';

interface MissionSelectorProps {
    selectedProfileId: string;
    onSelect: (id: string) => void;
}

const MissionSelector: FC<MissionSelectorProps> = ({ selectedProfileId, onSelect }) => {
    const [profiles, setProfiles] = useState<MissionProfile[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchProfiles = async () => {
            try {
                const data = await getMissionProfiles();
                // Colors are now provided by API, fallback if needed
                const enhancedData = data.map((p: any) => ({
                    ...p,
                    color: p.color || '#6366f1'  // Default fallback color
                })) as MissionProfile[];
                setProfiles(enhancedData);
            } catch (error) {
                console.error("Failed to fetch mission profiles", error);
            } finally {
                setIsLoading(false);
            }
        };
        fetchProfiles();
    }, []);

    if (isLoading) {
        return <div className="flex justify-center p-4"><Loader2 className="h-6 w-6 animate-spin text-primary" /></div>;
    }

    const container = {
        hidden: { opacity: 0 },
        show: {
            opacity: 1,
            transition: {
                staggerChildren: 0.1
            }
        }
    };

    const item = {
        hidden: { opacity: 0, y: 20 },
        show: { opacity: 1, y: 0 }
    };

    return (
        <motion.div
            className="grid gap-4 sm:grid-cols-3"
            variants={container}
            initial="hidden"
            animate="show"
        >
            {profiles.map((profile) => (
                <motion.div key={profile.id} variants={item}>
                    <MissionProfileCard
                        profile={profile}
                        isSelected={selectedProfileId === profile.id}
                        onSelect={onSelect}
                    />
                </motion.div>
            ))}
        </motion.div>
    );
};

export default MissionSelector;
