import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ComposedChart, Line, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine } from 'recharts';
import { Sparkles, TrendingUp, AlertTriangle, Activity, Crosshair, TrendingDown, Clock } from 'lucide-react';
import GlassCard from './ui/GlassCard';
import axios from 'axios';

export default function ForecastModule() {
    const [symbol, setSymbol] = useState("RELIANCE.NS");
    const [days, setDays] = useState(30);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [isTrayOpen, setIsTrayOpen] = useState(false);
    const [isPeriodTrayOpen, setIsPeriodTrayOpen] = useState(false);
    const [error, setError] = useState(null);

    const runForecast = async () => {
        setLoading(true);
        setResult(null);
        setError(null);
        try {
            const res = await axios.post('/api/forecast', { symbol, days });
            if (res.data.status === 'success') {
                setResult(res.data);
            } else {
                setError(res.data.message || "Unknown API Error");
            }
        } catch (e) {
            console.error(e);
            setError(e.message || "Network Request Failed");
        }
        setLoading(false);
    };

    // Combine History + Forecast for the Chart
    const chartData = result ? [
        ...result.history.map(h => ({ date: h.date, history: h.price })),
        ...result.forecast.map(f => ({
            date: f.date,
            p50: f.p50,
            range: [f.p10, f.p90] // Area Range
        }))
    ] : [];

    return (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4">
            {/* Header */}
            <GlassCard className="p-6 overflow-visible z-50 relative">
                <div className="flex flex-col md:flex-row items-center justify-between gap-6">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-purple-500/20 rounded-xl text-purple-400">
                            <Sparkles className="w-6 h-6" />
                        </div>
                        <div>
                            <h2 className="text-xl font-bold text-white">Oracle Prediction</h2>
                            <p className="text-sm text-gray-400">Monte Carlo Simulation (1000 Future Paths).</p>
                        </div>
                    </div>

                    <div className="flex items-center gap-3 w-full md:w-auto relative z-50">
                        {/* ASSET TRAY */}
                        <div className="relative">
                            <button
                                onClick={() => setIsTrayOpen(!isTrayOpen)}
                                className="bg-black/30 border border-white/10 rounded-lg px-4 py-2 text-white font-mono w-48 flex items-center justify-between hover:bg-white/5 transition-colors"
                            >
                                <span>{symbol}</span>
                                <motion.div animate={{ rotate: isTrayOpen ? 180 : 0 }}>
                                    <TrendingDown className="w-4 h-4 text-gray-400" />
                                </motion.div>
                            </button>

                            <AnimatePresence>
                                {isTrayOpen && (
                                    <motion.div
                                        initial={{ opacity: 0, y: -10, height: 0 }}
                                        animate={{ opacity: 1, y: 0, height: 'auto' }}
                                        exit={{ opacity: 0, y: -10, height: 0 }}
                                        className="absolute top-12 left-0 w-64 bg-gray-900/95 backdrop-blur-xl border border-white/10 rounded-xl shadow-2xl overflow-hidden z-50"
                                    >
                                        <div className="p-2 space-y-1">
                                            <div className="text-[10px] text-gray-500 px-2 py-1 uppercase tracking-wider font-bold">Stocks</div>
                                            {['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'TATAMOTORS.NS', 'ITC.NS'].map(s => (
                                                <button key={s} onClick={() => { setSymbol(s); setIsTrayOpen(false); }} className="w-full text-left px-3 py-2 rounded-lg hover:bg-white/10 text-xs font-mono text-gray-300 hover:text-white transition-colors">
                                                    {s}
                                                </button>
                                            ))}

                                            <div className="text-[10px] text-gray-500 px-2 py-1 uppercase tracking-wider font-bold border-t border-white/5 pt-2 mt-1">Commodities (ETFs)</div>
                                            {['GOLDBEES.NS', 'SILVERBEES.NS'].map(s => (
                                                <button key={s} onClick={() => { setSymbol(s); setIsTrayOpen(false); }} className="w-full text-left px-3 py-2 rounded-lg hover:bg-white/10 text-xs font-mono text-gray-300 hover:text-white transition-colors">
                                                    {s}
                                                </button>
                                            ))}
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>

                        {/* DURATION TRAY */}
                        <div className="relative">
                            <button
                                onClick={() => setIsPeriodTrayOpen(!isPeriodTrayOpen)}
                                className="bg-black/30 border border-white/10 rounded-lg px-4 py-2 text-white font-mono w-32 flex items-center justify-between hover:bg-white/5 transition-colors"
                            >
                                <span>{days} Days</span>
                                <motion.div animate={{ rotate: isPeriodTrayOpen ? 180 : 0 }}>
                                    <Clock className="w-4 h-4 text-gray-400" />
                                </motion.div>
                            </button>

                            <AnimatePresence>
                                {isPeriodTrayOpen && (
                                    <motion.div
                                        initial={{ opacity: 0, y: -10, height: 0 }}
                                        animate={{ opacity: 1, y: 0, height: 'auto' }}
                                        exit={{ opacity: 0, y: -10, height: 0 }}
                                        className="absolute top-12 left-0 w-32 bg-gray-900/95 backdrop-blur-xl border border-white/10 rounded-xl shadow-2xl overflow-hidden z-50"
                                    >
                                        <div className="p-2 space-y-1">
                                            {[15, 30, 60, 90].map(d => (
                                                <button
                                                    key={d}
                                                    onClick={() => { setDays(d); setIsPeriodTrayOpen(false); }}
                                                    className="w-full text-left px-3 py-2 rounded-lg hover:bg-white/10 text-xs font-mono text-gray-300 hover:text-white transition-colors"
                                                >
                                                    {d} DAYS
                                                </button>
                                            ))}
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>

                        <button
                            onClick={runForecast}
                            disabled={loading}
                            className="bg-purple-600 hover:bg-purple-500 text-white px-6 py-2 rounded-lg font-bold flex items-center gap-2 transition-all disabled:opacity-50"
                        >
                            {loading ? <span className="animate-spin h-4 w-4 border-2 border-white/30 border-t-white rounded-full" /> : <Crosshair className="w-4 h-4" />}
                            FORECAST
                        </button>
                    </div>
                </div>
            </GlassCard>

            {/* ERROR MESSAGE */}
            {error && (
                <div className="p-4 bg-red-500/20 border border-red-500/30 rounded-xl text-red-200 flex items-center gap-3">
                    <AlertTriangle className="w-5 h-5 text-red-400" />
                    <span><b>Prediction Failed:</b> {error}</span>
                </div>
            )}

            {/* Content */}
            {result && (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* INSIGHTS */}
                    <GlassCard className="lg:col-span-1 p-6 space-y-6">
                        <h3 className="text-sm font-mono text-gray-400 uppercase tracking-widest">Oracle Insight</h3>

                        <div className={`p-4 rounded-xl border ${result.metrics.confidence > 70 ? 'bg-emerald-500/10 border-emerald-500/20' : 'bg-yellow-500/10 border-yellow-500/20'}`}>
                            <div className="flex items-center gap-2 mb-2">
                                <Activity className="w-4 h-4 text-white" />
                                <span className="font-bold text-white text-sm">Neural Verdict</span>
                            </div>
                            <p className="text-sm font-bold text-gray-200">{result.metrics.insight}</p>
                            <p className="text-xs text-purple-300 mt-2 font-mono border-t border-purple-500/20 pt-2 leading-relaxed">
                                <b>Analysis:</b> {result.metrics.reasoning}
                            </p>
                        </div>

                        <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-xl">
                            <h4 className="text-[10px] text-blue-400 font-bold uppercase mb-1">Methodology</h4>
                            <p className="text-xs text-gray-400">
                                This is not a crystal ball. We ran <b>1,000 Monte Carlo Simulations</b> based on historical volatility to map the most likely mathematical outcomes.
                            </p>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="p-3 bg-white/5 rounded-xl border border-white/5">
                                <span className="text-[10px] text-gray-500 block mb-1">EXPECTED (P50)</span>
                                <span className="text-lg font-bold font-mono text-purple-400">₹{result.metrics.expected_price}</span>
                            </div>
                            <div className="p-3 bg-white/5 rounded-xl border border-white/5">
                                <span className="text-[10px] text-gray-500 block mb-1">WORST CASE (P10)</span>
                                <span className="text-lg font-bold font-mono text-rose-400">₹{result.metrics.worst_case}</span>
                            </div>
                        </div>

                        {/* Confidence Gauge */}
                        <div>
                            <div className="flex justify-between text-xs text-gray-500 mb-1">
                                <span>Confidence Score</span>
                                <span>{result.metrics.confidence}%</span>
                            </div>
                            <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                                <motion.div
                                    initial={{ width: 0 }}
                                    animate={{ width: `${result.metrics.confidence}%` }}
                                    className={`h-full ${result.metrics.confidence > 70 ? 'bg-emerald-500' : 'bg-yellow-500'}`}
                                />
                            </div>
                        </div>
                    </GlassCard>

                    {/* FAN CHART */}
                    <GlassCard className="lg:col-span-2 p-6 h-[400px]">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-sm font-mono text-gray-400 uppercase tracking-widest">Probability Cone</h3>
                            <div className="flex gap-4">
                                <div className="flex items-center gap-1 text-[10px] text-gray-400"><div className="w-2 h-2 rounded-full bg-blue-400" />History</div>
                                <div className="flex items-center gap-1 text-[10px] text-gray-400"><div className="w-2 h-2 rounded-full bg-purple-500" />Expected</div>
                                <div className="flex items-center gap-1 text-[10px] text-gray-400"><div className="w-2 h-2 rounded-full bg-purple-500/20" />Range (P10-P90)</div>
                            </div>
                        </div>
                        <ResponsiveContainer width="100%" height="100%">
                            <ComposedChart data={chartData}>
                                <defs>
                                    <linearGradient id="colorFan" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#a855f7" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#a855f7" stopOpacity={0.1} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                                <XAxis
                                    dataKey="date"
                                    stroke="#6b7280"
                                    tick={{ fontSize: 10 }}
                                    tickFormatter={(str) => {
                                        const d = new Date(str);
                                        return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
                                    }}
                                />
                                <YAxis stroke="#6b7280" domain={['auto', 'auto']} tick={{ fontSize: 10 }} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#111827', borderColor: '#374151' }}
                                    itemStyle={{ fontSize: '12px' }}
                                    formatter={(val, name) => [typeof val === 'number' ? `₹${val.toFixed(2)}` : val, name]}
                                />

                                {/* History Line */}
                                <Line type="monotone" dataKey="history" stroke="#60a5fa" strokeWidth={2} dot={false} />

                                {/* Forecast Fan Area (Range) */}
                                <Area type="monotone" dataKey="range" stroke="none" fill="url(#colorFan)" />

                                {/* Forecast P50 Line */}
                                <Line type="monotone" dataKey="p50" stroke="#a855f7" strokeWidth={2} dot={false} strokeDasharray="5 5" />

                            </ComposedChart>
                        </ResponsiveContainer>
                    </GlassCard>
                </div>
            )}
        </div>
    );
}
