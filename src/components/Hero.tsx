import { useEffect, useState } from 'react';
import { profile } from '../data/profile';
import { useReducedMotion } from '../hooks/useReducedMotion';
import { Terminal } from './Terminal';

/** 打字机：逐字输入 → 停顿 → 快速删除 → 下一句 */
function useTypewriter(lines: string[], enabled: boolean) {
  const [index, setIndex] = useState(0);
  const [text, setText] = useState('');
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    if (!enabled || lines.length === 0) return;

    const full = lines[index];
    let timer = 0;

    if (!deleting) {
      if (text.length < full.length) {
        timer = window.setTimeout(() => setText(full.slice(0, text.length + 1)), 62);
      } else {
        // 输入完成后停顿一下再删
        timer = window.setTimeout(() => setDeleting(true), 1600);
      }
    } else if (text.length > 0) {
      // 删除比输入快，观感更自然
      timer = window.setTimeout(() => setText(full.slice(0, text.length - 1)), 24);
    } else {
      timer = window.setTimeout(() => {
        setDeleting(false);
        setIndex((i) => (i + 1) % lines.length);
      }, 280);
    }

    return () => window.clearTimeout(timer);
  }, [text, deleting, index, enabled, lines]);

  return enabled ? text : lines[0] ?? '';
}

export function Hero() {
  const reduced = useReducedMotion();
  const typed = useTypewriter(profile.taglines, !reduced);

  return (
    <section id="home" className="section hero">
      <div className="wrap hero-grid">
        <div>
          <span className="hero-badge">
            <span className="pulse" aria-hidden="true" />
            {profile.location} · 正在学习大模型
          </span>

          <h1 className="hero-name">
            你好，我是 <span className="grad-text">{profile.name}</span>
          </h1>
          <p className="hero-title">{profile.title}</p>

          <p className="type-line" aria-live="polite">
            <span className="prompt" aria-hidden="true">
              $
            </span>
            {typed}
            {!reduced ? <span className="caret" aria-hidden="true" /> : null}
          </p>

          <div className="hero-actions">
            <a className="btn btn-primary" href="#projects">
              看看我的项目
            </a>
            <a className="btn btn-ghost" href="#contact">
              联系我
            </a>
          </div>

          <div className="hero-stats">
            {profile.stats.map((s) => (
              <div key={s.label}>
                <div className="stat-value">{s.value}</div>
                <div className="stat-label">{s.label}</div>
              </div>
            ))}
          </div>

          <div className="scroll-hint">
            <i aria-hidden="true" />
            向下滚动了解更多
          </div>
        </div>

        <Terminal />
      </div>
    </section>
  );
}