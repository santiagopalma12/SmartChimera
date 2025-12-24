
import GraphExplorer from '@/components/graph/GraphExplorer';

const GraphPage = () => {
    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-3xl font-bold tracking-tight">Knowledge Graph</h2>
                <p className="text-muted-foreground">
                    Explore the relationships between employees, skills, and projects in the Neo4j database.
                </p>
            </div>
            <GraphExplorer />
        </div>
    );
};

export default GraphPage;
