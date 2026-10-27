import { useEffect, useState } from 'react';
import { terminalLines } from '../data/profile';
import { useReducedMotion } from '../hooks/useReducedMotion';

function lineClass(line: string): string {
  if (line.startsWith('$')) return 'tl-cmd';
  if (line.includes('→')) return 'tl-arrow';
  return 'tl-out';
}

/**
 * Hero 右侧的终端卡片：逐行输出 `whoami` 的结果。
 * 点「重新执行」可以重放动画。
 */
export function Terminal() {
  const reduced = useReducedMotion();
  const [runId, setRunId] = useState(0);
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (reduced) {
      // 命中「减少动态效果」：直接全部显示，不做逐行动画
      setCount(terminalLines.length);
      return;
    }

    setCount(0);
    let shown = 0;
    const timer = window.setInterval(() => {
      shown += 1;
      setCount(shown);
      if (shown >= terminalLines.length) window.clearInterval(timer);
    }, 165);

    return () => window.clearInterval(timer);
  }, [reduced, runId]);

  const done = count >= terminalLines.length;

  return (
    <div className="terminal">
      <div className="terminal-bar">
        <span className="dot r" />
        <span className="dot y" />
        <span className="dot g" />
        <span className="terminal-name">zsh — profile — 80×24</span>
      </div>

      <div className="terminal-body">
        {terminalLines.slice(0, count).map((line, i) => (
          <div key={i} className={lineClass(line)}>
            {line === '' ? '\u00A0' : line}
            {!done && i === count - 1 ? <span className="caret" /> : null}
          </div>
        ))}
      </div>

      <div className="terminal-foot">
        <span className="terminal-hint">{done ? '执行完成 · exit 0' : '正在执行…'}</span>
        <button type="button" className="terminal-btn" onClick={() => setRunId((v) => v + 1)}>
          ↻ 重新执行
        </button>
      </div>
    </div>
  );
}