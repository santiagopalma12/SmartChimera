import { FC } from 'react';
import { ExecutiveSummary as IExecutiveSummary } from '@/types/api';
import { CheckCircle2, XCircle, AlertCircle } from 'lucide-react';
import { cn } from '@/utils/cn';
import { motion } from 'framer-motion';

interface ExecutiveSummaryProps {
    summary: IExecutiveSummary;
    score?: number;
}

const ExecutiveSummary: FC<ExecutiveSummaryProps> = ({ summary }) => {
    const statusColor: Record<string, string> = {
        APPROVE: 'text-green-600 bg-green-50 border-green-200',
        REVIEW: 'text-yellow-600 bg-yellow-50 border-yellow-200',
        REJECT: 'text-red-600 bg-red-50 border-red-200',
    };

    const StatusIcon = {
        APPROVE: CheckCircle2,
        REVIEW: AlertCircle,
        REJECT: XCircle,
    }[summary.recommendation] || AlertCircle;

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
            className="space-y-4 rounded-lg border bg-card p-4"
        >
            <div className={cn("flex items-center justify-between rounded-md border px-4 py-2", statusColor[summary.recommendation])}>
                <span className="font-semibold">Recommendation</span>
                <div className="flex items-center gap-2 font-bold">
                    <StatusIcon className="h-5 w-5" />
                    {summary.recommendation}
                </div>
            </div>

            <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                    <h4 className="mb-2 font-medium text-green-600 flex items-center">
                        <CheckCircle2 className="mr-1 h-4 w-4" /> Pros
                    </h4>
                    <ul className="space-y-1 text-muted-foreground">
                        {summary.pros.map((pro, i) => (
                            <li key={i} className="flex items-start">
                                <span className="mr-2">•</span> {pro}
                            </li>
                        ))}
                    </ul>
                </div>
                <div>
                    <h4 className="mb-2 font-medium text-red-600 flex items-center">
                        <XCircle className="mr-1 h-4 w-4" /> Cons
                    </h4>
                    <ul className="space-y-1 text-muted-foreground">
                        {summary.cons.map((con, i) => (
                            <li key={i} className="flex items-start">
                                <span className="mr-2">•</span> {con}
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
        </motion.div>
    );
};

export default ExecutiveSummary;
