import React from 'react';

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null, errorInfo: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        console.error("Uncaught error:", error, errorInfo);
        this.setState({ error, errorInfo });
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="p-10 bg-black text-white min-h-screen font-mono">
                    <h1 className="text-2xl text-red-500 mb-4">⚠️ SYSTEM CRASH (React Error)</h1>
                    <p className="text-gray-400 mb-4">The dashboard encountered a critical error during rendering.</p>

                    <div className="bg-gray-900 p-4 rounded border border-gray-700 overflow-auto whitespace-pre-wrap text-sm text-red-300">
                        {this.state.error && this.state.error.toString()}
                        <br />
                        {this.state.errorInfo && this.state.errorInfo.componentStack}
                    </div>

                    <button
                        onClick={() => window.location.reload()}
                        className="mt-6 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded text-white"
                    >
                        REBOOT SYSTEM (Reload)
                    </button>

                    <button
                        onClick={() => {
                            localStorage.removeItem('sovereign_token');
                            window.location.reload();
                        }}
                        className="mt-6 ml-4 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded text-white"
                    >
                        HARD RESET (Logout)
                    </button>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
