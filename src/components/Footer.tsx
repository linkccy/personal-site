import { useEffect, useState } from 'react';
import { profile } from '../data/profile';

export function Footer() {
  const [showTop, setShowTop] = useState(false);

  useEffect(() => {
    const onScroll = () => setShowTop(window.scrollY > 600);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <>
      <footer className="footer">
        <div className="wrap footer-inner">
          <span>© 2026 {profile.name} · 个人主页</span>
          <span className="footer-tech">
            React + TypeScript + Vite 构建，星空背景为 Canvas 手写，未使用任何动效库
          </span>
          <a href="#home">回到顶部 ↑</a>
        </div>
      </footer>

      <button
        type="button"
        className={`to-top ${showTop ? 'show' : ''}`}
        aria-label="回到页面顶部"
        onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
      >
        ↑
      </button>
    </>
  );
}