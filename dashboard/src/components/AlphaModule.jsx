import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { TrendingUp, Activity, AlertCircle } from 'lucide-react'

export default function AlphaModule() {
    const [trades, setTrades] = useState([])

    useEffect(() => {
        const fetchEntries = async () => {
            try {
                const res = await fetch('/api/alpha_details')
                const data = await res.json()
                if (Array.isArray(data)) {
                    setTrades(data)
                }
            } catch (e) {
                console.error("Failed to fetch Alpha Log", e)
            }
        }

        fetchEntries() // Initial Fetch
        const interval = setInterval(fetchEntries, 2000) // Poll every 2 seconds
        return () => clearInterval(interval)
    }, [])

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                    <TrendingUp className="w-6 h-6 text-emerald-600 dark:text-emerald-500" />
                    ALPHA GENERATION LOG
                </h2>
                <div className="text-xs font-mono text-gray-500 dark:text-zinc-500">Live Trade Execution Data</div>
            </div>

            <div className="overflow-hidden rounded-xl bg-white dark:bg-white/5 backdrop-blur-xl border border-gray-200 dark:border-white/10">
                <div className="grid grid-cols-[90px_90px_80px_180px_80px_80px_80px_80px_1fr] gap-4 p-4 border-b border-gray-200 dark:border-white/10 bg-gray-50 dark:bg-white/[0.02] text-xs font-mono text-gray-500 dark:text-zinc-500 uppercase tracking-wider">
                    <div>Date</div>
                    <div>Time</div>
                    <div>Source</div>
                    <div>Symbol</div>
                    <div>Order ID</div>
                    <div>Entry</div>
                    <div>Exit</div>
                    <div>ROI</div>
                    <div className="text-right">Rationale</div>
                </div>
                <div className="divide-y divide-gray-100 dark:divide-white/5 h-[500px] overflow-y-auto custom-scrollbar">
                    {trades.length === 0 ? (
                        <div className="h-full flex flex-col items-center justify-center text-gray-400 dark:text-zinc-500 opacity-50 space-y-4">
                            <Activity className="w-12 h-12 animate-pulse" />
                            <div className="font-mono text-sm">Waiting for Alpha Signals...</div>
                        </div>
                    ) : (
                        trades.map((trade, idx) => (
                            <motion.div
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: idx * 0.05 }}
                                key={trade.id || idx}
                                className="grid grid-cols-[90px_90px_80px_180px_80px_80px_80px_80px_1fr] gap-4 p-4 hover:bg-gray-50 dark:hover:bg-white/[0.05] transition-colors items-center text-sm"
                            >
                                <div className="font-mono text-gray-500 dark:text-zinc-400">{trade.date}</div>
                                <div className="font-mono text-gray-900 dark:text-zinc-500">{trade.time}</div>

                                <div>
                                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold tracking-wider ${trade.origin === 'USER' ? 'bg-purple-500/10 text-purple-400 border border-purple-500/20' : 'bg-blue-500/10 text-blue-400 border border-blue-500/20'}`}>
                                        {trade.origin || 'BOT'}
                                    </span>
                                </div>

                                <div className="font-bold text-gray-900 dark:text-white font-mono">{trade.symbol}</div>
                                <div className="font-mono text-xs text-gray-500 dark:text-zinc-600 truncate" title={trade.orderId}>{trade.orderId}</div>

                                <div className="font-mono text-emerald-600 dark:text-emerald-400">
                                    {trade.entryPrice !== '-' ? `₹${parseFloat(trade.entryPrice).toFixed(1)}` : '-'}
                                </div>
                                <div className="font-mono text-rose-600 dark:text-rose-400">
                                    {trade.exitPrice !== '-' ? `₹${parseFloat(trade.exitPrice).toFixed(1)}` : '-'}
                                </div>

                                <div className={`font-mono font-bold ${trade.profitability?.includes('+') ? 'text-emerald-600 dark:text-emerald-400' : trade.profitability?.includes('-') && trade.profitability !== '-' ? 'text-rose-600 dark:text-rose-400' : 'text-gray-500 dark:text-zinc-500'}`}>
                                    {trade.profitability || '-'}
                                </div>

                                <div className="text-sm font-medium text-gray-700 dark:text-zinc-300 text-right">
                                    {trade.rationale}
                                </div>
                            </motion.div>
                        ))
                    )}
                </div>
            </div>
        </div>
    )
}
