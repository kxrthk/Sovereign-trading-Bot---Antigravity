import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';

export default function PerformanceModule() {
    const [equityData, setEquityData] = useState([]);
    const [monthlyData, setMonthlyData] = useState([]);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await fetch('http://localhost:8000/api/performance');
                const data = await res.json();

                if (data.equity_curve) setEquityData(data.equity_curve);
                if (data.monthly_returns) setMonthlyData(data.monthly_returns);
            } catch (error) {
                console.error("Failed to fetch performance data:", error);
            }
        }
        fetchData();
        const interval = setInterval(fetchData, 5000); // Poll every 5s
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="space-y-8">
            <h2 className="text-2xl font-bold text-white flex items-center gap-3">
                PERFORMANCE ANALYTICS
                <span className="text-xs bg-emerald-500/10 text-emerald-500 px-2 py-1 rounded border border-emerald-500/20 font-mono">LIVE SYNC_</span>
            </h2>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

                {/* Equity Curve */}
                <div className="p-6 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl">
                    <h3 className="text-sm font-mono text-zinc-400 mb-6 uppercase tracking-widest">Equity Curve (INR)</h3>
                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={equityData}>
                                <defs>
                                    <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
                                <XAxis dataKey="name" stroke="#666" fontSize={12} tickLine={false} axisLine={false} />
                                <YAxis stroke="#666" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `₹${value / 1000}k`} />
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
                <div className="p-6 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl">
                    <h3 className="text-sm font-mono text-zinc-400 mb-6 uppercase tracking-widest">Monthly Returns</h3>
                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={monthlyData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
                                <XAxis dataKey="name" stroke="#666" fontSize={12} tickLine={false} axisLine={false} />
                                <YAxis stroke="#666" fontSize={12} tickLine={false} axisLine={false} />
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
