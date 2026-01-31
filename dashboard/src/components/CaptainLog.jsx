import React, { useState, useEffect } from 'react';
import { Scroll, Feather, Calendar, RefreshCw } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import GlassCard from './ui/GlassCard';

const CaptainLog = () => {
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);

    const fetchLogs = async () => {
        try {
            const res = await fetch('/api/logs');
            const data = await res.json();
            setLogs(data);
        } catch (e) {
            console.error("Log fetch failed", e);
        } finally {
            setLoading(false);
        }
    };

    const handleGenerate = async () => {
        setGenerating(true);
        try {
            await fetch('/api/logs/generate', { method: 'POST' });
            await fetchLogs();
        } catch (e) {
            console.error("Generation failed", e);
        } finally {
            setGenerating(false);
        }
    };

    useEffect(() => {
        fetchLogs();
    }, []);

    return (
        <div className="flex flex-col h-full overflow-hidden">
            {/* Header / Actions */}
            <div className="flex justify-between items-center mb-6">
                <div className="flex items-center gap-3">
                    <Scroll className="w-6 h-6 text-amber-400" />
                    <h2 className="text-xl font-bold text-white tracking-widest">CAPTAIN'S LOG</h2>
                </div>
                <button
                    onClick={handleGenerate}
                    disabled={generating}
                    className="flex items-center gap-2 px-4 py-2 bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/30 rounded-lg transition-all active:scale-95 disabled:opacity-50"
                >
                    <RefreshCw className={`w-4 h-4 ${generating ? 'animate-spin' : ''}`} />
                    <span className="text-xs font-bold uppercase">{generating ? 'Scribing...' : 'Update Log'}</span>
                </button>
            </div>

            {/* Timeline Scroll */}
            <div className="flex-1 overflow-y-auto pr-2 space-y-6 pb-20 scrollbar-hide">
                {loading ? (
                    <div className="text-center text-gray-500 animate-pulse text-sm font-mono mt-10">
                        Decrypting Archives...
                    </div>
                ) : logs.length === 0 ? (
                    <div className="text-center text-gray-500 text-sm font-mono mt-10">
                        No logs recorded. Initialize the Scribe.
                    </div>
                ) : (
                    logs.map((log, index) => (
                        <motion.div
                            key={log.date}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.1 }}
                            className="relative pl-8 border-l border-white/10 group"
                        >
                            {/* Timeline Node */}
                            <div className="absolute left-[-5px] top-0 w-2.5 h-2.5 rounded-full bg-gray-600 group-hover:bg-amber-400 transition-colors shadow-[0_0_10px_rgba(0,0,0,0.5)] group-hover:shadow-[0_0_10px_rgba(251,191,36,0.5)]" />

                            <GlassCard className="p-5 flex flex-col gap-3 group-hover:bg-white/5 transition-colors">
                                <div className="flex justify-between items-start">
                                    <div>
                                        <h3 className="text-lg font-bold text-white flex items-center gap-2">
                                            {log.title}
                                            <span className={`text-[10px] px-2 py-0.5 rounded-full border ${log.mood?.includes('Bullish') ? 'border-emerald-500 text-emerald-400' :
                                                    log.mood?.includes('Cautious') ? 'border-amber-500 text-amber-400' :
                                                        'border-gray-500 text-gray-400'
                                                }`}>
                                                MOOD: {log.mood}
                                            </span>
                                        </h3>
                                        <span className="text-xs text-gray-500 font-mono flex items-center gap-1">
                                            <Calendar className="w-3 h-3" /> {log.date}
                                        </span>
                                    </div>
                                    <Feather className="w-5 h-5 text-gray-600 group-hover:text-amber-400/50 transition-colors" />
                                </div>

                                <div className="text-sm text-gray-300 font-serif leading-relaxed whitespace-pre-wrap">
                                    {log.content}
                                </div>

                                <div className="flex gap-4 mt-2 pt-3 border-t border-white/5">
                                    <div className="text-[10px] text-gray-400 uppercase tracking-wider">
                                        Intel Sources: <span className="text-white">{log.stats?.news_count || 0}</span>
                                    </div>
                                    <div className="text-[10px] text-gray-400 uppercase tracking-wider">
                                        Actions Taken: <span className="text-white">{log.stats?.trade_count || 0}</span>
                                    </div>
                                </div>
                            </GlassCard>
                        </motion.div>
                    ))
                )}
            </div>
        </div>
    );
};

export default CaptainLog;
