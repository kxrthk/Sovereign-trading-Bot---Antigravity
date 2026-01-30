import { motion } from 'framer-motion'
import { useState, useEffect } from 'react'

export default function SystemStatus() {
    const [status, setStatus] = useState('CONNECTING...')
    const [isOnline, setIsOnline] = useState(false)
    const [lastHeartbeat, setLastHeartbeat] = useState(null)
    const [riskStatus, setRiskStatus] = useState("CHECKING...")

    useEffect(() => {
        const checkStatus = async () => {
            try {
                const res = await fetch('http://localhost:8000/api/status');
                const data = await res.json();

                if (data.server_timestamp) {
                    const serverTime = new Date(data.server_timestamp).getTime();
                    const now = new Date().getTime();
                    // 5 seconds tolerance (local dev might have slight drift, keeping it loose for demo)
                    const diff = Math.abs(now - serverTime);

                    // Note: In local dev, timezones might match exactly. 
                    // For 'Disconnected' test, we rely on fetch failing or backend stalling.

                    setIsOnline(true);
                    setStatus('SYSTEM ONLINE');
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

    return (
        <div className={`flex items-center gap-3 px-4 py-3 rounded-lg border backdrop-blur-xl transition-colors duration-500 ${isOnline ? 'bg-emerald-500/10 border-emerald-500/30' : 'bg-red-500/10 border-red-500/30'}`}>
            <div className="relative">
                <div className={`w-2.5 h-2.5 rounded-full ${isOnline ? 'bg-emerald-500' : 'bg-red-500'}`} />
                <motion.div
                    animate={{ scale: [1, 2, 1], opacity: [0.5, 0, 0.5] }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className={`absolute inset-0 rounded-full ${isOnline ? 'bg-emerald-500' : 'bg-red-500'}`}
                />
            </div>
            <div className="flex flex-col">
                <span className={`text-sm font-mono font-semibold ${isOnline ? 'text-emerald-500' : 'text-red-500'}`}>
                    {status}
                </span>
                {lastHeartbeat && isOnline && (
                    <span className="text-[10px] text-zinc-500 font-mono">
                        HB: {lastHeartbeat}
                    </span>
                )}
            </div>

            {/* Risk Status Dialogue Box */}
            {status !== 'CONNECTING...' && (
                <div className={`flex flex-col border-l pl-3 ml-2 ${riskStatus.includes("STOPPED") ? 'border-red-500/30' :
                    riskStatus.includes("CAUTIOUS") ? 'border-yellow-500/30' :
                        'border-emerald-500/30'
                    }`}>
                    <span className="text-[10px] text-zinc-500 font-mono uppercase tracking-wider">
                        Risk Protocol
                    </span>
                    <span className={`text-xs font-bold font-mono ${riskStatus.includes("STOPPED") ? 'text-red-400' :
                        riskStatus.includes("CAUTIOUS") ? 'text-yellow-400' :
                            'text-emerald-400'
                        }`}>
                        {riskStatus}
                    </span>
                </div>
            )}
        </div>
    )
}
