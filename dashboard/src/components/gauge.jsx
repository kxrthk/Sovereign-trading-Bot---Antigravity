import { motion } from 'framer-motion'
import CountUp from 'react-countup'

export default function GaugeComponent({
    title,
    subtitle,
    value,
    percentage,
    grossValue,
    netValue,
    isPulse = false,
}) {
    const circumference = 2 * Math.PI * 90
    const strokeDashoffset = circumference - (percentage / 100) * circumference

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6 }}
            className="relative p-8 rounded-2xl bg-white dark:bg-white/5 backdrop-blur-xl border border-gray-200 dark:border-white/10 hover:border-gray-300 dark:hover:border-white/20 hover:bg-gray-50 dark:hover:bg-white/[0.07] transition-all duration-300"
        >
            <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-primary/10 to-transparent opacity-0 hover:opacity-100 transition-opacity duration-300" />
            <div className="relative z-10 flex flex-col items-center gap-6">
                <div className="text-center">
                    <h3 className="text-lg font-mono font-semibold text-gray-900 dark:text-white">{title}</h3>
                    <p className="text-xs text-gray-500 dark:text-zinc-400 font-mono mt-1">{subtitle}</p>
                </div>
                <div className="relative w-48 h-48">
                    <svg className="w-full h-full transform -rotate-90" viewBox="0 0 200 200">
                        <circle cx="100" cy="100" r="90" fill="none" stroke="currentColor" className="text-gray-200 dark:text-[#1a2a3a]" strokeWidth="2" opacity="0.3" />
                        <motion.circle
                            cx="100" cy="100" r="90" fill="none" stroke="#10B981" strokeWidth="3"
                            strokeDasharray={circumference}
                            initial={{ strokeDashoffset: circumference }}
                            animate={{ strokeDashoffset }}
                            transition={{ duration: 1.2, ease: 'easeOut' }}
                            strokeLinecap="round"
                        />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                        {grossValue !== undefined ? (
                            <>
                                <div className="text-center">
                                    <p className="text-xs text-gray-500 dark:text-zinc-500 font-mono mb-1">GROSS</p>
                                    <p className="text-sm text-gray-600 dark:text-zinc-400 font-mono">
                                        ₹<CountUp end={grossValue} separator="," />
                                    </p>
                                </div>
                                <div className="w-16 h-px bg-emerald-500/30 my-3" />
                                <div className="text-center">
                                    <p className="text-xs text-gray-500 dark:text-zinc-500 font-mono mb-1">NET</p>
                                    <p className="text-3xl font-mono font-bold text-emerald-600 dark:text-emerald-500">
                                        ₹<CountUp end={netValue || 0} separator="," />
                                    </p>
                                </div>
                            </>
                        ) : (
                            <motion.p
                                animate={isPulse ? { scale: [1, 1.05, 1] } : {}}
                                transition={{ duration: 1, repeat: Infinity }}
                                className="text-4xl font-mono font-bold text-emerald-600 dark:text-emerald-500"
                            >
                                {percentage}%
                            </motion.p>
                        )}
                    </div>
                </div>
            </div>
        </motion.div>
    )
}
