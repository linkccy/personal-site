import { projects } from '../data/profile';
import { Reveal } from './Reveal';

export function Projects() {
  return (
    <section id="projects" className="section">
      <div className="wrap">
        <Reveal className="section-head">
          <div>
            <span className="section-tag">Projects</span>
            <h2 className="section-title">
              项目<span className="grad-text">展示</span>
            </h2>
            <p className="section-sub">
              每个项目都给出了可核对的关键指标，而不是"完成了 XX 系统"这种描述。
            </p>
          </div>
        </Reveal>

        <div className="project-grid">
          {projects.map((p, i) => (
            <Reveal key={p.title} delay={(i % 2) * 110}>
              <article
                className="card project-card"
                style={{ ['--pc' as string]: p.accent }}
              >
                <div className="project-head">
                  <span className="project-no">P{i + 1}</span>
                  <h3 className="project-title">{p.title}</h3>
                </div>

                <p className="project-summary">{p.summary}</p>

                <ul className="project-metrics">
                  {p.metrics.map((m) => (
                    <li key={m}>{m}</li>
                  ))}
                </ul>

                <div className="project-tags">
                  {p.tags.map((t) => (
                    <span className="chip" key={t}>
                      {t}
                    </span>
                  ))}
                </div>

                {p.links.length > 0 ? (
                  <div className="project-links">
                    {p.links.map((l) => (
                      <a
                        key={l.label + l.href}
                        className="project-link"
                        href={l.href}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        {l.label} ↗
                      </a>
                    ))}
                  </div>
                ) : null}
              </article>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}