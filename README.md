# 个人网站 · chaoyi

第七天实训产出：一个用 React + TypeScript + Vite 手写的深色主题个人主页，
带 Canvas 星空背景、终端风 Hero、技能进度条、项目卡、踩坑笔记与联系方式。

线上地址：**<https://linkccy.github.io/personal-site/>**（2026-10-27 由 GitHub Actions 自动发布）

---

## 一、这个仓库里有什么

| 文件 / 目录 | 说明 |
| --- | --- |
| `PRD.md` | 产品需求文档：功能清单（FR-1 ~ FR-9）、非目标、视觉规范、验收标准 |
| `TECH_DESIGN.md` | 技术设计文档：选型与理由、目录结构、数据模型、六个关键技术点、性能预算 |
| `AGENTS.md` | 给 AI 编码助手的项目规则：改哪、别改哪、代码风格、绝对底线、测试要求 |
| `src/data/profile.ts` | 全站可变内容（姓名、邮箱、技能、项目、时间轴、终端输出） |
| `src/data/posts.ts` | 三篇踩坑笔记的正文 |
| `src/components/` | 九个区块组件 + 两个通用组件（`Reveal` / `Starfield`） |
| `src/hooks/useReducedMotion.ts` | 读取系统「减少动态效果」偏好 |
| `src/index.css` | 全部样式：设计变量、布局、动画、响应式 |
| `.github/workflows/deploy.yml` | GitHub Actions 工作流：push 到 main 后自动构建并发布到 Pages |
| `_tools/shot_site.py` | 用无头 Chrome 给本地站点拍截图（开发辅助，不参与构建） |
| `_tools/shot_live.py` | 给已经部署的线上地址拍截图，并打印线上页面自检信息 |

> 顺序上先有需求（PRD），再有设计（TECH_DESIGN），最后才有代码 —— 这也是
> 实训里「AI 项目开发五步流程」要求的顺序。

---

## 二、本地运行

需要 Node.js 18 以上（开发时用的是 Node 24）。

```bash
npm install          # 安装依赖
npm run dev          # 开发服务器，默认 http://localhost:5173
npm run build        # 类型检查 + 打包到 dist/
npm run preview      # 本地预览 dist/ 的构建结果
npx tsc --noEmit     # 只做类型检查
```

---

## 三、和课件示例不一样的地方

课件给了一份参考 PRD，我保留了大框架，但在主题和几个区块上做了替换：

| 维度 | 课件示例 | 本站 |
| --- | --- | --- |
| 底色 | `#0B0F1A` | `#070A12`，更深，星空更亮得出来 |
| 强调色 | 蓝色系 | **青 → 靛 → 紫** 三色渐变 `#22D3EE → #818CF8 → #C084FC` |
| Hero 右侧 | 头像 / 插画 | **可交互终端卡片**，逐行输出 `whoami`，可点「重新执行」重放 |
| 关于 | 大段自我介绍 | 三句话 + **教育背景信息卡** + **七条学习时间轴** |
| 项目 | 名称 + 描述 | 额外强制一行**可核对的关键指标**（如「loss 8.69 → 2.20」「往返一致性 10/10」） |
| 博客 | 外链或列表 | **站内展开阅读**，正文用结构化块描述，不引 Markdown 库 |
| 联系 | 静态列表 | 邮箱**一键复制**，且带 `execCommand` 降级 |
| 额外 | — | 星空有**鼠标视差**与**随机流星**，鼠标不动时也保持呼吸闪烁 |

配色、终端卡片、指标行、站内博客这四处是主要差异，
其余（内容宽度 1200px、卡片圆角、三档断点、验收标准）遵循课件要求。

---

## 四、部署

**当前状态：已上线 ✅**

| 项目 | 值 |
| --- | --- |
| 线上地址 | <https://linkccy.github.io/personal-site/> |
| 仓库 | <https://github.com/linkccy/personal-site> |
| 平台 | GitHub Pages（Source = `GitHub Actions`） |
| 发布方式 | 工作流 `Deploy to GitHub Pages`，push 到 `main` 自动触发 |
| 首次成功运行 | run `#2`，提交 `550eaf3`（2026-10-27） |

### 踩过的坑（都记在这，下次别再踩）

1. **`Get Pages site failed ... Error: Not Found`** —— 第一次运行（run `#1`）卡在「配置 Pages」这一步，
   前四步（拉代码 / 装 Node / `npm ci` / 构建）全是绿的。根因是仓库 **Settings → Pages → Source
   还是 `Deploy from a branch`**。改成 `GitHub Actions` 后立刻成功。
2. **`Node.js 20 is deprecated`** —— `checkout@v4`、`setup-node@v4` 这些旧版本被 GitHub 强制跑在
   Node 24 上。已升级到 `checkout@v7` / `setup-node@v7` / `configure-pages@v6` /
   `upload-pages-artifact@v5` / `deploy-pages@v5`，并把构建用的 Node 设为 24。
3. **`Failed to connect to github.com:443`** —— 国内访问 GitHub 时好时坏。
   本机 `127.0.0.1:7897` 有可用代理，一次性推送用：
   ```powershell
   git -c http.proxy=http://127.0.0.1:7897 -c https.proxy=http://127.0.0.1:7897 push
   ```

### 线上验证结果

用 `python _tools/shot_live.py` 拍线上站点时顺便读回页面信息：

```json
{"title":"chaoyi · 个人主页","sections":["home","about","skills","projects","blog","contact"],
 "canvas":true,"email":"linkccy04@163.com","scrollW":758,"clientW":758}
```

`canvas: true` 说明星空在跑，六个锚点区全在，`scrollW == clientW` 说明没有横向滚动。
资源也都正常：首页 1,291 字节、`index-*.js` 173,586 字节、`index-*.css` 20,835 字节、`favicon.svg` 853 字节，全部 HTTP 200。

---

以下三条路线任选，路线 A 是本次实际使用的。

本站是**纯静态站点**，`npm run build` 产出的 `dist/` 目录可以直接丢到任何托管平台。
`vite.config.ts` 里设了 `base: './'`，所以放在域名根目录或子路径下都能正常加载。

### 路线 A（推荐）：GitHub Actions + GitHub Pages

不用注册任何新账号，仓库自带的 Actions 负责构建和发布。
仓库里已经放好了工作流文件 `.github/workflows/deploy.yml`，推上去就能跑。

1. 在 GitHub 建一个**空的公开仓库**（三个初始化选项一个都别勾）。
2. 推代码（见下面「推送到 GitHub」）。
3. 仓库 **Settings → Pages → Source** 改成 **`GitHub Actions`**
   —— 这一步最容易漏，忘了会出现「Actions 跑绿了但网址打不开」。
4. 仓库 **Actions** 标签里会看到 `Deploy to GitHub Pages` 在跑，1~2 分钟后变绿。
5. 回到 **Settings → Pages**，顶部会显示 `Your site is live at https://<用户名>.github.io/<仓库名>/`。
6. 以后每次 `git push` 到 `main` 都会自动重新构建发布。

工作流做四件事：`checkout` → `setup-node`（Node 20，带 npm 缓存）→ `npm ci` → `npm run build`，
然后把 `dist/` 通过 `upload-pages-artifact` 上传、`deploy-pages` 发布。
用 `npm ci` 而不是 `npm install` 是为了严格按 lock 文件装依赖，保证本地和线上构建结果一致。

### 路线 B：Cloudflare Pages

1. 打开 <https://dash.cloudflare.com/> → 左侧 **Workers 和 Pages** → **创建** → **Pages** → **连接到 Git**。
2. 授权 GitHub，选中刚建的仓库。
3. 构建配置填写：
   - 框架预设：**Vite**（选成 `None` 又不填构建命令会 404）
   - 构建命令：`npm run build`
   - 输出目录：`dist`
4. 点 **保存并部署**，等 1~2 分钟，会得到一个 `xxx.pages.dev` 的地址。
5. 以后每次 `git push`，它会自动重新构建部署。

### 路线 C：Vercel

1. 打开 <https://vercel.com/> → 用 GitHub 登录 → 注册时选 **Hobby**（免费）。
2. 中途如果被要求绑定账户，选 **Skip securing my account** 跳过。
3. **Add New → Project** → 导入仓库。
4. Framework Preset 会自动识别为 Vite，Build Command `npm run build`、Output Directory `dist`，直接点 Deploy。
5. 得到 `xxx.vercel.app` 地址。

### 备选：手动推 gh-pages 分支

不想用 Actions 的话，也可以把构建产物直接推到 `gh-pages` 分支：

```bash
npm run build
cd dist
git init -b gh-pages
git add -A
git commit -m "build: 发布 dist"
git remote add origin https://github.com/<你的用户名>/<仓库名>.git
git push -f origin gh-pages
```

然后 **Settings → Pages → Source** 选 `Deploy from a branch` → 分支 `gh-pages`、目录 `/ (root)`。

### 推送到 GitHub

```bash
cd D:\软件开发实训\10_个人网站
git remote add origin https://github.com/<你的用户名>/<仓库名>.git
git push -u origin main
```

---

## 五、常见问题

**Q：部署后页面一片空白？**
打开浏览器控制台看是不是 `assets/index-xxx.js` 404。
GitHub Pages 子路径部署最容易踩这个坑，本站已通过 `base: './'` 规避；如果自己改过
`vite.config.ts`，记得改回来。

**Q：手机上星空会不会卡？**
星星数量按视口面积算，小于 768px 时再乘 0.4（约 100~240 颗），
并且动画完全跑在 `requestAnimationFrame` 里，不经过 React 状态更新。

**Q：系统开了「减少动态效果」会怎样？**
打字机、逐行输出、进度条增长、淡入位移四类动画全部停用，直接显示最终状态。
另外所有动画都用 `transform` / `opacity` 实现，避免触发重排。

**Q：怎么换成我自己的信息？**
只改 `src/data/profile.ts` 和 `src/data/posts.ts`，组件一行都不用动。
`name`、`email`、`github` 三处是必须替换的。

---

## 六、开发辅助

`_tools/shot_site.py` 会把 `dist/` 用本地静态服务跑起来，
再用无头 Chrome + CDP 分别按桌面 / 平板 / 手机的尺寸截图，
截图前会把入场动画强制置为终态，避免截到半透明的中间帧。

```bash
npm run build
python _tools/shot_site.py
```

输出目录默认是 `..\第七天作业截图\`。