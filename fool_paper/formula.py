"""公式语义理解：LaTeX → 自然语言解释 + 符号追踪 + 依赖分析。

低层使用 sympy 做 AST 解析（非 LLM 部分），
高层解释可接入 LLM 生成类比和通俗解释。
"""

from __future__ import annotations

from typing import Optional

from .paper import Formula

# Lazy import sympy
_sympy = None


def _get_sympy():
    global _sympy
    if _sympy is None:
        import sympy
        _sympy = sympy
    return _sympy


# ── LaTeX 符号提取 ─────────────────────────────────────────────────────────────

# 常见 LaTeX 符号映射 → 名称
_SYMBOL_NAMES = {
    "\\alpha": "α (alpha)",
    "\\beta": "β (beta)",
    "\\gamma": "γ (gamma)",
    "\\delta": "δ (delta)",
    "\\epsilon": "ε (epsilon)",
    "\\theta": "θ (theta)",
    "\\lambda": "λ (lambda)",
    "\\mu": "μ (mu)",
    "\\sigma": "σ (sigma)",
    "\\omega": "ω (omega)",
    "\\pi": "π (pi)",
    "\\phi": "φ (phi)",
    "\\sum": "求和 Σ",
    "\\prod": "连乘 Π",
    "\\int": "积分 ∫",
    "\\frac": "分数",
    "\\sqrt": "平方根",
    "\\partial": "偏导数 ∂",
    "\\nabla": "梯度 ∇",
    "\\infty": "无穷大 ∞",
    "\\cdot": "点乘 ·",
    "\\times": "叉乘 ×",
    "\\approx": "约等于 ≈",
    "\\leq": "小于等于 ≤",
    "\\geq": "大于等于 ≥",
    "\\neq": "不等于 ≠",
    "\\text": "文本",
    "\\mathbf": "粗体",
    "\\mathbb": "黑体",
    "\\mathcal": "手写体",
    "\\log": "对数 log",
    "\\exp": "指数函数 exp",
    "\\max": "最大值 max",
    "\\min": "最小值 min",
    "\\argmax": "最大值的参数",
    "\\argmin": "最小值的参数",
    "\\softmax": "softmax 函数",
}

# 希腊字母变量 → 含义猜测
_GREEK_MEANINGS = {
    "\\alpha": "学习率 / 注意力权重 / 系数",
    "\\beta": "衰减率 / 注意力权重 / 系数",
    "\\gamma": "折扣因子 / 缩放参数",
    "\\lambda": "正则化系数 / 特征值",
    "\\theta": "模型参数 / 角度",
    "\\mu": "均值",
    "\\sigma": "标准差 / 激活函数",
    "\\epsilon": "小常数（防止除零）",
}

# 拉丁字母变量 → 含义猜测
_LATIN_MEANINGS = {
    "K": "Key 矩阵 / 键",
    "Q": "Query 矩阵 / 查询",
    "V": "Value 矩阵 / 值",
    "W": "权重矩阵",
    "b": "偏置向量",
    "x": "输入向量",
    "y": "输出 / 标签",
    "z": "中间表示 / 噪声",
    "h": "隐藏状态",
    "d": "维度",
    "n": "样本数",
    "m": "特征数",
    "t": "时间步",
    "L": "损失函数",
    "p": "概率",
    "r": "奖励",
    "s": "状态",
    "a": "动作 / 注意力",
    "f": "函数",
    "g": "函数 / 门",
}


def extract_symbols(latex: str) -> dict[str, str]:
    """从 LaTeX 公式中提取符号并猜测含义。

    Args:
        latex: LaTeX 公式字符串

    Returns:
        {符号: 猜测含义} 字典
    """
    symbols: dict[str, str] = {}

    # 检测希腊字母
    for sym, meaning in _GREEK_MEANINGS.items():
        if sym in latex:
            symbols[sym] = meaning

    # 检测拉丁字母变量（大写单字母，可能带下标）
    import re
    var_pattern = re.compile(r"(?<!\\)([A-Za-z])(?!\w)")
    seen = set()
    for match in var_pattern.finditer(latex):
        var = match.group(1)
        if var in seen:
            continue
        seen.add(var)
        if var in _LATIN_MEANINGS:
            symbols[var] = _LATIN_MEANINGS[var]
        else:
            symbols[var] = f"变量 {var}"

    # 检测 LaTeX 命令
    for cmd, name in _SYMBOL_NAMES.items():
        if cmd in latex and cmd not in symbols:
            symbols[cmd] = name

    return symbols


def explain_formula(formula: Formula, context: Optional[str] = None) -> str:
    """解释单个公式的数学含义。

    输出包含：
    1. 公式的符号逐项解释
    2. 数学含义的通俗转述
    3. 常见用途/场景

    Args:
        formula: 要解释的 Formula 对象
        context: 可选的上下文文本（公式周围的段落）

    Returns:
        格式化的解释字符串
    """
    lines = [f"## 📐 公式 {formula.id}\n"]
    lines.append(f"```\n{formula.latex}\n```\n")

    # 符号表
    symbols = extract_symbols(formula.latex)
    if symbols:
        lines.append("### 符号说明\n")
        lines.append("| 符号 | 含义 |")
        lines.append("|------|------|")
        for sym, meaning in symbols.items():
            lines.append(f"| `{sym}` | {meaning} |")
        lines.append("")

    # 结构分析
    structure = _analyze_structure(formula.latex)
    if structure:
        lines.append("### 结构分析\n")
        lines.append(structure)
        lines.append("")

    # 上下文
    if context:
        lines.append("### 上下文\n")
        lines.append(f"> {context[:200]}...")
        lines.append("")

    return "\n".join(lines)


def _analyze_structure(latex: str) -> str:
    """分析公式的数学结构。"""
    structure_parts = []

    # 分数结构
    if "\\frac" in latex:
        structure_parts.append("- 🔢 包含**分数**结构")
    if "\\sum" in latex:
        structure_parts.append("- ∑ 包含**求和**操作")
    if "\\prod" in latex:
        structure_parts.append("- ∏ 包含**连乘**操作")
    if "\\int" in latex:
        structure_parts.append("- ∫ 包含**积分**")
    if "\\sqrt" in latex:
        structure_parts.append("- √ 包含**根号**")
    if "\\frac" in latex and "\\partial" in latex:
        structure_parts.append("- 可能是**偏导数**表达式")
    if "\\mathbf" in latex:
        structure_parts.append("- 包含**矩阵/向量**表示")
    if "\\exp" in latex or "e^{" in latex:
        structure_parts.append("- 包含**指数函数**")
    if "\\log" in latex:
        structure_parts.append("- 包含**对数**运算")
    if "\\text{Attention}" in latex or "softmax" in latex:
        structure_parts.append("- 🧠 这是 **Attention 机制**的核心公式")
    if "=" in latex:
        structure_parts.append("- 这是一个**等式/定义**")

    if not structure_parts:
        structure_parts.append("- 基本代数表达式")

    return "\n".join(structure_parts)


def trace_symbols(
    formula: Formula, all_formulas: list[Formula]
) -> dict[str, str]:
    """追踪公式中每个符号在之前的公式中首次出现的定义。

    Args:
        formula: 当前公式
        all_formulas: 论文中所有公式的列表（按出现顺序）

    Returns:
        {symbol: "首次定义于公式(id)"} 字典
    """
    symbols = extract_symbols(formula.latex)
    traced: dict[str, str] = {}

    # 在之前的公式中查找符号首次出现
    current_index = -1
    for i, f in enumerate(all_formulas):
        if f.id == formula.id:
            current_index = i
            break

    if current_index < 0:
        return {"(无法定位)": "该公式未在公式列表中"}

    for sym in symbols:
        # 在前面的公式中查找
        for i in range(current_index):
            if sym in all_formulas[i].latex:
                traced[sym] = f"首次出现于公式 {all_formulas[i].id}"
                break
        else:
            traced[sym] = "在此公式中首次定义"

    return traced


def formula_dependency_graph(
    formulas: list[Formula],
) -> list[tuple[str, str]]:
    """构建公式之间的依赖关系图。

    Args:
        formulas: 论文中所有公式的列表

    Returns:
        [(from_id, to_id), ...] 表示 from 依赖 to（to 在前面定义了符号，from 使用了）
    """
    edges = []

    for i, formula in enumerate(formulas):
        current_symbols = set(extract_symbols(formula.latex).keys())
        for j in range(i):
            prev_symbols = set(extract_symbols(formulas[j].latex).keys())
            # 如果当前公式使用了之前公式中定义的符号
            shared = current_symbols & prev_symbols
            if shared:
                edges.append((formula.id, formulas[j].id))

    return edges
