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
        const interval = setInterval(fetchEntries, 5000) // Poll every 5 seconds
        return () => clearInterval(interval)
    }, [])

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                    <TrendingUp className="w-6 h-6 text-emerald-500" />
                    ALPHA GENERATION LOG
                </h2>
                <div className="text-xs font-mono text-zinc-500">Live Trade Execution Data</div>
            </div>

            <div className="overflow-hidden rounded-xl bg-white/5 backdrop-blur-xl border border-white/10">
                <div className="grid grid-cols-[100px_100px_100px_120px_1fr_100px_100px_100px] gap-4 p-4 border-b border-white/10 bg-white/[0.02] text-xs font-mono text-zinc-500 uppercase tracking-wider">
                    <div>Date</div>
                    <div>Time</div>
                    <div>Symbol</div>
                    <div>Order ID</div>
                    <div>Rationale</div>
                    <div>Entry</div>
                    <div>Exit</div>
                    <div>ROI</div>
                </div>
                <div className="divide-y divide-white/5 h-[500px] overflow-y-auto custom-scrollbar">
                    {trades.length === 0 ? (
                        <div className="h-full flex flex-col items-center justify-center text-zinc-500 opacity-50 space-y-4">
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
                                className="grid grid-cols-[100px_100px_100px_120px_1fr_100px_100px_100px] gap-4 p-4 hover:bg-white/[0.05] transition-colors items-center text-sm"
                            >
                                <div className="font-mono text-zinc-400">{trade.date}</div>
                                <div className="font-mono text-zinc-500">{trade.time}</div>
                                <div className="font-bold text-white font-mono">{trade.symbol}</div>
                                <div className="font-mono text-xs text-zinc-600 truncate" title={trade.orderId}>{trade.orderId}</div>

                                <div className="text-xs font-mono text-zinc-400">
                                    {trade.rationale}
                                </div>

                                <div className="font-mono text-emerald-400">
                                    {trade.entryPrice !== '-' ? `₹${trade.entryPrice}` : '-'}
                                </div>
                                <div className="font-mono text-rose-400">
                                    {trade.exitPrice !== '-' ? `₹${trade.exitPrice}` : '-'}
                                </div>

                                <div className={`font-mono font-bold ${trade.profitability?.includes('+') ? 'text-emerald-400' : trade.profitability?.includes('-') && trade.profitability !== '-' ? 'text-rose-400' : 'text-zinc-500'}`}>
                                    {trade.profitability || '-'}
                                </div>
                            </motion.div>
                        ))
                    )}
                </div>
            </div>
        </div>
    )
}
