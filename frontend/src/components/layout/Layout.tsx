import { FC, ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Users, Network, Shield } from 'lucide-react';
import { cn } from '@/utils/cn';

interface LayoutProps {
    children: ReactNode;
}

const Layout: FC<LayoutProps> = ({ children }) => {
    const location = useLocation();

    const navItems = [
        { name: 'Dashboard', path: '/', icon: LayoutDashboard },
        { name: 'Recommend', path: '/recommend', icon: Users },
        { name: 'Graph Explorer', path: '/graph', icon: Network },
        { name: 'Linchpins', path: '/linchpins', icon: Shield },
    ];

    return (
        <div className="min-h-screen bg-background">
            {/* OBYS-style Minimal Sidebar */}
            <aside className="fixed left-0 top-0 z-50 h-screen w-20 border-r border-border bg-background">
                <div className="flex h-20 items-center justify-center border-b border-border">
                    <div className="w-10 h-10 rounded-sm bg-accent flex items-center justify-center">
                        <span className="text-xl font-black text-background">SC</span>
                    </div>
                </div>
                <nav className="flex flex-col items-center py-8 gap-6">
                    {navItems.map((item) => {
                        const Icon = item.icon;
                        const isActive = location.pathname === item.path;
                        return (
                            <Link
                                key={item.path}
                                to={item.path}
                                className={cn(
                                    "group relative flex h-12 w-12 items-center justify-center rounded-sm transition-all duration-300",
                                    isActive
                                        ? "bg-accent text-background"
                                        : "text-muted-foreground hover:bg-card hover:text-foreground"
                                )}
                                title={item.name}
                            >
                                <Icon className="h-5 w-5" />
                                {/* Tooltip */}
                                <span className="absolute left-20 whitespace-nowrap rounded-sm bg-card px-3 py-2 text-sm font-medium opacity-0 transition-opacity group-hover:opacity-100 pointer-events-none border border-border">
                                    {item.name}
                                </span>
                            </Link>
                        );
                    })}
                </nav>
                <div className="absolute bottom-6 left-0 w-full flex justify-center">
                    <div className="w-2 h-2 rounded-full bg-accent animate-pulse"></div>
                </div>
            </aside>

            {/* Main Content - Full Width with Sidebar Offset */}
            <main className="ml-20 min-h-screen bg-background">
                {children}
            </main>
        </div>
    );
};

export default Layout;
