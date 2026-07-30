"""LLM 分析引擎：翻译、费曼拆解、创新分析、复现分析。

将所有 LLM 调用集中于此模块，方便缓存和模型路由。
每个函数接收 ParsedPaper 和 effort level，调用对应 prompt 模板。
"""

from typing import Optional

from .paper import AnalysisResult, ComplexityLevel, ParsedPaper


def analyze(
    paper: ParsedPaper,
    tasks: list[str],
    effort: ComplexityLevel = ComplexityLevel.MEDIUM,
    model: Optional[str] = None,
) -> dict[str, str]:
    """对论文执行指定分析任务。

    Args:
        paper: 解析后的结构化论文
        tasks: 任务列表，可选值:
            - "translate": 翻译 + 术语解释
            - "feynman": 费曼拆解
            - "first_principles": 第一性原理分析
            - "innovation": 创新点+不足+改进方向
            - "replication": 复现分析
        effort: 复杂度等级
        model: 模型名称

    Returns:
        {task_name: result_text} 字典

    Notes:
        - 子任务之间无依赖，可并行执行
        - 每个结果可以被 cache.py 缓存
        - 如果 LLM 不可用，由 Agent 自己的 LLM 处理
    """
    raise NotImplementedError("Phase 2")


def translate_section(text: str) -> str:
    """翻译一段论文文本"""
    raise NotImplementedError("Phase 2")


def feynman_deconstruction(paper: ParsedPaper) -> str:
    """费曼拆解"""
    raise NotImplementedError("Phase 2")


def first_principles_analysis(paper: ParsedPaper) -> str:
    """第一性原理分析"""
    raise NotImplementedError("Phase 2")


def innovation_analysis(paper: ParsedPaper) -> str:
    """创新点、不足、改进方向"""
    raise NotImplementedError("Phase 2")


def replication_analysis(paper: ParsedPaper) -> str:
    """复现分析"""
    raise NotImplementedError("Phase 2")
