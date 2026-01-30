import { useEffect, useRef } from 'react'
import { motion } from 'framer-motion'

export default function CinematicBackground() {
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

        const draw = () => {
            ctx.clearRect(0, 0, width, height)

            // 1. Draw The Grid
            ctx.beginPath()
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.03)'
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
            ctx.fillStyle = 'rgba(16, 185, 129, 0.15)' // Emerald
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
    }, [])

    return (
        <div className="fixed inset-0 w-full h-full overflow-hidden z-0 pointer-events-none bg-[#09090b]">
            {/* Base: Zinc-950 (Professional Dark) */}
            <div className="absolute inset-0 bg-gradient-to-tr from-[#000000] via-[#09090b] to-[#18181b]" />

            {/* Geometric Grid Canvas */}
            <canvas ref={canvasRef} className="absolute inset-0 z-0" />

            {/* Subtle Vignette */}
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_0%,rgba(0,0,0,0.8)_100%)] z-10" />
        </div>
    )
}
