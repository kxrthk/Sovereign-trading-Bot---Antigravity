import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Volume2, User, Play, Square } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

export default function VoiceControl() {
    const [isListening, setIsListening] = useState(false);
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [transcript, setTranscript] = useState("");
    const [reply, setReply] = useState("");
    const [voiceGender, setVoiceGender] = useState("male"); // "male" | "female"

    // NEW STATE
    const [errorMsg, setErrorMsg] = useState("");
    const [manualInput, setManualInput] = useState("");
    const [showInput, setShowInput] = useState(false);

    // Audio Player
    const audioRef = useRef(new Audio());

    // Web Speech API for STT
    const recognitionRef = useRef(null);

    useEffect(() => {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognitionRef.current = new SpeechRecognition();
            recognitionRef.current.continuous = false;
            recognitionRef.current.interimResults = true; // Enable Real-time typing
            recognitionRef.current.lang = 'en-IN'; // Indian English explicit

            recognitionRef.current.onstart = () => {
                setErrorMsg("");
                setTranscript("Listening...");
            };

            recognitionRef.current.onresult = (event) => {
                let interm = '';
                let final = '';

                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    if (event.results[i].isFinal) {
                        final += event.results[i][0].transcript;
                    } else {
                        interm += event.results[i][0].transcript;
                    }
                }

                if (final) {
                    setTranscript(final);
                    setIsListening(false);
                    handleSendQuery(final);
                } else if (interm) {
                    setTranscript(interm + "..."); // Show live feedback
                }
            };

            recognitionRef.current.onerror = (event) => {
                console.error("Speech Error", event.error);
                setErrorMsg(`Mic Error: ${event.error}`);
                setIsListening(false);
            };

            recognitionRef.current.onend = () => {
                setIsListening(false);
            };
        } else {
            setErrorMsg("Browser does not support Voice.");
        }

        // Cleanup function to prevent double-listeners in React StrictMode
        return () => {
            if (recognitionRef.current) {
                recognitionRef.current.abort();
            }
        };
    }, []);

    const toggleListen = () => {
        if (isListening) {
            recognitionRef.current?.stop();
        } else {
            setTranscript("Listening...");
            setReply("");
            recognitionRef.current?.start();
            setIsListening(true);
        }
    };

    const handleSendQuery = async (text) => {
        console.log("Asking Oracle:", text);
        try {
            // Use axios to ensure Bearer Token is attached
            const res = await axios.post('/api/chat', {
                message: text,
                voice: voiceGender,
                context: "Dashboard"
            });
            const data = res.data;

            if (data.status === 'success') {
                setReply(data.reply_text);
                playAudio(data.audio_url);
            }
        } catch (e) {
            console.error(e);
            setReply("Connection Error.");
        }
    };

    const playAudio = async (url) => {
        setIsSpeaking(true);
        try {
            // FIX: Fetch as Blob first to prevent streaming quality switches
            const response = await fetch(url);
            const blob = await response.blob();
            const blobUrl = URL.createObjectURL(blob);

            audioRef.current.src = blobUrl;
            await audioRef.current.play();
        } catch (e) {
            console.error("Playback failed:", e);
            setReply(prev => prev + " (Click to play)");
            setIsSpeaking(false);
        }

        audioRef.current.onended = () => {
            setIsSpeaking(false);
            // Cleanup memory
            URL.revokeObjectURL(audioRef.current.src);
        };
    };

    const handleManualSubmit = (e) => {
        e.preventDefault();
        if (!manualInput.trim()) return;
        setTranscript(manualInput);
        handleSendQuery(manualInput);
        setManualInput("");
        setShowInput(false);
    };

    return (
        <div className="fixed bottom-6 right-6 z-[100] flex flex-col items-end gap-4">
            {/* Thinking Bubble */}
            <AnimatePresence>
                {(transcript || reply || errorMsg) && (
                    <motion.div
                        initial={{ opacity: 0, y: 10, scale: 0.9 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.9 }}
                        onClick={() => audioRef.current.play()}
                        className="bg-black/90 backdrop-blur-xl border border-white/10 p-4 rounded-2xl shadow-2xl max-w-xs mb-2 text-sm cursor-pointer hover:bg-black"
                    >
                        {errorMsg && <p className="text-red-400 font-bold mb-2">⚠️ {errorMsg}</p>}
                        {transcript && !errorMsg && <p className="text-slate-400 mb-1"><span className="font-bold">You:</span> "{transcript}"</p>}
                        {reply && <p className="text-emerald-400 font-medium"><span className="font-bold">Oracle:</span> "{reply}"</p>}
                        {reply && <p className="text-[10px] text-slate-500 mt-2 text-right">Click to Replay</p>}
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Manual Input Field (Hidden by default) */}
            <AnimatePresence>
                {showInput && (
                    <motion.form
                        initial={{ width: 0, opacity: 0 }}
                        animate={{ width: 200, opacity: 1 }}
                        exit={{ width: 0, opacity: 0 }}
                        onSubmit={handleManualSubmit}
                        className="bg-white/10 backdrop-blur rounded-full flex items-center overflow-hidden border border-white/10"
                    >
                        <input
                            type="text"
                            value={manualInput}
                            onChange={(e) => setManualInput(e.target.value)}
                            placeholder="Type command..."
                            className="bg-transparent text-white text-sm px-4 py-2 outline-none w-full"
                            autoFocus
                        />
                    </motion.form>
                )}
            </AnimatePresence>

            {/* Controls */}
            <div className="flex items-center gap-3">
                {/* Voice Toggle Removed - Defaulting to Jarvis (Male) */}
                {/* 
                <div className="bg-white/10 backdrop-blur-md rounded-full p-1 flex border border-white/5">
                   Buttons removed as per request
                </div> 
                */}

                {/* Keyboard Toggle */}
                <button
                    onClick={() => setShowInput(!showInput)}
                    className="w-12 h-12 rounded-full bg-gray-700 hover:bg-gray-600 flex items-center justify-center text-white shadow-lg transition-all"
                    title="Type instead"
                >
                    <Square className="w-5 h-5" />
                </button>

                {/* Main Mic Button */}
                <button
                    onClick={toggleListen}
                    className={`w-16 h-16 rounded-full flex items-center justify-center shadow-2xl transition-all duration-300 ${isListening
                        ? 'bg-red-500 animate-pulse scale-110 shadow-red-500/50'
                        : isSpeaking
                            ? 'bg-emerald-500 shadow-emerald-500/50 ring-4 ring-emerald-500/20'
                            : 'bg-gradient-to-br from-blue-500 to-indigo-600 hover:scale-105 shadow-blue-500/30'
                        }`}
                >
                    {isListening ? (
                        <MicOff className="w-8 h-8 text-white" />
                    ) : isSpeaking ? (
                        <Volume2 className="w-8 h-8 text-white animate-bounce" />
                    ) : (
                        <Mic className="w-8 h-8 text-white" />
                    )}
                </button>
            </div>
        </div>
    );
}
