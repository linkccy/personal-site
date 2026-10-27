import { useEffect, useState } from 'react';
import { profile } from '../data/profile';

export const SECTIONS = [
  { id: 'home', label: '首页' },
  { id: 'about', label: '关于' },
  { id: 'skills', label: '技能' },
  { id: 'projects', label: '项目' },
  { id: 'blog', label: '博客' },
  { id: 'contact', label: '联系' },
] as const;

type SectionId = (typeof SECTIONS)[number]['id'];

/**
 * 吸顶导航。
 *
 * 注意：这里用「滚动位置比较」而不是 IntersectionObserver 来判断当前区块。
 * 原因见 TECH_DESIGN.md 4.2 —— 首屏时视口内可能同时有两个区块，
 * 按"进入即高亮"会把靠后的区块误判为当前项。
 */
export function Nav() {
  const [scrolled, setScrolled] = useState(false);
  const [active, setActive] = useState<SectionId>('home');
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => {
      setScrolled(window.scrollY > 12);

      let current: SectionId = 'home';
      // 高亮线放在视口上三分之一处，稳定且符合直觉
      const line = window.scrollY + window.innerHeight * 0.35;
      for (const s of SECTIONS) {
        const el = document.getElementById(s.id);
        if (el && el.offsetTop <= line) current = s.id;
      }
      setActive(current);
    };

    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  // 窗口拉宽回桌面端时，把汉堡菜单收起来，避免残留展开状态
  useEffect(() => {
    const onResize = () => {
      if (window.innerWidth > 767) setOpen(false);
    };
    window.addEventListener('resize', onResize);
    return () => window.removeEventListener('resize', onResize);
  }, []);

  return (
    <header className={`nav ${scrolled ? 'scrolled' : ''}`}>
      <div className="wrap nav-inner">
        <a className="logo" href="#home" aria-label="回到首页">
          <span className="logo-mark" aria-hidden="true">
            {profile.name.slice(0, 1).toUpperCase()}
          </span>
          <span>{profile.name}</span>
        </a>

        <nav className={`nav-links ${open ? 'open' : ''}`} aria-label="主导航">
          {SECTIONS.map((s) => (
            <a
              key={s.id}
              href={`#${s.id}`}
              className={`nav-link ${active === s.id ? 'active' : ''}`}
              onClick={() => setOpen(false)}
            >
              {s.label}
            </a>
          ))}
        </nav>

        <button
          type="button"
          className={`nav-toggle ${open ? 'open' : ''}`}
          aria-label={open ? '关闭菜单' : '打开菜单'}
          aria-expanded={open}
          onClick={() => setOpen((v) => !v)}
        >
          <span />
          <span />
          <span />
        </button>
      </div>
    </header>
  );
}