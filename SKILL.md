---
name: fool-paper
description: "Use when the user asks to read, analyze, summarize, translate, or understand an academic paper / research article. Covers: Feynman deconstruction, first-principles analysis, formula explanation, innovation critique, reproducibility check, paper classification, and Q&A on a paper's content."
version: 0.1.0
author: FOOL-paper contributors
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [academic, research, paper-reading, feynman, first-principles, knowledge-management]
    related_skills: []
---

# FOOL-paper — 学术论文智能阅读助手

## Overview

FOOL-paper 是一个 AI Agent 驱动的学术论文阅读辅助系统。核心思想：

1. **降低阅读障碍** — 翻译 + 术语解释 + 句式简化
2. **降低理解难度** — 费曼技巧 + 第一性原理层层拆解
3. **辅助深度思考** — 创新点识别、不足分析、改进方向推荐
4. **构建知识网络** — 论文自动归类、标签管理、知识库构建
5. **交互式学习** — 基于论文上下文的问答

> **名字由来**：F = Feynman Deconstruction, O = Open Reading, O = Organized Knowledge, L = Literature Intelligence

## When to Use

- 用户要求阅读/分析/总结一篇论文（arxiv/PDF/URL）
- 用户要求理解论文中的公式、概念、方法
- 用户需要评估论文的创新点和不足之处
- 用户想复现论文的实验或方法
- 用户想将论文归纳到自己的知识库中
- 用户想基于某篇论文进行问答/讨论

**不要用于**：非学术文本的分析（新闻、博客等），没有全文可获取的论文（无法获取时告知用户原因）。

## Core Workflow

当你收到论文分析请求时，遵循以下流程：

### Step 1: 识别论文来源

确定用户提供的论文来源类型：

| 来源 | 示例 | 提取方式 |
|------|------|---------|
| arxiv URL/ID | `arxiv:2306.xxxxx` / `https://arxiv.org/abs/2306.xxxxx` | `fool_paper.fetcher.from_arxiv()` |
| arxiv PDF | `https://arxiv.org/pdf/2306.xxxxx.pdf` | `fool_paper.fetcher.from_arxiv_pdf()` |
| 本地 PDF | `/path/to/paper.pdf` | `fool_paper.fetcher.from_local_pdf()` |
| 通用 URL | `https://openreview.net/forum?id=xxx` | `fool_paper.fetcher.from_url()` |
| OpenReview | OpenReview forum URL | `fool_paper.fetcher.from_openreview()` |

若为纯文本/LaTeX 源码直接让用户提供即可。

### Step 2: 门户检查 — Safety + Complexity

#### Safety Check

对论文标题和摘要进行安全扫描：

```
safety_level = fool_paper.safety.classify(title, abstract)
```

| 级别 | 含义 | 行为 |
|------|------|------|
| `safe` | 常规学术论文 | 正常分析 |
| `sensitive` | 涉及敏感领域（生物/化学/网络/国防） | 降级：仅做客观翻译和概念解释，不做改进建议 |
| `restricted` | 明确违禁内容 | 拒绝分析，说明原因 |

#### Complexity Estimate

```
effort = fool_paper.complexity.estimate(pages, formula_density, ref_count)
```

| Effort Level | 适用场景 | 建议模型 |
|-------------|---------|---------|
| `low` | ≤8 页、少公式、survey | 快速模型 |
| `medium` | 8-15 页、常规 | 标准模型 |
| `high` | >15 页、密集公式、方法论论文 | 强模型 + 高 effort |
| `very_high` | 数学/理论论文、>25 页 | 最强模型 + 最大 effort |

**向用户报告**：安全分类结果 + 预估复杂度 + 预计模型选择，让用户确认或调整。

### Step 3: 获取与解析

```python
from fool_paper.fetcher import fetch_paper
from fool_paper.parser import parse_paper

# 获取论文全文
raw = fetch_paper(source)

# 解析为结构化文本
parsed = parse_paper(raw)
# 返回: {title, authors, abstract, sections, formulas, figures, references, ...}
```

如果 arxiv API 无法获取摘要/元数据，尝试直接从 PDF 提取。

**无法获取时**：明确告知用户原因（网络问题、PDF 损坏、PDF 受密码保护等），不要假装成功。

**解析要点**：
- 按章节(section)组织正文段落
- 单独提取公式（LaTeX 形式）
- 记录图表标题和引用
- 记录参考文献列表

### Step 4: 运行分析

根据用户的意图（可以一次跑多项），调用 `analyzer.py` 执行分析任务：

```python
from fool_paper.analyzer import analyze

results = analyze(
    paper=parsed,
    tasks=[           # 根据用户需求组合
        "translate",  # 翻译 + 术语解释
        "feynman",    # 费曼拆解
        "first_principles", # 第一性原理
        "innovation", # 创新+不足+改进
        "replication",# 复现分析
    ],
    effort=effort,   # 从 Step 2 获取
)
```

**各任务说明**：

#### 翻译 (translate)
- 长文分段翻译（必要时保持原文对照）
- 专业术语首次出现时给出解释和背景
- 难句进行句式简化

#### 费曼拆解 (feynman)
- 核心步骤：
  1. **一句话总结全篇** — 这篇论文到底在说什么？
  2. **用最简单的话解释核心方法** — 假设你的听众是本科生
  3. **指出"这里我其实没讲清楚"的部分** — 哪些地方还没有完全理解？
  4. **类比和实例** — 用生活例子类比论文的核心思想
  5. **重新整理** — 用自己的逻辑重新组织论文的论证链条
- 提示词模板参考 `prompts/feynman-deconstruction.md`

#### 第一性原理 (first_principles)
- 拆解过程：
  1. **基本假设** — 论文隐含/显式的假设是什么？
  2. **推导链条** — 从假设到结论的逻辑链
  3. **哪一步可以质疑** — 哪些推导环节比较薄弱？
  4. **还原到基础学科** — 核心理念对应到数学/物理/计算机科学的最基础原理
- 提示词模板参考 `prompts/first-principles.md`

#### 创新分析 (innovation)
- 结构化输出：
  - **Novelty** — 这篇论文的原创贡献是什么？和已有工作相比真正新在哪里？
  - **Strengths** — 方法/实验/理论上的亮点
  - **Limitations** — 方法的局限、假设的缺陷、实验的不足
  - **Improvements** — 至少推荐 2-3 个可行的改进方向（具体、可操作）
- 提示词模板参考 `prompts/innovation-analysis.md`

#### 复现分析 (replication)
- 检查内容：
  - **数据集** — 使用的数据集是否公开？
  - **代码** — 论文是否有官方/第三方实现？链接？
  - **环境** — 训练/实验环境配置是否可重建？
  - **核心步骤** — 算法的关键步骤是否描述足够详细
  - **复现难度评估** — 容易/中等/困难，理由
- 提示词模板参考 `prompts/replication-guide.md`

#### 公式理解 (formula) — 并行进行分析
如果论文包含公式，用户可能需要额外理解公式：
```python
from fool_paper.formula import explain_formula
explanations = explain_formula(parsed.formulas, parsed.sections)
```
每个公式输出：
- 公式的数学含义（自然语言）
- 每个符号的定义和出处（"公式(3)中的 Σ 在 3.1 节定义为…"）
- 与前文公式的依赖关系
- 通俗类比

### Step 5: 归类入库

```python
from fool_paper.organizer import classify_and_store

# 自动分配标签并存入知识库
classify_and_store(parsed, results, kb_path="knowledge_base/")
```

**归类策略**：
- 基于标题+摘要+关键词自动分配标签（如 NLP / CV / RL / 理论等）
- 优先匹配已有标签，必要时创建新标签
- 每篇论文在 `knowledge_base/papers/` 下创建一个 Markdown 文件
- 更新 `knowledge_base/index.md` 全局索引

### Step 6: 生成阅读报告

```python
from fool_paper.reporter import generate_report

report = generate_report(parsed, results, format="markdown")
```

**报告输出格式**：

```markdown
# [论文标题]

> 作者 | 年份 | 来源 | 标签

## 📝 摘要（翻译）

## 🧠 费曼拆解

### 一句话总结
...

### 用最简单的话解释
...

### 类比
...

## 🔬 第一性原理

### 基本假设
...
### 推导链条
...
### 可以质疑的环节
...

## 💡 创新与不足

| 项目 | 内容 |
|------|------|
| Novelty | ... |
| Strengths | ... |
| Limitations | ... |
| 改进方向 | 1. ... 2. ... 3. ... |

## 🔄 复现分析

| 项目 | 状态 |
|------|------|
| 数据集 | ✅/⚠️/❌ |
| 代码 | ✅/⚠️/❌ |
| 环境 | ✅/⚠️/❌ |
| 复现难度 | 容易/中等/困难 |

## 📐 公式理解

[公式相关解释]

## 🤔 我的思考

[留给用户记录自己的理解和疑问]

## 📎 引用

- 重要引用 1
- 重要引用 2
```

### Step 7: 交付用户

将 `report` 返回给用户，内容包括：

1. **简短开场** — 论文标题 + 来源 + 基本信息
2. **报告全文** — 完整的 Markdown 报告
3. **后续操作建议**：
   - "需要进一步解释某个公式/概念吗？"
   - "想深入讨论某个改进方向吗？"
   - "这篇论文和之前读过的那篇 XX 有联系，需要我建立关联吗？"
   - "有任何地方讲得太快需要重新解释吗？"

## 交互问答模式

如果用户在阅读报告后想继续对话：

```python
from fool_paper.qa import ask_about_paper

# 基于论文上下文回答用户问题
answer = ask_about_paper(question, parsed, context=results)
```

这种模式下：
- 始终引用论文原文段落的出处
- 不确定时明确指出"论文中没有明确说明，我的理解是…"
- 对于超出论文范围的问题，引导回论文 + 提供已知的最佳猜测

## 知识管理

### 查看知识库

```
显示我的知识库
→ 按标签展示已读论文列表
→ 或查询特定标签下的论文
```

### 跨论文关联

```
这篇文章和之前读的 XX 有什么关系？
→ 对比两篇论文的核心方法、假设、实验设置
→ 找出共同引用和不同点
```

### 导出知识库

```
导出我的知识库
→ knowledge_base/ 目录打包
→ 或生成知识图谱可视化
```

## Common Pitfalls

1. **PDF 解析不完整** — 某些 PDF（扫描版、双栏紧凑排版）可能提取失败或丢失顺序。告知用户局限性，尝试用 OCR 模式。
2. **arxiv API 被限流** — 短时间多次请求可能被限。内部自动重试 + 退避。
3. **公式提取错误** — 复杂 LaTeX 或嵌入图片的公式无法正确提取。向用户报告哪些公式无法解析。
4. **LLM 幻觉** — AI 分析尤其是"创新分析"和"改进方向"可能产生幻觉。在报告中标注"这是 AI 生成的分析，建议人工复核"。
5. **长论文 token 超限** — 超过上下文窗口的论文需要分段处理。自动将长论文按章节分段分析后合并。
6. **不要一次性跑所有分析** — 除非用户明确要求，否则根据上下文判断用户真正需要什么。一个用户说"帮我翻译这篇论文"，你不要跑去分析创新点和复现。

## Verification Checklist

- [ ] 论文来源已识别，获取成功或明确告知失败原因
- [ ] 安全分类已执行并告知用户
- [ ] 复杂度已评估，模型选择已确定
- [ ] 分析任务仅包含用户需要的（不额外增加）
- [ ] 阅读报告已生成并交付用户
- [ ] 论文已存入知识库（若用户同意）
- [ ] 给出了后续操作的建议

## 已知限制

- 不支持扫描版 PDF 的 OCR（依赖 PyMuPDF 的文本提取精度）
- 不支持数学公式的语义理解（v1 仅做 LaTeX → 自然语言解释）
- 跨论文知识图谱 v2 实现
