import { profile, timeline } from '../data/profile';
import { Reveal } from './Reveal';

export function About() {
  return (
    <section id="about" className="section">
      <div className="wrap">
        <Reveal className="section-head">
          <div>
            <span className="section-tag">About</span>
            <h2 className="section-title">
              关于<span className="grad-text">我</span>
            </h2>
            <p className="section-sub">
              从环境配置到模型上线，这条链路我完整走过一遍，也把踩过的坑都记了下来。
            </p>
          </div>
        </Reveal>

        <div className="about-grid">
          <Reveal>
            <div>
              {profile.intro.map((p, i) => (
                <p className="intro-p" key={i}>
                  {p}
                </p>
              ))}
            </div>
          </Reveal>

          <Reveal delay={120}>
            <div className="card edu-card">
              <h3 style={{ fontSize: 17, marginBottom: 10 }}>教育背景</h3>
              <div className="edu-row">
                <span className="edu-key">学校</span>
                <span className="edu-val">{profile.school}</span>
              </div>
              <div className="edu-row">
                <span className="edu-key">专业</span>
                <span className="edu-val">{profile.major}</span>
              </div>
              <div className="edu-row">
                <span className="edu-key">方向</span>
                <span className="edu-val">{profile.direction}</span>
              </div>
              <div className="edu-row">
                <span className="edu-key">所在地</span>
                <span className="edu-val">{profile.location}</span>
              </div>
            </div>
          </Reveal>
        </div>

        <Reveal>
          <div className="timeline">
            {timeline.map((item) => (
              <div className="tl-item" key={item.date + item.title}>
                <div className="tl-date">{item.date}</div>
                <h3 className="tl-title">{item.title}</h3>
                <p className="tl-desc">{item.desc}</p>
              </div>
            ))}
          </div>
        </Reveal>
      </div>
    </section>
  );
}