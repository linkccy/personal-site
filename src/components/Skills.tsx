import { useEffect, useRef, useState } from 'react';
import { skillGroups } from '../data/profile';
import { useReducedMotion } from '../hooks/useReducedMotion';
import { Reveal } from './Reveal';

/**
 * 技能区。进度条在整块进入视口后才增长，
 * 否则用户滚到这里时动画已经播完了。
 */
export function Skills() {
  const ref = useRef<HTMLDivElement>(null);
  const reduced = useReducedMotion();
  const [grown, setGrown] = useState(false);

  useEffect(() => {
    if (reduced) {
      setGrown(true);
      return;
    }
    const el = ref.current;
    if (!el) return;

    if (typeof IntersectionObserver === 'undefined') {
      setGrown(true);
      return;
    }

    const io = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            setGrown(true);
            io.unobserve(entry.target);
          }
        }
      },
      { threshold: 0.15 },
    );
    io.observe(el);
    return () => io.disconnect();
  }, [reduced]);

  return (
    <section id="skills" className="section">
      <div className="wrap" ref={ref}>
        <Reveal className="section-head">
          <div>
            <span className="section-tag">Skills</span>
            <h2 className="section-title">
              技能<span className="grad-text">清单</span>
            </h2>
            <p className="section-sub">
              熟练度是自评，按「能独立写完并调通」这一条标准给分，不虚标。
            </p>
          </div>
        </Reveal>

        <div className="skill-groups">
          {skillGroups.map((group, gi) => (
            <Reveal key={group.category} delay={gi * 110}>
              <div className="card skill-group">
                <div className="skill-group-head">
                  <span
                    className="skill-dot"
                    style={{ background: group.accent }}
                    aria-hidden="true"
                  />
                  <span className="skill-cat">{group.category}</span>
                </div>

                {group.items.map((item) => (
                  <div className="skill-item" key={item.name}>
                    <div className="skill-top">
                      <span className="skill-name">
                        <span aria-hidden="true">{item.icon}</span>
                        {item.name}
                      </span>
                      <span className="skill-num">{item.level}%</span>
                    </div>
                    <div
                      className="skill-bar"
                      role="progressbar"
                      aria-label={item.name}
                      aria-valuenow={item.level}
                      aria-valuemin={0}
                      aria-valuemax={100}
                    >
                      <div
                        className="skill-fill"
                        style={{
                          width: grown ? `${item.level}%` : '0%',
                          background: `linear-gradient(90deg, ${group.accent}, rgba(255,255,255,.75))`,
                        }}
                      />
                    </div>
                    <div className="skill-note">{item.note}</div>
                  </div>
                ))}
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}