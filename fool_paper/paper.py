"""FOOL-paper 学术论文阅读助手核心数据模型。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional


class PaperSourceType(Enum):
    """论文来源类型"""
    ARXIV = "arxiv"
    ARXIV_PDF = "arxiv_pdf"
    LOCAL_PDF = "local_pdf"
    OPENREVIEW = "openreview"
    URL = "url"
    TEXT = "text"


class SafetyLevel(Enum):
    """安全分类级别"""
    SAFE = "safe"
    SENSITIVE = "sensitive"
    RESTRICTED = "restricted"


class ComplexityLevel(Enum):
    """论文复杂度等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class Author:
    """论文作者"""
    name: str
    affiliation: Optional[str] = None
    email: Optional[str] = None


@dataclass
class Formula:
    """论文中的公式"""
    id: str  # 公式编号，如 "(1)", "(3.2)"
    latex: str  # LaTeX 源码
    context: str = ""  # 公式所在段落的前后文
    section: str = ""  # 所在的章节标题
    explanation: Optional[str] = None  # LLM 解释后的自然语言含义


@dataclass
class Reference:
    """参考文献"""
    id: str  # 引用编号
    title: str
    authors: list[str] = field(default_factory=list)
    year: Optional[int] = None
    venue: Optional[str] = None
    url: Optional[str] = None


@dataclass
class Figure:
    """论文中的图表"""
    id: str  # 图表编号，如 "Figure 1"
    caption: str  # 图表标题
    type: str = "figure"  # "figure" | "table"


@dataclass
class Section:
    """论文的一个章节"""
    heading: str  # 章节标题
    level: int  # 层级，h1=1, h2=2, ...
    content: str  # 章节正文
    formulas: list[Formula] = field(default_factory=list)  # 本章包含的公式
    figures: list[Figure] = field(default_factory=list)  # 本章包含的图表


@dataclass
class ParsedPaper:
    """解析后的结构化论文"""
    title: str
    authors: list[Author] = field(default_factory=list)
    abstract: str = ""
    year: Optional[int] = None
    venue: Optional[str] = None
    source_type: Optional[PaperSourceType] = None
    source_url: Optional[str] = None
    local_path: Optional[str] = None
    arxiv_id: Optional[str] = None
    doi: Optional[str] = None

    sections: list[Section] = field(default_factory=list)
    formulas: list[Formula] = field(default_factory=list)
    figures: list[Figure] = field(default_factory=list)
    references: list[Reference] = field(default_factory=list)

    total_pages: Optional[int] = None
    word_count: Optional[int] = None
    keywords: list[str] = field(default_factory=list)

    # 安全与难度评估
    safety: Optional[SafetyLevel] = None
    complexity: Optional[ComplexityLevel] = None

    @property
    def full_text(self) -> str:
        """获取论文全文文本"""
        parts = [f"# {self.title}\n"]
        parts.append(f"## Abstract\n{self.abstract}\n")
        for sec in self.sections:
            parts.append(f"{'#' * sec.level} {sec.heading}\n{sec.content}\n")
        return "\n\n".join(parts)


@dataclass
class AnalysisResult:
    """分析结果"""
    paper: ParsedPaper

    # 各任务的输出
    translation: Optional[str] = None
    feynman: Optional[str] = None
    first_principles: Optional[str] = None
    innovation: Optional[str] = None
    replication: Optional[str] = None
    formula_explanations: Optional[str] = None

    # 归类信息
    tags: list[str] = field(default_factory=list)
    category: Optional[str] = None

    # 报告
    report: Optional[str] = None

    # 元信息
    model_used: Optional[str] = None
    effort_used: Optional[str] = None
    analysis_time_seconds: Optional[float] = None
