import { motion, useSpring, useTransform, useMotionValue, animate } from 'framer-motion';
import { useEffect } from 'react';

export function AnimatedCounter({ value, prefix = "", suffix = "", decimals = 0, className }) {
    const motionValue = useMotionValue(0);
    const springValue = useSpring(motionValue, {
        damping: 30,
        stiffness: 100,
    });

    const displayValue = useTransform(springValue, (latest) => {
        if (decimals === 0) {
            return Math.round(latest).toLocaleString();
        }
        return latest.toFixed(decimals);
    });

    useEffect(() => {
        const controls = animate(motionValue, value, {
            duration: 1
        });
        return controls.stop;
    }, [value, motionValue]);

    return (
        <motion.span className={className}>
            {prefix}
            <motion.span>{displayValue}</motion.span>
            {suffix}
        </motion.span>
    );
}
