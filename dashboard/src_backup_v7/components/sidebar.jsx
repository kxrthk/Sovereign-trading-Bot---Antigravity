import { motion } from 'framer-motion'
import { BarChart3, Settings, QrCode, LayoutDashboard } from 'lucide-react'

export default function Sidebar({ activeTab, onTabChange, onQRClick }) {
    const menuItems = [
        { id: 'dashboard', icon: LayoutDashboard, label: 'Dashboard' },
        { id: 'performance', icon: BarChart3, label: 'Performance' },
        { id: 'settings', icon: Settings, label: 'Settings' },
    ]

    return (
        <motion.aside
            initial={{ x: -100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="w-24 border-r border-white/10 backdrop-blur-xl bg-white/5 flex flex-col items-center justify-between py-8 sticky left-0 top-0 h-screen z-50"
        >
            <div className="flex flex-col items-center gap-8">
                <div className="w-12 h-12 rounded-lg bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center cursor-pointer">
                    <div className="w-6 h-6 bg-emerald-500 rounded-sm" />
                </div>
                <nav className="flex flex-col gap-6">
                    {menuItems.map((item) => {
                        const isActive = activeTab === item.id;
                        return (
                            <div
                                key={item.id}
                                onClick={() => onTabChange(item.id)}
                                className={`p-3 rounded-lg transition-all duration-200 cursor-pointer relative group ${isActive ? 'text-emerald-500 bg-emerald-500/10' : 'text-zinc-400 hover:bg-white/10 hover:text-emerald-500'}`}
                            >
                                <item.icon className="w-5 h-5" />
                                {isActive && (
                                    <motion.div
                                        layoutId="activeTabIndicator"
                                        className="absolute left-0 top-2 bottom-2 w-1 bg-emerald-500 rounded-r-full"
                                    />
                                )}
                            </div>
                        )
                    })}
                </nav>
            </div>
            <div className="flex flex-col gap-4">
                <button
                    onClick={onQRClick}
                    className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 hover:border-emerald-500/50 text-emerald-500 transition-colors"
                >
                    <QrCode className="w-5 h-5" />
                </button>
                <button
                    onClick={async () => {
                        if (confirm('⚠️ EMERGENCY: SHUT DOWN ALL TRADING SYSTEMS?')) {
                            try {
                                await fetch('http://localhost:8000/api/kill_switch', { method: 'POST' })
                                alert('SYSTEM HALTED. MANUALLY RESET REQUIRED.')
                            } catch (e) {
                                alert('FAILED TO REACH SERVER. PULL THE PLUG.')
                            }
                        }
                    }}
                    className="p-3 rounded-lg bg-red-500/10 border border-red-500/30 hover:border-red-500/50 hover:bg-red-500/20 text-red-500 transition-colors group"
                    title="EMERGENCY STOP"
                >
                    <div className="w-5 h-5 rounded-full border-2 border-red-500 flex items-center justify-center">
                        <div className="w-2 h-2 bg-red-500 rounded-sm group-hover:animate-pulse" />
                    </div>
                </button>
            </div>
        </motion.aside>
    )
}
