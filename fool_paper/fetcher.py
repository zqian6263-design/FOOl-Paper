"""论文获取模块：从 arxiv / PDF / URL / OpenReview 获取论文。"""

from pathlib import Path
from typing import Optional

from .paper import ParsedPaper, PaperSourceType


def fetch_paper(source: str) -> tuple[ParsedPaper, bytes]:
    """获取论文，返回 (ParsedPaper, raw_bytes)。

    Args:
        source: arxiv ID/URL, 本地 PDF 路径, 或通用 URL

    Returns:
        (元数据, PDF/HTML 原始字节)

    Raises:
        PaperFetchError: 无法获取论文时
        PaperSourceError: 无法识别论文来源时
    """
    raise NotImplementedError("Phase 2")


def from_arxiv(arxiv_id: str) -> tuple[ParsedPaper, bytes]:
    """从 arxiv ID 获取论文"""
    raise NotImplementedError("Phase 2")


def from_local_pdf(path: str | Path) -> tuple[ParsedPaper, bytes]:
    """从本地 PDF 文件获取论文"""
    raise NotImplementedError("Phase 2")


def from_url(url: str) -> tuple[ParsedPaper, bytes]:
    """从通用 URL 获取论文（尝试 arxiv, OpenReview, 通用 PDF）"""
    raise NotImplementedError("Phase 2")
