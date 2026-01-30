export default {
    darkMode: 'class',
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            fontFamily: {
                sans: ['"Space Grotesk"', 'sans-serif'],
                mono: ['"JetBrains Mono"', 'monospace'],
            },
            colors: {
                cyber: {
                    bg: '#18181b', // Zinc-900
                    card: '#27272a', // Zinc-800
                    text: '#f4f4f5', // Zinc-100
                    primary: '#10b981', // Emerald-500
                    secondary: '#8b5cf6', // Violet-500 (Neon Purple-ish)
                    accent: '#06b6d4', // Cyan-500
                }
            },
            animation: {
                'pulse-fast': 'pulse 1s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            }
        },
    },
    plugins: [],
}
