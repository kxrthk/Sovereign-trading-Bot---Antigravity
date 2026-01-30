import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown, BookOpen } from 'lucide-react'
import { useState, useEffect } from 'react'

export default function LiveJournal() {
    const [entries, setEntries] = useState([])

    useEffect(() => {
        const fetchEntries = async () => {
            try {
                const res = await fetch('http://localhost:8000/api/alpha_details')
                const data = await res.json()
                if (Array.isArray(data)) {
                    setEntries(data)
                }
            } catch (e) {
                console.error("Failed to fetch journal", e)
            }
        }

        // Initial Fetch
        fetchEntries()

        // Poll every 5 seconds
        const interval = setInterval(fetchEntries, 5000)
        return () => clearInterval(interval)
    }, [])

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                    <BookOpen className="w-6 h-6 text-purple-500" />
                    LIVE JOURNAL
                </h2>
                <div className="text-xs font-mono text-zinc-500">Real-time Strategy Execution</div>
            </div>

            <div className="overflow-hidden rounded-xl bg-white/5 backdrop-blur-xl border border-white/10">
                <div className="hidden md:grid grid-cols-[100px_80px_100px_100px_60px_100px_100px_1fr_100px] gap-4 p-4 border-b border-white/10 bg-white/[0.02] text-xs font-mono text-zinc-500">
                    <div>DATE</div><div>TIME</div><div>ORDER ID</div><div>SYMBOL</div><div>STATUS</div><div>ENTRY</div><div>EXIT</div><div>AI RATIONALE</div><div>P&L</div>
                </div>
                <div className="divide-y divide-white/5">
                    {entries.length === 0 ? (
                        <div className="p-8 text-center text-zinc-500 font-mono text-sm">
                            Waiting for Alpha Signals...
                        </div>
                    ) : (
                        entries.map((entry, idx) => (
                            <div key={entry.id || idx} className="hidden md:grid grid-cols-[100px_80px_100px_100px_60px_100px_100px_1fr_100px] gap-4 p-4 hover:bg-white/[0.05] transition-colors">
                                <div className="text-sm font-mono text-zinc-400">{entry.date}</div>
                                <div className="text-sm font-mono text-white">{entry.time}</div>
                                <div className="text-xs font-mono text-zinc-500 bg-white/5 px-2 py-1 rounded border border-white/5">{entry.orderId}</div>
                                <div className="text-sm font-mono font-semibold text-white">{entry.symbol}</div>
                                <div className={`text-sm font-mono font-bold flex items-center gap-1 ${entry.action === 'OPEN' ? 'text-emerald-500' : 'text-zinc-400'}`}>
                                    {entry.action}
                                </div>
                                <div className="text-sm font-mono text-emerald-400">
                                    {entry.entryPrice !== '-' ? `₹${parseFloat(entry.entryPrice).toFixed(2)}` : '-'}
                                </div>
                                <div className="text-sm font-mono text-amber-400">
                                    {entry.exitPrice !== '-' ? `₹${parseFloat(entry.exitPrice).toFixed(2)}` : '-'}
                                </div>
                                <div className="text-xs font-mono text-zinc-400 truncate">{entry.rationale}</div>
                                <div className={`text-sm font-mono font-semibold ${entry.profitability.includes('+') ? 'text-emerald-500' : entry.profitability.includes('-') && entry.profitability !== '-' ? 'text-red-500' : 'text-zinc-500'}`}>
                                    {entry.profitability}
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    )
}
