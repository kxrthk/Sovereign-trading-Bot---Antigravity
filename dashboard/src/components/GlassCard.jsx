import { motion } from 'framer-motion';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function GlassCard({
  children,
  className,
  delay = 0,
  onClick
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        duration: 0.5,
        delay: delay,
        ease: "easeOut"
      }}
      whileHover={{
        y: -5,
        boxShadow: "0 0 20px rgba(255, 255, 255, 0.05)"
      }}
      onClick={onClick}
      className={twMerge(
        "glass-panel rounded-2xl p-6 relative overflow-hidden transition-colors duration-300",
        className
      )}
    >
      <div className="relative z-10 w-full h-full">
        {children}
      </div>

      {/* Optional: Add a subtle gradient overlay if needed */}
      <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent pointer-events-none" />
    </motion.div>
  );
}
