import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { motion } from 'framer-motion';
import GlassCard from './ui/GlassCard';
import AnimatedCounter from './ui/AnimatedCounter';

ChartJS.register(ArcElement, Tooltip, Legend);

const createChartData = (value, color) => ({
    datasets: [
        {
            data: [value, 100 - value],
            backgroundColor: [color, 'rgba(255,255,255,0.05)'],
            borderWidth: 0,
            cutout: '85%',
            borderRadius: 20,
        },
    ],
});

export const AlphaGauge = ({ grossPnl, netPnl }) => {
    const isProfitable = grossPnl >= 0;
    // Cap at 100 for visual gauge, but show real numbers
    const gaugeValue = Math.min(Math.abs(grossPnl) / 100, 100);
    const color = '#10b981'; // Emerald

    return (
        <GlassCard className="h-[280px] flex items-center justify-center relative !bg-black/40 !border-white/10 overflow-hidden group">
            {/* Ambient Glow */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[180px] h-[180px] bg-emerald-500/10 rounded-full blur-[60px] group-hover:bg-emerald-500/20 transition-all duration-500" />

            <div className="flex items-center gap-10 z-10">
                {/* Gauge */}
                <div className="w-[180px] h-[180px] relative">
                    <Doughnut data={createChartData(75, color)} options={{ events: [], plugins: { legend: { display: false }, tooltip: { enabled: false } } }} />
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                        <span className="text-4xl font-bold text-white tracking-tighter">
                            <AnimatedCounter value={0.0} suffix="%" />
                        </span>
                    </div>
                </div>

                {/* Text Info */}
                <div className="flex flex-col gap-2">
                    <div className="text-zinc-400 text-sm font-bold tracking-widest uppercase">Alpha</div>
                    <div>
                        <div className="text-3xl font-bold text-emerald-400">
                            <AnimatedCounter value={0.0} suffix="%" />
                        </div>
                        <div className="text-zinc-500 text-xs mt-2">
                            Gross P&L: <span className="text-white font-mono">₹{grossPnl?.toLocaleString() || 0}</span>
                        </div>
                        <div className="text-zinc-500 text-xs">
                            Net: <span className="text-white font-mono">₹{netPnl?.toLocaleString() || 0}</span>
                        </div>
                    </div>
                </div>
            </div>
        </GlassCard>
    );
};

export const KarmaGauge = ({ oracleConf, mood }) => {
    const color = '#a855f7'; // Purple

    return (
        <GlassCard className="h-[280px] flex items-center justify-center relative !bg-black/40 !border-white/10 overflow-hidden group">
            {/* Ambient Glow */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[180px] h-[180px] bg-purple-500/10 rounded-full blur-[60px] group-hover:bg-purple-500/20 transition-all duration-500" />

            <div className="flex items-center gap-10 z-10">
                {/* Gauge */}
                <motion.div
                    className="w-[180px] h-[180px] relative"
                    animate={{ scale: [1, 1.02, 1] }}
                    transition={{ duration: 3, repeat: Infinity }}
                >
                    <Doughnut data={createChartData(oracleConf || 0, color)} options={{ events: [], plugins: { legend: { display: false }, tooltip: { enabled: false } } }} />
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                        <span className="text-4xl font-bold text-white tracking-tighter">
                            <AnimatedCounter value={Math.round(oracleConf || 0)} suffix="%" />
                        </span>
                    </div>
                </motion.div>

                {/* Text Info */}
                <div className="flex flex-col gap-2">
                    <div className="text-zinc-400 text-sm font-bold tracking-widest uppercase">Karma</div>
                    <div>
                        <div className="text-3xl font-bold text-purple-400">
                            <AnimatedCounter value={Math.round(oracleConf || 0)} suffix="%" />
                        </div>
                        <div className="text-zinc-500 text-xs mt-2 uppercase tracking-wider">
                            Oracle State
                        </div>
                        <div className="text-white text-sm font-medium">
                            {mood || 'Calibrating'}
                        </div>
                    </div>
                </div>
            </div>
        </GlassCard>
    );
};
