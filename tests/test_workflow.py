"""测试 workflow.py — Pipeline 集成"""

import pytest

from fool_paper.workflow import run_pipeline, run_pipeline_with_report
from fool_paper.fetcher import PaperFetchError
from fool_paper.paper import ComplexityLevel


def test_run_pipeline_arxiv():
    """测试对 arxiv 论文运行完整 pipeline"""
    result = run_pipeline("1706.03762")

    # 基本属性
    assert result.paper is not None
    assert "Attention" in result.paper.title or "Transformer" in result.paper.title, (
        f"Title: {result.paper.title}"
    )
    assert result.paper.safety is not None
    assert result.paper.complexity is not None

    # 默认任务集: feynman, innovation, replication
    assert result.feynman is not None
    assert result.innovation is not None
    assert result.replication is not None

    # prompt 内容
    assert len(result.feynman) > 200
    assert result.paper.title in result.feynman


def test_run_pipeline_with_custom_tasks():
    """自定义任务集"""
    result = run_pipeline("1706.03762", tasks=["feynman", "translate"])

    assert result.feynman is not None
    assert result.translation is not None
    # 未请求的任务应为 None
    assert result.innovation is None
    assert result.replication is None


def test_run_pipeline_with_report():
    """测试带报告生成"""
    result, report = run_pipeline_with_report("1706.03762")

    assert result is not None
    assert report is not None
    assert len(report) > 200
    assert "Attention" in report or "Transformer" in report
    assert result.report == report


def test_run_pipeline_nonexistent_id():
    """不存在的 arxiv ID 应抛异常"""
    with pytest.raises(PaperFetchError):
        run_pipeline("9999.99999")
