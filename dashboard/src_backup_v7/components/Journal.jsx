import React from 'react';

const Journal = ({ journalData }) => {
    // Reverse to show newest first
    const entries = [...journalData].reverse().slice(0, 10); // Last 10

    return (
        <div className="w-full h-full flex flex-col">

            {/* Table Header - Custom to match Image */}
            <div className="flex items-center px-6 py-4 bg-white/[0.03] border-b border-white/[0.05]">
                <div className="grid grid-cols-12 w-full text-[10px] font-bold text-zinc-500 uppercase tracking-widest">
                    <div className="col-span-2 flex items-center gap-2">Time <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" /></div>
                    <div className="col-span-2">Symbol</div>
                    <div className="col-span-2">Action</div>
                    <div className="col-span-2">Price</div>
                    <div className="col-span-1 flex items-center gap-1">RSI <div className="w-1.5 h-1.5 rounded-full bg-rose-500" /></div>
                    <div className="col-span-2">Internal Mood</div>
                    <div className="col-span-1 text-right">Result</div>
                </div>
            </div>

            {/* Table Body */}
            <div className="flex-1 overflow-y-auto min-h-[200px]">
                {entries.length === 0 ? (
                    <div className="h-full flex items-center justify-center flex-col text-zinc-600 gap-2 mb-10">
                        <div>No entries in the Matrix yet. waiting for market data...</div>
                    </div>
                ) : (
                    <div className="divide-y divide-white/[0.02]">
                        {entries.map((trade, idx) => (
                            <div key={idx} className="grid grid-cols-12 px-6 py-3 items-center hover:bg-white/[0.02] transition-colors text-sm group">
                                <div className="col-span-2 text-zinc-400 font-mono text-xs">{trade.timestamp?.split(' ')[1]?.split('.')[0] || '--:--'}</div>
                                <div className="col-span-2 font-medium text-white">{trade.symbol}</div>
                                <div className="col-span-2">
                                    <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider ${trade.action === 'BUY' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'}`}>
                                        {trade.action}
                                    </span>
                                </div>
                                <div className="col-span-2 text-zinc-300 font-mono">₹{trade.price}</div>
                                <div className="col-span-1 text-zinc-400 font-mono">{trade.rsi}</div>
                                <div className="col-span-2 text-zinc-400 italic text-xs">{trade.mood_at_time}</div>
                                <div className="col-span-1 text-right font-bold">
                                    {trade.result === 'WIN' && <span className="text-emerald-500">WIN</span>}
                                    {trade.result === 'LOSS' && <span className="text-rose-500">LOSS</span>}
                                    {trade.result === 'OPEN' && <span className="text-amber-500 animate-pulse">RUNNING</span>}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default Journal;
