import { useEffect, useRef } from 'react'
import { motion } from 'framer-motion'

export default function CinematicBackground({ theme = 'dark' }) {
    const canvasRef = useRef(null)

    useEffect(() => {
        const canvas = canvasRef.current
        if (!canvas) return

        const ctx = canvas.getContext('2d')
        let width = canvas.width = window.innerWidth
        let height = canvas.height = window.innerHeight

        const resize = () => {
            width = canvas.width = window.innerWidth
            height = canvas.height = window.innerHeight
        }
        window.addEventListener('resize', resize)

        // Grid Properties
        const gridSize = 40
        let offset = 0

        // Theme Configuration
        const isDark = theme === 'dark';
        const gridColor = isDark ? 'rgba(255, 255, 255, 0.12)' : 'rgba(249, 115, 22, 0.15)'; // White vs Orange
        const nodeColor = isDark ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)'; // Emerald vs Red
        const bgColor = isDark
            ? 'linear-gradient(to top right, #000000, #09090b, #18181b)'
            : 'linear-gradient(to top right, #FFFBEB, #FEF3C7, #FFF7ED)'; // Zinc Dark vs Amber Light

        const draw = () => {
            ctx.clearRect(0, 0, width, height)

            // 1. Draw The Grid
            ctx.beginPath()
            ctx.strokeStyle = gridColor
            ctx.lineWidth = 1

            // Vertical Lines
            for (let x = 0; x <= width; x += gridSize) {
                ctx.moveTo(x, 0)
                ctx.lineTo(x, height)
            }

            // Horizontal Lines (Moving)
            for (let y = offset; y <= height; y += gridSize) {
                ctx.moveTo(0, y)
                ctx.lineTo(width, y)
            }
            ctx.stroke()

            // 2. Moving Nodes (Data Points)
            ctx.fillStyle = nodeColor
            for (let x = 0; x <= width; x += gridSize * 4) {
                for (let y = offset; y <= height; y += gridSize * 4) {
                    if (Math.random() > 0.95) { // Random flickering nodes
                        ctx.beginPath()
                        ctx.arc(x, y, 2, 0, Math.PI * 2)
                        ctx.fill()
                    }
                }
            }

            offset = (offset + 0.2) % gridSize
            requestAnimationFrame(draw)
        }
        draw()

        return () => window.removeEventListener('resize', resize)
    }, [theme]) // Critical: Re-run when theme changes

    // Background Container
    // We use dynamic styles for simple gradient switching vs canvas re-draw
    const containerStyle = {
        background: theme === 'dark'
            ? 'radial-gradient(circle at center, #18181b 0%, #09090b 50%, #000000 100%)'
            : 'radial-gradient(circle at center, #FFF7ED 0%, #FFFBEB 50%, #FEF3C7 100%)',
    };

    return (
        <div
            className="fixed inset-0 w-full h-full overflow-hidden z-0 pointer-events-none transition-all duration-1000"
            style={containerStyle}
        >
            {/* Geometric Grid Canvas */}
            <canvas ref={canvasRef} className="absolute inset-0 z-0 opacity-60" />

            {/* Subtle Vignette */}
            <div className={`absolute inset-0 z-10 ${theme === 'dark'
                ? 'bg-[radial-gradient(circle_at_center,transparent_0%,rgba(0,0,0,0.8)_100%)]'
                : 'bg-[radial-gradient(circle_at_center,transparent_0%,rgba(251,191,36,0.1)_100%)]'
                }`} />
        </div>
    )
}
