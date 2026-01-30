import { motion, useSpring, useTransform } from 'framer-motion';
import { useState, useEffect } from 'react';

const AnimatedCounter = ({ value, prefix = '', suffix = '', className = '' }) => {
    const spring = useSpring(0, { stiffness: 50, damping: 20 });
    const display = useTransform(spring, (current) =>
        `${prefix}${Math.round(current).toLocaleString()}${suffix}`
    );

    useEffect(() => {
        spring.set(value);
    }, [spring, value]);

    return <motion.span className={className}>{display}</motion.span>;
};

export default AnimatedCounter;
