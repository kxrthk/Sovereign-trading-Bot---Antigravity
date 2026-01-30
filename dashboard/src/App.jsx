import { useState, useEffect } from 'react';
import { Target, Activity, Settings, Zap, BookOpen, Eye, ArrowLeft, LineChart, ClipboardList, Award, Sparkles } from 'lucide-react';
import { AnimatePresence, motion } from 'framer-motion';

import Sidebar from './components/sidebar';
import SystemStatus from './components/system-status';
import ActiveProtocols from './components/active-protocols';
import AlphaModule from './components/AlphaModule';
import PerformanceModule from './components/PerformanceModule';
import SettingsModule from './components/SettingsModule';
import VisionCenter from './components/VisionCenter';
import Journal from './components/Journal';
import LiveJournal from './components/live-journal';
import GaugeComponent from './components/gauge';
import SuperChart from './components/SuperChart';
import HolographicCard from './components/ui/HolographicCard';
import MouseParticles from './components/ui/MouseParticles';
import QRCodeModal from './components/ui/QRCodeModal';

// NEW COMPONENTS
import DailyPulse from './components/DailyPulse';
import TrophyCabinet from './components/TrophyCabinet';
import BacktestModule from './components/BacktestModule'; // NEW
import ForecastModule from './components/ForecastModule'; // NEW
import VoiceControl from './components/VoiceControl';
import LoginPage from './components/LoginPage';
import axios from 'axios';

// --- GLOBAL API CONFIGURATION ---
// 1. If running locally (localhost:8000), use relative path (Fast).
// 2. If running on Vercel/Cloud, connect to the Laptop via Ngrok.
const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const NGROK_URL = "https://densimetrically-nontortuous-emerson.ngrok-free.dev"; // Ver: 16:15 FORCE UPDATE

axios.defaults.baseURL = isLocal ? "" : NGROK_URL;

console.log(`[SYSTEM] API Mode: ${isLocal ? "LOCAL (Direct)" : "REMOTE (Ngrok Bridge)"}`);
console.log(`[SYSTEM] Target Brain: ${axios.defaults.baseURL || "localhost"}`);


// Configure Axios Default Logic for Token
const setupAxiosInterceptors = (onUnauth) => {
    // Add Token to every request if exists
    axios.interceptors.request.use(config => {
        const token = localStorage.getItem('sovereign_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    });

    // Handle 401 (Logout)
    axios.interceptors.response.use(
        response => response,
        error => {
            if (error.response && error.response.status === 401) {
                onUnauth();
            }
            return Promise.reject(error);
        }
    );
};

function App() {
    const [activeTab, setActiveTab] = useState('dashboard');
    const [history, setHistory] = useState(['dashboard']); // Navigation History
    const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
    const [theme, setTheme] = useState('dark');
    const [metrics, setMetrics] = useState({ gross: 0, net: 0, percent: 0, confidence: 0 });
    const [showQR, setShowQR] = useState(false);

    // --- AUTH STATE ---
    const [token, setToken] = useState(localStorage.getItem('sovereign_token'));

    const handleLogout = () => {
        localStorage.removeItem('sovereign_token');
        setToken(null);
    };

    // Setup Axios Interceptors only once
    useEffect(() => {
        setupAxiosInterceptors(handleLogout);
    }, []);

    // If NO TOKEN, Login Page is rendered below in JSX to avoid Hook Rule Violation (Rendered fewer hooks than expected)


    // --- FETCH METRICS (Realtime) ---
    useEffect(() => {
        if (!token) return; // Guard: Don't fetch if not logged in

        const fetchMetrics = async () => {
            try {
                // Use AXIOS to ensure Bearer Token is attached
                const res = await axios.get('/api/status');
                const data = res.data;
                const startBalance = 2000;
                const currentBalance = data.wallet_balance || 2000;
                const pnl = currentBalance - startBalance;

                setMetrics({
                    gross: currentBalance,
                    net: pnl,
                    percent: ((pnl / startBalance) * 100).toFixed(1),
                    confidence: (data.latest_oracle_confidence * 100).toFixed(0) || 0
                });
            } catch (e) { console.error("Metrics Access:", e); }
        };
        fetchMetrics();
        const interval = setInterval(fetchMetrics, 5000); // Optimized to 5s (was 2s) to reduce lag
        return () => clearInterval(interval);
    }, [token]); // Add token dependency

    // --- THEME TOGGLE ---
    useEffect(() => {
        const savedTheme = localStorage.getItem('theme') || 'dark';
        setTheme(savedTheme);
        document.documentElement.classList.toggle('dark', savedTheme === 'dark');
    }, []);

    const toggleTheme = () => {
        const newTheme = theme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
        localStorage.setItem('theme', newTheme);
        document.documentElement.classList.toggle('dark', newTheme === 'dark');
    };

    const handleNav = (tabId) => {
        if (tabId === activeTab) return;
        setHistory(prev => [...prev, tabId]);
        setActiveTab(tabId);
    };

    const handleBack = () => {
        if (history.length <= 1) return;
        const newHistory = [...history];
        newHistory.pop();
        const prevTab = newHistory[newHistory.length - 1];
        setHistory(newHistory);
        setActiveTab(prevTab);
    };

    const navItems = [
        { id: 'dashboard', label: 'Mission Control', icon: Target },
        { id: 'vision', label: 'Vision Center', icon: Eye },
        { id: 'backtest', label: 'Backtest Lab', icon: LineChart }, // NEW
        { id: 'oracle', label: 'Oracle Prediction', icon: Sparkles }, // NEW
        { id: 'alpha', label: 'Alpha Signals', icon: Zap },
        { id: 'daily_pulse', label: 'Daily Pulse', icon: ClipboardList },
        { id: 'trophies', label: 'Trophy Cabinet', icon: Award },
        { id: 'performance', label: 'Performance', icon: Activity },
        { id: 'journal', label: 'Trade Journal', icon: BookOpen },
        { id: 'charts', label: 'Super Charts', icon: LineChart },
        { id: 'settings', label: 'Settings', icon: Settings },
    ];

    const renderContent = () => {
        switch (activeTab) {
            case 'dashboard':
                return (
                    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
                        <SystemStatus />

                        {/* MIDDLE ROW: Protocols (Top) + Gauges (Bottom Horizontal) */}
                        <div className="space-y-6">
                            <ActiveProtocols />

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <HolographicCard onClick={() => handleNav('alpha')} className="cursor-pointer hover:scale-[1.02] transition-transform">
                                    <div className="p-4">
                                        <GaugeComponent
                                            title="ALPHA"
                                            subtitle="Click for Details"
                                            grossValue={metrics.gross}
                                            netValue={metrics.net}
                                            percentage={metrics.percent}
                                        />
                                    </div>
                                </HolographicCard>
                                <HolographicCard>
                                    <div className="p-4">
                                        <GaugeComponent
                                            title="CONFIDENCE"
                                            subtitle="AI Prediction Accuracy"
                                            value={metrics.confidence}
                                            percentage={metrics.confidence}
                                            isPulse={true}
                                        />
                                    </div>
                                </HolographicCard>
                            </div>
                        </div>

                        {/* BOTTOM ROW: Journal (Full Width) */}
                        <LiveJournal />
                    </div >
                );
            case 'vision': return <VisionCenter />;
            case 'backtest': return <BacktestModule />; // NEW
            case 'oracle': return <ForecastModule />; // NEW
            case 'alpha': return <AlphaModule />;
            case 'daily_pulse': return <DailyPulse />;
            case 'trophies': return <TrophyCabinet />;
            case 'performance': return <PerformanceModule />;
            case 'journal': return <Journal />;
            case 'charts': return <SuperChart />;
            case 'settings': return <SettingsModule />;
            default: return <div className="text-white">Module Not Loaded</div>;
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 text-gray-900 dark:bg-black dark:text-gray-100 font-sans selection:bg-purple-500/30 overflow-hidden relative">
            {/* AUTH GUARD: If no token, show Login Page (but hooks still run above) */}
            {!token ? (
                <LoginPage onLogin={setToken} />
            ) : (
                <>
                    <div className="flex h-screen relative z-10">
                        <Sidebar
                            items={navItems}
                            activeTab={activeTab} // Note: Prop name was mismatching in some versions (active vs activeTab). Using activeTab to be safe, Sidebar expects 'activeTab' in previous read.
                            onSelect={handleNav}
                            onQRClick={() => setShowQR(true)}
                            collapsed={sidebarCollapsed}
                            setCollapsed={setSidebarCollapsed}
                        />

                        <main className={`flex-1 relative overflow-y-auto overflow-x-hidden transition-all duration-300 scroll-smooth will-change-scroll`}>
                            <div className="w-full px-4 pt-16 pb-32">

                                {/* HEADER WITH BACK BUTTON */}
                                <div className="flex items-center gap-4 mb-6">
                                    {history.length > 1 && (
                                        <button
                                            onClick={handleBack}
                                            className="p-2 rounded-full bg-white/10 hover:bg-white/20 border border-white/10 transition-all text-gray-400 hover:text-white"
                                            title="Go Back"
                                        >
                                            <ArrowLeft className="w-5 h-5" />
                                        </button>
                                    )}
                                    <h1 className="text-2xl font-bold tracking-tight uppercase opacity-50 flex items-center gap-2">
                                        {navItems.find(i => i.id === activeTab)?.label || "Sovereign Bot"}
                                        <span className="text-[10px] bg-emerald-500/10 text-emerald-500 px-1.5 py-0.5 rounded border border-emerald-500/20 tracking-normal font-mono">v37.0</span>
                                    </h1>
                                </div>

                                <AnimatePresence mode="wait">
                                    <motion.div
                                        key={activeTab}
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        exit={{ opacity: 0, y: -10 }}
                                        transition={{ duration: 0.3 }}
                                    >
                                        {renderContent()}
                                    </motion.div>
                                </AnimatePresence>
                            </div>
                        </main>
                    </div>

                    <QRCodeModal isOpen={showQR} onClose={() => setShowQR(false)} />
                    <VoiceControl />
                </>
            )}
        </div>
    );
}

export default App;
