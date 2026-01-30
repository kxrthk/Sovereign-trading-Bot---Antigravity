import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Smartphone, Wifi } from 'lucide-react';

const QRCodeModal = ({ isOpen, onClose }) => {
    const [networkData, setNetworkData] = useState(null);

    useEffect(() => {
        if (isOpen) {
            // Fetch IP, but with a timeout to prevent "Spinning forever"
            const timer = setTimeout(() => {
                setNetworkData({ url: window.location.href.replace('localhost', '192.168.1.X') });
            }, 3000);

            fetch('/api/network-ip')
                .then(res => res.json())
                .then(data => {
                    clearTimeout(timer);
                    if (data && data.url) setNetworkData(data);
                })
                .catch(err => {
                    clearTimeout(timer);
                    console.error("Failed to get IP", err);
                    // Fallback: guess based on window
                    setNetworkData({ url: window.location.href });
                });
        }
    }, [isOpen]);

    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                    />

                    {/* Modal */}
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0, y: 20 }}
                        animate={{ scale: 1, opacity: 1, y: 0 }}
                        exit={{ scale: 0.9, opacity: 0, y: 20 }}
                        className="relative bg-gray-900 border border-purple-500/30 rounded-2xl p-8 max-w-sm w-full shadow-[0_0_40px_rgba(168,85,247,0.2)]"
                    >
                        <button
                            onClick={onClose}
                            className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors"
                        >
                            <X className="w-5 h-5" />
                        </button>

                        <div className="text-center space-y-6">
                            <div className="space-y-2">
                                <h3 className="text-2xl font-bold text-white tracking-tight">Connect Device</h3>
                                <p className="text-sm text-gray-400">Scan to control from your phone</p>
                            </div>

                            <div className="bg-white p-4 rounded-xl mx-auto w-fit">
                                {networkData ? (
                                    <img
                                        src={`https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(networkData.url)}&color=000000`}
                                        alt="QR Code"
                                        className="w-48 h-48"
                                    />
                                ) : (
                                    <div className="w-48 h-48 flex items-center justify-center bg-gray-100 rounded-lg">
                                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
                                    </div>
                                )}
                            </div>

                            <div className="space-y-4">
                                <div className="flex items-center justify-center gap-2 text-xs font-mono text-purple-400 bg-purple-500/10 py-2 px-4 rounded-full border border-purple-500/20">
                                    <Wifi className="w-3 h-3" />
                                    <span>{networkData?.url || "Detecting Network..."}</span>
                                </div>

                                <div className="flex items-start gap-3 text-left bg-gray-800/50 p-3 rounded-lg border border-gray-700">
                                    <Smartphone className="w-5 h-5 text-gray-400 shrink-0 mt-0.5" />
                                    <p className="text-xs text-gray-400">
                                        Ensure your phone is connected to the same Wi-Fi network as this computer.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
};

export default QRCodeModal;
