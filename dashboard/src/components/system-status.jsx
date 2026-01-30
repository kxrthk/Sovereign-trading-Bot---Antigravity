import { motion } from 'framer-motion'
import { useState, useEffect } from 'react'
import axios from 'axios';

export default function SystemStatus() {
    const [status, setStatus] = useState('CONNECTING...')
    const [isOnline, setIsOnline] = useState(false)
    const [lastHeartbeat, setLastHeartbeat] = useState(null)
    const [riskStatus, setRiskStatus] = useState("CHECKING...")
    const [botRunning, setBotRunning] = useState(true);

    // 1. Poll Server Status
    useEffect(() => {
        const checkStatus = async () => {
            try {
                const res = await axios.get('/api/status');
                const data = res.data;

                if (data.server_timestamp) {
                    setIsOnline(true);

                    // Logic Status
                    if (data.risk_status && (data.risk_status.includes("STOPPED") || data.risk_status.includes("HALTED"))) {
                        setStatus('TRADING HALTED');
                    } else {
                        setStatus('SERVER ACTIVE');
                    }

                    setLastHeartbeat(new Date().toLocaleTimeString());
                    setRiskStatus(data.risk_status || "UNKNOWN");
                }
            } catch (e) {
                setIsOnline(false);
                setStatus('DISCONNECTED');
                setRiskStatus("OFFLINE");
            }
        }

        const interval = setInterval(checkStatus, 2000); // Check every 2s
        checkStatus();
        return () => clearInterval(interval);
    }, [])

    // 2. Poll Bot Status (Separate Logic)
    useEffect(() => {
        const fetchBotStatus = async () => {
            try {
                const res = await axios.get('/api/bot/status');
                setBotRunning(res.data.status === 'running');
            } catch (e) { }
        }
        fetchBotStatus();
        // Poll less frequently for bot status
        const interval = setInterval(fetchBotStatus, 5000);
        return () => clearInterval(interval);
    }, []);

    const toggleBot = async () => {
        try {
            const action = botRunning ? 'stop' : 'start';
            await axios.post(`/api/bot/${action}`);
            setBotRunning(!botRunning);
        } catch (e) {
            console.error("Toggle Failed", e);
        }
    };

    return (
        <div className={`flex items-center gap-3 px-4 py-3 rounded-lg border backdrop-blur-xl transition-colors duration-500 ${isOnline && status !== 'TRADING HALTED' ? 'bg-emerald-500/10 border-emerald-500/30' : 'bg-red-500/10 border-red-500/30'}`}>

            {/* PULSING INDICATOR */}
            <div className="relative">
                <div className={`w-2.5 h-2.5 rounded-full ${isOnline && status !== 'TRADING HALTED' ? 'bg-emerald-500' : 'bg-red-500'}`} />
                <motion.div
                    animate={{ scale: [1, 2, 1], opacity: [0.5, 0, 0.5] }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className={`absolute inset-0 rounded-full ${isOnline && status !== 'TRADING HALTED' ? 'bg-emerald-500' : 'bg-red-500'}`}
                />
            </div>

            {/* MASTER SWITCH BUTTON */}
            <button
                onClick={toggleBot}
                className={`ml-2 px-3 py-1 rounded-full text-[10px] font-bold border transition-all ${botRunning ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50 hover:bg-emerald-500/30' : 'bg-red-500/20 text-red-400 border-red-500/50 hover:bg-red-500/30'}`}
            >
                {botRunning ? 'AUTO-PILOT ACTIVE' : 'AUTO-PILOT PAUSED'}
            </button>

            {/* MAIN STATUS TEXT */}
            <div className="flex flex-col">
                <span className={`text-sm font-mono font-semibold ${isOnline && status !== 'TRADING HALTED' ? 'text-emerald-600 dark:text-emerald-500' : 'text-red-600 dark:text-red-500'}`}>
                    {status}
                </span>
                {lastHeartbeat && isOnline && (
                    <span className="text-[10px] text-gray-500 dark:text-zinc-500 font-mono">
                        LOS: {lastHeartbeat}
                    </span>
                )}
            </div>

            {/* RISK PROTOCOL BOX */}
            <div className={`flex flex-col border-l pl-3 ml-2 ${riskStatus.includes("STOPPED") ? 'border-red-500/30' :
                riskStatus.includes("CAUTIOUS") ? 'border-yellow-500/30' :
                    'border-emerald-500/30'
                }`}>
                <span className="text-[10px] text-gray-500 dark:text-zinc-500 font-mono uppercase tracking-wider">
                    Risk Protocol
                </span>
                <span className={`text-xs font-bold font-mono ${riskStatus.includes("STOPPED") ? 'text-red-500 dark:text-red-400' :
                    riskStatus.includes("CAUTIOUS") ? 'text-yellow-600 dark:text-yellow-400' :
                        'text-emerald-600 dark:text-emerald-400'
                    }`}>
                    {riskStatus}
                </span>
            </div>
        </div>
    )
}
