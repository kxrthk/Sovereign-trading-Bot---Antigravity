import { motion } from 'framer-motion';
import { Terminal, Activity, Clock } from 'lucide-react';
import { useState, useEffect } from 'react';

export default function BotActionBar() {
    const [status, setStatus] = useState({
        bot_message: "Initializing Neural Link...",
        risk_status: "STANDBY",
        trading_mode: "PAPER",
        uptime: "00:00"
    });

    useEffect(() => {
        const fetchStatus = async () => {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();
                setStatus(prev => ({
                    ...prev,
                    bot_message: data.bot_message,
                    risk_status: data.risk_status,
                    trading_mode: data.trading_mode
                }));
            } catch (e) {
                // Silent Error (Keep previous state)
            }
        };

        const interval = setInterval(fetchStatus, 2000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="fixed bottom-0 left-0 md:left-24 right-0 z-40 bg-white/90 dark:bg-[#09090b]/90 border-t border-gray-200 dark:border-white/5 backdrop-blur-lg px-6 py-2 flex items-center justify-between transition-colors duration-500">
            <div className="flex items-center gap-3">
                <div className="p-1.5 rounded bg-emerald-500/10">
                    <Terminal className="w-4 h-4 text-emerald-600 dark:text-emerald-500" />
                </div>
                <div className="flex flex-col">
                    <span className="text-[10px] uppercase tracking-widest text-gray-500 dark:text-zinc-500 font-mono">Sovereign Intelligence</span>
                    <motion.span
                        key={status.bot_message}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="text-xs text-gray-800 dark:text-zinc-300 font-mono truncate max-w-[300px] md:max-w-none"
                    >
                        {status.bot_message}
                    </motion.span>
                </div>
            </div>

            <div className="hidden md:flex items-center gap-6 text-[10px] text-gray-400 dark:text-zinc-600 font-mono uppercase tracking-wider">
                <div className="flex items-center gap-1.5">
                    <Activity className="w-3 h-3" />
                    <span>{status.risk_status}</span>
                </div>
                <div className="flex items-center gap-1.5">
                    <div className={`w-1.5 h-1.5 rounded-full ${status.trading_mode === 'LIVE' ? 'bg-red-500 animate-pulse' : 'bg-yellow-500'}`} />
                    <span>Mode: {status.trading_mode}</span>
                </div>
            </div>
        </div>
    )
}
