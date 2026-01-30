import React, { useState, useEffect } from 'react';
import { ClipboardList, TrendingUp, AlertTriangle, ShieldCheck } from 'lucide-react';
import HolographicCard from './ui/HolographicCard';

export default function DailyPulse() {
    const [report, setReport] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch('/api/daily-pulse')
            .then(res => res.json())
            .then(data => {
                if (data && !data.error) {
                    setReport(data);
                } else {
                    console.error("Daily Pulse Error:", data);
                    setReport({ error: true });
                }
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setLoading(false);
            });
    }, []);

    if (loading) return <div className="text-white p-10 animate-pulse">Scanning Trading Journal...</div>;
    if (!report || report.error) return <div className="text-red-400 p-10">System Offline or No Data.</div>;

    const getGradeColor = (g) => {
        if (g.includes("A")) return "text-emerald-400";
        if (g.includes("B")) return "text-blue-400";
        if (g.includes("C")) return "text-yellow-400";
        return "text-red-500";
    };

    return (
        <div className="space-y-6 max-w-4xl mx-auto">
            <header className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
                        <ClipboardList className="w-8 h-8 text-amber-500" />
                        The Daily Pulse
                    </h1>
                    <p className="text-slate-400 mt-1">AI Performance Debrief • {report.date}</p>
                </div>
                <div className={`text-6xl font-black ${getGradeColor(report.grade)} drop-shadow-[0_0_15px_rgba(255,255,255,0.2)]`}>
                    {report.grade}
                </div>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <HolographicCard className="col-span-2">
                    <div className="p-6 space-y-4">
                        <h2 className="text-lg font-semibold text-slate-300 border-b border-white/10 pb-2">Advisor Insight</h2>
                        <p className="text-xl text-white font-medium leading-relaxed">
                            "{report.insight}"
                        </p>
                        <div className="flex gap-2 mt-4">
                            <span className="bg-emerald-500/10 text-emerald-400 px-3 py-1 rounded-full text-xs border border-emerald-500/20">Discipline High</span>
                            {report.stats.manual > 2 && <span className="bg-red-500/10 text-red-400 px-3 py-1 rounded-full text-xs border border-red-500/20">Manual Interference</span>}
                        </div>
                    </div>
                </HolographicCard>

                <div className="space-y-6">
                    <HolographicCard>
                        <div className="p-4 flex justify-between items-center">
                            <div>
                                <p className="text-xs text-slate-400 uppercase tracking-widest">Total Trades</p>
                                <p className="text-3xl font-bold text-white mt-1">{report.stats.trades}</p>
                            </div>
                            <TrendingUp className="w-8 h-8 text-slate-600" />
                        </div>
                    </HolographicCard>

                    <HolographicCard>
                        <div className="p-4 flex justify-between items-center">
                            <div>
                                <p className="text-xs text-slate-400 uppercase tracking-widest">Bot Execution</p>
                                <p className="text-3xl font-bold text-emerald-400 mt-1">{report.stats.bot}</p>
                            </div>
                            <ShieldCheck className="w-8 h-8 text-emerald-900" />
                        </div>
                    </HolographicCard>

                    <HolographicCard>
                        <div className="p-4 flex justify-between items-center">
                            <div>
                                <p className="text-xs text-slate-400 uppercase tracking-widest">Manual Override</p>
                                <p className="text-3xl font-bold text-amber-500 mt-1">{report.stats.manual}</p>
                            </div>
                            <AlertTriangle className="w-8 h-8 text-amber-900" />
                        </div>
                    </HolographicCard>
                </div>
            </div>
        </div>
    );
}
