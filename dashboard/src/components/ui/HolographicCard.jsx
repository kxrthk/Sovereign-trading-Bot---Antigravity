import React from "react";

export default function HolographicCard({ children, className = "", ...props }) {
    return (
        <div
            {...props}
            className={`relative rounded-xl backdrop-blur-md overflow-hidden bg-white border-gray-200 dark:bg-black/40 dark:border-white/5 shadow-sm border ${className}`}
        >
            <div className="relative z-10 h-full">
                {children}
            </div>
        </div>
    );
}
