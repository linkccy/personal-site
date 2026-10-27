import { useEffect, useRef } from 'react';
import { useReducedMotion } from '../hooks/useReducedMotion';

type Star = {
  x: number;
  y: number;
  r: number;
  base: number;
  speed: number;
  phase: number;
  layer: number;
};

type Meteor = {
  x: number;
  y: number;
  vx: number;
  vy: number;
  life: number;
  max: number;
};

/** 视差系数：远层几乎不动，近层跟随鼠标更明显 */
const PARALLAX = [0.15, 0.35, 0.7];
/** 各层基础亮度与半径 */
const BASE_ALPHA = [0.18, 0.32, 0.5];
const BASE_RADIUS = [0.6, 0.95, 1.4];

/**
 * 全屏星空背景。
 *
 * 性能要点（详见 TECH_DESIGN.md 4.1）：
 * - 所有绘制在 requestAnimationFrame 里完成，不进入 React state；
 * - 星星数组只在窗口尺寸变化时重建；
 * - 组件卸载时取消动画帧并移除事件监听，避免内存泄漏。
 */
export function Starfield() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const reduced = useReducedMotion();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let stars: Star[] = [];
    let meteor: Meteor | null = null;
    let raf = 0;
    let w = 0;
    let h = 0;

    // 鼠标 / 滚动带来的视差偏移：目标值与当前值，用插值让移动更柔和
    let targetX = 0;
    let targetY = 0;
    let curX = 0;
    let curY = 0;

    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const isSmall = () => window.innerWidth < 768;

    const build = () => {
      w = window.innerWidth;
      h = window.innerHeight;

      // 高清屏适配：canvas 位图尺寸 = CSS 尺寸 × dpr，
      // 再把坐标系缩放回 CSS 像素，之后按 CSS 坐标绘制即可，不会糊。
      canvas.width = Math.floor(w * dpr);
      canvas.height = Math.floor(h * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

      const byArea = Math.round((w * h) / 9000);
      const count = Math.max(
        70,
        Math.min(isSmall() ? 240 : 620, Math.round(isSmall() ? byArea * 0.4 : byArea)),
      );

      stars = Array.from({ length: count }, (_, i): Star => {
        const layer = i % 3;
        return {
          x: Math.random() * w,
          y: Math.random() * h,
          r: BASE_RADIUS[layer] * (0.7 + Math.random() * 0.6),
          base: BASE_ALPHA[layer] + Math.random() * 0.2,
          speed: 0.0006 + Math.random() * 0.0018,
          phase: Math.random() * Math.PI * 2,
          layer,
        };
      });
    };

    const paint = (t: number) => {
      ctx.clearRect(0, 0, w, h);

      for (const s of stars) {
        const p = PARALLAX[s.layer];
        const x = s.x + curX * p * 16;
        const y = s.y + curY * p * 16;
        const alpha = reduced ? s.base + 0.15 : s.base + 0.38 * Math.sin(t * s.speed + s.phase);
        ctx.globalAlpha = Math.max(0.04, Math.min(1, alpha));
        ctx.fillStyle = s.layer === 2 ? '#d5e6ff' : '#e8ecf6';
        ctx.beginPath();
        ctx.arc(x, y, s.r, 0, Math.PI * 2);
        ctx.fill();
      }

      // 流星：偶尔划过一颗
      if (meteor) {
        const k = meteor.life / meteor.max;
        ctx.globalAlpha = Math.max(0, Math.sin(k * Math.PI)) * 0.9;
        const grad = ctx.createLinearGradient(
          meteor.x,
          meteor.y,
          meteor.x - meteor.vx * 9,
          meteor.y - meteor.vy * 9,
        );
        grad.addColorStop(0, 'rgba(255,255,255,0.95)');
        grad.addColorStop(1, 'rgba(255,255,255,0)');
        ctx.strokeStyle = grad;
        ctx.lineWidth = 1.7;
        ctx.beginPath();
        ctx.moveTo(meteor.x, meteor.y);
        ctx.lineTo(meteor.x - meteor.vx * 9, meteor.y - meteor.vy * 9);
        ctx.stroke();
      }

      ctx.globalAlpha = 1;
    };

    let last = performance.now();

    const loop = (now: number) => {
      const dt = Math.min(now - last, 48);
      last = now;

      // 视差插值：当前值缓动追向目标值
      curX += (targetX - curX) * 0.055;
      curY += (targetY - curY) * 0.055;

      if (!meteor && Math.random() < 0.0016) {
        const startX = w * (0.25 + Math.random() * 0.7);
        const speed = 4 + Math.random() * 3;
        meteor = {
          x: startX,
          y: -20,
          vx: -speed * 0.55,
          vy: speed,
          life: 0,
          max: 90,
        };
      }
      if (meteor) {
        meteor.x += meteor.vx * (dt / 16.7);
        meteor.y += meteor.vy * (dt / 16.7);
        meteor.life += dt / 16.7;
        if (meteor.life > meteor.max || meteor.y > h + 60 || meteor.x < -80) meteor = null;
      }

      paint(now);
      raf = window.requestAnimationFrame(loop);
    };

    const onResize = () => {
      build();
      if (reduced) paint(0);
    };

    const onPointerMove = (e: PointerEvent) => {
      targetX = (e.clientX / window.innerWidth - 0.5) * 2;
      targetY = (e.clientY / window.innerHeight - 0.5) * 2;
    };

    const onScroll = () => {
      // 滚动时让星星轻微反向位移，制造纵深感
      targetY = Math.min(1.4, window.scrollY / (window.innerHeight * 1.6));
    };

    build();

    if (reduced) {
      // 命中「减少动态效果」：只画一帧静态星点，不启动动画循环
      paint(0);
    } else {
      raf = window.requestAnimationFrame(loop);
      window.addEventListener('pointermove', onPointerMove, { passive: true });
      window.addEventListener('scroll', onScroll, { passive: true });
    }
    window.addEventListener('resize', onResize);

    return () => {
      window.cancelAnimationFrame(raf);
      window.removeEventListener('resize', onResize);
      window.removeEventListener('pointermove', onPointerMove);
      window.removeEventListener('scroll', onScroll);
    };
  }, [reduced]);

  return (
    <canvas
      id="starfield"
      ref={canvasRef}
      aria-hidden="true"
      // 装饰元素不能拦截鼠标事件
      style={{ pointerEvents: 'none' }}
    />
  );
}