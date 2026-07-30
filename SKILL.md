---
name: fool-paper
description: "Use when the user asks to read, analyze, summarize, translate, or understand an academic paper / research article. Covers: Feynman deconstruction, first-principles analysis, formula explanation, innovation critique, reproducibility check, paper classification, and Q&A on a paper's content."
version: 0.2.0
author: FOOL-paper contributors
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [academic, research, paper-reading, feynman, first-principles, knowledge-management]
    related_skills: []
---

# FoolPaper — 学术论文智能阅读助手

> "Explain it like I'm a fool — then you truly understand it."

## 能力总览

| 能力 | 触发方式 | 说明 |
|------|---------|------|
| **📥 获取论文** | `arxiv:XXXX.XXXXX` / 本地PDF路径 / URL | 从 arxiv/OpenReview/本地获取全文 |
| **🌐 翻译+术语** | 自动随分析执行 | 中英翻译 + 术语延展解释 |
| **🧠 费曼拆解** | 每篇论文必须执行 | 层层简化，用自己的话解释 |
| **🔬 第一性原理** | 每篇论文必须执行 | 拆到不可再分的基本原理 |
| **📐 公式理解** | 论文中有 LaTeX 公式时必须执行 | 符号指代追踪 + 自然语言解释（调用 concept-explanation.md） |
| **💡 创新与不足** | 每篇论文必须执行 | novelty / limitation / improvement |
| **🔄 复现分析** | 每篇论文必须执行 | 数据集 + 环境 + 代码链接分析 |
| **🗂️ 归类入库** | 报告生成后自动 | 标签 + knowledge_base 存储 |
| **💬 追问** | 用户提出具体问题 | 基于论文上下文的交互问答 |

## 工作流程

用户输入论文来源后，按以下 pipeline 执行：

---

### ⚠️ 强制规则

以下分析模块对每篇论文**必须全部执行，不得跳过**。除非用户明确说"只做费曼拆解"等指定子集：

- ✅ 翻译 + 术语解释
- ✅ 费曼拆解
- ✅ 第一性原理分析
- ✅ 创新点与不足分析
- ✅ 复现分析
- ✅ 公式理解（论文包含数学符号或公式时自动触发）

执行完成后，**必须填充「我的思考」部分**，总结这篇论文对你个人的启发和疑惑，不得保留模板占位符。

---

### 第 1 步：入口检查

1. `safety.py` — 扫描论文标题/摘要，判断是否属于敏感领域
2. `complexity.py` — 预估页数、公式密度、引用数，决定 effort level

### 第 2 步：获取与解析

1. `fetcher.py` — 从 arxiv/URL/本地路径获取论文
2. `parser.py` — 提取正文段落、公式（LaTeX）、图表、引用
3. `cache.py` — 缓存解析结果（按文件 hash）

#### 元数据验证

生成笔记前必须检查以下字段，**禁止使用占位符或未经验证的值**：

- `arxiv_id`：必须去 arxiv API 查询确认，格式必须是 `XXXX.XXXXX`。如果找不到对应论文，标注 `⚠️ 未核实` 并说明原因，禁止使用文件名当 ID
- `title`：必须与论文原文标题一致，禁止截断
- `year`：必须核对论文出版年份
- `tags`：不能留 `未分类`（见标签规则）

### 第 3 步：分析（并行执行）

- `analyzer.py` 执行以下子任务（默认并行，用户可选串行）：
  - **翻译 + 术语解释**：调用 `prompts/translation.md`，遇到重要概念时引用 `prompts/concept-explanation.md`
  - **费曼拆解**：调用 `prompts/feynman-deconstruction.md`
  - **第一性原理**：调用 `prompts/first-principles.md`
  - **创新点分析**：调用 `prompts/innovation-analysis.md`
  - **复现分析**：调用 `prompts/replication-guide.md`
- `formula.py`（并行）：提取论文中的 LaTeX 公式，调用 `prompts/concept-explanation.md` 做语义解释
- `cache.py` 缓存每一路的分析结果

### 第 4 步：产出

1. `organizer.py` — 自动打标签、分类
2. `reporter.py` — 生成结构化 Markdown 阅读报告，写入 `knowledge_base/papers/`
3. `qa.py` — 进入交互问答模式，等待用户追问

#### 标签规则

- **禁止**将标签设为 `未分类`
- 如果 Agent 无法从论文内容推断标签，**必须调用 LLM 推断至少 1-3 个标签**
- 标签偏好顺序：论文原文关键词 > arxiv 分类 > LLM 推断 > 已有知识库标签
- 标签使用英文（便于跨语言检索），中文论文也可用中文

#### index.md 维护

写入新笔记时，同时更新 `index.md` 的概览表：

- 表头：`论文 | 年份 | 标签 | 一句话核心 | 星级`
- "一句话核心"从费曼拆解的"一句话总结"提取
- 按年份降序排列，最新在前
- 如旧笔记的信息已落后（如星级不合理），一并修正
- 删除重复或错误的条目

## 输出格式规范

### 报告结构（必须遵守）

每篇论文的 Markdown 笔记按以下顺序输出：

```markdown
---
title: ...
authors: ...
year: ...
arxiv_id: XXXX.XXXXX        # 必须真实，禁止占位符
tags: [tag1, tag2, ...]     # 禁止 未分类
date_read: YYYY-MM-DD
---

# 标题

**作者**: ...
**年份**: ...
**arxiv**: [ID](链接)

`标签1` `标签2`

## 摘要

[论文原文摘要翻译]

## 费曼拆解

### 一句话总结
...

### 术语降级表
...

### 从头推导
...

### 反事实
...

## 第一性原理分析

### 追问链
...

### 假设审计
...

## 公式解释

<!-- 对论文中每个关键公式执行 concept-explanation 模板，如果论文无公式则删除本节 -->

## 创新与不足

### 创新点
...

### 不足
...

### 改进方向
...

## 复现分析

### 环境/数据/代码
...

### 复现难度
...

## 我的思考

<!-- Agent 必须填充至少 3-5 句实际内容，禁止保留任何占位符或模板文字 -->
```

### 输出格式清单（每篇笔记写入前逐条检查）

- [ ] arxiv_id 在 YAML 中不带引号
- [ ] 标题行格式统一：`**作者**: ... | **年份**: ... | **会议**: ...`
- [ ] emoji（🧠 / 🔬 / 💡 / 🔄 / 📐）只在三级标题，不在二级
- [ ] 公式解释表中符号列使用 `**符号**` 加粗
- [ ] 「我的思考」每条以数字序号开头（1. / 2. / …）
- [ ] 复现难度评估用 🟢/🟡/🔴 开头
- [ ] 标签行使用反引号包裹每个标签
- [ ] ⚠️ **输出降级禁止**：知识库文件的输出内容和深度不得低于 Agent 在聊天框中的分析质量
- [ ] 写完后自检一遍，有不符合的修正后再提交

### 文件命名规则

笔记文件名使用 `{arxiv_id}.md` 格式（优先），无 arxiv ID 的论文使用 `{作者简写-标题关键词}.md`。

文件名中禁止出现 `unnamed` / `untitled` / `test` 等占位名称。

## 用户常用指令

### 🎯 新用户首次体验

输入以下指令了解全貌：

```
展示你的全部能力和输出结构
```

Agent 会：列出所有可执行模块 → 从知识库中选一篇已有论文展示分析结构 → 询问用户想读哪篇新论文。

这保证新用户第一次接触时不茫然，一条指令看到全貌。

---

```
"帮我读这篇论文 arxiv:2305.12345"
"用费曼技巧拆解第三章的证明"
"解释公式 (3) 里的符号都是什么"
"这篇的创新点在哪？有什么明显缺陷？"
"能复现吗？需要什么环境？"
"总结一下，然后归类到 Transformer 方向"
```

## Prompt 模板引用

分析时从 `prompts/` 目录加载对应的提示词模板。各模板的定位：

- `feynman-deconstruction.md` — 费曼拆解：层层简化到外行能懂
- `first-principles.md` — 第一性原理：追到不证自明的基本公理
- `innovation-analysis.md` — 识别 novelty / limitation / improvement
- `replication-guide.md` — 提取环境、依赖、代码库
- `concept-explanation.md` — 概念阐释引擎：类比+对偶+反向+盲区
- `translation.md` — 翻译指令：学术准确 + 术语加注

## 知识库结构

```
knowledge_base/
├── index.md              # 全局索引（自动维护）
└── papers/
    ├── 1512.03385.md               # 每篇论文一个笔记文件
    └── causal-feature-survey-wang.md
```

每个笔记文件包含 YAML frontmatter：
```yaml
---
title: 论文标题
authors: [作者列表]
arxiv_id: XXXX.XXXXX
tags: [transformer, scaling, attention]
category: NLP
read_at: 2025-01-15
rating: ★★★★☆
---
```

#### 引用边自动捕获

写入「我的思考」时，检查每一条思考是否明确提及了知识库中其他论文的标题或 ID：

- 如果匹配到已有论文，在 `graph.md` 中追加一条 `---|引用|---` 边
- 引用边使用 Mermaid 虚线样式 `-.->`
- 同时更新 graph.md 顶部的关系统计
- 多条思考提及同一篇论文只记一条引用，不重复计数
