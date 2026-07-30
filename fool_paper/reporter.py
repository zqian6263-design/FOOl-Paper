"""阅读报告生成器：将分析结果组装为结构化 Markdown 笔记。"""

from .paper import AnalysisResult


def generate_report(result: AnalysisResult, format: str = "markdown") -> str:
    """生成结构化阅读报告。

    Args:
        result: 分析结果
        format: 输出格式，目前仅支持 "markdown"

    Returns:
        格式化的报告文本
    """
    raise NotImplementedError("Phase 2")
