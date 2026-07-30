# FoolPaper — 学术论文智能阅读助手

> "Explain it like I'm a fool — then you truly understand it."

---

## 一、项目定位

**FoolPaper 不是一个论文摘要器。它是一个反懒惰的深度阅读框架。**

市面上用 AI 读论文的常见做法是：把 PDF 丢给 ChatGPT/Claude，说一句"帮我总结一下"，得到一个听起来合理的摘要——然后用户以为自己懂了。这是**"听起来对"陷阱**：AI 流畅的概括能力掩盖了它没有真正理解的事实。

FoolPaper 的解法是**强制拆解**：通过一整套必须执行的规则，强迫 AI 将自己从泛化惯性中拽出来，从"听起来对"变成"真的对"。

### 定位对比

| | 普通 AI + 提示词 | FoolPaper |
|--|-----------------|-----------|
| 本质 | 被动摘要器 | 主动解剖框架 |
| 产出风格 | 流畅但可能空洞 | 结构化但有据可查 |
| 对公式 | 忽略或字符串模式匹配 | 符号追踪 + 结构分析 + 类比 |
| 对术语 | 照搬 | 降级为日常语言 |
| 对创新 | 不分真假 | 强制写"本质区别" |
| 验证环节 | 无 | concept-explanation + 复现分析 |
| 知识积累 | 单次对话即消失 | 知识库持久化 + 跨论文关联 |
| 使用趋势 | 越用越浅（92.86% 退化为阅读理解） | 强制多维度分析，无法退化 |

---

## 二、行业痛点映射

基于 2025-2026 年多项独立研究（剑桥大学、康奈尔大学+Google、TLDR Scholar 翻车实录、Science 社论等），用普通 AI 读论文存在 6 个深层问题：

### 痛点 1：泛化偏见（Overgeneralization Bias）

AI 总结科学文献时，倾向于比原文更宽泛地概括。人类 vs AI 对比：**AI 的泛化概率高出近 5 倍**（Royal Society Open Science, 2025）。越新的模型泛化越严重——优化流畅度的代价是牺牲了精确性。

**FoolPaper 的 kill**：费曼拆解的"术语降级表"强制将抽象术语逐条转为可验证的具体大白话。不允许"模型的某些参数被优化"——必须说"把大矩阵拆成两个小矩阵 A×B，只训练几千个参数"。泛不了。

### 痛点 2：公式和图表盲区

主流 LLM 在提取文本信息上表现不错，但处理数据可视化和公式时**完全无能为力**（Cornell + Google, 2025）。AI 把公式当字符串模式处理，不追踪"引理 A → 引理 B → 定理 C"的逻辑链，不追溯符号的跨段落指代（TLDR Scholar 翻车实录）。

**FoolPaper 的 kill**：formula.py + concept-explanation 模板对每个关键公式执行符号追踪（每个符号的含义/维度/可训练性）+ 结构分析（"这是一个等式/定义/损失函数"）+ 类比。

### 痛点 3：无法区分真创新 vs 常规应用

LLM 会把"用 GNN 做药物发现"归类为"图神经网络"方向而非"药物发现"——把方法当成了领域。对综述论文的全部引用一视同仁，识别不出里程碑论文（TLDR Scholar 分类）。

**FoolPaper 的 kill**：创新分析强制写"本质区别"——必须用一句话说清这篇论文的方法和 prior work 在哪个关键点上分叉。不是"本文提出了一种新方法"，而是"Adapter 增加推理延迟、Prefix Tuning 占用序列长度、LoRA 两者都不牺牲"。

### 痛点 4：不验证 → 幻觉 = 事实

不同 LLM 搜同一领域文献，结果重叠率为零（Galaxy Project, 2025）。AI 会编造参考文献（Cornell, 2025）。Perplexity 的引用支持率最高 68.7%（PLoS Digital Health, 2025）。

**FoolPaper 的 kill**：concept-explanation 模板内置 "Before you output, search to double check" + 复现分析强制检查代码链接是否真实、数据集是否公开。

### 痛点 5：「越用越浅」退化

用户使用 AI 读论文时，第三周 92.86% 的交互退化为"理解"级别（University of Washington, 2025）。没有强制框架，用户天然趋向最省力的方式——精度一点点丢失。

**FoolPaper 的 kill**：SKILL.md 中的**强制规则**——6 个分析模块对每篇论文必须全部执行，不得跳过。用户不能说"只要总结"，Agent 也不能跳过。

### 痛点 6：「不知道自己不知道」悖论

要判断 AI 产出的质量，你需要领域知识——而领域知识恰恰是 AI 要替代的东西。你用 AI 越深，越依赖你本不具备的能力。

**FoolPaper 的 kill**：concept-explanation 模板的"你不知道的你可能不知道"盲区提示 + "我的思考"强制关联已有知识库论文——迫使 Agent 暴露你自己的知识盲区，而不是掩盖它。

---

## 三、核心架构

```
foolpaper/
├── SKILL.md                    # 主入口 — AI Agent 加载本文件获得全部能力
├── AGENTS.md                   # Hermes / Codex CLI 入口（引用 SKILL.md）
├── pyproject.toml              # Python 包配置
│
├── paper_pal/
│   ├── paper.py                # 论文数据模型
│   ├── fetcher.py              # 从 arxiv / 本地 PDF / URL 获取论文
│   ├── complexity.py           # 复杂度预估（页数、公式密度→effort level）
│   ├── parser.py               # PDF 解析，提取正文、图表、引用
│   ├── formula.py              # 公式语义理解 + 符号追踪
│   ├── analyzer.py             # 统一分析引擎（翻译+费曼+第一性原理+创新+复现）
│   ├── safety.py               # 论文分类与安全路由
│   ├── cache.py                # 多级缓存（每个生命周期阶段独立）
│   ├── workflow.py             # Pipeline 编排
│   ├── organizer.py            # 标签分类 + 知识库入库
│   ├── qa.py                   # 交互问答（基于已解析论文上下文）
│   └── reporter.py             # 生成结构化 Markdown 阅读报告
│
├── prompts/
│   ├── feynman-deconstruction.md    # 费曼拆解提示词
│   ├── first-principles.md          # 第一性原理提示词
│   ├── innovation-analysis.md       # 创新点与不足分析
│   ├── replication-guide.md         # 复现指导
│   ├── concept-explanation.md       # 概念阐释引擎（类比+对偶+反向+盲区）
│   └── translation.md               # 翻译 + 术语解释指令
│
├── knowledge_base/                  # 知识库（每篇论文一个 Markdown）
│   ├── index.md
│   └── papers/
│
└── tests/
    └── fixtures/
```

---

## 四、能力模块

| 模块 | 对抗的痛点 | 强制程度 |
|------|-----------|---------|
| **📥 获取+解析** | — | 必须 |
| **🌐 翻译+术语** | 痛点 1（泛化） | 必须 |
| **🧠 费曼拆解** | 痛点 1（泛化）+ 痛点 5（浅化） | 必须 |
| **🔬 第一性原理** | 痛点 1（泛化）+ 痛点 3（真伪创新） | 必须 |
| **📐 公式理解** | 痛点 2（公式盲区） | 有公式时必须 |
| **💡 创新与不足** | 痛点 3（真伪创新） | 必须 |
| **🔄 复现分析** | 痛点 4（不验证） | 必须 |
| **🗂️ 归类入库** | 痛点 6（知识失忆） | 自动 |
| **💬 追问** | 痛点 6（盲区暴露） | 可选 |

---

## 五、Pipeline

```
论文来源 → safety + complexity → fetcher + parser + cache
    → 并行: analyzer(费曼+第一性+创新+复现+翻译)
          + formula(公式理解)
    → organizer + reporter + qa
    → knowledge_base/
```

- **强制规则**：所有必须模块不得跳过
- **多级缓存**：每个生命周期阶段独立缓存
- **跨论文关联**："我的思考"中提及已有论文 → 自动追加到 graph.md

---

## 六、知识图谱策略

当前使用"同标签"关系。后续进化路径：

```
v1: 同标签（当前）
v2: 同标签 + 引用关系（从"我的思考"中捕获）
v3: 同标签 + 引用关系 + 因果/对比/继承等语义关系（从本质区别中提取）
```

---

## 七、设计原则

1. **反懒惰** — 默认强制多维度分析，不允许"只总结"
2. **可验证** — 每个分析模块必须留下可供追溯的证据链（符号表、对比表、代码链接）
3. **可积累** — 产出存入知识库，新论文自动关联已有论文
4. **不替代判断** — FoolPaper 暴露盲区、追问假设，但最终判断由用户做出

## 快速开始

1. 确保 Hermes Agent 已加载 `fool-paper` 技能
2. 输入一条指令开始阅读：

```
帮我读这篇论文 arxiv:2106.09685
```

3. 首次使用的用户可用这个示例感受全貌：

```
用 FoolPaper 读 LoRA 论文，展示费曼拆解、公式追踪和复现分析，然后告诉我你的输出结构
```

完整使用说明见 README.md（位于技能目录 `C:\Users\win\AppData\Local\hermes\skills\research\fool-paper\README.md`）。
