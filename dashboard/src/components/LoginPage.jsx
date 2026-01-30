import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Lock, User, Key, Shield, AlertTriangle } from 'lucide-react';
import HolographicCard from './ui/HolographicCard';
import axios from 'axios';

const LoginPage = ({ onLogin }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        // --- HARDCODED MASTER KEY (FOR VERCEL/OFFLINE MODE) ---
        // Since Vercel is Frontend-Only, we need a way to "Login" even if backend is unreachable.
        if (password === "sovereign" || password === "admin123" || password === "9392352630sk") {
            setTimeout(() => {
                const fakeToken = "sovereign-master-access-token-offline-mode";
                localStorage.setItem('sovereign_token', fakeToken);
                onLogin(fakeToken);
                setLoading(false);
            }, 800); // Fake Loading Delay
            return;
        }

        // --- REAL BACKEND AUTH ---
        // Prepare OAuth2 form data (URL Encoded)
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        try {
            const response = await axios.post('/token', formData.toString(), {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
            });

            const token = response.data.access_token;
            // Store token in localStorage
            localStorage.setItem('sovereign_token', token);
            // Notify App
            onLogin(token);
        } catch (err) {
            console.error("Login failed:", err);
            setError("Access Denied: Invalid Credentials (Try 'sovereign' or '9392352630sk')");
        } finally {
            setLoading(false);
        }
    };

    const handleSignup = () => {
        alert("🔒 SECURITY ALERT\n\nPublic registration is disabled for security.\nOnly the Sovereign (Owner) can access this terminal.\n\nUse your admin credentials.");
    };

    return (
        <div className="min-h-screen bg-black flex items-center justify-center p-4 relative overflow-hidden">
            {/* NEBULA BACKGROUND */}
            <div className="absolute top-[-20%] left-[-20%] w-[140%] h-[140%] bg-[radial-gradient(circle_at_center,_rgba(168,85,247,0.15),_transparent_60%)] animate-pulse-slow pointer-events-none" />
            <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 pointer-events-none" />

            <motion.div
                initial={{ opacity: 0, scale: 0.9, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                transition={{ duration: 0.8, ease: "easeOut" }}
                className="w-full max-w-md relative z-10"
            >
                <HolographicCard className="p-10 flex flex-col items-center space-y-8 backdrop-blur-3xl bg-black/60 border-purple-500/30 shadow-[0_0_50px_rgba(168,85,247,0.15)]">

                    {/* LOGO AREA */}
                    <div className="text-center space-y-2">
                        <motion.div
                            animate={{ rotate: 360 }}
                            transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                            className="w-20 h-20 mx-auto rounded-full border-2 border-dashed border-purple-500/50 flex items-center justify-center mb-4 relative"
                        >
                            <div className="w-16 h-16 rounded-full bg-purple-500/10 flex items-center justify-center shadow-[0_0_20px_rgba(168,85,247,0.5)]">
                                <Lock className="w-8 h-8 text-purple-400" />
                            </div>
                        </motion.div>
                        <h1 className="text-2xl font-black tracking-[0.2em] text-transparent bg-clip-text bg-gradient-to-r from-purple-300 to-blue-300">
                            SOVEREIGN
                        </h1>
                        <p className="text-xs font-mono text-purple-400/60 uppercase tracking-widest">
                            Authorized Personnel Only
                        </p>
                    </div>

                    {/* FORM */}
                    <form onSubmit={handleSubmit} className="w-full space-y-6">

                        {/* USERNAME */}
                        <div className="space-y-1">
                            <label className="text-xs font-bold text-gray-500 ml-1 uppercase tracking-wider">Identity</label>
                            <div className="relative group">
                                <User className="absolute left-3 top-3.5 w-5 h-5 text-gray-400 group-focus-within:text-purple-400 transition-colors" />
                                <input
                                    type="text"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    className="w-full bg-black/50 border border-white/10 rounded-xl py-3 pl-10 pr-4 text-white focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition-all outline-none placeholder-gray-600"
                                    placeholder="Username"
                                    required
                                />
                            </div>
                        </div>

                        {/* PASSWORD */}
                        <div className="space-y-1">
                            <label className="text-xs font-bold text-gray-500 ml-1 uppercase tracking-wider">Passcode</label>
                            <div className="relative group">
                                <Key className="absolute left-3 top-3.5 w-5 h-5 text-gray-400 group-focus-within:text-purple-400 transition-colors" />
                                <input
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="w-full bg-black/50 border border-white/10 rounded-xl py-3 pl-10 pr-4 text-white focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition-all outline-none placeholder-gray-600"
                                    placeholder="••••••••"
                                    required
                                />
                            </div>
                        </div>

                        {/* ERROR MESSAGE */}
                        {error && (
                            <motion.div
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: 'auto' }}
                                className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 flex items-center space-x-3"
                            >
                                <AlertTriangle className="w-5 h-5 text-red-500" />
                                <p className="text-xs text-red-300 font-bold">{error}</p>
                            </motion.div>
                        )}


                        {/* SUBMIT */}
                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full py-3.5 rounded-xl bg-gradient-to-r from-purple-600 to-blue-600 text-white font-bold tracking-wider uppercase shadow-[0_0_20px_rgba(168,85,247,0.4)] hover:shadow-[0_0_30px_rgba(168,85,247,0.6)] hover:scale-[1.02] transition-all disabled:opacity-50 disabled:cursor-not-allowed group"
                        >
                            {loading ? (
                                <span className="flex items-center justify-center gap-2">
                                    <span className="w-2 h-2 rounded-full bg-white animate-bounce" />
                                    <span className="w-2 h-2 rounded-full bg-white animate-bounce delay-75" />
                                    <span className="w-2 h-2 rounded-full bg-white animate-bounce delay-150" />
                                </span>
                            ) : (
                                <span className="flex items-center justify-center gap-2">
                                    <Shield className="w-4 h-4" />
                                    <span>Authenticate</span>
                                </span>
                            )}
                        </button>

                    </form>

                    {/* FOOTER */}
                    <div className="w-full flex justify-between items-center text-xs text-gray-500 border-t border-white/5 pt-6">
                        <button onClick={handleSignup} className="hover:text-purple-400 transition-colors font-medium">
                            Request Access
                        </button>
                        <span className="font-mono opacity-50">V 2.5.0 S</span>
                    </div>

                </HolographicCard>
            </motion.div>
        </div>
    );
};

export default LoginPage;
