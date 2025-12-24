import { FC } from 'react';
import { Dossier } from '@/types/api';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import ExecutiveSummary from './ExecutiveSummary';
import TeamMemberCard from './TeamMemberCard';
import { Badge } from '@/components/ui/badge';
import { Droppable, Draggable } from '@hello-pangea/dnd';
import { cn } from '@/utils/cn';

interface DossierCardProps {
    dossier: Dossier;
    index: number;
    isEditMode?: boolean;
}

const DossierCard: FC<DossierCardProps> = ({ dossier, index, isEditMode = false }) => {
    return (
        <Card className={cn("h-full flex flex-col obys-card", isEditMode && "border-accent")}>
            <CardHeader className="pb-4 space-y-4">
                <div className="flex items-start justify-between gap-4">
                    <div className="space-y-3">
                        <div className="flex items-center gap-3">
                            <span className="text-xs font-bold text-muted-foreground tracking-wider">
                                0{index + 1}
                            </span>
                            <div className="h-px flex-1 bg-border"></div>
                        </div>
                        <CardTitle className="text-2xl font-bold uppercase tracking-tight">{dossier.title}</CardTitle>
                        <CardDescription className="text-sm leading-relaxed">{dossier.description}</CardDescription>
                    </div>
                    <div className="text-right flex-shrink-0">
                        <div className="text-4xl font-black tabular-nums text-accent">{dossier.total_score.toFixed(1)}</div>
                        <div className="text-[10px] font-medium text-muted-foreground uppercase tracking-widest mt-1">SCORE</div>
                    </div>
                </div>
            </CardHeader>

            <CardContent className="flex-1 space-y-8">
                {/* Executive Summary */}
                <ExecutiveSummary summary={dossier.executive_summary} />

                {/* Team Members */}
                <div>
                    <div className="flex items-center justify-between mb-4">
                        <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-widest">
                            Team Configuration
                        </h4>
                        {isEditMode && (
                            <span className="text-[10px] text-accent font-medium uppercase tracking-wider animate-pulse">
                                Drag · Reorder
                            </span>
                        )}
                    </div>

                    <Droppable droppableId={index.toString()} isDropDisabled={!isEditMode}>
                        {(provided, snapshot) => (
                            <div
                                {...provided.droppableProps}
                                ref={provided.innerRef}
                                className={cn(
                                    "grid gap-3 min-h-[100px] rounded-md transition-colors",
                                    snapshot.isDraggingOver && "bg-primary/10 p-2"
                                )}
                            >
                                {dossier.team.map((member, memberIndex) => (
                                    <Draggable
                                        key={member.id}
                                        draggableId={`${index}-${member.id}`}
                                        index={memberIndex}
                                        isDragDisabled={!isEditMode}
                                    >
                                        {(provided, snapshot) => (
                                            <div
                                                ref={provided.innerRef}
                                                {...provided.draggableProps}
                                                {...provided.dragHandleProps}
                                                style={{ ...provided.draggableProps.style }}
                                                className={cn(snapshot.isDragging && "opacity-50")}
                                            >
                                                <TeamMemberCard member={member} />
                                            </div>
                                        )}
                                    </Draggable>
                                ))}
                                {provided.placeholder}
                            </div>
                        )}
                    </Droppable>
                </div>

                {/* Rationale */}
                <div className="rounded-md bg-muted/50 p-3 text-xs text-muted-foreground italic">
                    "{dossier.rationale}"
                </div>
            </CardContent>
        </Card>
    );
};

export default DossierCard;
