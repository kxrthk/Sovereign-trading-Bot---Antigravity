import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Camera, FileText, Target, Shield, AlertTriangle, CheckCircle, Brain, RefreshCw } from 'lucide-react';
import axios from 'axios';
import HolographicCard from './ui/HolographicCard';
import NeuralLink from './NeuralLink';

const ModeButton = ({ mode, currentMode, setMode, icon: Icon, label, color }) => (
    <button
        onClick={() => setMode(mode)}
        className={`relative flex flex-col items-center justify-center p-4 rounded-xl border transition-all duration-300 ${currentMode === mode
            ? `bg-${color}-500/20 border-${color}-400 text-${color}-400 shadow-[0_0_20px_rgba(var(--color-${color}-500),0.3)]`
            : 'bg-black/40 border-white/10 text-gray-400 hover:border-white/30 hover:bg-white/5'
            }`}
    >
        <Icon className={`w-6 h-6 mb-2 ${currentMode === mode ? 'scale-110' : ''}`} />
        <span className="text-xs font-bold tracking-wider">{label}</span>
        {currentMode === mode && (
            <motion.div
                layoutId="activeMode"
                className={`absolute inset-0 rounded-xl border-2 border-${color}-500/50`}
                initial={false}
                transition={{ type: "spring", stiffness: 300, damping: 30 }}
            />
        )}
    </button>
);

const VisionCenter = () => {
    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [mode, setMode] = useState('SWING');
    const [analysis, setAnalysis] = useState(null);
    const [loading, setLoading] = useState(false);
    const [stage, setStage] = useState("IDLE"); // SCANNING, CITING, REASONING, DECIDING
    const [error, setError] = useState(null);
    const [dragActive, setDragActive] = useState(false);

    const handleDrag = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    }, []);

    const handleDrop = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0]);
        }
    }, []);

    const handleChange = (e) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            handleFile(e.target.files[0]);
        }
    };

    const handleFile = (file) => {
        setFile(file);
        setPreview(URL.createObjectURL(file));
        setAnalysis(null);
        setError(null);
    };

    const analyzeChart = async () => {
        if (!file) return;
        setLoading(true);
        setError(null);

        const formData = new FormData();
        formData.append('file', file);
        formData.append('mode', mode);

        try {
            // --- STAGE 1: SCANNING ---
            setStage("SCANNING");
            await new Promise(r => setTimeout(r, 1500)); // Cinematic Delay

            // --- STAGE 2: CITING ---
            setStage("CITING");
            await new Promise(r => setTimeout(r, 1500));

            // --- STAGE 3: REASONING ---
            setStage("REASONING");
            // Assuming backend is on localhost:8000
            const res = await axios.post('/api/analyze-chart', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            // --- STAGE 4: DECIDING ---
            setStage("DECIDING");
            await new Promise(r => setTimeout(r, 1000));

            if (res.data.status === 'success') {
                setAnalysis(res.data.analysis);
            } else {
                setError(res.data.message || "Analysis Failed");
            }
        } catch (err) {
            console.error("VISION ERROR:", err);
            setError(err.message || "Network Error");
        } finally {
            setLoading(false);
            setStage("IDLE");
        }
    };

    const saveToJournal = async () => {
        if (!analysis) return;
        try {
            await axios.post('/api/save-journal', {
                symbol: "VISION_UPLOAD", // Could add an input for this
                mode: mode,
                analysis: analysis,
                image_path: "Upload",
                user_notes: "Saved from Vision Center"
            });
            alert("Saved to Journal! 📔");
        } catch (err) {
            alert("Failed to save: " + err.message);
        }
    };

    return (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">

            {/* HEADER */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-black tracking-custom text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 drop-shadow-[0_0_10px_rgba(168,85,247,0.5)]">
                        VISION CENTER
                    </h2>
                    <p className="text-gray-400 mt-1">AI-Powered Chart Analysis (Gemini 1.5)</p>
                </div>
                <div className="flex items-center space-x-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/20">
                    <Brain className="w-4 h-4 text-purple-400" />
                    <span className="text-xs font-mono text-purple-300">NEURAL ENGINE READY</span>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                {/* LEFT COLUMN: UPLOAD & CONTROLS */}
                <div className="space-y-6">
                    <HolographicCard className="p-1">
                        <div
                            className={`relative h-64 rounded-xl border-2 border-dashed flex flex-col items-center justify-center transition-all duration-300 ${dragActive ? 'border-purple-400 bg-purple-500/10' : 'border-gray-700 bg-black/40 hover:border-gray-500'
                                }`}
                            onDragEnter={handleDrag}
                            onDragLeave={handleDrag}
                            onDragOver={handleDrag}
                            onDrop={handleDrop}
                        >
                            <input
                                type="file"
                                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                onChange={handleChange}
                                accept="image/*"
                            />

                            {preview ? (
                                <img src={preview} alt="Chart" className="h-full w-full object-contain rounded-lg" />
                            ) : (
                                <div className="text-center p-6 space-y-3 pointer-events-none">
                                    <div className="w-16 h-16 rounded-full bg-gray-800 flex items-center justify-center mx-auto">
                                        <Upload className="w-8 h-8 text-gray-400" />
                                    </div>
                                    <div>
                                        <p className="text-sm font-bold text-gray-300">Drop Chart Image Here</p>
                                        <p className="text-xs text-gray-500">or click to browse</p>
                                    </div>
                                </div>
                            )}
                        </div>
                    </HolographicCard>

                    {/* MODE SELECTOR */}
                    <div className="grid grid-cols-3 gap-3">
                        <ModeButton mode="SCALP" setMode={setMode} currentMode={mode} icon={Target} label="SCALP" color="yellow" />
                        <ModeButton mode="SWING" setMode={setMode} currentMode={mode} icon={FileText} label="SWING" color="blue" />
                        <ModeButton mode="RISK" setMode={setMode} currentMode={mode} icon={Shield} label="RISK" color="red" />
                    </div>

                    {/* DEEP SCAN BUTTON */}
                    <button
                        onClick={() => setMode('DEEP_SCAN')}
                        className={`w-full py-3 rounded-xl border transition-all duration-300 flex items-center justify-center gap-2 ${mode === 'DEEP_SCAN'
                            ? 'bg-purple-500/20 border-purple-400 text-purple-400 shadow-[0_0_20px_rgba(168,85,247,0.3)]'
                            : 'bg-black/40 border-white/10 text-gray-400 hover:border-purple-500/50 hover:text-purple-400'
                            }`}
                    >
                        <Brain className="w-5 h-5" />
                        <span className="text-xs font-bold tracking-wider">DEEP SCAN (ALL-IN-ONE)</span>
                    </button>

                    <button
                        onClick={analyzeChart}
                        disabled={!file || loading}
                        className={`w-full py-4 rounded-xl font-black text-sm tracking-wider uppercase transition-all duration-300 flex items-center justify-center space-x-2 ${!file || loading
                            ? 'bg-gray-800 text-gray-500 cursor-not-allowed'
                            : 'bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-[0_0_20px_rgba(147,51,234,0.5)] hover:scale-[1.02]'
                            }`}
                    >
                        {loading ? (
                            <>
                                <RefreshCw className="w-5 h-5 animate-spin" />
                                <span>ANALYZING...</span>
                            </>
                        ) : (
                            <>
                                <Camera className="w-5 h-5" />
                                <span>SCAN CHART</span>
                            </>
                        )}
                    </button>
                </div>

                {/* RIGHT COLUMN: ANALYSIS RESULT */}
                <div className="lg:col-span-2">
                    <HolographicCard className="h-full min-h-[500px] flex flex-col relative overflow-hidden">
                        <div className="p-6 flex-1 overflow-y-auto custom-scrollbar flex flex-col">
                            {!analysis && !loading && !error && (
                                <div className="flex-grow flex flex-col items-center justify-center text-gray-600 space-y-4">
                                    <Brain className="w-24 h-24 opacity-20" />
                                    <p className="text-sm">Upload a chart to begin neural analysis.</p>
                                </div>
                            )}

                            {loading && (
                                <div className="flex-grow flex flex-col items-center justify-center space-y-6 h-full w-full">
                                    <NeuralLink stage={stage} />
                                </div>
                            )}

                            {error && (
                                <div className="p-6 rounded-xl bg-red-500/10 border border-red-500/30 flex items-start space-x-4">
                                    <AlertTriangle className="w-6 h-6 text-red-400 shrink-0" />
                                    <div>
                                        <h3 className="text-red-400 font-bold">Analysis Failed</h3>
                                        <p className="text-red-300/80 text-sm mt-1">{error}</p>
                                    </div>
                                </div>
                            )}

                            {analysis && (
                                <div className="space-y-6 animate-in fade-in duration-500">
                                    <div className="flex items-center justify-between pb-4 border-b border-gray-800">
                                        <span className="text-xs font-mono text-purple-400">GEMINI-1.5-FLASH // {mode}_MODE</span>
                                        <span className="text-xs text-gray-500">{new Date().toLocaleTimeString()}</span>
                                    </div>

                                    <div className="prose prose-invert max-w-none text-gray-300 leading-relaxed whitespace-pre-wrap">
                                        {analysis}
                                    </div>

                                    <div className="pt-6 border-t border-gray-800 flex justify-end">
                                        <button
                                            onClick={saveToJournal}
                                            className="px-6 py-2 rounded-lg bg-green-500/10 border border-green-500/30 text-green-400 text-sm font-bold hover:bg-green-500/20 transition-colors flex items-center space-x-2"
                                        >
                                            <CheckCircle className="w-4 h-4" />
                                            <span>SAVE TO JOURNAL</span>
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>
                    </HolographicCard>
                </div>

            </div>
        </div>
    );
};

export default VisionCenter;
