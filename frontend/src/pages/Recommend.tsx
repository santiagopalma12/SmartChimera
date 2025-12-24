import { useState } from 'react';
import RequirementsForm from '@/components/dossier/RequirementsForm';
import DossierCard from '@/components/dossier/DossierCard';
import { recommendTeams } from '@/services/api';
import { TeamRequest, Dossier } from '@/types/api';
import { AlertCircle, Edit2, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { DragDropContext, DropResult } from '@hello-pangea/dnd';
import ComparisonChart from '@/components/dossier/ComparisonChart';

const Recommend = () => {
    const [dossiers, setDossiers] = useState<Dossier[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [isEditMode, setIsEditMode] = useState(false);

    const handleRecommend = async (request: TeamRequest) => {
        setIsLoading(true);
        setError(null);
        try {
            const results = await recommendTeams(request);
            setDossiers(results);
        } catch (err) {
            console.error(err);
            setError('Failed to generate recommendations. Please check the backend connection.');
        } finally {
            setIsLoading(false);
        }
    };

    const onDragEnd = (result: DropResult) => {
        const { source, destination } = result;

        // Dropped outside the list
        if (!destination) {
            return;
        }

        // Dropped in the same place
        if (
            source.droppableId === destination.droppableId &&
            source.index === destination.index
        ) {
            return;
        }

        // Create deep copy of dossiers
        const newDossiers = [...dossiers];
        const sourceDossierIndex = parseInt(source.droppableId);
        const destDossierIndex = parseInt(destination.droppableId);

        const sourceDossier = newDossiers[sourceDossierIndex];
        const destDossier = newDossiers[destDossierIndex];

        const sourceTeam = [...sourceDossier.team];
        const destTeam = sourceDossierIndex === destDossierIndex ? sourceTeam : [...destDossier.team];

        // Remove from source
        const [removed] = sourceTeam.splice(source.index, 1);

        // Add to destination
        destTeam.splice(destination.index, 0, removed);

        // Update dossiers
        newDossiers[sourceDossierIndex] = { ...sourceDossier, team: sourceTeam };
        if (sourceDossierIndex !== destDossierIndex) {
            newDossiers[destDossierIndex] = { ...destDossier, team: destTeam };
        }

        // Mark as modified (optional: recalculate score logic here)
        // For now, we just update the state
        setDossiers(newDossiers);
    };

    return (
        <div className="min-h-screen">
            {/* OBYS-style Hero Section */}
            <div className="obys-container">
                <div className="flex flex-col gap-12 obys-fade-in">
                    <div className="flex items-start justify-between">
                        <div className="space-y-6 max-w-4xl">
                            <h1 className="obys-hero-text obys-gradient-text">
                                SMART CHIMERA
                            </h1>
                            <h2 className="text-2xl md:text-4xl font-light tracking-wide text-muted-foreground uppercase">
                                Team Assembly / Bus Factor Mitigation
                            </h2>
                            <p className="text-lg text-muted-foreground max-w-2xl leading-relaxed">
                                Define requirements. Guardian analyzes collaboration graphs.
                                Optimal teams emerge. Risk minimized.
                            </p>
                        </div>
                        {dossiers.length > 0 && (
                            <Button
                                variant={isEditMode ? "default" : "outline"}
                                onClick={() => setIsEditMode(!isEditMode)}
                                className="obys-button gap-2"
                            >
                                {isEditMode ? <Check className="h-4 w-4" /> : <Edit2 className="h-4 w-4" />}
                                {isEditMode ? 'DONE' : 'EDIT'}
                            </Button>
                        )}
                    </div>
                    <div className="obys-divider"></div>
                </div>
            </div>

            {/* Main Content Section */}
            <div className="obys-container">
                <div className="space-y-12">
                    {/* Requirements Section - Full Width */}
                    <div className="space-y-8">
                        <div>
                            <h3 className="text-xl font-bold uppercase tracking-wide mb-2">
                                01 / Requirements
                            </h3>
                            <p className="text-sm text-muted-foreground">
                                Define project needs
                            </p>
                        </div>
                        <div className="max-w-4xl">
                            <RequirementsForm onSubmit={handleRecommend} isLoading={isLoading} />
                        </div>

                        {error && (
                            <div className="obys-card border-destructive bg-destructive/10 p-6 max-w-4xl">
                                <div className="flex items-start gap-3">
                                    <AlertCircle className="h-5 w-5 text-destructive flex-shrink-0 mt-0.5" />
                                    <div className="space-y-1">
                                        <p className="text-sm font-medium text-destructive">Error</p>
                                        <p className="text-sm text-destructive/90">{error}</p>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>

                    <div className="obys-divider"></div>

                    {/* Results Section - Full Width */}
                    <div className="space-y-12">
                        <div>
                            <h3 className="text-xl font-bold uppercase tracking-wide mb-2">
                                02 / Generated Teams
                            </h3>
                            <p className="text-sm text-muted-foreground">
                                Mission-Critical team configurations based on mission profile
                            </p>
                        </div>

                        {dossiers.length === 0 && !isLoading && !error && (
                            <div className="flex h-[500px] items-center justify-center obys-card">
                                <div className="text-center space-y-4 p-12">
                                    <div className="w-24 h-24 mx-auto rounded-full bg-muted/50 flex items-center justify-center">
                                        <span className="text-4xl">⚡</span>
                                    </div>
                                    <div className="space-y-2">
                                        <p className="text-xl font-medium">Ready to Generate Teams</p>
                                        <p className="text-sm text-muted-foreground max-w-sm mx-auto">
                                            Submit requirements on the left. Guardian will analyze collaboration networks and propose optimal team configurations.
                                        </p>
                                    </div>
                                </div>
                            </div>
                        )}

                        {isLoading && (
                            <div className="obys-grid">
                                {[1, 2, 3].map((i) => (
                                    <div key={i} className="h-[650px] w-full animate-pulse obys-card bg-muted/30" />
                                ))}
                            </div>
                        )}

                        {dossiers.length > 0 && (
                            <div className="space-y-12">
                                <ComparisonChart dossiers={dossiers} />
                                <DragDropContext onDragEnd={onDragEnd}>
                                    <div className="obys-grid">
                                        {dossiers.map((dossier, index) => (
                                            <DossierCard
                                                key={index}
                                                dossier={dossier}
                                                index={index}
                                                isEditMode={isEditMode}
                                            />
                                        ))}
                                    </div>
                                </DragDropContext>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Recommend;
