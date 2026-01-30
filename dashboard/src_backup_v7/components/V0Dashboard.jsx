export default function V0Dashboard() {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-8 bg-zinc-950 min-h-screen text-zinc-50">
            <div className="col-span-1 md:col-span-2 lg:col-span-3">
                <h1 className="text-3xl font-bold tracking-tight">V0 Dashboard</h1>
                <p className="text-zinc-400">Placeholder component created.</p>
            </div>

            {/* Example Card */}
            <div className="p-6 rounded-xl bg-zinc-900 border border-zinc-800">
                <h3 className="font-semibold mb-2">Stat Card</h3>
                <p className="text-2xl font-mono">0.00</p>
            </div>
        </div>
    );
}
