import { motion } from 'framer-motion';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs) {
    return twMerge(clsx(inputs));
}

const GlassCard = ({ children, className, noHover = false, ...props }) => {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            whileHover={!noHover ? {
                scale: 1.02,
                backgroundColor: "rgba(255, 255, 255, 0.03)",
                borderColor: "rgba(255, 255, 255, 0.1)",
                boxShadow: "0 0 20px rgba(255,255,255,0.02)"
            } : {}}
            transition={{
                type: "spring",
                stiffness: 400,
                damping: 30
            }}
            className={cn(
                "relative backdrop-blur-2xl bg-white/[0.02] border border-white/[0.05] rounded-3xl overflow-hidden",
                "shadow-2xl shadow-black/50 ring-1 ring-white/5",
                "transition-colors duration-300",
                className
            )}
            {...props}
        >
            {/* Glossy Reflection Overlay */}
            <div className="absolute inset-0 bg-gradient-to-br from-white/[0.05] to-transparent pointer-events-none" />

            {/* Content */}
            <div className="relative z-10 h-full">
                {children}
            </div>
        </motion.div>
    );
};

export default GlassCard;
