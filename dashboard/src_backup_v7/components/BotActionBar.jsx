import { motion } from 'framer-motion'
import { Terminal } from 'lucide-react'

export default function BotActionBar() {
    return (
        <div className="fixed bottom-0 left-0 md:left-24 right-0 z-40 bg-[#09090b]/90 border-t border-white/5 backdrop-blur-lg px-6 py-2 flex items-center justify-between">
            <div className="flex items-center gap-3">
                <div className="p-1.5 rounded bg-emerald-500/10">
                    <Terminal className="w-4 h-4 text-emerald-500" />
                </div>
                <div className="flex flex-col">
                    <span className="text-[10px] uppercase tracking-widest text-zinc-500 font-mono">Sovereign Intelligence</span>
                    <motion.span
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        key="action-text"
                        className="text-xs text-zinc-300 font-mono"
                    >
                        Scanned RELIANCE.NS: Holding position. RSI (42) is neutral. Waiting for Volume spike.
                    </motion.span>
                </div>
            </div>

            <div className="hidden md:flex items-center gap-4 text-[10px] text-zinc-600 font-mono uppercase tracking-wider">
                <span>Cycle: 5m</span>
                <span>Mode: Advisory</span>
                <span>Uptime: 14h 22m</span>
            </div>
        </div>
    )
}
