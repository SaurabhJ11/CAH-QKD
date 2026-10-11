import { motion } from 'framer-motion';

export default function Header() {
  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId);
    element?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="fixed top-0 left-0 right-0 z-50 bg-surface/80 backdrop-blur-md border-b border-secondary-container/20"
    >
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-6">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-2">
            <img src="/Updated Logo.png" alt="Logo" className="h-12 w-35" />
          </div>

          <div className="hidden md:flex items-center gap-6">
            <button
              onClick={() => scrollToSection('recommendation')}
              className="text-sm text-secondary hover:text-primary transition-colors"
            >
              Try It
            </button>
            <button
              onClick={() => scrollToSection('protocols')}
              className="text-sm text-secondary hover:text-primary transition-colors"
            >
              Protocols
            </button>
            <button
              onClick={() => scrollToSection('model')}
              className="text-sm text-secondary hover:text-primary transition-colors"
            >
              Model
            </button>
            <button
              onClick={() => scrollToSection('hardware')}
              className="text-sm text-secondary hover:text-primary transition-colors"
            >
              Hardware
            </button>
          </div>

          <div className="flex items-center gap-3">
            <a
              href="#recommendation"
              className="px-4 py-2 text-sm font-medium text-primary-on bg-primary rounded-lg hover:bg-primary/90 transition-colors"
            >
              Get Started
            </a>
          </div>
        </div>
      </nav>
    </motion.header>
  );
}
