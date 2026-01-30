import { useEffect, useRef } from "react";

export default function MouseParticles({ theme = 'dark' }) {
    const cursorRef = useRef(null);
    const pos = useRef({ x: 0, y: 0 }); // Current Position
    const mouse = useRef({ x: 0, y: 0 }); // Target Position (Mouse)

    useEffect(() => {
        const moveCursor = (e) => {
            mouse.current = { x: e.clientX, y: e.clientY };
        };

        const animate = () => {
            if (cursorRef.current) {
                // Magnetic Physics: Stronger pull when closer
                const dx = mouse.current.x - pos.current.x;
                const dy = mouse.current.y - pos.current.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                // Base speed 0.15 (smooth trail). 
                // Adds up to +0.35 speed when close (<150px), creating a "Snap" effect.
                let speed = 0.15;
                if (dist < 200) {
                    speed += (1 - (dist / 200)) * 0.35;
                }

                pos.current.x += dx * speed;
                pos.current.y += dy * speed;

                cursorRef.current.style.transform = `translate3d(${pos.current.x - 8}px, ${pos.current.y - 8}px, 0)`;
            }
            requestAnimationFrame(animate);
        };

        window.addEventListener("mousemove", moveCursor);
        const rafId = requestAnimationFrame(animate);

        return () => {
            window.removeEventListener("mousemove", moveCursor);
            cancelAnimationFrame(rafId);
        };
    }, []);

    return (
        <div
            ref={cursorRef}
            className={`fixed top-0 left-0 w-4 h-4 rounded-full border-[1.5px] pointer-events-none z-50 transition-colors duration-300 ${theme === 'dark'
                ? 'border-emerald-400/80 bg-emerald-500/10 shadow-[0_0_10px_rgba(52,211,153,0.3)]'
                : 'border-orange-500/80 bg-orange-500/10 shadow-[0_0_10px_rgba(249,115,22,0.3)]'
                }`}
            style={{ willChange: 'transform' }}
        />
    );
}
