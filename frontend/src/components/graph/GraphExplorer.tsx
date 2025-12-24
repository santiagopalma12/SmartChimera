import { useEffect, useRef, useState, FC } from 'react';
import * as d3 from 'd3';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import api from '@/services/api';
import { cn } from '@/utils/cn';

interface GraphNode extends d3.SimulationNodeDatum {
    id: string;
    labels: string[];
    properties: any;
}

interface GraphLink extends d3.SimulationLinkDatum<GraphNode> {
    type: string;
    properties: any;
}

const GraphExplorer: FC = () => {
    const svgRef = useRef<SVGSVGElement>(null);
    const [data, setData] = useState<{ nodes: GraphNode[], links: GraphLink[] } | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    // zoomLevel removed as it was unused

    const fetchGraph = async () => {
        setIsLoading(true);
        try {
            const response = await api.get('/api/graph');
            setData(response.data);
        } catch (error) {
            console.error("Failed to fetch graph data", error);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchGraph();
    }, []);

    useEffect(() => {
        if (!data || !svgRef.current) return;

        const width = 800;
        const height = 600;

        // Clear previous SVG content
        d3.select(svgRef.current).selectAll("*").remove();

        const svg = d3.select(svgRef.current)
            .attr("viewBox", [0, 0, width, height])
            .attr("width", "100%")
            .attr("height", "100%");

        // Add zoom behavior
        const g = svg.append("g");
        const zoom = d3.zoom<SVGSVGElement, unknown>()
            .scaleExtent([0.1, 4])
            .on("zoom", (event) => {
                g.attr("transform", event.transform);
            });

        svg.call(zoom);

        // Simulation setup
        const simulation = d3.forceSimulation<GraphNode>(data.nodes)
            .force("link", d3.forceLink<GraphNode, GraphLink>(data.links).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collide", d3.forceCollide(30));

        // Render links
        const link = g.append("g")
            .attr("stroke", "#52525b")
            .attr("stroke-opacity", 0.5)
            .selectAll("line")
            .data(data.links)
            .join("line")
            .attr("stroke-width", d => Math.sqrt(d.properties.weight || 1));

        // Render nodes
        const node = g.append("g")
            .attr("stroke", "#18181b")
            .attr("stroke-width", 2)
            .selectAll("circle")
            .data(data.nodes)
            .join("circle")
            .attr("r", d => (d.labels.includes('Employee') || d.labels.includes('Empleado')) ? 10 : 6)
            .attr("fill", d => (d.labels.includes('Employee') || d.labels.includes('Empleado')) ? "#34D399" : "#3b82f6") // Accent green for Employee, Blue for Skill
            .call(d3.drag<any, any>()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));

        // Add labels
        const labels = g.append("g")
            .selectAll("text")
            .data(data.nodes)
            .join("text")
            .text(d => d.id)
            .attr("font-size", 11)
            .attr("dx", 12)
            .attr("dy", 4)
            .attr("fill", "#e4e4e7")
            .attr("font-weight", 500);

        node.append("title")
            .text(d => `${d.id}\n${d.labels.join(", ")}`);

        // Simulation tick
        simulation.on("tick", () => {
            link
                .attr("x1", d => (d.source as GraphNode).x!)
                .attr("y1", d => (d.source as GraphNode).y!)
                .attr("x2", d => (d.target as GraphNode).x!)
                .attr("y2", d => (d.target as GraphNode).y!);

            node
                .attr("cx", d => d.x!)
                .attr("cy", d => d.y!);

            labels
                .attr("x", d => d.x!)
                .attr("y", d => d.y!);
        });

        function dragstarted(event: any) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }

        function dragged(event: any) {
            event.subject.fx = event.x;
            event.subject.fy = event.y;
        }

        function dragended(event: any) {
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }

        return () => {
            simulation.stop();
        };
    }, [data]);

    return (
        <Card className="h-full">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle>Graph Explorer</CardTitle>
                <div className="flex gap-2">
                    <Button variant="outline" size="icon" onClick={fetchGraph} disabled={isLoading}>
                        <RefreshCw className={cn("h-4 w-4", isLoading && "animate-spin")} />
                    </Button>
                </div>
            </CardHeader>
            <CardContent className="p-0 relative h-[600px] bg-zinc-900 overflow-hidden rounded-b-lg">
                {isLoading && !data && (
                    <div className="absolute inset-0 flex items-center justify-center bg-zinc-900/80 z-10">
                        <Loader2 className="h-8 w-8 animate-spin text-accent" />
                    </div>
                )}
                <svg ref={svgRef} className="w-full h-full cursor-move"></svg>

                <div className="absolute bottom-4 right-4 flex flex-col gap-2 bg-black/80 backdrop-blur-sm p-3 rounded-md shadow-lg border border-zinc-800">
                    <div className="flex items-center gap-2 text-xs text-zinc-300">
                        <span className="w-3 h-3 rounded-full bg-accent"></span> Employee
                    </div>
                    <div className="flex items-center gap-2 text-xs text-zinc-300">
                        <span className="w-3 h-3 rounded-full bg-blue-500"></span> Skill
                    </div>
                </div>
            </CardContent>
        </Card>
    );
};

export default GraphExplorer;
