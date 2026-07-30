# FOOL-paper 🎓

> **F**eynman Deconstruction • **O**pen Reading • **O**rganized Knowledge • **L**iterature Intelligence

学术论文智能阅读助手 — 让你读论文像读故事一样轻松。

## 亮点

- 🧠 **费曼拆解** — "如果你不能简单地解释它，说明你还没有真正理解它"
- 🔬 **第一性原理** — 层层剥解到不可再分的基本原理
- 🌐 **翻译 + 术语解释** — 扫清语言障碍
- 📐 **公式理解** — LaTeX → 自然语言，符号指代追踪
- 💡 **创新点与不足** — 自动识别 Novelty、Limitation、改进方向
- 🔄 **可复现分析** — 数据集、环境、代码链接一站式梳理
- 📁 **自动归类** — 同类论文自动聚簇，构建个人知识库
- 🗣 **交互问答** — 基于论文上下文的对话

## 安装

### 方式一：作为 AI Agent 技能（推荐）

```bash
git clone https://github.com/zqian6263-design/FOOL-paper.git
cd FOOL-paper
pip install -e .
```

然后在你的 Agent 中引用 `SKILL.md`：

- **Hermes Agent**: 在对话中输入 `@FOOL-paper` 或手动 load skill
- **Claude Code**: 项目自带 `CLAUDE.md`，自动识别
- **OpenCode**: 项目自带 `OPENCODE.md`，自动识别
- **Codex CLI**: 项目自带 `AGENTS.md`，自动识别

### 方式二：作为 Python 库

```bash
pip install git+https://github.com/zqian6263-design/FOOL-paper.git
```

## 快速开始

```python
from fool_paper.workflow import run_pipeline

# 分析一篇 arxiv 论文
report = run_pipeline("https://arxiv.org/abs/2306.xxxxx")

# 分析本地 PDF
report = run_pipeline("/path/to/paper.pdf")
```

## 使用方式

### 读一篇论文

```
帮我读这篇 arxiv:2306.xxxxx，用费曼技巧拆解
```

### 分析创新点

```
分析这篇论文的创新点和不足，给出改进建议
```

### 公式理解

```
解释论文第3节的公式，每个符号指代什么，和前面的公式有什么联系
```

### 知识管理

```
把这篇归类到「大语言模型」文件夹，和之前读的 Transformer 论文建立关联
```

## 知识库结构

```
knowledge_base/
├── index.md              # 全局索引
├── papers/
│   ├── attention-is-all-you-need.md
│   ├── llama-3-report.md
│   └── ...
└── concepts/
    ├── transformer.md
    ├── attention.md
    └── ...
```

每篇论文笔记包含：
- **YAML frontmatter** — 标题、作者、年份、标签、引用关系、文件路径
- **概要** — 一句话总结
- **费曼拆解** — 用最简单的语言解释核心思想
- **第一性原理** — 基本假设 → 推导链条
- **创新与不足** — 结构化分析
- **我的思考** — 连接已有知识的笔记

## 项目架构

```
FOOL-paper/
├── SKILL.md              # AI Agent 主入口
├── CLAUDE.md             # Claude Code 入口
├── OPENCODE.md           # OpenCode 入口
├── AGENTS.md             # Codex CLI 入口
├── install.sh            # 一键安装
├── fool_paper/           # 核心 Python 包
│   ├── paper.py          # 论文数据模型
│   ├── fetcher.py        # 论文获取
│   ├── parser.py         # PDF/HTML 解析
│   ├── analyzer.py       # LLM 分析引擎
│   ├── workflow.py       # Pipeline 编排
│   ├── reporter.py       # 阅读报告生成
│   ├── cache.py          # 多级缓存
│   ├── formula.py        # 公式理解
│   ├── complexity.py     # 难度评估
│   ├── safety.py         # 安全路由
│   ├── organizer.py      # 自动归类
│   ├── qa.py             # 交互问答
│   └── knowledge_base/   # 知识库
├── prompts/              # LLM 提示词模板
└── tests/                # 测试
```

## 开发

```bash
pip install -e ".[dev]"
pytest
ruff check fool_paper/
```

## 路线图

| 阶段 | 状态 | 功能 |
|------|------|------|
| Phase 1 | ✅ 完成 | 项目骨架 + SKILL.md + 数据模型 |
| Phase 2 | ⏳ 进行中 | 核心 pipeline（获取→解析→分析→报告） |
| Phase 3 | ⏳ 待开始 | 基础设施（缓存/安全/难度评估/工作流） |
| Phase 4 | ⏳ 待开始 | 增强功能（公式/问答/知识库/提示词） |
| Phase 5 | ⏳ 待开始 | 知识图谱 v2（跨论文引用/关系图） |

## License

MIT
