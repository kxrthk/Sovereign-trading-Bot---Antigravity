import { motion } from 'framer-motion'
import { TrendingUp, AlertCircle, Shield } from 'lucide-react'

export default function ActiveProtocols() {
    const protocols = [
        { title: 'Daily Volatility', value: '3.47%', status: 'MODERATE', icon: TrendingUp, color: 'text-blue-400', bgColor: 'bg-blue-500/10', borderColor: 'border-blue-500/30' },
        { title: 'Current Strategy', value: 'SMA 200 + RSI', status: 'ACTIVE', icon: AlertCircle, color: 'text-purple-400', bgColor: 'bg-purple-500/10', borderColor: 'border-purple-500/30' },
        { title: 'Risk Status', value: 'SAFE', status: 'OK', icon: Shield, color: 'text-emerald-500', bgColor: 'bg-emerald-500/10', borderColor: 'border-emerald-500/30' },
    ]

    return (
        <div>
            <h2 className="text-lg font-mono font-semibold text-white mb-4 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                ACTIVE PROTOCOLS
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {protocols.map((protocol) => {
                    const Icon = protocol.icon
                    return (
                        <motion.div
                            key={protocol.title}
                            whileHover={{ y: -4, borderColor: 'rgba(255,255,255,0.2)' }}
                            className={`p-6 rounded-xl bg-white/5 backdrop-blur-xl border border-white/10 hover:bg-white/[0.07] transition-all duration-300 ${protocol.borderColor}`}
                        >
                            <div className="flex items-start justify-between mb-4">
                                <div className={`p-3 rounded-lg ${protocol.bgColor}`}>
                                    <Icon className={`w-5 h-5 ${protocol.color}`} />
                                </div>
                                <span className="text-xs font-mono font-semibold text-emerald-500 bg-emerald-500/20 px-2 py-1 rounded">{protocol.status}</span>
                            </div>
                            <h3 className="text-sm font-mono text-zinc-400 mb-2">{protocol.title}</h3>
                            <p className={`text-2xl font-mono font-bold ${protocol.color}`}>{protocol.value}</p>
                        </motion.div>
                    )
                })}
            </div>
        </div>
    )
}
