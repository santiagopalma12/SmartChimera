import { FC } from 'react';
import { usePrivacy } from '@/context/PrivacyContext';
import { Eye, EyeOff } from 'lucide-react';
import { cn } from '@/utils/cn';

export const PrivacyToggle: FC = () => {
    const { isPrivacyMode, togglePrivacyMode } = usePrivacy();

    return (
        <div className="flex items-center gap-2">
            <div className={cn("text-sm font-medium transition-colors", isPrivacyMode ? "text-green-600" : "text-muted-foreground")}>
                {isPrivacyMode ? "Privacy ON" : "Privacy OFF"}
            </div>
            <button
                onClick={togglePrivacyMode}
                className={cn(
                    "relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background",
                    isPrivacyMode ? "bg-green-600" : "bg-input"
                )}
            >
                <span
                    className={cn(
                        "pointer-events-none block h-5 w-5 rounded-full bg-background shadow-lg ring-0 transition-transform",
                        isPrivacyMode ? "translate-x-5" : "translate-x-0.5"
                    )}
                >
                    <div className="flex h-full w-full items-center justify-center text-xs text-muted-foreground">
                        {isPrivacyMode ? <EyeOff className="h-3 w-3" /> : <Eye className="h-3 w-3" />}
                    </div>
                </span>
            </button>
        </div>
    );
};
