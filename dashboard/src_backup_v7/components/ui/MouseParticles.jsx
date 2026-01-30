import { useEffect, useRef } from "react";

export default function MouseParticles() {
    const canvasRef = useRef(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext("2d");
        let animationFrameId;
        let particles = [];
        let mouse = { x: 0, y: 0 };

        // Resize canvas
        const resize = () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        };
        window.addEventListener("resize", resize);
        resize();

        // Track mouse with interpolation
        let lastMouse = { x: 0, y: 0 };

        const handleMouseMove = (e) => {
            const currentMouse = { x: e.clientX, y: e.clientY };

            // Calculate distance
            const dx = currentMouse.x - lastMouse.x;
            const dy = currentMouse.y - lastMouse.y;
            const dist = Math.sqrt(dx * dx + dy * dy);

            // Interpolate particles based on distance (Fill the gaps)
            // Spawn a particle every 2 pixels of movement (Ultra Dense)
            const steps = Math.max(1, Math.floor(dist / 2));

            for (let i = 0; i < steps; i++) {
                const t = i / steps;
                const x = lastMouse.x + dx * t;
                const y = lastMouse.y + dy * t;

                // Spawn particle at interpolated position
                particles.push(createParticle(x, y));
            }

            lastMouse = currentMouse;
            mouse.x = e.clientX;
            mouse.y = e.clientY;
        };
        window.addEventListener("mousemove", handleMouseMove);

        function createParticle(x, y) {
            return {
                x,
                y,
                size: Math.random() * 1.5 + 0.5, // Finer particles
                speedX: Math.random() * 0.5 - 0.25, // Less chaotic spread for "fluid" feel
                speedY: Math.random() * 0.5 - 0.25,
                life: 1.0,
                // Quant Colors: Emerald (Profit) to Cyan (Data)
                color: `hsl(${Math.random() > 0.5 ? 150 : 180}, 100%, 60%)`
            };
        }

        const animate = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            particles.forEach((p, index) => {
                p.x += p.speedX;
                p.y += p.speedY;
                p.life -= 0.02;
                p.size *= 0.95; // Shrink

                if (p.life <= 0) {
                    particles.splice(index, 1);
                } else {
                    ctx.globalAlpha = p.life;
                    ctx.fillStyle = p.color;
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                    ctx.fill();
                }
            });

            // Reset alpha
            ctx.globalAlpha = 1.0;

            // Draw Cursor Ring
            ctx.beginPath();
            ctx.strokeStyle = "rgba(16, 185, 129, 0.3)";
            ctx.lineWidth = 1;
            ctx.arc(mouse.x, mouse.y, 8, 0, Math.PI * 2);
            ctx.stroke();

            animationFrameId = requestAnimationFrame(animate);
        };

        animate();

        return () => {
            window.removeEventListener("resize", resize);
            window.removeEventListener("mousemove", handleMouseMove);
            cancelAnimationFrame(animationFrameId);
        };
    }, []);

    return (
        <canvas
            ref={canvasRef}
            className="fixed inset-0 pointer-events-none z-50 mix-blend-screen"
        />
    );
}
