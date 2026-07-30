# FoolPaper — 不是摘要器，是解剖框架

> "Explain it like I'm a fool — then you truly understand it."

用 AI 读论文的 92.86% 用户第三周就退化成了"帮我总结一下"。FoolPaper 用一套**强制规则**阻止退化——翻译、费曼拆解、第一性原理、公式追踪、创新分析、复现检查，6 个模块必须全部跑完。

---

## 和普通 AI 读论文的区别

| | 普通 AI + 提示词 | FoolPaper |
|--|-----------------|-----------|
| 本质 | 被动摘要器 | 主动解剖框架 |
| 对公式 | 忽略或模式匹配 | 符号追踪 + 结构分析 + 类比 |
| 对术语 | 照搬 | 降级为日常白话 |
| 对创新 | 不分真假 | 强制写"本质区别" |
| 对验证 | 无 | 复现分析（代码链接是否真实？） |
| 知识积累 | 对话结束即消失 | 知识库持久化 + 跨论文关联 |
| 使用趋势 | 越用越浅 | 框架强制多维，无法退化 |

---

## 它杀了 6 个行业痛点

| # | 痛点 | 研究来源 | FoolPaper 怎么杀 |
|---|------|---------|-----------------|
| 1 | **泛化偏见** — AI 泛化概率高 5 倍 | Royal Society Open Science, 2025 | 术语降级表：不许说"参数被优化"，必须说"大矩阵拆成 A×B，只训练几千个参数" |
| 2 | **公式盲区** — LLM 对公式完全无力 | Cornell + Google, 2025 | formula.py：每个符号追踪含义/维度/可训练性 + 结构分析 + 类比 |
| 3 | **真伪不分** — 把方法当领域，不分里程碑 | TLDR Scholar 翻车 | 强制写"本质区别"——一句话说清和 prior work 在哪个关键点分叉 |
| 4 | **幻觉当事实** — 不同 LLM 搜同一领域结果重叠率 0% | Galaxy Project, 2025 | concept-explanation 内置验证指令 + 复现分析硬检查代码/数据是否真实 |
| 5 | **越用越浅** — 第三周 92.86% 退化 | U of Washington, 2025 | SKILL.md 强制规则：6 个模块全部执行，不可跳过 |
| 6 | **不知道自己不知道** — 验证能力依赖你本不具备的领域知识 | FoolPaper 推导 | concept-explanation 盲区提示 + "我的思考"强制跨论文关联，暴露知识盲区 |

---

## 项目状态

当前版本 v0.2.0 — 已产出的实验版本。6 篇论文（LoRA / ResNet / NCA / BD-CLS / TeACFNet / 综述）已完成全模块分析并通过验证。知识库可用，持续迭代中。

## 适用人群

- 每天需要读学术论文的研究者 / 学生
- 想让 AI 做深度分析而非表面摘要的人
- 使用 Hermes Agent / Claude Code / OpenCode / Codex CLI 的用户

不适用：不需要分析深度、只想要两句话摘要的快速浏览场景。

---

## 快速开始

让任意 AI Agent（Hermes / Claude Code / Codex / OpenCode）加载 `SKILL.md`，然后说：

```
帮我读这篇论文 arxiv:2106.09685
```

Agent 自动跑完：安全扫描 → 复杂度预估 → PDF 解析 → 费曼拆解 → 第一性原理 → 公式追踪 → 创新分析 → 复现检查 → 打标签 → 入库 → 生成笔记。

---

## 能力列表

| 模块 | 做什么 |
|------|--------|
| `feynman-deconstruction` | 术语降级 + 从头推导 + 反事实——不许说"参数被优化" |
| `first-principles` | 追问链 + 假设审计——这个假设不成立会怎样？ |
| `formula` | 符号表（含义/维度/可训）+ 结构分析 + 类比 |
| `innovation-analysis` | 强制写"本质区别"——不是"提出新方法" |
| `replication` | 硬检查代码链接真实性、数据集可获取性 |
| `concept-explanation` | 类比 + 对偶 + 反向 + 盲区——不自欺 |
| `organizer` | 自动打标签 + 知识库入库 + 跨论文图 |
| `qa` | 基于论文上下文的追问 |

---

## 输出示例

从已生成的 LoRA 论文笔记中摘录：

**公式解释（符号追踪 + 结构分析 + 类比）：**

| 符号 | 含义 | 维度 | 可调？ |
|------|------|------|--------|
| W₀ | 预训练权重矩阵 | d×d | ❌ 冻结 |
| A | 低秩矩阵（压缩） | d×r | ✅ 训练 |
| B | 低秩矩阵（解压） | r×d | ✅ 训练 |
| r | 秩（rank） | r<<d | ✅ 超参 |

**费曼拆解·术语降级表：**

| 术语 | 通俗解释 |
|------|---------|
| Low-Rank | 瘦身版小矩阵 |
| Rank decomposition | 大矩阵拆成两个小矩阵相乘 |
| Fine-tuning | 先通识教育 → 再专业课 |

**「我的思考」摘录（跨论文关联）：**

> LoRA 的成功暗示了大模型的知识高度冗余——这与 Neural Causal Abstractions 在"高维冗余中寻找低维结构"上异曲同工。

完整笔记见知识库 `papers/2106.09685.md`。

项目展示页：`foolpaper.html`（位于项目根目录，双击即可在浏览器打开）。

---

## 项目结构

```
fool-paper/
├── SKILL.md                    # 主入口 — Agent 加载即得全部能力
├── AGENTS.md / CLAUDE.md / OPENCODE.md   # 各 Agent 入口
├── DESIGN.md                   # 完整设计文档
├── pyproject.toml              # Python 包配置
├── install.sh                  # 一键安装脚本
├── foolpaper.html              # 知识库静态展示页
├── fool_paper/                 # Python 核心（17 模块）
│   ├── paper.py                # 数据模型
│   ├── fetcher.py              # arxiv / PDF / URL 获取
│   ├── parser.py               # PDF 解析
│   ├── analyzer.py             # 6 路并行分析引擎
│   ├── formula.py              # 公式语义理解 + 符号追踪
│   ├── reporter.py             # 报告生成
│   ├── organizer.py            # 标签 + 入库
│   ├── knowledge_graph.py      # 跨论文关系图
│   ├── workflow.py             # Pipeline 编排
│   ├── cache.py                # 多级缓存
│   ├── safety.py               # 安全分类
│   ├── complexity.py           # 难度预估
│   ├── qa.py                   # 交互问答
│   └── knowledge_base/         # 产物目录
├── prompts/                    # 6 个分析模板
│   ├── feynman-deconstruction.md
│   ├── first-principles.md
│   ├── innovation-analysis.md
│   ├── replication-guide.md
│   ├── concept-explanation.md
│   └── translation.md
├── tests/                      # 单元测试
├── LICENSE                     # MIT
└── README.md
```

---

## 设计理念

FoolPaper 的完整设计决策、6 个行业痛点的完整论证、Pipeline 架构和知识图谱进化路线见 **[DESIGN.md](DESIGN.md)**（项目根目录）。

## License

MIT License — 详见 [LICENSE](LICENSE)。
