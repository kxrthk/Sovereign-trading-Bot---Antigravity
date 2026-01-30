import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Sun, Moon, Activity } from 'lucide-react'
import GaugeComponent from './components/gauge'
import ActiveProtocols from './components/active-protocols'
import LiveJournal from './components/live-journal'
import Sidebar from './components/sidebar'
import SystemStatus from './components/system-status'
import AlphaModule from './components/AlphaModule'
import PerformanceModule from './components/PerformanceModule'
import SettingsModule from './components/SettingsModule'
import BotActionBar from './components/BotActionBar'
import { MobileAccessFab, MobileAccessModal } from './components/MobileAccess'
import { isMarketOpen, getMarketStatusConfig } from './utils/MarketHours'

// UI Components
import CinematicBackground from './components/ui/CinematicBackground'
import HolographicCard from './components/ui/HolographicCard'
import MouseParticles from './components/ui/MouseParticles'

export default function App() {
    const [activeTab, setActiveTab] = useState('dashboard');
    const [isMobileOpen, setIsMobileOpen] = useState(false);
    const [theme, setTheme] = useState('dark'); // 'dark' | 'light'
    const [marketStatus, setMarketStatus] = useState(isMarketOpen());

    // Sync Market Status every minute
    useEffect(() => {
        const interval = setInterval(() => {
            setMarketStatus(isMarketOpen());
        }, 60000);
        return () => clearInterval(interval);
    }, []);

    // Theme Classes
    const bgClass = theme === 'dark' ? 'text-zinc-100' : 'text-slate-900 selection:bg-orange-500/30';
    const marketConfig = getMarketStatusConfig(marketStatus);

    // Navigation Handler to switch tabs
    const handleNav = (tab) => setActiveTab(tab);

    // Animation Variants
    const containerVariants = {
        hidden: { opacity: 0 },
        show: { opacity: 1, transition: { staggerChildren: 0.15, delayChildren: 0.1 } },
    }
    const itemVariants = {
        hidden: { opacity: 0, y: 20 },
        show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: 'easeOut' } },
    }

    return (

        <div className={`min-h-screen overflow-hidden flex ${bgClass} font-sans tracking-tight transition-colors duration-500`}>
            {/* 1. Cinematic Video Background */}
            <CinematicBackground theme={theme} />

            {/* 2. Mouse Micro-Interaction */}
            <MouseParticles theme={theme} />

            {/* Navigation & Controls */}
            <Sidebar
                activeTab={activeTab}
                onTabChange={setActiveTab}
                onQRClick={() => setIsMobileOpen(true)}
            />
            <MobileAccessFab onClick={() => setIsMobileOpen(true)} />
            <MobileAccessModal isOpen={isMobileOpen} onClose={() => setIsMobileOpen(false)} />

            {/* Main Content Area */}
            <main className="flex-1 relative z-10 h-screen overflow-y-auto pb-20 scrollbar-hide">
                <div className="p-8 space-y-8 max-w-7xl mx-auto">

                    {/* Header */}
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="flex justify-between items-start"
                    >
                        <div>
                            <h1 className={`text-5xl font-bold mb-2 tracking-tighter bg-clip-text text-transparent bg-gradient-to-r ${theme === 'dark' ? 'from-white to-white/50' : 'from-slate-900 to-slate-600'}`}>
                                MISSION CONTROL
                            </h1>
                            <div className="flex items-center gap-4">
                                <p className={`font-mono text-sm tracking-widest uppercase ${theme === 'dark' ? 'text-zinc-500' : 'text-slate-500'}`}>Sovereign Trading Protocol v2.1 • {activeTab}</p>
                                {/* Market Badge */}
                                <div className={`flex items-center gap-2 px-3 py-1 rounded-full border ${theme === 'dark' ? 'border-white/10' : 'border-slate-900/10'} bg-black/20 backdrop-blur-md`}>
                                    <div className={`w-2 h-2 rounded-full ${marketConfig.color} ${marketConfig.glow} animate-pulse`} />
                                    <span className={`text-xs font-bold ${marketConfig.color}`}>{marketConfig.label}</span>
                                </div>
                            </div>
                        </div>

                        {/* Right Actions: System Status + Theme Toggle */}
                        <div className="flex items-center gap-6">
                            {/* Theme Toggle */}
                            <button
                                onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
                                className={`p-3 rounded-full border transition-all duration-300 ${theme === 'dark'
                                        ? 'bg-zinc-900 border-zinc-700 text-yellow-400 hover:bg-zinc-800'
                                        : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50 shadow-md'
                                    }`}
                            >
                                <motion.div
                                    initial={false}
                                    animate={{ rotate: theme === 'dark' ? 0 : 180 }}
                                    transition={{ duration: 0.5 }}
                                >
                                    {theme === 'dark' ? <Moon size={20} /> : <Sun size={20} />}
                                </motion.div>
                            </button>

                            <SystemStatus />
                        </div>
                    </motion.div>

                    {/* Views */}
                    {activeTab === 'dashboard' && (
                        <motion.div variants={containerVariants} initial="hidden" animate="show" className="space-y-8">
                            <motion.div variants={itemVariants}>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                    <HolographicCard className="cursor-pointer" onClick={() => setActiveTab('alpha')}>
                                        <div className="p-6">
                                            <GaugeComponent title="ALPHA" subtitle="Click for Trade Details" grossValue={24850} netValue={18420} percentage={74} />
                                        </div>
                                    </HolographicCard>

                                    <HolographicCard>
                                        <div className="p-6">
                                            <GaugeComponent title="ORACLE CONFIDENCE" subtitle="AI Prediction Accuracy" value={87} percentage={87} isPulse={true} />
                                        </div>
                                    </HolographicCard>
                                </div>
                            </motion.div>

                            <motion.div variants={itemVariants}>
                                <HolographicCard>
                                    <div className="p-6">
                                        <ActiveProtocols />
                                    </div>
                                </HolographicCard>
                            </motion.div>

                            <motion.div variants={itemVariants}>
                                <HolographicCard>
                                    <div className="p-6">
                                        <LiveJournal />
                                    </div>
                                </HolographicCard>
                            </motion.div>
                        </motion.div>
                    )}

                    {activeTab === 'alpha' && (
                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                            <AlphaModule />
                        </motion.div>
                    )}

                    {activeTab === 'performance' && (
                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                            <PerformanceModule />
                        </motion.div>
                    )}

                    {activeTab === 'settings' && (
                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                            <SettingsModule />
                        </motion.div>
                    )}

                </div>
            </main>

            {/* Persistent Bot Status Bar */}
            <BotActionBar />
        </div>
    )
}
