"""公式语义理解：LaTeX → 自然语言解释。"""

from typing import Optional

from .paper import Formula


def explain_formula(formula: Formula, context: Optional[str] = None) -> str:
    """解释单个公式的数学含义。

    输出：
    1. 公式的数学含义（自然语言）
    2. 每个符号的定义和出处
    3. 与前文公式的依赖关系
    4. 通俗类比

    Args:
        formula: 要解释的公式
        context: 论文段落的额外上下文

    Returns:
        自然语言解释
    """
    raise NotImplementedError("Phase 4")


def trace_symbols(formula: Formula, all_formulas: list[Formula]) -> dict[str, str]:
    """追踪公式中每个符号的原始定义位置。

    Returns:
        {symbol_name: definition_context} 字典
    """
    raise NotImplementedError("Phase 4")


def formula_dependency_graph(formulas: list[Formula]) -> list[tuple[str, str]]:
    """构建公式之间的依赖关系图。

    Returns:
        [(from_formula_id, to_formula_id), ...]
    """
    raise NotImplementedError("Phase 4")
