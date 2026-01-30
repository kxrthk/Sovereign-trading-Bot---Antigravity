import { motion } from 'framer-motion';

const container = {
    hidden: { opacity: 0 },
    show: {
        opacity: 1,
        transition: {
            staggerChildren: 0.1
        }
    }
};

const DashboardGrid = ({ children }) => {
    return (
        <motion.div
            variants={container}
            initial="hidden"
            animate="show"
            className="grid grid-cols-12 gap-6 p-6 h-full overflow-hidden"
        >
            {children}
        </motion.div>
    );
};

export default DashboardGrid;
