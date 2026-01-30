import { motion } from 'framer-motion'
import { TrendingUp, AlertCircle, Shield, CloudLightning } from 'lucide-react'
import { useState, useEffect } from 'react'

export default function ActiveProtocols() {
    const [regime, setRegime] = useState('LOADING');

    useEffect(() => {
        const fetchRegime = async () => {
            try {
                const res = await fetch('/api/regime');
                const data = await res.json();
                if (data.status === 'success') setRegime(data.regime);
            } catch (e) {
                console.error("Regime fetch error", e);
            }
        };
        fetchRegime();
        const interval = setInterval(fetchRegime, 10000); // 10s Poll
        return () => clearInterval(interval);
    }, []);

    const protocols = [
        { title: 'Daily Volatility', value: '3.47%', status: 'MODERATE', icon: TrendingUp, color: 'text-blue-500 dark:text-blue-400', bgColor: 'bg-blue-500/10', borderColor: 'border-blue-500/30' },
        { title: 'Current Strategy', value: 'SMA 200 + RSI', status: 'ACTIVE', icon: AlertCircle, color: 'text-purple-600 dark:text-purple-400', bgColor: 'bg-purple-500/10', borderColor: 'border-purple-500/30' },
        { title: 'Risk Status', value: 'SAFE', status: 'OK', icon: Shield, color: 'text-emerald-600 dark:text-emerald-500', bgColor: 'bg-emerald-500/10', borderColor: 'border-emerald-500/30' },
        {
            title: 'Market Regime',
            value: regime,
            status: regime === 'TREND' ? 'GOLDILOCKS' : regime === 'CRASH' ? 'PANIC' : 'CHOP',
            icon: CloudLightning,
            color: regime === 'CRASH' ? 'text-red-500' : regime === 'TREND' ? 'text-amber-500' : 'text-gray-500',
            bgColor: regime === 'CRASH' ? 'bg-red-500/10' : regime === 'TREND' ? 'bg-amber-500/10' : 'bg-gray-500/10',
            borderColor: regime === 'CRASH' ? 'border-red-500/30' : 'border-amber-500/30'
        },
    ]

    return (
        <div>
            <h2 className="text-lg font-mono font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                ACTIVE PROTOCOLS
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
                {protocols.map((protocol) => {
                    const Icon = protocol.icon
                    return (
                        <motion.div
                            key={protocol.title}
                            whileHover={{ y: -4 }}
                            className={`p-6 rounded-xl bg-white dark:bg-white/5 backdrop-blur-xl border border-gray-200 dark:border-white/10 hover:bg-gray-50 dark:hover:bg-white/[0.07] transition-all duration-300 ${protocol.borderColor}`}
                        >
                            <div className="flex items-start justify-between mb-4">
                                <div className={`p-3 rounded-lg ${protocol.bgColor}`}>
                                    <Icon className={`w-5 h-5 ${protocol.color}`} />
                                </div>
                                <span className="text-xs font-mono font-semibold text-emerald-600 dark:text-emerald-500 bg-emerald-500/20 px-2 py-1 rounded">{protocol.status}</span>
                            </div>
                            <h3 className="text-sm font-mono text-gray-500 dark:text-zinc-400 mb-2">{protocol.title}</h3>
                            <p className={`text-2xl font-mono font-bold ${protocol.color}`}>{protocol.value}</p>
                        </motion.div>
                    )
                })}
            </div>
        </div>
    )
}
