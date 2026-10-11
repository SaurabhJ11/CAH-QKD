export default function Footer() {
  return (
    <footer className="bg-surface border-t border-secondary-container/20 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <img src="/Updated Logo.png" alt="Logo" className="h-15 w-45" />
            </div>
            <p className="text-sm text-secondary/70">
              Quantum Key Distribution protocol recommendation system powered by
              machine learning.
            </p>
          </div>

          <div>
            <h4 className="font-display font-semibold text-primary mb-4">
              Project
            </h4>
            <ul className="space-y-2">
              <li>
                <a
                  href="#recommendation"
                  className="text-sm text-secondary hover:text-primary transition-colors"
                >
                  Live Demo
                </a>
              </li>
              <li>
                <a
                  href="#model"
                  className="text-sm text-secondary hover:text-primary transition-colors"
                >
                  Model Details
                </a>
              </li>
              <li>
                <a
                  href="#protocols"
                  className="text-sm text-secondary hover:text-primary transition-colors"
                >
                  Protocol Explorer
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="font-display font-semibold text-primary mb-4">
              Status
            </h4>
            <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-tertiary-container/30 rounded-full">
              <span className="w-2 h-2 bg-tertiary rounded-full animate-pulse" />
              <span className="text-sm text-tertiary">MVP Version</span>
            </div>
            <p className="text-sm text-secondary/70 mt-4">
              This is a demonstration of QKD protocol prediction capabilities.
              Contact for production inquiries.
            </p>
          </div>
        </div>

        <div className="mt-12 pt-8 border-t border-secondary-container/20">
          <p className="text-center text-sm text-secondary/50">
            Built for Quantum Key Distribution research and education.
          </p>
        </div>
      </div>
    </footer>
  );
}
