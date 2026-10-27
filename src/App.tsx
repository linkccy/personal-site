import { About } from './components/About';
import { Blog } from './components/Blog';
import { Contact } from './components/Contact';
import { Footer } from './components/Footer';
import { Hero } from './components/Hero';
import { Nav } from './components/Nav';
import { Projects } from './components/Projects';
import { Skills } from './components/Skills';
import { Starfield } from './components/Starfield';

export function App() {
  return (
    <>
      {/* 背景层：星空 Canvas + 两团星云光斑 */}
      <Starfield />
      <div className="bg-glow a" aria-hidden="true" />
      <div className="bg-glow b" aria-hidden="true" />

      {/* 内容层 */}
      <div className="page">
        <Nav />
        <main>
          <Hero />
          <About />
          <Skills />
          <Projects />
          <Blog />
          <Contact />
        </main>
        <Footer />
      </div>
    </>
  );
}