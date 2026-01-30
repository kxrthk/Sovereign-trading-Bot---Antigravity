export const isMarketOpen = () => {
    const now = new Date();

    // Convert to IST (UTC + 5:30)
    const utcTime = now.getTime() + (now.getTimezoneOffset() * 60000);
    const istOffset = 5.5 * 60 * 60 * 1000;
    const istTime = new Date(utcTime + istOffset);

    const day = istTime.getDay();
    const hours = istTime.getHours();
    const minutes = istTime.getMinutes();

    // 1. Check Weekend (Saturday=6, Sunday=0)
    if (day === 0 || day === 6) return false;

    // 2. Check Time (9:15 AM - 3:30 PM)
    const timeInMinutes = hours * 60 + minutes;
    const openTime = 9 * 60 + 15; // 09:15
    const closeTime = 15 * 60 + 30; // 15:30

    return timeInMinutes >= openTime && timeInMinutes <= closeTime;
};

export const getMarketStatusConfig = (isOpen) => {
    return isOpen
        ? { label: 'MARKET OPEN', color: 'text-emerald-400', glow: 'shadow-[0_0_10px_rgba(52,211,153,0.5)]' }
        : { label: 'MARKET CLOSED', color: 'text-rose-400', glow: 'shadow-[0_0_10px_rgba(251,113,133,0.5)]' };
};
