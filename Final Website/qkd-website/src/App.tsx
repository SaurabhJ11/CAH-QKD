import Header from './components/layout/Header';
import Footer from './components/layout/Footer';
import {
  Hero,
  RecommendationPanel,
  ProtocolExplorer,
  ModelOverview,
  HardwareComparison,
} from './components/sections';

function App() {
  const scrollTo = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-surface">
      <Header />
      <main>
        <Hero
          onTryRecommendation={() => scrollTo('recommendation')}
          onViewModel={() => scrollTo('model')}
        />
        <RecommendationPanel />
        <ProtocolExplorer />
        <ModelOverview />
        <HardwareComparison />
      </main>
      <Footer />
    </div>
  );
}

export default App;
