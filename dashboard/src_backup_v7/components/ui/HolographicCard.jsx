import { motion, useMotionTemplate, useMotionValue, useSpring } from "framer-motion";
import { useRef, useEffect } from "react";

const ROTATION_RANGE = 20; // Max tilt angle
const HALF_ROTATION_RANGE = ROTATION_RANGE / 2;

export default function HolographicCard({ children, className = "" }) {
    const ref = useRef(null);

    // Mouse Position Values
    const x = useMotionValue(0);
    const y = useMotionValue(0);

    // Smooth Physics (Spring)
    const xSpring = useSpring(x, { stiffness: 300, damping: 30 }); // Spotlight movement
    const ySpring = useSpring(y, { stiffness: 300, damping: 30 }); // Spotlight movement

    // Tilt Transforms
    const rotateX = useMotionValue(0);
    const rotateY = useMotionValue(0);

    // Smooth Tilt
    const rotateXSpring = useSpring(rotateX, { stiffness: 150, damping: 20 });
    const rotateYSpring = useSpring(rotateY, { stiffness: 150, damping: 20 });

    // Dynamic Background Gradient (The Spotlight)
    const background = useMotionTemplate`radial-gradient(
    600px circle at ${xSpring}px ${ySpring}px,
    rgba(16, 185, 129, 0.06),
    transparent 80%
  )`;

    // Magnetic Proximity Effect
    useEffect(() => {
        const handleGlobalMouseMove = (e) => {
            if (!ref.current) return;
            const rect = ref.current.getBoundingClientRect();

            // Calculate distance to center of card
            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;
            const distance = Math.sqrt(Math.pow(e.clientX - centerX, 2) + Math.pow(e.clientY - centerY, 2));

            // Proximity Threshold (e.g. 400px)
            const threshold = 400;
            if (distance < threshold) {
                // Calculate intensity (0 to 1) based on closeness
                const intensity = 1 - (distance / threshold);

                // Subtle lift toward mouse
                const moveX = (e.clientX - centerX) * 0.02 * intensity; // Slight pull
                const moveY = (e.clientY - centerY) * 0.02 * intensity;

                x.set(moveX); // Reuse for translation if preferred, or new values
                y.set(moveY);

                // Set glow opacity based on proximity
                ref.current.style.setProperty('--proximity-glow', intensity * 0.2); // Max 20% opacity
            } else {
                ref.current.style.setProperty('--proximity-glow', 0);
            }
        };

        window.addEventListener('mousemove', handleGlobalMouseMove);
        return () => window.removeEventListener('mousemove', handleGlobalMouseMove);
    }, [x, y]);

    const handleMouseMove = (e) => {
        // ... (Keep existing tilt logic)
        // We combine proximity movement with Tilt interaction
        if (!ref.current) return;

        const rect = ref.current.getBoundingClientRect();
        const width = rect.width;
        const height = rect.height;

        // Mouse relative to card
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;

        // Calculate rotation (-RANGE/2 to +RANGE/2)
        const rX = ((mouseY / height) * ROTATION_RANGE) - HALF_ROTATION_RANGE;
        const rY = ((mouseX / width) * ROTATION_RANGE) - HALF_ROTATION_RANGE;

        rotateX.set(rX * -1);
        rotateY.set(rY);
    };

    const handleMouseLeave = () => {
        // Reset tilt but proximity logic stays pending on global listener
        rotateX.set(0);
        rotateY.set(0);
    };

    return (
        <motion.div
            ref={ref}
            onMouseMove={handleMouseMove}
            onMouseLeave={handleMouseLeave}

            // Interaction: Scale Up & Ambient Float
            whileHover={{ scale: 1.02 }}
            animate={{ y: [0, -5, 0] }}
            transition={{
                y: { duration: 4, repeat: Infinity, ease: "easeInOut" },
                scale: { duration: 0.2 }
            }}

            style={{
                transformStyle: "preserve-3d",
                rotateX: rotateXSpring,
                rotateY: rotateYSpring,
            }}
            className={`relative group rounded-xl bg-black/40 border border-white/5 backdrop-blur-md overflow-hidden ${className}`}
        >
            {/* Spotlight Overlay */}
            <motion.div
                style={{ background }}
                className="absolute inset-0 z-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-xl"
            />

            {/* Content Layer (Lifted z-index) */}
            <div className="relative z-10 h-full">
                {children}
            </div>
        </motion.div>
    );
}
