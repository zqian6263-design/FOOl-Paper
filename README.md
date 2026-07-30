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

每篇论文生成一个 Markdown 笔记（7-9KB），含完整 frontmatter + 全模块分析：

```markdown
---
title: "LoRA: Low-Rank Adaptation of Large Language Models"
authors: "Edward Hu et al."
year: 2022
arxiv_id: 2106.09685
tags: [parameter-efficient-fine-tuning, low-rank-decomposition, ...]
---

# LoRA

**作者**: ... | **会议**: ICLR 2022 | **引用**: 20,000+

## 费曼拆解
### 术语降级表
| 术语 | 通俗解释 |
| Low-Rank | 瘦身版小矩阵 |

### 从头推导
1. W₀ ∈ R^(d×d)，ΔW 也是 d×d
2. 核心洞察: ΔW 不需要 d×d 自由度——低秩的

## 公式解释
| 符号 | 含义 | 维度 | 可调？|
| A | 压缩矩阵 | d×r | ✅ |

## 我的思考
> LoRA 与 Neural Causal Abstractions 有结构性共鸣——都在高维冗余中找低维结构。
```

完整案例见 `knowledge_base/papers/2106.09685.md`（LoRA）等 6 篇已生成笔记。

---

## 项目结构

```
foolpaper/
├── SKILL.md                    # 主入口 — Agent 加载即得全部能力
├── fool_paper/                 # Python 核心
│   ├── analyzer.py             # 6 路并行分析引擎
│   ├── formula.py              # 公式语义理解 + 符号追踪
│   ├── organizer.py            # 标签 + 入库
│   ├── knowledge_graph.py      # 跨论文关系图
│   └── ...
├── prompts/                    # 6 个分析模板
├── knowledge_base/             # 产物目录
└── tests/                      # 90 个测试
```

---

## 完整设计文档

本文档是给人看的概述。完整的设计决策、Pipeline 架构、知识图谱进化路线和 6 个痛点的完整论证见：

→ **[DESIGN.md](https://github.com/zqian6263-design/FOOl-Paper/blob/master/DESIGN.md)**
