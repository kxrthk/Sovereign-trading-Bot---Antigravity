import { motion, AnimatePresence } from 'framer-motion';
import QRCode from 'react-qr-code';
import { Scan, X } from 'lucide-react';
import { GlassCard } from './GlassCard';

const PUBLIC_URL = "https://roommate-likewise-rod-throughout.trycloudflare.com/";

export function MobileAccessFab({ onClick }) {
    return (
        <motion.button
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            whileHover={{ scale: 1.1, boxShadow: "0 0 20px #8b5cf6" }}
            whileTap={{ scale: 0.9 }}
            onClick={onClick}
            className="fixed bottom-16 right-8 z-50 p-4 rounded-full bg-indigo-600 text-white shadow-lg shadow-indigo-500/30 border border-white/20"
            title="Mobile Access"
        >
            <Scan className="w-6 h-6" />
        </motion.button>
    );
}

export function MobileAccessModal({ isOpen, onClose }) {
    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 z-[60] bg-black/80 backdrop-blur-sm"
                    />
                    <div className="fixed inset-0 z-[70] flex items-center justify-center p-4 pointer-events-none">
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0, y: 20 }}
                            animate={{ scale: 1, opacity: 1, y: 0 }}
                            exit={{ scale: 0.9, opacity: 0, y: 20 }}
                            className="pointer-events-auto"
                        >
                            <GlassCard className="p-8 flex flex-col items-center gap-6 max-w-sm w-full relative bg-black/40">
                                <button
                                    onClick={onClose}
                                    className="absolute top-4 right-4 text-zinc-500 hover:text-white transition-colors"
                                >
                                    <X className="w-5 h-5" />
                                </button>

                                <div className="text-center space-y-2">
                                    <h3 className="text-xl font-bold text-white tracking-widest uppercase">Mobile Access</h3>
                                    <p className="text-xs text-zinc-400 font-mono">SCAN TO INITIALIZE REMOTE LINK</p>
                                </div>

                                <div className="p-4 bg-white rounded-xl shadow-2xl shadow-white/10">
                                    <QRCode
                                        value={PUBLIC_URL}
                                        size={200}
                                        level="M"
                                        fgColor="#000000"
                                        bgColor="#FFFFFF"
                                    />
                                </div>

                                <div className="text-center">
                                    <div className="px-3 py-1 rounded-full bg-white/5 border border-white/10 text-[10px] sm:text-xs text-zinc-400 font-mono break-all max-w-[240px]">
                                        {PUBLIC_URL}
                                    </div>
                                </div>
                            </GlassCard>
                        </motion.div>
                    </div>
                </>
            )}
        </AnimatePresence>
    );
}
