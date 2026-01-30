import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

// A Holographic "Brain" Visualization
const NeuralLink = ({ stage = "IDLE" }) => {
    // Stages: SCANNING, CITING, REASONING, DECIDING
    const [activeNodes, setActiveNodes] = useState([]);

    // Logic to light up nodes based on stage
    useEffect(() => {
        if (stage === "SCANNING") setActiveNodes([0, 1, 2]); // Data Inputs
        if (stage === "CITING") setActiveNodes([3, 4, 5]);   // Knowledge Base
        if (stage === "REASONING") setActiveNodes([6, 7]);   // Logic Core
        if (stage === "DECIDING") setActiveNodes([8]);       // Final Output
    }, [stage]);

    // Fixed Node Positions for a "Circuit Tree" look
    const nodes = [
        // Level 1: Inputs (Bottom)
        { id: 0, x: 20, y: 80, label: "PRICE" },
        { id: 1, x: 50, y: 85, label: "VOL" },
        { id: 2, x: 80, y: 80, label: "RSI" },

        // Level 2: Knowledge (Middle)
        { id: 3, x: 30, y: 50, label: "STRATEGY" },
        { id: 4, x: 50, y: 50, label: "RISK.PDF" },
        { id: 5, x: 70, y: 50, label: "MACRO" },

        // Level 3: Logic (Upper Middle)
        { id: 6, x: 40, y: 30, label: "BULLISH" },
        { id: 7, x: 60, y: 30, label: "BEARISH" },

        // Level 4: Output (Top)
        { id: 8, x: 50, y: 10, label: "ALPHA" },
    ];

    // Connections (From -> To)
    const links = [
        [0, 3], [1, 3], [1, 4], [2, 5], // Input -> Knowledge
        [3, 6], [3, 7], [4, 6], [4, 7], [5, 7], // Knowledge -> Logic
        [6, 8], [7, 8] // Logic -> Decision
    ];

    return (
        <div className="w-full h-full min-h-[300px] flex items-center justify-center relative bg-black/20 rounded-xl overflow-hidden border border-purple-500/20">
            {/* Grid Background */}
            <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-10"></div>

            <svg viewBox="0 0 100 100" className="w-[80%] h-[80%] drop-shadow-[0_0_10px_rgba(168,85,247,0.5)]">

                {/* 1. Draw Lines */}
                {links.map(([start, end], i) => {
                    const n1 = nodes[start];
                    const n2 = nodes[end];
                    const isActive = activeNodes.includes(start) || activeNodes.includes(end);

                    return (
                        <g key={`link-${i}`}>
                            {/* Base Line */}
                            <motion.line
                                x1={n1.x} y1={n1.y}
                                x2={n2.x} y2={n2.y}
                                stroke={isActive ? "#a855f7" : "#333"}
                                strokeWidth="0.5"
                                initial={{ pathLength: 0 }}
                                animate={{ pathLength: 1 }}
                                transition={{ duration: 1, delay: i * 0.1 }}
                            />

                            {/* Pulse Particle */}
                            {isActive && (
                                <motion.circle
                                    r="1"
                                    fill="#fff"
                                    initial={{ cx: n1.x, cy: n1.y }}
                                    animate={{ cx: n2.x, cy: n2.y }}
                                    transition={{
                                        duration: 1.5,
                                        repeat: Infinity,
                                        ease: "linear",
                                        delay: i * 0.2
                                    }}
                                />
                            )}
                        </g>
                    );
                })}

                {/* 2. Draw Nodes */}
                {nodes.map((node, i) => {
                    const isActive = activeNodes.includes(node.id);
                    return (
                        <g key={`node-${i}`}>
                            <motion.circle
                                cx={node.x}
                                cy={node.y}
                                r={isActive ? 3 : 1.5}
                                fill={isActive ? "#d8b4fe" : "#1f2937"}
                                stroke={isActive ? "#a855f7" : "#374151"}
                                strokeWidth="0.5"
                                animate={{ scale: isActive ? [1, 1.2, 1] : 1 }}
                                transition={{ duration: 1, repeat: Infinity }}
                            />
                            <text
                                x={node.x}
                                y={node.y + 5}
                                fontSize="3"
                                textAnchor="middle"
                                fill={isActive ? "#fff" : "#4b5563"}
                                className="font-mono tracking-widest"
                            >
                                {node.label}
                            </text>
                        </g>
                    );
                })}

            </svg>

            {/* Status Overlay */}
            <div className="absolute bottom-4 left-0 right-0 text-center">
                <span className="text-xs font-mono text-purple-400 animate-pulse uppercase tracking-[0.2em]">
                    System Status: {stage}
                </span>
            </div>
        </div>
    );
};

export default NeuralLink;
