# 技术设计文档（TECH_DESIGN）

> 配套文档：`PRD.md`（要做什么）、`AGENTS.md`（怎么协作）
> 本文件回答三个问题：**用什么做、代码怎么组织、有哪些坑要提前避开。**

---

## 一、技术栈选型

### 1.1 结论

| 层 | 选型 | 版本 |
|---|---|---|
| 构建工具 | Vite | ^6 |
| 语言 | TypeScript | ^5.6 |
| UI 框架 | React | ^18.3 |
| 样式 | 原生 CSS + CSS 变量，Tailwind 作补充 | Tailwind ^4 |
| 动效 | Canvas 2D + CSS transition + IntersectionObserver | 原生 |
| 状态管理 | 无（组件内 `useState`） | — |
| 路由 | 无（单页锚点滚动） | — |
| 后端 | 无 | — |
| 数据库 | 无 | — |
| 部署 | 静态托管平台 | — |

### 1.2 选型理由

**为什么用 Vite 而不是 Next.js？**
这是个纯静态展示页，没有服务端数据、也不需要 SEO 优化到极致。Next.js 会引入 Node 运行时和
SSR 概念，部署时要区分 Node/静态两种模式，对个人站是过度设计。Vite 开发时秒级热更新，
构建产物就是一堆静态文件，扔到任何托管平台都能跑。

**为什么用 React 而不是纯 HTML？**
区块有 6 个，每个区块内部还有列表渲染（技能分组、项目卡片、博客列表）。纯 HTML 写出来会有
大量重复结构，改一处要改多行。用 React 把数据抽到 `src/data/` 之后，加一个项目只需加一个对象。

**为什么样式以原生 CSS 为主、Tailwind 为辅？**
本项目的视觉是高度定制的：星空渐隐、玻璃拟态卡片、渐变文字、时间轴竖线、进度条动画。
这些用原子类写出来会变成一长串 `className`，可读性反而更差。所以：
- **布局类**（flex、grid、间距、断点）用 Tailwind 原子类，写起来快；
- **视觉类**（渐变、阴影、动画、canvas 层级）写在 `index.css` 里，用 CSS 变量统一管理。

**为什么不用 Framer Motion 之类的动画库？**
本项目只用到「淡入上移」一种入场动画，用 `IntersectionObserver` 加一个 class 就能实现，
不到 20 行代码。为一个效果引入 30KB+ 的库不划算。

**为什么不用全局状态管理？**
唯一需要跨组件共享的状态是「哪个项目/文章被展开了」，而这个状态归属于各自区块内部。
`useState` 完全够用，引入 Redux/Zustand 属于杀鸡用牛刀。

---

## 二、项目结构

```
10_个人网站/
├── PRD.md                      # 产品需求文档
├── TECH_DESIGN.md              # 本文档
├── AGENTS.md                   # AI 协作规范
├── README.md                   # 怎么跑、怎么部署
├── package.json
├── vite.config.ts              # Vite 配置（含 Tailwind 插件、base 路径）
├── tsconfig.json
├── index.html                  # 单页入口，含 SEO meta 与防闪白脚本
├── src/
│   ├── main.tsx                # React 挂载入口
│   ├── App.tsx                 # 区块编排（谁在前谁在后）
│   ├── index.css               # 全局样式：变量、布局、动画、工具类
│   ├── data/
│   │   ├── profile.ts          # ★ 个人信息、技能、项目、时间轴（改内容只动这里）
│   │   └── posts.ts            # ★ 博客文章（含正文段落）
│   └── components/
│       ├── Starfield.tsx       # 星空 Canvas（性能敏感）
│       ├── Nav.tsx             # 吸顶导航 + 汉堡菜单 + 滚动高亮
│       ├── Hero.tsx            # 首屏：简介 + 打字机 + 终端卡片
│       ├── Terminal.tsx        # 终端卡片（逐行输出动画）
│       ├── About.tsx           # 个人简介 + 时间轴 + 教育背景
│       ├── Skills.tsx          # 技能分组 + 进度条
│       ├── Projects.tsx        # 项目卡片网格
│       ├── Blog.tsx            # 文章列表 + 正文展开
│       ├── Contact.tsx         # 邮箱复制 + 社交链接
│       ├── Footer.tsx
│       └── Reveal.tsx          # 通用「进入视口淡入」包装组件
├── public/
│   └── favicon.svg
└── _资料/                       # 课件 PDF 与提取文本（不参与构建）
```

**约定**：`_资料/`、`dist/`、`node_modules/` 都写进 `.gitignore`，不提交。

---

## 三、数据模型

项目没有数据库，但数据形状需要先定好，否则组件之间会打架。

### 3.1 Profile（`src/data/profile.ts`）

```ts
export const profile = {
  name: string;          // 显示名
  title: string;         // 一句话职位
  school: string;        // 学校
  major: string;         // 专业
  direction: string;     // 方向
  email: string;
  github: string;        // 完整 URL
  taglines: string[];    // 打字机轮播的三句话
  intro: string[];       // 关于我的段落数组
  stats: { label: string; value: string }[];  // Hero 下方数字徽章
};

export const timeline: { date: string; title: string; desc: string }[];

export const skillGroups: {
  category: string;      // 分类名
  accent: string;        // 该分类的主题色（十六进制）
  items: { name: string; icon: string; level: number; note?: string }[];
}[];                     // level 取 0~100

export const projects: {
  title: string;
  summary: string;
  tags: string[];
  metrics: string[];     // 关键指标行，如 "loss 8.69 → 2.20"
  links?: { label: string; href: string }[];
  accent: string;
}[];
```

### 3.2 Post（`src/data/posts.ts`）

```ts
export type Block =
  | { t: 'p'; text: string }        // 段落
  | { t: 'ul'; items: string[] }    // 无序列表
  | { t: 'code'; text: string };    // 代码块

export type Post = {
  date: string;      // YYYY-MM-DD
  tags: string[];
  title: string;
  summary: string;
  minutes: number;   // 预计阅读时长
  body: Block[];
};
```

**为什么正文用结构化 Block 而不是 Markdown 字符串？**
避免为了渲染 Markdown 引入 `marked` + `highlight.js`（约 60KB）。
本项目正文只需要段落、列表、代码块三种形态，用联合类型描述即可，
渲染时 `switch` 一下，零依赖且类型安全。等文章多了再换 Markdown。

---

## 四、关键技术点

### 4.1 星空 Canvas（最容易写崩的一块）

**要求**：全屏、三层星星、独立闪烁相位、轻微视差、窗口缩放不模糊、不卡。

**实现要点**：

```ts
// 1. 高分屏适配：canvas 的 width 要用 CSS 尺寸 × dpr
canvas.width  = Math.floor(w * dpr);
canvas.height = Math.floor(h * dpr);
ctx.setTransform(dpr, 0, 0, dpr, 0, 0);   // 之后按 CSS 像素坐标画即可

// 2. 星星数量随屏幕面积与设备变化
const base = Math.round((w * h) / 9000);
const count = isMobile ? base * 0.4 : base;

// 3. 三层：远层暗小、近层亮大，各自视差系数不同
const layer = i % 3;                       // 0 远 / 1 中 / 2 近
const parallax = [0.15, 0.35, 0.7][layer];

// 4. 闪烁：每颗星有独立相位，用正弦而不是随机数
star.alpha = 0.35 + 0.4 * Math.sin(t * star.speed + star.phase);
```

**必须避开的坑**：

| 坑 | 现象 | 处理 |
|---|---|---|
| 不做 dpr 处理 | 高分屏上星星糊成一团 | `setTransform(dpr,0,0,dpr,0,0)` |
| 忘了 `cancelAnimationFrame` | 组件卸载后仍在跑，内存泄漏 | `useEffect` 返回值里取消 |
| 监听 resize 用匿名函数 | 无法移除，重复绑定 | 用具名函数并 `removeEventListener` |
| 每帧重算星星数组 | 帧率掉到 20 以下 | 星星数组只在 resize 时重建 |
| 忽略 reduced-motion | 晕动症用户不适 | 命中则只画一次静态星点 |
| 动画跑在 React 状态里 | 每帧触发 re-render，直接卡死 | 一切绘制走 `requestAnimationFrame`，**不进 state** |

### 4.2 滚动高亮（导航）

**不要用 IntersectionObserver 判断当前区块**。原因：首屏加载时，视口内可能同时存在两个区块，
按"进入即高亮"会把「核心功能」这类靠后的区块误判为当前项。

**改用位置比较**：

```ts
const line = window.scrollY + window.innerHeight * 0.35;
// 找到最后一个 top <= line 的区块
```

这样高亮线固定在视口上三分之一处，稳定且符合直觉。

### 4.3 入场动画（Reveal）

```tsx
// 思路：初始 opacity:0 + translateY(18px)，进入视口后加 .in
const io = new IntersectionObserver(([e]) => {
  if (e.isIntersecting) { el.classList.add('in'); io.unobserve(e.target); }
}, { threshold: 0.12 });
```

**降级**：`typeof IntersectionObserver === 'undefined'` 时直接加 `.in`，
避免老浏览器上整页空白（这是最常见的"白屏"投诉来源）。

### 4.4 打字机效果

用 `setInterval` 逐字追加，注意三件事：

1. 组件卸载时 `clearInterval`，否则切换页面后仍在后台跑。
2. 到达句尾后停留约 1.4 秒再删除，删除速度比输入快（观感更自然）。
3. 命中 `prefers-reduced-motion` 时**直接显示完整第一句**，不做动画。

### 4.5 邮箱复制

```ts
await navigator.clipboard.writeText(email);      // 需要 HTTPS 或 localhost
```

`clipboard` API 在 **http 环境（非 localhost）下不存在**，所以必须有降级：
用 `document.execCommand('copy')` 配合临时 `textarea`，都失败则提示手动复制。
部署到托管平台后是 HTTPS，正常路径不会走到降级分支。

### 4.6 构建与部署路径

托管平台分两种发布方式：

| 平台 | 发布内容 | base 路径 |
|---|---|---|
| Cloudflare Pages / Vercel | 构建产物 `dist/` | `/` |
| GitHub Pages（项目页） | `dist/` 推到 `gh-pages` 或 `docs/` | `/<仓库名>/` |

**注意**：GitHub Pages 的项目页部署在子路径下，必须在 `vite.config.ts` 里设
`base: '/<仓库名>/'`，否则 CSS/JS 全部 404（页面白屏、样式全丢）。
本项目默认 `base: './'`（相对路径），三种平台都能用，这是最省心的选择。

---

## 五、开发顺序（三步走）

| 阶段 | 做什么 | 完成标志 |
|---|---|---|
| 一、框架 | Vite 项目 + 六个空区块 + 导航能跳 | `npm run dev` 打开能看到骨架 |
| 二、核心 | 星空 → Hero → 项目 → 技能 → 关于 → 博客 → 联系 | 内容都在，能滚动看完 |
| 三、打磨 | 动效、响应式、对比度、reduced-motion、性能 | PRD 第七节全部打勾 |

每完成一个区块就 `git commit` 一次，出问题能快速回退。

---

## 六、性能预算

| 项 | 预算 | 实测 |
|---|---|---|
| 首屏 JS（gzip） | < 200 KB | 见 README 实测值 |
| 首屏 CSS（gzip） | < 20 KB | 同上 |
| 构建总耗时 | < 10 s | — |
| 星空帧率（桌面） | ≥ 55 fps | — |
| 星空帧率（移动） | ≥ 50 fps | — |

达成手段：不引动画库、不引 Markdown 库、图标全部内联 SVG/emoji、不使用外部字体 CDN。

---

## 七、已知限制

1. 博客正文是手写数据结构，写作体验不如 Markdown，文章多了需要换成构建期解析。
2. 没有后端，联系区只能做复制邮箱，不能提交表单。
3. 星空用 Canvas 2D 而非 WebGL，星星数量上万时会掉帧（当前用量约 1500 以内，安全）。