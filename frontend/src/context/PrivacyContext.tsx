import { createContext, useContext, useState, ReactNode, FC } from 'react';

interface PrivacyContextType {
    isPrivacyMode: boolean;
    togglePrivacyMode: () => void;
}

const PrivacyContext = createContext<PrivacyContextType | undefined>(undefined);

export const PrivacyProvider: FC<{ children: ReactNode }> = ({ children }) => {
    const [isPrivacyMode, setIsPrivacyMode] = useState(false);

    const togglePrivacyMode = () => {
        setIsPrivacyMode(prev => !prev);
    };

    return (
        <PrivacyContext.Provider value={{ isPrivacyMode, togglePrivacyMode }}>
            {children}
        </PrivacyContext.Provider>
    );
};

export const usePrivacy = () => {
    const context = useContext(PrivacyContext);
    if (context === undefined) {
        throw new Error('usePrivacy must be used within a PrivacyProvider');
    }
    return context;
};
