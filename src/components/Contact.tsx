import { useEffect, useRef, useState } from 'react';
import { profile } from '../data/profile';
import { Reveal } from './Reveal';

/**
 * 复制文本。
 * navigator.clipboard 只在 HTTPS 或 localhost 下可用，
 * 所以正式路径失败时降级到 execCommand。
 */
async function copyText(text: string): Promise<boolean> {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return true;
    }
  } catch {
    // 继续走降级分支
  }

  try {
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.style.position = 'fixed';
    ta.style.top = '-1000px';
    document.body.appendChild(ta);
    ta.select();
    const ok = document.execCommand('copy');
    document.body.removeChild(ta);
    return ok;
  } catch {
    return false;
  }
}

export function Contact() {
  const [state, setState] = useState<'idle' | 'done' | 'fail'>('idle');
  const timerRef = useRef(0);

  // 组件卸载时清掉定时器，避免对已卸载组件 setState
  useEffect(() => () => window.clearTimeout(timerRef.current), []);

  const onCopy = async () => {
    const ok = await copyText(profile.email);
    setState(ok ? 'done' : 'fail');
    window.clearTimeout(timerRef.current);
    timerRef.current = window.setTimeout(() => setState('idle'), 2000);
  };

  return (
    <section id="contact" className="section">
      <div className="wrap">
        <Reveal className="section-head">
          <div>
            <span className="section-tag">Contact</span>
            <h2 className="section-title">
              联系<span className="grad-text">方式</span>
            </h2>
            <p className="section-sub">
              对项目有疑问、想一起做点什么，或者只是想交流大模型，都欢迎找我。
            </p>
          </div>
        </Reveal>

        <div className="contact-grid">
          <Reveal>
            <div className="card contact-card">
              <span className="contact-icon" aria-hidden="true">
                📮
              </span>
              <span className="contact-label">邮箱</span>
              <span className="contact-value">{profile.email}</span>
              <button
                type="button"
                className={`copy-btn ${state === 'done' ? 'done' : ''}`}
                onClick={onCopy}
              >
                {state === 'done' ? '✓ 已复制' : state === 'fail' ? '复制失败，请手动选中' : '复制邮箱'}
              </button>
            </div>
          </Reveal>

          <Reveal delay={110}>
            <div className="card contact-card">
              <span className="contact-icon" aria-hidden="true">
                🐙
              </span>
              <span className="contact-label">GitHub</span>
              <span className="contact-value">
                {profile.github.replace(/^https?:\/\//, '')}
              </span>
              <a
                className="copy-btn"
                href={profile.github}
                target="_blank"
                rel="noopener noreferrer"
              >
                打开主页 ↗
              </a>
            </div>
          </Reveal>

          <Reveal delay={220}>
            <div className="card contact-card">
              <span className="contact-icon" aria-hidden="true">
                📍
              </span>
              <span className="contact-label">所在地</span>
              <span className="contact-value">{profile.location}</span>
              <span className="contact-note" style={{ marginTop: 4 }}>
                线上交流随时可以
              </span>
            </div>
          </Reveal>
        </div>

        <p className="contact-note">
          备注：这个站点是纯静态页面，没有后端，所以没有做留言表单 —— 上面三个入口都是真实有效的。
        </p>
      </div>
    </section>
  );
}