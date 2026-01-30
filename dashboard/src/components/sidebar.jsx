import { motion, AnimatePresence } from 'framer-motion'
import { BarChart3, Settings, QrCode, LayoutDashboard, Menu, X, ChevronRight, Zap, Target, BookOpen, Eye, Activity, LineChart } from 'lucide-react'

export default function Sidebar({ items, activeTab, onSelect, onQRClick, collapsed, setCollapsed }) {
    const menuItems = items || [
        { id: 'dashboard', icon: LayoutDashboard, label: 'Dashboard' },
        { id: 'performance', icon: BarChart3, label: 'Performance' },
        { id: 'settings', icon: Settings, label: 'Settings' },
    ]

    const sidebarVariants = {
        expanded: { width: 256, transition: { type: "spring", stiffness: 200, damping: 25 } },
        collapsed: { width: 80, transition: { type: "spring", stiffness: 200, damping: 25 } }
    }

    const labelVariants = {
        expanded: { opacity: 1, x: 0, display: "block", transition: { delay: 0.2, duration: 0.3 } },
        collapsed: { opacity: 0, x: -10, transition: { duration: 0.05 }, transitionEnd: { display: "none" } }
    }

    return (
        <motion.aside
            initial={false}
            animate={collapsed ? "collapsed" : "expanded"}
            variants={sidebarVariants}
            className="border-r backdrop-blur-3xl flex flex-col justify-between py-6 sticky left-0 top-0 h-screen z-50 shadow-2xl bg-white/80 border-slate-200/50 text-slate-600 dark:bg-black/40 dark:border-white/5 dark:text-zinc-400 overflow-hidden"
        >
            <div className="flex flex-col gap-8 w-full px-3">
                {/* LOGO / TOGGLE */}
                <div
                    onClick={() => setCollapsed(!collapsed)}
                    className="flex items-center gap-3 px-3 cursor-pointer group select-none h-14"
                    title={collapsed ? "Expand" : "Collapse"}
                >
                    <div className="w-10 h-10 min-w-[2.5rem] rounded-xl flex items-center justify-center transition-all duration-500 bg-gradient-to-br from-amber-400 to-orange-500 shadow-lg shadow-orange-500/20 dark:from-emerald-500 dark:to-cyan-500 dark:shadow-emerald-500/20 group-hover:scale-105">
                        <div className="w-5 h-5 bg-white rounded-md opacity-90" />
                    </div>

                    <motion.div variants={labelVariants} className="whitespace-nowrap">
                        <h1 className="font-bold text-lg tracking-tight text-slate-800 dark:text-white">SOVEREIGN</h1>
                        <p className="text-[10px] uppercase tracking-widest text-slate-400 dark:text-zinc-500 font-bold">Trading Bot</p>
                    </motion.div>
                </div>

                {/* NAV ITEMS */}
                <nav className="flex flex-col gap-2 w-full">
                    {menuItems.map((item) => {
                        const isActive = activeTab === item.id;
                        return (
                            <div
                                key={item.id}
                                onClick={() => onSelect(item.id)}
                                className={`flex items-center gap-3 p-3 rounded-xl transition-all duration-200 cursor-pointer relative group overflow-hidden h-11 ${isActive
                                    ? 'text-amber-600 bg-amber-50 dark:text-emerald-400 dark:bg-white/5 shadow-sm'
                                    : 'hover:bg-slate-100 dark:hover:bg-white/5 hover:text-slate-900 dark:hover:text-white'
                                    }`}
                            >
                                <item.icon className={`w-5 h-5 min-w-[1.25rem] transition-colors ${isActive ? 'text-amber-500 dark:text-emerald-400' : 'group-hover:text-amber-500 dark:group-hover:text-emerald-400'}`} />

                                <motion.span variants={labelVariants} className="font-medium whitespace-nowrap">
                                    {item.label}
                                </motion.span>

                                {isActive && (
                                    <motion.div
                                        layoutId="activeTabIndicator"
                                        className="absolute left-0 top-2 bottom-2 w-1 rounded-r-full bg-amber-500 dark:bg-emerald-500"
                                    />
                                )}
                            </div>
                        )
                    })}
                </nav>
            </div>

            {/* FOOTER ACTIONS */}
            <div className="flex flex-col gap-3 px-3 w-full">
                <button
                    onClick={onQRClick}
                    className={`flex items-center gap-3 p-3 rounded-xl transition-colors bg-slate-100 hover:bg-slate-200 dark:bg-white/5 dark:hover:bg-white/10 text-slate-600 dark:text-zinc-400`}
                >
                    <QrCode className="w-5 h-5 min-w-[1.25rem]" />
                    <motion.span variants={labelVariants} className="text-sm font-medium whitespace-nowrap">Connect App</motion.span>
                </button>

                <button
                    onClick={async () => {
                        if (confirm('⚠️ EMERGENCY: SHUT DOWN ALL TRADING SYSTEMS?')) {
                            try {
                                await fetch('/api/kill_switch', { method: 'POST' })
                                alert('SYSTEM HALTED. MANUALLY RESET REQUIRED.')
                            } catch (e) {
                                alert('FAILED TO REACH SERVER. PULL THE PLUG.')
                            }
                        }
                    }}
                    className="flex items-center gap-3 p-3 rounded-xl bg-red-50 hover:bg-red-100 border border-red-200 dark:bg-red-500/10 dark:border-red-500/20 dark:hover:bg-red-500/20 text-red-600 dark:text-red-400 transition-colors group"
                    title="EMERGENCY STOP"
                >
                    <div className="w-5 h-5 min-w-[1.25rem] rounded-full border-2 border-current flex items-center justify-center">
                        <div className="w-2 h-2 bg-current rounded-sm group-hover:animate-pulse" />
                    </div>
                    <motion.span variants={labelVariants} className="text-sm font-bold whitespace-nowrap group-hover:text-red-700 dark:group-hover:text-red-300">KILL SWITCH</motion.span>
                </button>
            </div>
        </motion.aside>
    )
}
