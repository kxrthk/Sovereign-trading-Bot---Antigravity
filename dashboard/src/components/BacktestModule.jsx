import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Area, AreaChart } from 'recharts';
import { Play, TrendingUp, TrendingDown, Clock, FlaskConical } from 'lucide-react';
import GlassCard from './ui/GlassCard';
import axios from 'axios';

export default function BacktestModule() {
    const [symbol, setSymbol] = useState("RELIANCE.NS");
    const [period, setPeriod] = useState("1y");
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [isTrayOpen, setIsTrayOpen] = useState(false);
    const [isPeriodTrayOpen, setIsPeriodTrayOpen] = useState(false);

    const runSimulation = async () => {
        setLoading(true);
        setResult(null);
        try {
            const res = await axios.post('/api/backtest', { symbol, period });
            if (res.data.status === 'success') {
                setResult(res.data);
            }
        } catch (e) {
            console.error(e);
        }
        setLoading(false);
    };

    return (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4">
            {/* Header / Controls */}
            <GlassCard className="p-6 overflow-visible z-50 relative">
                <div className="flex flex-col md:flex-row items-center justify-between gap-6">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-indigo-500/20 rounded-xl text-indigo-400">
                            <FlaskConical className="w-6 h-6" />
                        </div>
                        <div>
                            <h2 className="text-xl font-bold text-white">Historical Simulation</h2>
                            <p className="text-sm text-gray-400">Testing strategy on <span className="text-indigo-400 font-bold">PAST DATA</span> to enable future trust.</p>
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
                                        className="absolute top-12 left-0 w-64 bg-gray-900/95 backdrop-blur-xl border border-white/10 rounded-xl shadow-2xl overflow-hidden"
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

                        {/* PERIOD TRAY */}
                        <div className="relative">
                            <button
                                onClick={() => setIsPeriodTrayOpen(!isPeriodTrayOpen)}
                                className="bg-black/30 border border-white/10 rounded-lg px-4 py-2 text-white font-mono w-32 flex items-center justify-between hover:bg-white/5 transition-colors"
                            >
                                <span>{period}</span>
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
                                        className="absolute top-12 left-0 w-32 bg-gray-900/95 backdrop-blur-xl border border-white/10 rounded-xl shadow-2xl overflow-hidden"
                                    >
                                        <div className="p-2 space-y-1">
                                            {['1mo', '3mo', '6mo', '1y', '2y', '5y'].map(p => (
                                                <button
                                                    key={p}
                                                    onClick={() => { setPeriod(p); setIsPeriodTrayOpen(false); }}
                                                    className="w-full text-left px-3 py-2 rounded-lg hover:bg-white/10 text-xs font-mono text-gray-300 hover:text-white transition-colors"
                                                >
                                                    {p.toUpperCase()}
                                                </button>
                                            ))}
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>

                        <button
                            onClick={runSimulation}
                            disabled={loading}
                            className="bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-2 rounded-lg font-bold flex items-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loading ? (
                                <span className="animate-spin h-4 w-4 border-2 border-white/30 border-t-white rounded-full" />
                            ) : (
                                <Play className="w-4 h-4 fill-current" />
                            )}
                            RUN SIM
                        </button>
                    </div>
                </div>
            </GlassCard>

            {/* Results */}
            {result && (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* STATS */}
                    <GlassCard className="lg:col-span-1 p-6 space-y-6">
                        <h3 className="text-sm font-mono text-gray-400 uppercase tracking-widest">Performance Report</h3>

                        <div className="space-y-4">
                            <div className="p-4 bg-white/5 rounded-xl border border-white/5">
                                <span className="text-xs text-gray-500 block mb-1">TOTAL RETURN (ROI)</span>
                                <span className={`text-3xl font-bold font-mono ${result.metrics.roi >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                    {result.metrics.roi > 0 ? '+' : ''}{result.metrics.roi}%
                                </span>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div className="p-3 bg-white/5 rounded-xl border border-white/5">
                                    <span className="text-[10px] text-gray-500 block mb-1">FINAL BALANCE</span>
                                    <span className="text-lg font-bold font-mono text-white">₹{Math.round(result.metrics.final_strategy).toLocaleString()}</span>
                                </div>
                                <div className="p-3 bg-white/5 rounded-xl border border-white/5">
                                    <span className="text-[10px] text-gray-500 block mb-1">VS BENCHMARK</span>
                                    <span className={`text-lg font-bold font-mono ${result.metrics.final_strategy > result.metrics.final_benchmark ? 'text-emerald-400' : 'text-rose-400'}`}>
                                        {result.metrics.final_strategy > result.metrics.final_benchmark ? 'WIN' : 'LOSS'}
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div className="mt-4 p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-xl">
                            <h4 className="text-[10px] text-indigo-400 font-bold uppercase mb-1">Strategy Logic</h4>
                            <p className="text-xs text-gray-400">
                                <b>Golden Cross Algorithm:</b> The AI buys when the 20-Day Average crosses <i>above</i> the 50-Day Average, capturing strong momentum trends.
                            </p>
                        </div>
                    </GlassCard>

                    {/* CHART */}
                    <GlassCard className="lg:col-span-2 p-6 h-[400px] flex flex-col">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-sm font-mono text-gray-400 uppercase tracking-widest">Equity Curve</h3>
                            <div className="flex items-center gap-4">
                                <div className="flex items-center gap-2">
                                    <div className="w-2 h-2 rounded-full bg-indigo-400 shadow-[0_0_10px_rgba(129,140,248,0.5)]"></div>
                                    <span className="text-xs font-mono text-indigo-300">AI Strategy</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <div className="w-2 h-2 rounded-full bg-gray-400"></div>
                                    <span className="text-xs font-mono text-gray-400">Buy & Hold</span>
                                </div>
                            </div>
                        </div>
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={result.data}>
                                <defs>
                                    <linearGradient id="colorStrat" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#818cf8" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#818cf8" stopOpacity={0} />
                                    </linearGradient>
                                    <linearGradient id="colorBench" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#9ca3af" stopOpacity={0.1} />
                                        <stop offset="95%" stopColor="#9ca3af" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                                <XAxis
                                    dataKey="date"
                                    stroke="#6b7280"
                                    tick={{ fontSize: 10 }}
                                    tickFormatter={(str) => {
                                        const d = new Date(str);
                                        return d.toLocaleDateString(undefined, { month: 'short', year: '2-digit' });
                                    }}
                                />
                                <YAxis
                                    stroke="#6b7280"
                                    tick={{ fontSize: 10 }}
                                    domain={['auto', 'auto']}
                                />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', borderRadius: '8px' }}
                                    itemStyle={{ fontSize: '12px' }}
                                    formatter={(value) => [`₹${value.toLocaleString()}`, '']}
                                />
                                <Area
                                    type="monotone"
                                    dataKey="benchmark"
                                    stroke="#9ca3af"
                                    strokeWidth={2}
                                    fillOpacity={1}
                                    fill="url(#colorBench)"
                                    name="Buy & Hold"
                                />
                                <Area
                                    type="monotone"
                                    dataKey="strategy"
                                    stroke="#818cf8"
                                    strokeWidth={3}
                                    fillOpacity={1}
                                    fill="url(#colorStrat)"
                                    name="AI Strategy"
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </GlassCard>
                </div>
            )}
        </div>
    );
}
