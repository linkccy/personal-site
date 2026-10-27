import { useState } from 'react';
import { posts, type Block } from '../data/posts';
import { Reveal } from './Reveal';

function BlockView({ block }: { block: Block }) {
  switch (block.t) {
    case 'p':
      return <p>{block.text}</p>;
    case 'ul':
      return (
        <ul>
          {block.items.map((it) => (
            <li key={it}>{it}</li>
          ))}
        </ul>
      );
    case 'code':
      return <pre className="post-code">{block.text}</pre>;
  }
}

export function Blog() {
  // 同一时间只展开一篇，避免一次拉出很长的页面
  const [openId, setOpenId] = useState<string | null>(null);

  return (
    <section id="blog" className="section">
      <div className="wrap">
        <Reveal className="section-head">
          <div>
            <span className="section-tag">Notes</span>
            <h2 className="section-title">
              踩坑<span className="grad-text">笔记</span>
            </h2>
            <p className="section-sub">
              都是实训期间真实遇到的问题。写下来是因为当时卡了很久，不想再卡第二次。
            </p>
          </div>
        </Reveal>

        {posts.map((post, i) => {
          const id = `${post.date}-${post.title}`;
          const open = openId === id;

          return (
            <Reveal key={id} delay={i * 90}>
              <article className="card post">
                <div className="post-head">
                  <span className="post-date">{post.date}</span>
                  {post.tags.map((t) => (
                    <span className="chip" key={t}>
                      {t}
                    </span>
                  ))}
                  <span className="post-minutes">约 {post.minutes} 分钟</span>
                </div>

                <h3 className="post-title">{post.title}</h3>
                <p className="post-summary">{post.summary}</p>

                <button
                  type="button"
                  className="post-toggle"
                  aria-expanded={open}
                  aria-controls={`body-${i}`}
                  onClick={() => setOpenId(open ? null : id)}
                >
                  {open ? '收起全文 ▲' : '阅读全文 ▼'}
                </button>

                {open ? (
                  <div className="post-body" id={`body-${i}`}>
                    {post.body.map((b, bi) => (
                      <BlockView block={b} key={bi} />
                    ))}
                  </div>
                ) : null}
              </article>
            </Reveal>
          );
        })}
      </div>
    </section>
  );
}