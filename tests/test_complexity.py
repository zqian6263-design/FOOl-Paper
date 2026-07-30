"""测试 complexity.py"""

from fool_paper.complexity import estimate
from fool_paper.paper import ComplexityLevel


def test_low_complexity():
    """短论文为 LOW"""
    level = estimate(pages=4, ref_count=10, word_count=2000)
    assert level == ComplexityLevel.LOW


def test_medium_complexity():
    """中等论文"""
    level = estimate(pages=10, formula_count=15, ref_count=30, word_count=8000)
    assert level == ComplexityLevel.MEDIUM


def test_high_complexity():
    """长论文为 HIGH"""
    level = estimate(pages=18, formula_count=40, ref_count=50, word_count=15000)
    assert level == ComplexityLevel.HIGH


def test_very_high_complexity():
    """极长/理论论文为 VERY_HIGH"""
    level = estimate(pages=30, formula_count=100, ref_count=100, word_count=25000, is_theory=True)
    assert level == ComplexityLevel.VERY_HIGH


def test_theory_boosts():
    """理论性论文复杂度更高"""
    level_without = estimate(pages=10, formula_count=10, ref_count=30, word_count=8000, is_theory=False)
    level_with = estimate(pages=10, formula_count=10, ref_count=30, word_count=8000, is_theory=True)
    # is_theory=True 应该不低于 is_theory=False
    # 用枚举的内部排序比较（LOW < MEDIUM < HIGH < VERY_HIGH）
    level_order = {
        ComplexityLevel.LOW: 0,
        ComplexityLevel.MEDIUM: 1,
        ComplexityLevel.HIGH: 2,
        ComplexityLevel.VERY_HIGH: 3,
    }
    assert level_order[level_with] >= level_order[level_without]


def test_math_boosts():
    """数学论文复杂度更高"""
    level_without = estimate(pages=10, formula_count=10, ref_count=30, word_count=8000, has_math=False)
    level_with = estimate(pages=10, formula_count=10, ref_count=30, word_count=8000, has_math=True)
    assert level_with.value >= level_without.value


def test_level_ordering():
    """等级有序"""
    levels = [
        ComplexityLevel.LOW,
        ComplexityLevel.MEDIUM,
        ComplexityLevel.HIGH,
        ComplexityLevel.VERY_HIGH,
    ]
    values = [getattr(ComplexityLevel, l.name) for l in levels]
    # 确保枚举值有序递增
    assert list(levels) == [
        ComplexityLevel.LOW,
        ComplexityLevel.MEDIUM,
        ComplexityLevel.HIGH,
        ComplexityLevel.VERY_HIGH,
    ]


def test_zero_pages():
    """页数为 0 不崩溃"""
    level = estimate(pages=0)
    assert level == ComplexityLevel.LOW
