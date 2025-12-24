import { FC, useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { getEmployees } from '@/services/api';

interface Employee {
    id: string;
    nombre: string;
    rol: string;
}

const Dashboard: FC = () => {
    const [employees, setEmployees] = useState<Employee[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const data = await getEmployees();
                setEmployees(data);
            } catch (error) {
                console.error("Failed to fetch dashboard data", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    return (
        <div className="space-y-6">
            <h1 className="text-3xl font-bold tracking-tight text-white">Dashboard</h1>

            <div className="grid gap-4 md:grid-cols-3">
                <Card className="bg-slate-800 border-slate-700">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">
                            Total Employees
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-white">{loading ? '...' : employees.length}</div>
                        <p className="text-xs text-slate-400">Active in database</p>
                    </CardContent>
                </Card>

                <Card className="bg-slate-800 border-slate-700">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium text-slate-200">
                            System Status
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-green-400">Operational</div>
                        <p className="text-xs text-slate-400">Backend & Database connected</p>
                    </CardContent>
                </Card>
            </div>

            <div className="grid gap-4 md:grid-cols-1">
                <Card className="bg-slate-800 border-slate-700">
                    <CardHeader>
                        <CardTitle className="text-slate-200">Recent Employees</CardTitle>
                    </CardHeader>
                    <CardContent>
                        {loading ? (
                            <div className="text-slate-400">Loading...</div>
                        ) : (
                            <div className="space-y-4">
                                {employees.slice(0, 5).map((emp) => (
                                    <div key={emp.id} className="flex items-center justify-between border-b border-slate-700 pb-2 last:border-0">
                                        <div>
                                            <p className="font-medium text-white">{emp.nombre}</p>
                                            <p className="text-sm text-slate-400">{emp.rol}</p>
                                        </div>
                                        <div className="text-sm text-slate-500">{emp.id}</div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    );
};

export default Dashboard;
