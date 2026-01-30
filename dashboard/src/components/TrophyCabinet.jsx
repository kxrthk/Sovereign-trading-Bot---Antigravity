import React, { useState, useEffect } from 'react';
import { Award, Lock } from 'lucide-react';
import HolographicCard from './ui/HolographicCard';

const ALL_POSSIBLE_BADGES = [
    { id: 'sniper', name: "The Sniper", desc: "3 Consecutive Wins", icon: "🎯", rarity: "Legendary" },
    { id: 'diamond_hands', name: "Diamond Hands", desc: "Held >30m & Won", icon: "💎", rarity: "Epic" },
    { id: 'iron_will', name: "Iron Will", desc: "5 Trades w/o Interference", icon: "🛡️", rarity: "Rare" },
    { id: 'first_blood', name: "First Blood", desc: "First Profitable Trade", icon: "🩸", rarity: "Common" }
];

export default function TrophyCabinet() {
    const [unlocked, setUnlocked] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch('/api/trophies')
            .then(res => res.json())
            .then(data => {
                // API returns array of badge objects
                setUnlocked(data.map(b => b.name));
                setLoading(false);
            })
            .catch(() => setLoading(false));
    }, []);

    const isUnlocked = (name) => unlocked.includes(name);

    return (
        <div className="space-y-6 max-w-5xl mx-auto">
            <header className="mb-8 border-b border-white/10 pb-6">
                <h1 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
                    <Award className="w-8 h-8 text-yellow-400" />
                    Trophy Cabinet
                </h1>
                <p className="text-slate-400 mt-1">Trading Accolades & Achievements</p>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {ALL_POSSIBLE_BADGES.map((badge) => {
                    const active = isUnlocked(badge.name);

                    return (
                        <div key={badge.id} className={`relative group ${active ? '' : 'opacity-50 grayscale'}`}>
                            <HolographicCard className={`h-full transition-all duration-300 ${active ? 'border-yellow-500/30 shadow-[0_0_30px_-10px_rgba(234,179,8,0.3)]' : 'border-white/5'}`}>
                                <div className="p-6 flex flex-col items-center text-center gap-4 h-full justify-between">
                                    <div className={`text-6xl transition-transform duration-500 ${active ? 'scale-110 group-hover:scale-125' : 'scale-90 blur-[2px]'}`}>
                                        {active ? badge.icon : <Lock className="w-12 h-12 text-slate-700" />}
                                    </div>

                                    <div>
                                        <h3 className={`font-bold text-lg ${active ? 'text-white' : 'text-slate-500'}`}>{badge.name}</h3>
                                        <p className="text-xs text-slate-400 mt-2 font-mono h-8">{badge.desc}</p>
                                    </div>

                                    {active ? (
                                        <span className="text-[10px] uppercase tracking-widest text-yellow-500 font-bold px-2 py-1 bg-yellow-500/10 rounded border border-yellow-500/20 w-full">
                                            Unlocked
                                        </span>
                                    ) : (
                                        <span className="text-[10px] uppercase tracking-widest text-slate-600 font-bold px-2 py-1 bg-slate-800/50 rounded w-full">
                                            Locked
                                        </span>
                                    )}
                                </div>
                            </HolographicCard>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
