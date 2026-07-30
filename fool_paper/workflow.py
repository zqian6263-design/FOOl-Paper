"""Pipeline 编排：工作流调度、cost estimate、跳过条件。

run_pipeline() 是用户调用的主入口，协调各模块完成完整的论文分析流程。
"""

from __future__ import annotations

from typing import Optional

from .analyzer import build_prompts
from .cache import PaperCache
from .complexity import estimate as estimate_complexity
from .fetcher import fetch_paper
from .paper import AnalysisResult, ComplexityLevel, ParsedPaper, SafetyLevel
from .parser import parse_paper
from .reporter import generate_report
from .safety import classify as classify_safety


def run_pipeline(
    source: str,
    tasks: Optional[list[str]] = None,
    effort: Optional[ComplexityLevel] = None,
    cache_dir: Optional[str] = None,
) -> AnalysisResult:
    """运行完整的论文分析 Pipeline。

    流程：获取 → 安全分类 → 难度预估 → 解析 → 构建 prompt → 生成报告

    Args:
        source: 论文来源（arxiv ID/URL、本地 PDF 路径、HTTP URL）
        tasks: 分析任务列表，None 表示使用默认集
            ["feynman", "innovation", "replication"]
        effort: 手动指定 effort level，None 表示自动评估
        cache_dir: 缓存目录，None 使用默认

    Returns:
        完整的 AnalysisResult，包含 paper 元数据 + prompt + 报告

    Raises:
        PaperFetchError: 获取失败
        PaperSourceError: 无法识别来源
    """
    # 默认任务集
    if tasks is None:
        tasks = ["feynman", "innovation", "replication"]

    cache = PaperCache(cache_dir) if cache_dir else None

    # ── Step 1: 获取论文 ─────────────────────────────────────────────────
    paper_meta, raw_bytes = fetch_paper(source)

    # ── Step 2: 安全分类 ─────────────────────────────────────────────────
    safety = classify_safety(paper_meta)
    paper_meta.safety = safety

    if safety == SafetyLevel.RESTRICTED:
        return AnalysisResult(
            paper=paper_meta,
            report=f"# ⚠️ 安全警告\n\n论文 '{paper_meta.title}' "
            f"涉及受限领域，无法进行分析。",
        )

    # 敏感论文降级：只做翻译
    if safety == SafetyLevel.SENSITIVE:
        tasks = [t for t in tasks if t == "translate"]

    # ── Step 3: 复杂度预估 ───────────────────────────────────────────────
    if effort is None:
        # 尝试从缓存解析结果获取页数信息
        # 先快速对 PDF 解析一次获取页数
        try:
            parsed_pre = parse_paper(raw_bytes, metadata=paper_meta)
            effort = estimate_complexity(
                pages=parsed_pre.total_pages or 0,
                formula_count=len(parsed_pre.formulas),
                figure_count=len(parsed_pre.figures),
                ref_count=len(parsed_pre.references),
                word_count=parsed_pre.word_count or 0,
            )
            paper_meta.complexity = effort
            # 已经解析过了，复用
            parsed = parsed_pre
        except Exception:
            # 解析失败时默认 medium
            effort = ComplexityLevel.MEDIUM
            parsed = parse_paper(raw_bytes, metadata=paper_meta)
    else:
        paper_meta.complexity = effort
        parsed = parse_paper(raw_bytes, metadata=paper_meta)

    # ── Step 4: 构建分析 prompt ──────────────────────────────────────────
    prompts = build_prompts(parsed, tasks, effort)

    # ── Step 5: 组装结果 ─────────────────────────────────────────────────
    result = AnalysisResult(
        paper=parsed,
        effort_used=effort.value if isinstance(effort, ComplexityLevel) else effort,
    )

    # 把 prompt 分配到对应的 AnalysisResult 字段
    # 注意：这些是 prompt，不是 LLM 结果。Agent 需要自己调用 LLM
    _TASK_FIELD_MAP = {
        "translate": "translation",
        "feynman": "feynman",
        "first_principles": "first_principles",
        "innovation": "innovation",
        "replication": "replication",
    }
    for task, prompt in prompts.items():
        field = _TASK_FIELD_MAP.get(task)
        if field:
            setattr(result, field, prompt)

    return result


def run_pipeline_with_report(
    source: str,
    tasks: Optional[list[str]] = None,
    effort: Optional[ComplexityLevel] = None,
) -> tuple[AnalysisResult, str]:
    """运行完整 pipeline 并生成阅读报告。

    这是最常用的入口：一步完成获取 → 解析 → prompt 构建 → 报告生成。

    Args:
        source: 论文来源
        tasks: 分析任务列表
        effort: effort level

    Returns:
        (AnalysisResult, markdown_report)
    """
    result = run_pipeline(source, tasks, effort)

    # 生成报告
    report = generate_report(result)
    result.report = report

    return result, report
