import { motion } from 'framer-motion'
import { Save, ShieldAlert, Cpu } from 'lucide-react'

export default function SettingsModule() {
    return (
        <div className="max-w-2xl mx-auto space-y-8">
            <h2 className="text-2xl font-bold text-white">SYSTEM CONFIGURATION</h2>

            <div className="space-y-6">

                {/* API Config */}
                <div className="p-6 rounded-xl bg-white/5 border border-white/10 backdrop-blur-md">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-2 bg-purple-500/20 rounded-lg text-purple-400"><Cpu className="w-5 h-5" /></div>
                        <h3 className="text-lg font-semibold text-white">API Connections</h3>
                    </div>
                    <div className="space-y-4">
                        <div>
                            <label className="block text-xs font-mono text-zinc-400 mb-1">BROKER API KEY</label>
                            <input type="password" value="************************" disabled className="w-full bg-black/40 border border-white/10 rounded px-3 py-2 text-zinc-500 font-mono text-sm" />
                        </div>
                        <div>
                            <label className="block text-xs font-mono text-zinc-400 mb-1">TELEGRAM BOT TOKEN</label>
                            <input type="password" value="************************" disabled className="w-full bg-black/40 border border-white/10 rounded px-3 py-2 text-zinc-500 font-mono text-sm" />
                        </div>
                    </div>
                </div>

                {/* Risk Management */}
                <div className="p-6 rounded-xl bg-white/5 border border-white/10 backdrop-blur-md">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-2 bg-rose-500/20 rounded-lg text-rose-400"><ShieldAlert className="w-5 h-5" /></div>
                        <h3 className="text-lg font-semibold text-white">Risk Management</h3>
                    </div>
                    <div className="space-y-6">
                        <div>
                            <div className="flex justify-between text-sm mb-2">
                                <span className="text-zinc-400">Capital Allocation per Trade</span>
                                <span className="text-emerald-400 font-mono">25%</span>
                            </div>
                            <div className="h-2 bg-black/40 rounded-full overflow-hidden">
                                <div className="h-full w-1/4 bg-emerald-500 rounded-full" />
                            </div>
                        </div>

                        <div>
                            <div className="flex justify-between text-sm mb-2">
                                <span className="text-zinc-400">Max Daily Loss Limit</span>
                                <span className="text-rose-400 font-mono">₹5,000</span>
                            </div>
                            <div className="h-2 bg-black/40 rounded-full overflow-hidden">
                                <div className="h-full w-[10%] bg-rose-500 rounded-full" />
                            </div>
                        </div>
                    </div>
                </div>

                <button className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-bold tracking-wide transition-colors flex items-center justify-center gap-2">
                    <Save className="w-4 h-4" />
                    SAVE CONFIGURATION
                </button>

            </div>
        </div>
    )
}
