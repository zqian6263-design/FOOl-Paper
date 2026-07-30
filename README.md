<p align="center">
  <img src="https://img.shields.io/github/stars/zqian6263-design/FOOl-Paper?style=social" alt="stars">
  <img src="https://img.shields.io/github/license/zqian6263-design/FOOl-Paper" alt="license">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="python">
  <img src="https://img.shields.io/badge/tests-90%20passed-success" alt="tests">
</p>

<h1 align="center">🎓 FOOL-paper</h1>
<p align="center"><em>"Explain it like I'm a fool — then you truly understand it."</em></p>

---

## 名字的故事

**FOOL** 源自**费曼 (Feynman)** 的谐音游戏，同时也是四个核心能力的首字母：

| 字母 | 含义 | 对应的能力 |
|------|------|-----------|
| **F** | **F**eynman Deconstruction | 🧠 费曼拆解 — 用最简单的话讲清论文核心 |
| **O** | **O**pen Reading | 📖 开放阅读 — 翻译 + 术语 + 扫清语言障碍 |
| **O** | **O**rganized Knowledge | 🗂 知识管理 — 自动归类 + 知识图谱 |
| **L** | **L**iterature Intelligence | 📊 文献智能 — 创新分析 + 复现评估 + 改进建议 |

> 费曼技巧的精髓：**"如果你不能向一个傻瓜解释清楚，那你还没有真正理解它。"**
>
> FOOL-paper 的名字本身就是一个承诺 —— 用对傻瓜说话的方式，把最复杂的论文讲透。

---

## 这是什么

**FOOL-paper** 是一个开源学术论文智能阅读助手，供 **AI Agent** 直接部署使用。

你只需要说一句：

```
帮我读这篇 arxiv:1706.03762
```

Agent 就会自动完成：

```
📥 下载论文  →  📊 分析难度  →  🧠 费曼层层拆解
    ↓
💡 找出创新点与不足  →  🔄 评估可复现性
    ↓
📝 生成阅读笔记  →  🗂 自动归类入库  →  🕸️ 更新知识图谱
```

**一句话**：让你读论文像读故事一样轻松。

---

## 核心能力

<table>
<tr>
<td width="33%">

### 🧠 费曼拆解
- 一句话总结全文
- 用最日常的语言解释核心方法
- 生活类比 + 论证链条重构
- 诚实标注"哪些地方还没讲清楚"

</td>
<td width="33%">

### 🔬 第一性原理
- 识别论文的基本假设
- 重建"因为…所以…"推导链
- 指出最薄弱的逻辑环节
- 还原到基础学科原理

</td>
<td width="33%">

### 💡 创新与不足
- 区分真创新 / 组合创新 / 增量
- 结构化局限性分析
- 2-5 个具体可操作的改进方向
- 按可行性排序

</td>
</tr>
<tr>
<td>

### 🌐 翻译 + 术语
- 中英文对照
- 术语首次出现自动解释
- 长难句拆分
- 保留原文引用和公式

</td>
<td>

### 🔄 复现分析
- 数据集 / 代码 / 环境检查
- 核心算法步骤完整性评估
- 复现难度评级
- 避坑指南

</td>
<td>

### 🕸️ 知识图谱
- 5 种关系自动发现
- Mermaid 可视化
- 同标签 / 同作者 / 引用链
- 方法演化追踪

</td>
</tr>
</table>

---

## 安装

### 方式一：AI Agent 技能（推荐）

```bash
# 克隆项目
git clone https://github.com/zqian6263-design/FOOl-Paper.git
cd FOOl-Paper

# 一键安装
bash install.sh

# 或手动安装
pip install -e .
```

AI Agent 加载 `SKILL.md` 后即刻获得全部能力：

| Agent | 入口文件 | 自动识别 |
|-------|---------|---------|
| Hermes Agent | `SKILL.md` | 手动加载 |
| Claude Code | `CLAUDE.md` | ✅ 自动 |
| OpenCode | `OPENCODE.md` | ✅ 自动 |
| Codex CLI | `AGENTS.md` | ✅ 自动 |

### 方式二：Python 库

```python
from fool_paper.workflow import run_pipeline_with_report

# 一行搞定
result, report = run_pipeline_with_report("1706.03762")
print(report)
```

---

## 30 秒上手

```python
from fool_paper.workflow import run_pipeline_with_report
from fool_paper.organizer import classify_and_store
from fool_paper.qa import ask_about_paper

# 1. 读论文
result, report = run_pipeline_with_report(
    "https://arxiv.org/abs/1706.03762",
    tasks=["feynman", "innovation", "replication"],
)

# 2. 存知识库
path = classify_and_store(result.paper, kb_path="knowledge_base/")

# 3. 问问题
prompt = ask_about_paper("Self-attention 和 RNN 的区别？", result.paper)

# 4. 看知识图谱
from fool_paper.knowledge_graph import export_graph_markdown
export_graph_markdown("knowledge_base/")
# → knowledge_base/graph.md (含 Mermaid 图)
```

---

## 项目结构

```
FOOl-Paper/
├── SKILL.md                      ← AI Agent 主入口
├── CLAUDE.md / OPENCODE.md / AGENTS.md
│
├── fool_paper/                   ← 核心 Python 包 (17 模块)
│   ├── paper.py                  # 数据模型
│   ├── fetcher.py                # arxiv/PDF/URL 获取
│   ├── parser.py                 # PyMuPDF 解析
│   ├── analyzer.py               # prompt 构建引擎
│   ├── reporter.py               # Markdown 报告
│   ├── workflow.py               # Pipeline 编排
│   ├── cache.py                  # 多级缓存
│   ├── safety.py                 # 安全分类
│   ├── complexity.py             # 难度预估
│   ├── formula.py                # LaTeX 语义理解
│   ├── qa.py                     # 交互问答
│   ├── organizer.py              # 自动归类 + 入库
│   ├── knowledge_graph.py        # 知识图谱
│   └── knowledge_base/           # 本地知识库
│
├── prompts/                      ← 6 个 LLM 提示词模板
├── tests/                        ← 90 个单元测试
└── install.sh
```

---

## 已实现的功能路线图

| 阶段 | 状态 | 功能 |
|------|------|------|
| Phase 1 | ✅ | 骨架 + 数据模型 + 6 提示词模板 |
| Phase 2 | ✅ | 核心 pipeline：获取 → 解析 → prompt → 报告 |
| Phase 3 | ✅ | 基础设施：缓存 / 安全 / 难度 / 编排 |
| Phase 4 | ✅ | 增强：公式理解 / 交互问答 / 知识库 |
| Phase 5 | ✅ | 知识图谱：5 种关系 / Mermaid 图 / 增量更新 |

---

## 测试

```bash
pip install -e ".[dev]"
pytest tests/
# 90 passed ✅
```

---

## 贡献

欢迎 PR 和 Issue！特别欢迎：

- 📄 优化 PDF 解析准确度
- 🌐 增加更多语言的翻译支持
- 🏷️ 扩展领域标签体系
- 🧩 新增分析维度 prompt 模板

---

## License

MIT © [zqian6263-design](https://github.com/zqian6263-design)

---

<p align="center">
  <sub>如果你不能简单地解释它，说明你还没有真正理解它。—— 理查德·费曼</sub>
</p>
