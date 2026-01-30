import { useState, useEffect } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion'
import { Save, ShieldAlert, Activity } from 'lucide-react'

export default function SettingsModule() {
    const [settings, setSettings] = useState({
        risk_per_trade: 0.25,
        max_daily_loss: 5000,
        min_confidence: 0.60,
        trading_mode: 'PAPER'
    });
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        const load = async () => {
            try {
                const res = await axios.get('/api/settings');
                // Ensure defaults
                setSettings(prev => ({ ...prev, ...res.data }));
            } catch (e) { console.error(e); }
        }
        load();
    }, []);

    const handleChange = (key, val) => setSettings(p => ({ ...p, [key]: val }));

    const handleSave = async () => {
        setSaving(true);
        try {
            await axios.post('/api/settings', settings);
            alert("Configuration Saved!");
        } catch (e) {
            alert("Save Failed");
        }
        setSaving(false);
    };

    return (
        <div className="max-w-2xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">SYSTEM CONFIGURATION</h2>

            <div className="space-y-6">

                {/* STRATEGY PROFILER */}
                <div className="p-6 rounded-xl bg-white dark:bg-white/5 border border-gray-200 dark:border-white/10 backdrop-blur-md">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-2 bg-blue-500/10 rounded-lg text-blue-600 dark:text-blue-400"><Activity className="w-5 h-5" /></div>
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Strategy Aggression</h3>
                    </div>

                    <div className="grid grid-cols-3 gap-3">
                        {[{ label: 'AGGRESSIVE', val: 0.50, color: 'rose' }, { label: 'BALANCED', val: 0.60, color: 'indigo' }, { label: 'SAFE', val: 0.75, color: 'emerald' }].map(opt => (
                            <button
                                key={opt.label}
                                onClick={() => handleChange('min_confidence', opt.val)}
                                className={`py-3 rounded-lg border text-xs font-bold transition-all ${settings.min_confidence === opt.val
                                        ? `bg-${opt.color}-500 text-white border-${opt.color}-500`
                                        : 'bg-black/20 border-white/5 text-gray-400 hover:bg-white/5'
                                    }`}
                            >
                                {opt.label}
                            </button>
                        ))}
                    </div>
                    <p className="text-xs text-gray-500 mt-3 text-center">
                        Minimum Confidence to Trade: <b>{settings.min_confidence * 100}%</b>
                    </p>
                </div>

                {/* Risk Management */}
                <div className="p-6 rounded-xl bg-white dark:bg-white/5 border border-gray-200 dark:border-white/10 backdrop-blur-md">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-2 bg-rose-500/10 rounded-lg text-rose-600 dark:text-rose-400"><ShieldAlert className="w-5 h-5" /></div>
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Risk Management</h3>
                    </div>
                    <div className="space-y-6">

                        {/* Capital Allocation Slider */}
                        <div>
                            <div className="flex justify-between text-sm mb-2">
                                <span className="text-gray-600 dark:text-zinc-400">Capital Allocation per Trade</span>
                                <span className="text-emerald-600 dark:text-emerald-400 font-mono">{(settings.risk_per_trade * 100).toFixed(0)}%</span>
                            </div>
                            <input
                                type="range" min="0.05" max="1.0" step="0.05"
                                value={settings.risk_per_trade}
                                onChange={(e) => handleChange('risk_per_trade', parseFloat(e.target.value))}
                                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-emerald-500"
                            />
                        </div>

                        {/* Max Loss Input */}
                        <div>
                            <div className="flex justify-between text-sm mb-2">
                                <span className="text-gray-600 dark:text-zinc-400">Max Daily Loss Limit</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <span className="text-gray-500">₹</span>
                                <input
                                    type="number"
                                    value={settings.max_daily_loss}
                                    onChange={(e) => handleChange('max_daily_loss', parseFloat(e.target.value))}
                                    className="w-full bg-black/30 border border-white/10 rounded px-3 py-2 text-white font-mono text-sm focus:border-rose-500/50 outline-none"
                                />
                            </div>
                        </div>
                    </div>
                </div>

                <button
                    onClick={handleSave}
                    disabled={saving}
                    className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-bold tracking-wide transition-colors flex items-center justify-center gap-2"
                >
                    {saving ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <Save className="w-4 h-4" />}
                    {saving ? "SAVING..." : "SAVE CONFIGURATION"}
                </button>
            </div>
        </div>
    )
}
