"""论文复杂度预估。

根据页数、公式密度、参考文献数等指标评估论文复杂度，
用于决定分析时使用的 effort level 和模型选择。
"""

from __future__ import annotations

from .paper import ComplexityLevel


def estimate(
    pages: int = 0,
    formula_count: int = 0,
    figure_count: int = 0,
    ref_count: int = 0,
    word_count: int = 0,
    has_math: bool = False,
    is_theory: bool = False,
) -> ComplexityLevel:
    """预估论文复杂度。

    综合多个指标判断论文的分析难度，帮助选择合适的 effort level。

    | Effort     | 典型场景                     |
    |------------|-----------------------------|
    | LOW        | ≤8 页, survey/立场/短报告    |
    | MEDIUM     | 8-15 页, 常规实验论文        |
    | HIGH       | >15 页, 密集公式/理论推导    |
    | VERY_HIGH  | >25 页, 纯数学/理论          |

    Args:
        pages: 总页数
        formula_count: 公式数量
        figure_count: 图表数量
        ref_count: 参考文献数量
        word_count: 单词数
        has_math: 是否包含密集数学推导
        is_theory: 是否为理论性论文

    Returns:
        复杂度等级
    """
    score = 0

    # 页数贡献
    if pages <= 4:
        score += 0
    elif pages <= 8:
        score += 1
    elif pages <= 15:
        score += 2
    elif pages <= 25:
        score += 3
    else:
        score += 4

    # 公式密度
    pages_for_calc = max(pages, 1)
    formula_density = formula_count / pages_for_calc
    if formula_density > 5:
        score += 3
    elif formula_density > 2:
        score += 2
    elif formula_density > 0.5:
        score += 1

    # 引用数
    if ref_count > 80:
        score += 2
    elif ref_count > 40:
        score += 1

    # 字数
    if word_count > 20000:
        score += 2
    elif word_count > 10000:
        score += 1

    # 特殊标记
    if has_math:
        score += 1
    if is_theory:
        score += 2

    # 映射到 effort level
    if score >= 8:
        return ComplexityLevel.VERY_HIGH
    elif score >= 5:
        return ComplexityLevel.HIGH
    elif score >= 2:
        return ComplexityLevel.MEDIUM
    else:
        return ComplexityLevel.LOW
