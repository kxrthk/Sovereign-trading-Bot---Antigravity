import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';

export default function PerformanceModule() {
    const [equityData, setEquityData] = useState([]);
    const [monthlyData, setMonthlyData] = useState([]);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                // setLoading(true); // Don't flicker on refresh
                const res = await fetch('/api/performance');
                if (!res.ok) throw new Error(`Server Error: ${res.status}`);

                const data = await res.json();

                if (data.equity_curve) setEquityData(data.equity_curve);
                if (data.monthly_returns) setMonthlyData(data.monthly_returns);
                setError(null);
            } catch (err) {
                console.error("Failed to fetch performance data:", err);
                setError(err.message);
            } finally {
                setLoading(false);
            }
        }
        fetchData();
        const interval = setInterval(fetchData, 2000); // Poll every 5s
        return () => clearInterval(interval);
    }, []);

    if (error) {
        return (
            <div className="p-6 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-500 font-mono">
                DATA SYNC FAILURE: {error}
                <br /><span className="text-xs opacity-75">Check if dashboard_server.py is running.</span>
            </div>
        )
    }

    return (
        <div className="space-y-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
                PERFORMANCE ANALYTICS
                <span className="text-xs bg-emerald-500/10 text-emerald-600 dark:text-emerald-500 px-2 py-1 rounded border border-emerald-500/20 font-mono">LIVE SYNC_</span>
            </h2>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

                {/* Equity Curve */}
                <div className="p-6 rounded-2xl bg-white dark:bg-white/5 border border-gray-200 dark:border-white/10 backdrop-blur-xl">
                    <h3 className="text-sm font-mono text-gray-500 dark:text-zinc-400 mb-6 uppercase tracking-widest">Equity Curve (INR)</h3>
                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={equityData}>
                                <defs>
                                    <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#555" vertical={false} opacity={0.3} />
                                <XAxis dataKey="name" stroke="#888" fontSize={12} tickLine={false} axisLine={false} />
                                <YAxis stroke="#888" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `₹${value / 1000}k`} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#09090b', borderColor: '#333' }}
                                    itemStyle={{ color: '#10b981' }}
                                />
                                <Area type="monotone" dataKey="value" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#colorValue)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Monthly Returns */}
                <div className="p-6 rounded-2xl bg-white dark:bg-white/5 border border-gray-200 dark:border-white/10 backdrop-blur-xl">
                    <h3 className="text-sm font-mono text-gray-500 dark:text-zinc-400 mb-6 uppercase tracking-widest">Monthly Returns</h3>
                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={monthlyData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#555" vertical={false} opacity={0.3} />
                                <XAxis dataKey="name" stroke="#888" fontSize={12} tickLine={false} axisLine={false} />
                                <YAxis stroke="#888" fontSize={12} tickLine={false} axisLine={false} />
                                <Tooltip cursor={{ fill: 'rgba(255,255,255,0.05)' }} contentStyle={{ backgroundColor: '#09090b', borderColor: '#333' }} />
                                <Bar dataKey="pnl" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

            </div>
        </div>
    )
}
