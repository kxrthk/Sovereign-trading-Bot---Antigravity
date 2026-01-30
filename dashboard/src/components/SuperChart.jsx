import React, { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import { createChart, ColorType, CandlestickSeries } from 'lightweight-charts';
import { motion, AnimatePresence } from 'framer-motion';
import { Settings, Play, Pause, RotateCcw, ChevronDown, Search } from 'lucide-react';
import GlassCard from './ui/GlassCard';

const ASSETS = [
    { symbol: "RELIANCE", name: "Reliance Industries", type: "STOCK" },
    { symbol: "TCS", name: "Tata Consultancy Svc", type: "STOCK" },
    { symbol: "HDFCBANK", name: "HDFC Bank Ltd", type: "STOCK" },
    { symbol: "INFY", name: "Infosys Limited", type: "STOCK" },
    { symbol: "NIFTY 50", name: "NSE Indice", type: "INDEX" },
    { symbol: "BANKNIFTY", name: "NSE Indice", type: "INDEX" },
];

const SuperChart = () => {
    const chartContainerRef = useRef();
    const [candleSeries, setCandleSeries] = useState(null);
    const slLineRef = useRef(null);
    const targetLineRef = useRef(null);
    const [isPlaying, setIsPlaying] = useState(true);
    const [showDropdown, setShowDropdown] = useState(false);
    const [showTypeDropdown, setShowTypeDropdown] = useState(false);
    const [orderType, setOrderType] = useState('MARKET');
    const [timeframe, setTimeframe] = useState('15m');
    const [notification, setNotification] = useState(null);

    const handleOrder = async (side) => {
        const price = orderType === 'LIMIT' ? controls.limitPrice : controls.entry;
        const msg = `SENDING ${side} ORDER: ${controls.symbol} @ ${price.toFixed(2)}...`;
        setNotification({ message: msg, type: 'info' });

        try {
            const response = await axios.post('/api/manual_trade', {
                symbol: controls.symbol,
                action: side,
                quantity: controls.quantity,
                price: price,
                order_type: orderType,
                origin: "USER",
                stop_loss: controls.stopLoss,
                target: controls.target
            });

            const data = response.data;

            if (data.status === 'success') {
                setNotification({
                    message: `✅ ORDER EXECUTED: ${side} ${controls.symbol} (ID: ${data.order_id || 'CONFIRMED'})`,
                    type: 'success'
                });
            } else {
                setNotification({
                    message: `❌ FAILED: ${data.message || 'Unknown Error'}`,
                    type: 'error'
                });
            }
        } catch (error) {
            console.error(error);
            const errMsg = error.response?.data?.detail || error.message;
            setNotification({ message: `❌ NET ERROR: ${errMsg}`, type: 'error' });
        }

        setTimeout(() => setNotification(null), 5000);
    };

    const TIMEFRAMES = [
        { label: '1m', value: 60 },
        { label: '5m', value: 300 },
        { label: '15m', value: 900 },
        { label: '30m', value: 1800 },
        { label: '1H', value: 3600 },
        { label: '4H', value: 14400 },
        { label: '1D', value: 86400 },
    ];

    // Control Stats
    const [walletBalance, setWalletBalance] = useState(0);
    const [riskPerTrade, setRiskPerTrade] = useState(500); // Default Fallback, updated from API
    const [isSmartSizing, setIsSmartSizing] = useState(true); // Default to Smart for Beginners

    const [controls, setControls] = useState({
        symbol: "RELIANCE",
        entry: 2400.00,
        stopLoss: 2380.00,
        target: 2450.00,
        limitPrice: 2410.00,
        quantity: 1
    });

    // Mock Data Generator (Parameterized)
    const generateInitialData = (basePrice = 2400) => {
        let initialData = [];
        const intervalSeconds = TIMEFRAMES.find(t => t.label === timeframe)?.value || 900;
        let time = new Date(Date.now() - 1000 * intervalSeconds * 1000).getTime() / 1000;
        let price = basePrice;

        for (let i = 0; i < 1000; i++) {
            let volatility = basePrice * 0.002; // 0.2% volatility
            let change = (Math.random() - 0.5) * volatility;
            let open = price;
            let close = price + change;
            let high = Math.max(open, close) + Math.random() * (volatility * 0.5);
            let low = Math.min(open, close) - Math.random() * (volatility * 0.5);

            initialData.push({
                time: time + (i * intervalSeconds),
                open, high, low, close
            });
            price = close;
        }
        return initialData;
    };

    // Asset Switcher
    const handleAssetChange = (asset) => {
        setControls({
            ...controls,
            symbol: asset.symbol,
            entry: 2400 + (Math.random() * 500), // Randomize Mock Price
        });
        setShowDropdown(false);
    };

    // 1. Fetch Settings & Balance
    useEffect(() => {
        const initData = async () => {
            try {
                // Balance (Using Axios for Auth)
                const statusRes = await axios.get('/api/status');
                const statusData = statusRes.data;
                setWalletBalance(statusData.wallet_balance || 0);

                // Risk Settings
                const settingsRes = await axios.get('/api/settings');
                const settingsData = settingsRes.data;
                if (settingsData && settingsData.risk_per_trade) {
                    setRiskPerTrade(settingsData.risk_per_trade);
                }
            } catch (e) { console.error("Init failed", e); }
        };
        initData();
    }, []);

    // 2. SMART SIZING LOGIC (The "Pro" feature for Beginners)
    useEffect(() => {
        if (!isSmartSizing) return;

        const price = orderType === 'LIMIT' ? controls.limitPrice : controls.entry;
        const sl = controls.stopLoss;

        if (price > 0 && sl > 0 && price !== sl) {
            const riskPerShare = Math.abs(price - sl);
            // Formula: Quantity = RiskMoney / RiskPerShare
            let rawQty = Math.floor(riskPerTrade / riskPerShare);

            // Safety Limits
            if (rawQty < 1) rawQty = 1;
            if (rawQty > 1000) rawQty = 1000; // Cap for safety

            if (rawQty !== controls.quantity) {
                setControls(prev => ({ ...prev, quantity: rawQty }));
            }
        }
    }, [controls.entry, controls.stopLoss, controls.limitPrice, orderType, isSmartSizing, riskPerTrade]);

    // 3. Initialize Chart
    useEffect(() => {
        if (!chartContainerRef.current) return;

        const chart = createChart(chartContainerRef.current, {
            layout: {
                background: { type: ColorType.Solid, color: 'transparent' }, // TRANSPARENT
                textColor: '#9ca3af',
            },
            grid: {
                vertLines: { color: 'rgba(255, 255, 255, 0.05)' },
                horzLines: { color: 'rgba(255, 255, 255, 0.05)' },
            },
            width: chartContainerRef.current.clientWidth,
            height: chartContainerRef.current.clientHeight,
            timeScale: {
                borderColor: 'rgba(255, 255, 255, 0.1)',
            },
            rightPriceScale: {
                borderColor: 'rgba(255, 255, 255, 0.1)',
            },
        });

        const newSeries = chart.addSeries(CandlestickSeries, {
            upColor: '#10b981',
            downColor: '#ef4444',
            borderVisible: false,
            wickUpColor: '#10b981',
            wickDownColor: '#ef4444',
        });

        const data = generateInitialData(controls.entry);
        newSeries.setData(data);
        setCandleSeries(newSeries);

        // RESET REFS (Critical: Prevent "Zombie Lines" from previous chart instances)
        slLineRef.current = null;
        targetLineRef.current = null;

        // Efficient Resize Handler
        let resizeRequestId;
        const handleResize = () => {
            if (resizeRequestId) cancelAnimationFrame(resizeRequestId);
            resizeRequestId = requestAnimationFrame(() => {
                if (chartContainerRef.current) {
                    chart.applyOptions({ width: chartContainerRef.current.clientWidth, height: chartContainerRef.current.clientHeight });
                }
            });
        };

        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
            if (resizeRequestId) cancelAnimationFrame(resizeRequestId);
            chart.remove();
        };
    }, [controls.symbol, timeframe]); // Re-init on symbol or timeframe change

    // STOP LOSS UPDATE
    useEffect(() => {
        if (!candleSeries) return;

        // Remove old line if it exists
        if (slLineRef.current) {
            try {
                candleSeries.removePriceLine(slLineRef.current);
            } catch (e) {
                console.warn("Retrying SL removal", e);
            }
            slLineRef.current = null;
        }

        // Validate and Create new line
        const price = parseFloat(controls.stopLoss);
        if (!isNaN(price)) {
            slLineRef.current = candleSeries.createPriceLine({
                price: price,
                color: '#ef4444',
                lineWidth: 2,
                lineStyle: 2,
                axisLabelVisible: true,
                title: 'SL',
            });
        }
    }, [controls.stopLoss, candleSeries]);

    // TARGET UPDATE
    useEffect(() => {
        if (!candleSeries) return;

        // Remove old line
        if (targetLineRef.current) {
            try {
                candleSeries.removePriceLine(targetLineRef.current);
            } catch (e) {
                console.warn("Retrying TP removal", e);
            }
            targetLineRef.current = null;
        }

        // Validate and Create new line
        const price = parseFloat(controls.target);
        if (!isNaN(price)) {
            targetLineRef.current = candleSeries.createPriceLine({
                price: price,
                color: '#10b981',
                lineWidth: 2,
                lineStyle: 2,
                axisLabelVisible: true,
                title: 'TP',
            });
        }
    }, [controls.target, candleSeries]);

    return (
        <div className="flex flex-col h-[calc(100vh-100px)] gap-4 p-4 text-white relative">

            {/* NOTIFICATION TOAST */}
            <AnimatePresence>
                {notification && (
                    <motion.div
                        initial={{ opacity: 0, y: -20, x: '-50%' }}
                        animate={{ opacity: 1, y: 50, x: '-50%' }}
                        exit={{ opacity: 0, y: -20, x: '-50%' }}
                        className={`absolute top-0 left-1/2 z-50 px-6 py-3 rounded-xl border backdrop-blur-md shadow-2xl font-mono text-sm font-bold flex items-center gap-3 ${notification.type === 'success'
                            ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-400'
                            : 'bg-rose-500/20 border-rose-500/50 text-rose-400'
                            }`}
                    >
                        <div className={`w-2 h-2 rounded-full ${notification.type === 'success' ? 'bg-emerald-500' : 'bg-rose-500'} animate-pulse`} />
                        {notification.message}
                    </motion.div>
                )}
            </AnimatePresence>

            {/* TOP NAVBAR */}
            <GlassCard className="h-16 flex items-center justify-between px-6 z-20 shrink-0 !overflow-visible">
                <div className="flex items-center gap-6">
                    {/* ASSET SELECTOR */}
                    <div className="relative">
                        <motion.button
                            whileTap={{ scale: 0.95 }}
                            onClick={() => setShowDropdown(!showDropdown)}
                            className="flex items-center gap-4 bg-white/5 hover:bg-white/10 px-4 py-2.5 rounded-xl transition-all border border-white/5 min-w-[200px] justify-between group"
                        >
                            <div className="flex flex-col items-start gap-0.5">
                                <span className="text-sm font-bold tracking-wide text-white group-hover:text-amber-400 transition-colors">{controls.symbol}</span>
                                <span className="text-[10px] text-gray-400 font-mono tracking-wider">NSE EQUITY</span>
                            </div>
                            <ChevronDown className={`w-4 h-4 text-gray-500 group-hover:text-white transition-all duration-300 ${showDropdown ? 'rotate-180' : ''}`} />
                        </motion.button>

                        <AnimatePresence>
                            {showDropdown && (
                                <motion.div
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: 10 }}
                                    className="absolute top-full left-0 mt-2 w-64 bg-gray-900/95 backdrop-blur-xl border border-white/10 rounded-xl shadow-2xl overflow-hidden z-50"
                                >
                                    <div className="p-2 border-b border-white/5">
                                        <div className="flex items-center gap-2 px-2 py-1.5 bg-black/40 rounded-lg text-gray-400">
                                            <Search className="w-3 h-3" />
                                            <input className="bg-transparent border-none outline-none text-xs w-full text-white placeholder-gray-600" placeholder="Search symbol..." />
                                        </div>
                                    </div>
                                    <div className="max-h-64 overflow-y-auto">
                                        {ASSETS.map(asset => (
                                            <button
                                                key={asset.symbol}
                                                onClick={() => handleAssetChange(asset)}
                                                className="w-full flex items-center justify-between px-4 py-3 hover:bg-white/5 transition-colors text-left group"
                                            >
                                                <div>
                                                    <div className="font-bold text-sm text-gray-200 group-hover:text-white">{asset.symbol}</div>
                                                    <div className="text-[10px] text-gray-500">{asset.name}</div>
                                                </div>
                                                <span className="text-[10px] bg-white/5 px-1.5 py-0.5 rounded text-gray-500">{asset.type}</span>
                                            </button>
                                        ))}
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>

                    <div className="h-8 w-px bg-white/10" />

                    {/* TIMEFRAME SELECTOR */}
                    <div className="flex bg-black/40 rounded-lg p-1 border border-white/5">
                        {TIMEFRAMES.map(tf => (
                            <button
                                key={tf.label}
                                onClick={() => setTimeframe(tf.label)}
                                className={`px-3 py-1 text-[10px] font-mono font-bold rounded-md transition-all ${timeframe === tf.label
                                    ? 'bg-white/10 text-white shadow-lg'
                                    : 'text-gray-500 hover:text-gray-300 hover:bg-white/5'
                                    }`}
                            >
                                {tf.label}
                            </button>
                        ))}
                    </div>

                    <div className="h-8 w-px bg-white/10" />

                    <div className="flex gap-6 text-sm font-mono text-gray-400 items-center h-full">
                        <div className="flex flex-col justify-center">
                            <span className="text-[10px] opacity-60">PRICE</span>
                            <span className="text-emerald-400 font-bold">{controls.entry.toFixed(2)}</span>
                        </div>
                        <div className="flex flex-col justify-center">
                            <span className="text-[10px] opacity-60">24H CHG</span>
                            <span className="text-emerald-400">+1.24%</span>
                        </div>

                        <div className="h-8 w-px bg-white/10 mx-2" />

                        <div className="flex flex-col justify-center text-right mr-2">
                            <span className="text-[10px] opacity-60">BALANCE</span>
                            <span className="text-white font-bold font-mono">₹{walletBalance.toLocaleString('en-IN', { maximumFractionDigits: 2 })}</span>
                            <span className="text-[8px] text-gray-600 font-mono tracking-widest text-right mt-0.5">v2.1 PATCHED</span>
                        </div>

                        <div className="flex items-center gap-2">
                            <span className="flex items-center gap-1.5 text-[10px] text-emerald-500 bg-emerald-500/10 px-3 py-1.5 rounded-full border border-emerald-500/20 shadow-[0_0_10px_rgba(16,185,129,0.2)]">
                                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                                LIVE
                            </span>
                        </div>
                    </div>
                </div>
            </GlassCard>

            {/* MAIN CONTENT AREA */}
            <div className="flex-1 flex gap-4 min-h-0">
                {/* CHART */}
                <div className="flex-1 rounded-xl relative overflow-hidden ring-1 ring-white/5 bg-gradient-to-tr from-white/5 to-transparent backdrop-blur-sm">
                    {/* This div is absolutely positioned to ensure chart takes full space without flex collapse */}
                    <div ref={chartContainerRef} className="absolute inset-0" />
                </div>

                {/* SIDEBAR */}
                <GlassCard className="w-72 flex flex-col p-5 space-y-5 bg-gray-900/60 backdrop-blur-md border-l border-white/5">
                    <div className="flex items-center gap-2 text-purple-400">
                        <Settings className="w-4 h-4" />
                        <h3 className="font-bold text-xs tracking-widest">ORDER BLOTTER</h3>
                    </div>

                    <div className="space-y-4 flex-1 overflow-y-auto">
                        <div className="space-y-1">
                            <label className="text-[10px] text-gray-500 font-mono">STOCK SYMBOL</label>
                            <input
                                disabled
                                type="text"
                                value={controls.symbol}
                                className="w-full bg-black/40 border border-white/5 rounded-lg px-3 py-2 font-mono text-sm text-gray-400 cursor-not-allowed"
                            />
                        </div>

                        <div className="grid grid-cols-2 gap-3">
                            <div className="space-y-1">
                                <label className="text-[10px] text-gray-500 font-mono">QTY</label>
                                <input
                                    type="number"
                                    min="1"
                                    value={controls.quantity}
                                    onChange={(e) => {
                                        const val = e.target.value;
                                        // Allow empty string to let user delete (backspace) without forcing '1'
                                        if (val === '') {
                                            setControls({ ...controls, quantity: '' });
                                        } else {
                                            const num = parseInt(val);
                                            // Only update if it's a valid number
                                            if (!isNaN(num)) {
                                                setControls({ ...controls, quantity: num });
                                            }
                                        }
                                        if (isSmartSizing) setIsSmartSizing(false); // Manual override disables Smart Mode
                                    }}
                                    className={`w-full bg-black/40 border rounded-lg px-3 py-2 font-mono text-sm text-white focus:outline-none transition-colors ${isSmartSizing ? 'border-purple-500/50 shadow-[0_0_10px_rgba(168,85,247,0.2)]' : 'border-white/5'
                                        }`}
                                />
                                {isSmartSizing && <span className="text-[8px] text-purple-400 absolute right-1 -top-1">SMART</span>}
                            </div>
                            <div className="space-y-1 relative">
                                <label className="text-[10px] text-gray-500 font-mono">TYPE</label>
                                <button
                                    onClick={() => setShowTypeDropdown(!showTypeDropdown)}
                                    className="w-full flex items-center justify-between bg-black/40 border border-white/5 rounded-lg px-3 py-2 font-mono text-sm text-white hover:bg-white/5 transition-colors"
                                >
                                    <span>{orderType}</span>
                                    <ChevronDown className={`w-3 h-3 text-gray-500 transition-transform ${showTypeDropdown ? 'rotate-180' : ''}`} />
                                </button>

                                <AnimatePresence>
                                    {showTypeDropdown && (
                                        <motion.div
                                            initial={{ opacity: 0, y: 5 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            exit={{ opacity: 0, y: 5 }}
                                            className="absolute top-full left-0 w-full mt-1 bg-gray-900 border border-white/10 rounded-lg shadow-xl overflow-hidden z-20"
                                        >
                                            {['MARKET', 'LIMIT'].map(type => (
                                                <button
                                                    key={type}
                                                    onClick={() => { setOrderType(type); setShowTypeDropdown(false); }}
                                                    className={`w-full text-left px-3 py-2 text-xs font-mono hover:bg-white/10 transition-colors ${orderType === type ? 'text-emerald-400 bg-emerald-500/10' : 'text-gray-400'}`}
                                                >
                                                    {type}
                                                </button>
                                            ))}
                                        </motion.div>
                                    )}
                                </AnimatePresence>
                            </div>
                        </div>

                        {/* LIMIT PRICE INPUT (Conditional) */}
                        <AnimatePresence>
                            {orderType === 'LIMIT' && (
                                <motion.div
                                    initial={{ opacity: 0, height: 0 }}
                                    animate={{ opacity: 1, height: 'auto' }}
                                    exit={{ opacity: 0, height: 0 }}
                                    className="overflow-hidden"
                                >
                                    <div className="space-y-1">
                                        <label className="text-[10px] text-blue-400/80 font-mono">LIMIT PRICE</label>
                                        <div className="relative">
                                            <input
                                                type="number"
                                                value={controls.limitPrice}
                                                onChange={(e) => setControls({ ...controls, limitPrice: parseFloat(e.target.value) })}
                                                className="w-full bg-blue-500/5 border border-blue-500/20 rounded-lg pl-3 pr-8 py-2 font-mono text-sm text-blue-400 focus:border-blue-500/50 outline-none transition-colors"
                                            />
                                            <span className="absolute right-3 top-2.5 text-[10px] text-blue-500/50">INR</span>
                                        </div>
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        <div className="h-px bg-white/5" />

                        <div className="space-y-1">
                            <label className="text-[10px] text-rose-400/80 font-mono">STOP LOSS</label>
                            <div className="relative">
                                <input
                                    type="number"
                                    value={controls.stopLoss}
                                    onChange={(e) => setControls({ ...controls, stopLoss: parseFloat(e.target.value) })}
                                    className="w-full bg-rose-500/5 border border-rose-500/20 rounded-lg pl-3 pr-8 py-2 font-mono text-sm text-rose-400 focus:border-rose-500/50 outline-none transition-colors"
                                />
                                <span className="absolute right-3 top-2.5 text-[10px] text-rose-500/50">INR</span>
                            </div>
                        </div>

                        <div className="space-y-1">
                            <label className="text-[10px] text-emerald-400/80 font-mono">TARGET</label>
                            <div className="relative">
                                <input
                                    type="number"
                                    value={controls.target}
                                    onChange={(e) => setControls({ ...controls, target: parseFloat(e.target.value) })}
                                    className="w-full bg-emerald-500/5 border border-emerald-500/20 rounded-lg pl-3 pr-8 py-2 font-mono text-sm text-emerald-400 focus:border-emerald-500/50 outline-none transition-colors"
                                />
                                <span className="absolute right-3 top-2.5 text-[10px] text-emerald-500/50">INR</span>
                            </div>
                        </div>

                        {/* SMART SIZE TOGGLE */}
                        <div className="flex items-center justify-between pt-2">
                            <div className="flex flex-col">
                                <label className="text-[10px] text-gray-500 font-mono">SMART SIZE (AUTO-RISK)</label>
                                <span className="text-[9px] text-gray-600">Risking ₹{riskPerTrade} / Trade</span>
                            </div>
                            <button
                                onClick={() => setIsSmartSizing(!isSmartSizing)}
                                className={`w-10 h-5 rounded-full transition-colors relative ${isSmartSizing ? 'bg-purple-500' : 'bg-gray-700'}`}
                            >
                                <div className={`absolute top-1 w-3 h-3 bg-white rounded-full transition-all ${isSmartSizing ? 'left-6' : 'left-1'}`} />
                            </button>
                        </div>
                    </div>

                    {/* Recommended Logic */}
                    {(() => {
                        const isSellSetup = parseFloat(controls.stopLoss) > parseFloat(controls.target);
                        const isBuySetup = parseFloat(controls.stopLoss) < parseFloat(controls.target);

                        return (
                            <div className="flex gap-2 pt-2">
                                <button
                                    onClick={() => handleOrder('BUY')}
                                    className={`flex-1 relative border rounded-lg py-3 font-bold text-sm transition-all hover:scale-[1.02] active:scale-[0.98] ${isBuySetup
                                        ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50 shadow-[0_0_15px_rgba(16,185,129,0.3)] opacity-100 z-10'
                                        : 'bg-emerald-500/5 text-emerald-400/40 border-emerald-500/10 opacity-50'
                                        }`}
                                >
                                    BUY
                                    {isBuySetup && <span className="absolute -top-2 left-1/2 -translate-x-1/2 text-[8px] bg-emerald-500 text-black px-1.5 rounded-full font-bold tracking-tighter">SMART</span>}
                                </button>
                                <button
                                    onClick={() => handleOrder('SELL')}
                                    className={`flex-1 relative border rounded-lg py-3 font-bold text-sm transition-all hover:scale-[1.02] active:scale-[0.98] ${isSellSetup
                                        ? 'bg-rose-500/20 text-rose-400 border-rose-500/50 shadow-[0_0_15px_rgba(244,63,94,0.3)] opacity-100 z-10'
                                        : 'bg-rose-500/5 text-rose-400/40 border-rose-500/10 opacity-50'
                                        }`}
                                >
                                    SELL
                                    {isSellSetup && <span className="absolute -top-2 left-1/2 -translate-x-1/2 text-[8px] bg-rose-500 text-white px-1.5 rounded-full font-bold tracking-tighter">SMART</span>}
                                </button>
                            </div>
                        );
                    })()}
                </GlassCard>
            </div>
        </div>
    );
};

export default SuperChart;
