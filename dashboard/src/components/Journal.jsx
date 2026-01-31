import React, { useState, useEffect } from 'react';
import { BookOpen, TrendingUp, AlertTriangle, ShieldCheck, X, Activity } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import GlassCard from './ui/GlassCard';
import CaptainLog from './CaptainLog';

const Journal = () => {
    const [trades, setTrades] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedTrade, setSelectedTrade] = useState(null);
    const [analysis, setAnalysis] = useState(null);
    const [analyzing, setAnalyzing] = useState(false);
    const [context, setContext] = useState({ strategy: 'Trend Following', emotion: 'Neutral', notes: '' });
    const [viewMode, setViewMode] = useState('trades'); // 'trades' or 'log'

    // Fetch User Trades
    useEffect(() => {
        const fetchTrades = async () => {
            try {
                const res = await fetch('/api/user_trades');
                const data = await res.json();
                if (Array.isArray(data)) {
                    setTrades(data);
                } else {
                    console.error("Trades data format error:", data);
                    setTrades([]);
                }
            } catch (e) {
                console.error("Failed to load trades", e);
            } finally {
                setLoading(false);
            }
        };
        fetchTrades();
        const interval = setInterval(fetchTrades, 5000); // Poll for updates
        return () => clearInterval(interval);
    }, []);

    // Analyze Trade (Context-Aware)
    const handleAnalyze = async () => {
        if (!selectedTrade) return;

        setAnalysis(null);
        setAnalyzing(true);
        try {
            const res = await fetch('/api/analyze_trade', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    trade_id: selectedTrade.order_id,
                    strategy: context.strategy,
                    emotion: context.emotion,
                    notes: context.notes
                })
            });
            const data = await res.json();
            setAnalysis(data);
        } catch (e) {
            console.error(e);
        } finally {
            setAnalyzing(false);
        }
    };

    // Open Modal & Reset Context
    const handleOpenModal = (trade) => {
        setSelectedTrade(trade);
        setContext({ strategy: 'Trend Following', emotion: 'Neutral', notes: '' });
        setAnalysis(null);
    };

    return (
        <div className="h-full flex flex-col p-6 gap-6 relative">
            <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-3">
                    <BookOpen className="w-6 h-6 text-purple-400" />
                    <h2 className="text-xl font-bold text-white tracking-widest">ARCHIVES</h2>
                </div>

                {/* View Switcher */}
                <div className="flex bg-black/40 p-1 rounded-lg border border-white/10">
                    <button
                        onClick={() => setViewMode('trades')}
                        className={`px-4 py-1.5 rounded-md text-xs font-bold transition-all ${viewMode === 'trades' ? 'bg-purple-500 text-white shadow-lg' : 'text-gray-400 hover:text-white'}`}
                    >
                        TRADE LIST
                    </button>
                    <button
                        onClick={() => setViewMode('log')}
                        className={`px-4 py-1.5 rounded-md text-xs font-bold transition-all ${viewMode === 'log' ? 'bg-amber-500 text-white shadow-lg' : 'text-gray-400 hover:text-white'}`}
                    >
                        CAPTAIN'S LOG
                    </button>
                </div>
            </div>

            {viewMode === 'log' ? (
                <CaptainLog />
            ) : (
                <>
                    {loading ? (
                        <div className="flex-1 flex items-center justify-center text-gray-500 animate-pulse">Accessing Archives...</div>
                    ) : trades.length === 0 ? (
                        <div className="flex-1 flex flex-col items-center justify-center text-gray-600 gap-4">
                            <BookOpen className="w-16 h-16 opacity-20" />
                            <p>The Book is empty. Place a manual trade to begin your saga.</p>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 overflow-y-auto pb-20">
                            {trades.map((trade) => (
                                <GlassCard
                                    key={trade.order_id}
                                    className="p-4 hover:bg-white/5 transition-all cursor-pointer group relative overflow-hidden"
                                    onClick={() => handleOpenModal(trade)}
                                >
                                    <div className="absolute top-0 right-0 p-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                        <span className="text-[10px] bg-purple-500 text-white px-2 py-0.5 rounded-full font-bold">CLICK TO ANALYZE</span>
                                    </div>

                                    <div className="flex justify-between items-start mb-4">
                                        <div>
                                            <h3 className="text-lg font-bold text-white">{trade.symbol}</h3>
                                            <span className="text-[10px] text-gray-400 font-mono">{trade.timestamp.split('.')[0]}</span>
                                        </div>
                                        <span className={`px-2 py-1 rounded text-xs font-bold ${trade.action === 'BUY' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                                            }`}>
                                            {trade.action}
                                        </span>
                                    </div>

                                    <div className="grid grid-cols-2 gap-y-2 text-sm">
                                        <div className="text-gray-500 text-xs uppercase">Avg Price</div>
                                        <div className="text-right font-mono text-gray-300">₹{trade.avg_price.toFixed(2)}</div>

                                        <div className="text-gray-500 text-xs uppercase">Quantity</div>
                                        <div className="text-right font-mono text-gray-300">{trade.quantity}</div>

                                        <div className="text-gray-500 text-xs uppercase">Total Cost</div>
                                        <div className="text-right font-mono text-gray-300">₹{((trade.quantity * trade.avg_price) + trade.taxes_paid).toFixed(2)}</div>
                                    </div>
                                </GlassCard>
                            ))}
                        </div>
                    )}

                    {/* ANALYSIS MODAL */}
                    <AnimatePresence>
                        {selectedTrade && (
                            <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                                <motion.div
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    exit={{ opacity: 0 }}
                                    className="absolute inset-0 bg-black/80 backdrop-blur-sm"
                                    onClick={() => setSelectedTrade(null)}
                                />
                                <motion.div
                                    initial={{ scale: 0.9, y: 20, opacity: 0 }}
                                    animate={{ scale: 1, y: 0, opacity: 1 }}
                                    exit={{ scale: 0.9, y: 20, opacity: 0 }}
                                    className="bg-gray-900 border border-white/10 w-full max-w-2xl rounded-2xl shadow-2xl relative overflow-hidden flex flex-col max-h-[90vh]"
                                >
                                    {/* Modal Header */}
                                    <div className="p-6 border-b border-white/5 flex justify-between items-center bg-gray-900/50 backdrop-blur-md">
                                        <div>
                                            <h3 className="text-xl font-bold text-white flex items-center gap-2">
                                                <ShieldCheck className="w-5 h-5 text-purple-400" />
                                                TRADE ANALYSIS
                                            </h3>
                                            <p className="text-xs text-gray-400 font-mono mt-1">ID: {selectedTrade.order_id}</p>
                                        </div>
                                        <button onClick={() => setSelectedTrade(null)} className="p-2 hover:bg-white/10 rounded-full transition-colors">
                                            <X className="w-5 h-5 text-gray-400" />
                                        </button>
                                    </div>

                                    {/* Modal Content */}
                                    <div className="p-8 overflow-y-auto">
                                        {analyzing ? (
                                            <div className="flex flex-col items-center justify-center py-10 gap-4">
                                                <Activity className="w-12 h-12 text-purple-500 animate-spin" />
                                                <p className="text-sm font-mono text-purple-300 animate-pulse">THE RECTIFIER IS JUDGING YOUR LOGIC...</p>
                                            </div>
                                        ) : analysis ? (
                                            <div className="space-y-8">
                                                {/* SCORE SECTION */}
                                                <div className="flex flex-col items-center">
                                                    <div className="relative w-32 h-32 flex items-center justify-center">
                                                        <svg className="w-full h-full transform -rotate-90">
                                                            <circle cx="64" cy="64" r="60" stroke="currentColor" strokeWidth="8" fill="transparent" className="text-gray-800" />
                                                            <circle
                                                                cx="64" cy="64" r="60"
                                                                stroke="currentColor"
                                                                strokeWidth="8"
                                                                fill="transparent"
                                                                strokeDasharray={377}
                                                                strokeDashoffset={377 - (377 * analysis.score) / 100}
                                                                className={`${analysis.score > 70 ? 'text-emerald-500' : analysis.score > 40 ? 'text-amber-500' : 'text-rose-500'} transition-all duration-1000 ease-out`}
                                                            />
                                                        </svg>
                                                        <div className="absolute flex flex-col items-center">
                                                            <span className="text-4xl font-bold text-white">{analysis.score}</span>
                                                            <span className="text-[10px] text-gray-400 uppercase tracking-wider">Score</span>
                                                        </div>
                                                    </div>
                                                </div>

                                                {/* FEEDBACK GRID */}
                                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                                    {/* POSITIVES */}
                                                    <div className="bg-emerald-500/5 border border-emerald-500/10 rounded-xl p-4">
                                                        <h4 className="text-emerald-400 text-xs font-bold uppercase tracking-widest mb-3 flex items-center gap-2">
                                                            <TrendingUp className="w-4 h-4" /> Strengths
                                                        </h4>
                                                        <ul className="space-y-2">
                                                            {analysis.feedback.length > 0 ? analysis.feedback.map((item, i) => (
                                                                <li key={i} className="text-sm text-gray-300 flex items-start gap-2">
                                                                    <span className="text-emerald-500 mt-1">●</span> {item}
                                                                </li>
                                                            )) : <li className="text-gray-500 italic text-sm">No significant strengths detected.</li>}
                                                        </ul>
                                                    </div>

                                                    {/* RISKS */}
                                                    <div className="bg-rose-500/5 border border-rose-500/10 rounded-xl p-4">
                                                        <h4 className="text-rose-400 text-xs font-bold uppercase tracking-widest mb-3 flex items-center gap-2">
                                                            <AlertTriangle className="w-4 h-4" /> Risks Detected
                                                        </h4>
                                                        <ul className="space-y-2">
                                                            {analysis.risks.length > 0 ? analysis.risks.map((item, i) => (
                                                                <li key={i} className="text-sm text-gray-300 flex items-start gap-2">
                                                                    <span className="text-rose-500 mt-1">●</span> {item}
                                                                </li>
                                                            )) : <li className="text-gray-500 italic text-sm">No critical risks found. Good job!</li>}
                                                        </ul>
                                                    </div>
                                                </div>

                                                <button
                                                    onClick={() => setAnalysis(null)}
                                                    className="w-full py-3 rounded-xl bg-white/5 hover:bg-white/10 text-gray-400 text-xs font-bold tracking-widest transition-colors border border-white/5"
                                                >
                                                    RE-ANALYZE
                                                </button>
                                            </div>
                                        ) : (
                                            <div className="space-y-6">
                                                <div className="bg-purple-500/10 border border-purple-500/20 rounded-xl p-4 flex gap-4 items-start">
                                                    <div className="p-2 bg-purple-500/20 rounded-lg shrink-0">
                                                        <ShieldCheck className="w-6 h-6 text-purple-400" />
                                                    </div>
                                                    <div>
                                                        <h4 className="text-purple-300 font-bold text-sm">TRADE RECONSTRUCTION</h4>
                                                        <p className="text-xs text-gray-400 mt-1">
                                                            To get a valid critique, "The Rectifier" needs to know your state of mind.
                                                            Honesty is the only way to get better.
                                                        </p>
                                                    </div>
                                                </div>

                                                <div className="grid grid-cols-2 gap-4">
                                                    <div className="space-y-2">
                                                        <label className="text-xs font-mono text-gray-500">STRATEGY CLAIMED</label>
                                                        <select
                                                            className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2.5 text-sm text-white focus:border-purple-500/50 outline-none"
                                                            value={context.strategy}
                                                            onChange={e => setContext({ ...context, strategy: e.target.value })}
                                                        >
                                                            <option value="Trend Following">Trend Following</option>
                                                            <option value="Breakout">Breakout</option>
                                                            <option value="Reversal">Reversal / Mean Reversion</option>
                                                            <option value="Scalp">Scalp (Quick In/Out)</option>
                                                            <option value="Gamble">Gamble / Gut Feeling</option>
                                                        </select>
                                                    </div>
                                                    <div className="space-y-2">
                                                        <label className="text-xs font-mono text-gray-500">EMOTIONAL STATE</label>
                                                        <select
                                                            className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2.5 text-sm text-white focus:border-purple-500/50 outline-none"
                                                            value={context.emotion}
                                                            onChange={e => setContext({ ...context, emotion: e.target.value })}
                                                        >
                                                            <option value="Neutral">Neutral / Focused</option>
                                                            <option value="Confident">Confident</option>
                                                            <option value="FOMO">FOMO (Fear Of Missing Out)</option>
                                                            <option value="Panic">Panic / Fear</option>
                                                            <option value="Revenge">Revenge (Recovering Loss)</option>
                                                        </select>
                                                    </div>
                                                </div>

                                                <div className="space-y-2">
                                                    <label className="text-xs font-mono text-gray-500">RATIONALE / NOTES</label>
                                                    <textarea
                                                        className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2.5 text-sm text-white focus:border-purple-500/50 outline-none min-h-[100px]"
                                                        placeholder="Why did you take this trade? e.g. 'Price broke VWAP and Volume spiked...'"
                                                        value={context.notes}
                                                        onChange={e => setContext({ ...context, notes: e.target.value })}
                                                    />
                                                </div>

                                                <button
                                                    onClick={() => handleAnalyze()}
                                                    className="w-full py-4 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold tracking-widest shadow-lg shadow-purple-500/20 transition-all active:scale-[0.98] flex items-center justify-center gap-2"
                                                >
                                                    <Activity className="w-5 h-5" />
                                                    RUN DIAGNOSTIC
                                                </button>
                                            </div>
                                        )}
                                    </div>
                                </motion.div>
                            </div>
                        )}
                    </AnimatePresence>
                </>
            )}
        </div>
    );
};

export default Journal;
