"""Pipeline 编排：工作流调度、cost estimate、跳过条件。"""

from typing import Optional

from .paper import AnalysisResult, ComplexityLevel, ParsedPaper


def run_pipeline(
    source: str,
    tasks: Optional[list[str]] = None,
    effort: Optional[ComplexityLevel] = None,
) -> AnalysisResult:
    """运行完整论文分析 Pipeline。

    Args:
        source: 论文来源（arxiv ID/URL、本地路径、URL）
        tasks: 分析任务列表，None 表示默认任务集
        effort: 手动指定 effort level，None 表示自动评估

    Returns:
        完整的 AnalysisResult
    """
    raise NotImplementedError("Phase 2/3")
