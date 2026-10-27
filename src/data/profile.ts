/**
 * 站点全部可变内容集中在这里。
 * 改名字、改邮箱、加一个项目、加一条经历 —— 只改这个文件，组件不用动。
 *
 * ⚠️ 提交/部署前请把下面的 name / email / github 换成你自己的。
 */

export type Stat = { label: string; value: string };
export type TimelineItem = { date: string; title: string; desc: string };
export type SkillItem = { name: string; icon: string; level: number; note: string };
export type SkillGroup = { category: string; accent: string; items: SkillItem[] };
export type ProjectLink = { label: string; href: string };
export type Project = {
  title: string;
  summary: string;
  tags: string[];
  metrics: string[];
  links: ProjectLink[];
  accent: string;
};

export const profile = {
  /** 显示名，会用在导航 Logo、Hero 标题、页脚和终端卡片里 */
  name: 'chaoyi',
  title: '物联网工程在读 · 大模型方向',
  school: '大连民族大学',
  major: '物联网工程',
  direction: '大模型与深度学习工程',
  email: 'linkccy04@163.com',
  github: 'https://github.com/linkccy',
  location: '辽宁 · 大连',

  /** Hero 里循环打字的三句话 */
  taglines: [
    '从零训练了一个 63.91M 参数的中文预训练模型。',
    '手写过 BPE 分词器，也调过 Llama 3.1 的 LoRA。',
    '喜欢把踩过的坑写下来，而不是假装没踩过。',
  ],

  intro: [
    '我是物联网工程专业的在读学生，最近半年主要在做大模型相关的实践：从语料清洗、分词器训练，到 Transformer 结构实现、预训练、再到 LoRA 角色微调，整条链路都自己跑过一遍。',
    '相比"会调库"，我更在意"知道为什么"。所以训练脚本里的每一行我都逐行注释过，遇到模型输出异常也不会直接归因于"模型不行"，而是先回去看数据格式、学习率调度和损失遮盖是否符合预期。',
    '这个网站是我实训最后一天的产出：用 React 手写，没有用模板站。星空背景、终端卡片、时间轴都是自己实现的。',
  ],

  stats: [
    { label: '实训项目', value: '4' },
    { label: '模型参数', value: '63.91M' },
    { label: '训练语料', value: '1.24 GB' },
  ] satisfies Stat[],
};

/** 学习轨迹：按时间倒序或正序都行，这里用正序 */
export const timeline: TimelineItem[] = [
  {
    date: '10.19',
    title: '环境摸底与分词器',
    desc: '确认本机 CUDA 12.7 是驱动上限、无 nvcc；装好 PyTorch 与 tokenizers；手写 WordLevel 分词器，再用真实语料训练 6400 词表的 BPE。',
  },
  {
    date: '10.20',
    title: '逐行读懂 Transformer',
    desc: '把参考模型的每一行加上中文注释：RMSNorm、RoPE 旋转位置编码、GQA 分组注意力、SwiGLU 前馈，以及权重共享的 LM Head。',
  },
  {
    date: '10.21',
    title: '从零预训练 63.91M 模型',
    desc: '在自己电脑上先跑通流程，再抢到云端 A10 完整跑完 19848 步。加入 warmup 升温，最终 loss 从 8.69 降到 2.20。',
  },
  {
    date: '10.22',
    title: '三条微调路线',
    desc: '自研模型全参数 SFT、自研模型 LoRA、以及 Llama-3.1-8B 的 LoRA。自己写 SFTDataset 实现 loss 遮盖，只对回复部分计算损失。',
  },
  {
    date: '10.23',
    title: '零代码平台与版本管理',
    desc: '用秒哒和 Bolt.new 各生成并发布了一个应用，掌握了 Git 基本操作与远端仓库推送。',
  },
  {
    date: '10.24 – 10.26',
    title: '浏览器插件与官网',
    desc: '写了「图提取」Chrome 插件（MV3），能过滤小图、统一转 PNG、打包 ZIP 下载；配套做了官网并用 GitHub Pages 上线。',
  },
  {
    date: '10.27',
    title: '个人网站',
    desc: '先写 PRD 和技术设计文档，再让 AI 按文档实现。星空背景用 Canvas 手写，全站无第三方动画库。',
  },
];

/** 技能：level 取 0~100，只代表自评掌握程度 */
export const skillGroups: SkillGroup[] = [
  {
    category: '编程语言',
    accent: '#22d3ee',
    items: [
      { name: 'Python', icon: '🐍', level: 82, note: '日常主力，训练与数据处理脚本' },
      { name: 'TypeScript / JavaScript', icon: '🟨', level: 70, note: '插件与这个网站都是 TS 写的' },
      { name: 'C / C++', icon: '⚙️', level: 58, note: '课程基础，学过数据结构与嵌入式' },
      { name: 'SQL', icon: '🗄️', level: 55, note: '基本增删改查与联表查询' },
    ],
  },
  {
    category: '深度学习',
    accent: '#818cf8',
    items: [
      { name: 'PyTorch', icon: '🔥', level: 80, note: '手写训练循环、autocast 混合精度' },
      { name: 'Transformers 生态', icon: '🤗', level: 76, note: 'tokenizers、transformers、peft' },
      { name: '微调与 LoRA', icon: '🧩', level: 72, note: '自研 LoRA 层与 peft 都实践过' },
      { name: '数据处理', icon: '🧹', level: 74, note: 'JSONL 清洗、长度分布统计、去重' },
    ],
  },
  {
    category: '工程工具',
    accent: '#c084fc',
    items: [
      { name: 'Git / GitHub', icon: '🌿', level: 75, note: '分支、提交规范、Pages 部署' },
      { name: 'Linux 命令行', icon: '🐧', level: 72, note: '云端实例上跑训练的主力环境' },
      { name: 'React + Vite', icon: '⚛️', level: 65, note: '这个网站就是用它做的' },
      { name: 'Chrome 扩展开发', icon: '🧭', level: 68, note: 'Manifest V3、content script、CDP 调试' },
    ],
  },
];

export const projects: Project[] = [
  {
    title: '中文 BPE 分词器',
    summary:
      '用真实中文语料训练 6400 词表的 BPE 分词器，带完整的 chat template、特殊 token 与字节级回退，能在生僻字和 emoji 上无损还原。',
    tags: ['Python', 'tokenizers', 'BPE', 'ByteLevel'],
    metrics: [
      '语料 1.24 GB · 取前 6 万行训练',
      '压缩率 1.51 字符/token',
      '往返一致性 10 / 10',
      '36 个特殊 token，追加后 ID 不漂移',
    ],
    links: [],
    accent: '#22d3ee',
  },
  {
    title: '63.91M 中文预训练模型',
    summary:
      '从零实现 Transformer 结构（RMSNorm + RoPE + GQA + SwiGLU），在云端 A10 上完整跑完一轮预训练，并用余弦退火把学习率退到设定下限。',
    tags: ['PyTorch', 'RoPE', 'GQA', '预训练'],
    metrics: [
      'loss 8.69 → 2.20（19848 步）',
      '训练语料 4.3 亿 token',
      '引入 warmup 2000 步解决初期发散',
      '自建 loss 曲线绘制与断点拼接',
    ],
    links: [],
    accent: '#818cf8',
  },
  {
    title: '孙悟空角色 LoRA 微调',
    summary:
      '自写 SFTDataset 实现 loss 遮盖（只对回复部分计算损失），分别用全参数 SFT、自研 LoRA 层、以及 Llama-3.1-8B + peft 三种方式微调，并对比效果差异。',
    tags: ['LoRA', 'SFT', 'peft', '数据工程'],
    metrics: [
      '自建 301 条角色对话数据',
      'LoRA 可训练参数占比 0.31%',
      '自研模型 10 题答对 9 题',
      '发现"数据缺自我介绍会导致答非所问"',
    ],
    links: [],
    accent: '#c084fc',
  },
  {
    title: '图提取 · 电商图片下载插件',
    summary:
      'Chrome Manifest V3 扩展，在商品详情页右下角一键提取全部商品图，自动过滤图标与占位图，新标签页网格预览、勾选后统一转 PNG 并打包 ZIP。',
    tags: ['Chrome 扩展', 'TypeScript', 'Canvas', 'ZIP'],
    metrics: [
      '自动滚动触发懒加载后二次扫描',
      '过滤 100×100 以下与图标/占位图',
      '自写 store-only ZIP 打包器（零依赖）',
      '配套官网已用 GitHub Pages 上线',
    ],
    links: [
      { label: '在线预览', href: 'https://linkccy.github.io/image-grab/' },
      { label: '源码', href: 'https://github.com/linkccy/image-grab' },
    ],
    accent: '#34d399',
  },
];

/** Hero 右侧终端卡片逐行输出的内容 */
export const terminalLines: string[] = [
  '$ whoami',
  `${profile.name} · ${profile.school} ${profile.major}`,
  '',
  '$ cat direction.txt',
  profile.direction,
  '  → 从零训练过 63.91M 参数的中文预训练模型',
  '  → 手写过 BPE 分词器，调过 Llama 3.1 的 LoRA',
  '',
  '$ ls skills/',
  'Python  PyTorch  Transformers  LoRA  TypeScript  Git',
  '',
  '$ git log --oneline -1',
  '一切从"先把最小可用版本跑通"开始。',
];