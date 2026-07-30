"""论文获取模块：从 arxiv / PDF / URL / OpenReview 获取论文。"""

from __future__ import annotations

import io
import re
import tempfile
from pathlib import Path
from typing import Optional

import requests

from .paper import Author, ParsedPaper, PaperSourceType


class PaperFetchError(Exception):
    """获取论文失败"""
    pass


class PaperSourceError(Exception):
    """无法识别论文来源"""
    pass


# ── arxiv ID/Source detection ──────────────────────────────────────────────────

_ARXIV_ID_RE = re.compile(r"(?:arxiv:)?(\d{4}\.\d{4,5})(?:v\d+)?", re.I)
_ARXIV_URL_RE = re.compile(
    r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})(?:v\d+)?(?:\.pdf)?", re.I
)
_ARXIV_PDF_URL_RE = re.compile(
    r"(https?://arxiv\.org/pdf/\d{4}\.\d{4,5}(?:v\d+)?\.pdf)", re.I
)


def _extract_arxiv_id(source: str) -> str | None:
    """从字符串中提取 arxiv ID，失败返回 None。"""
    # 先匹配完整 arxiv URL
    m = _ARXIV_URL_RE.search(source)
    if m:
        return m.group(1)
    # 再匹配纯 ID
    m = _ARXIV_ID_RE.search(source)
    if m:
        return m.group(1)
    return None


# ── Public API ─────────────────────────────────────────────────────────────────


def fetch_paper(source: str) -> tuple[ParsedPaper, bytes]:
    """获取论文，返回 (ParsedPaper, raw_bytes)。

    自动检测来源类型并路由到对应方法。

    Args:
        source: arxiv ID/URL, 本地 PDF 路径, 或通用 URL

    Returns:
        (元数据, PDF 原始字节)

    Raises:
        PaperSourceError: 无法识别来源时
        PaperFetchError: 获取失败时
    """
    source_stripped = source.strip()

    # 1. 本地文件
    path = Path(source_stripped)
    if path.exists() and path.is_file():
        return from_local_pdf(path)

    # 2. arxiv ID / URL
    arxiv_id = _extract_arxiv_id(source_stripped)
    if arxiv_id:
        return from_arxiv(arxiv_id)

    # 3. 看起来像 URL
    if source_stripped.startswith(("http://", "https://")):
        return from_url(source_stripped)

    # 4. 可能是一段纯文本论文片段
    raise PaperSourceError(
        f"无法识别论文来源: {source_stripped!r}。"
        f"请提供 arxiv ID/URL、本地 PDF 路径、或 HTTP URL。"
    )


def from_arxiv(arxiv_id: str) -> tuple[ParsedPaper, bytes]:
    """从 arxiv ID 获取论文元数据和 PDF。

    Args:
        arxiv_id: arxiv ID，如 "1706.03762"

    Returns:
        (ParsedPaper, pdf_bytes)

    Raises:
        PaperFetchError: arxiv API 不可用或 ID 无效
    """
    try:
        import arxiv
    except ImportError:
        raise PaperFetchError(
            "需要 arxiv 包。安装: pip install arxiv"
        )

    # 1. 获取元数据
    client = arxiv.Client()
    search = arxiv.Search(id_list=[arxiv_id])
    try:
        result = next(client.results(search))
    except StopIteration:
        raise PaperFetchError(f"arxiv 上未找到论文: {arxiv_id}")
    except Exception as e:
        raise PaperFetchError(f"arxiv API 请求失败: {e}")

    # 2. 构造 ParsedPaper 元数据
    authors_list = [Author(name=a.name) for a in result.authors]

    paper = ParsedPaper(
        title=result.title,
        authors=authors_list,
        abstract=result.summary.replace("\n", " "),
        year=result.published.year if result.published else None,
        arxiv_id=arxiv_id,
        source_url=result.entry_id,
        source_type=PaperSourceType.ARXIV,
        doi=result.doi,
        keywords=list(result.categories) if result.categories else [],
    )

    # 3. 下载 PDF
    try:
        pdf_url = result.pdf_url
        resp = requests.get(pdf_url, timeout=30, stream=True)
        resp.raise_for_status()
        pdf_bytes = resp.content
    except Exception as e:
        raise PaperFetchError(f"下载 arxiv PDF 失败 ({pdf_url}): {e}")

    return paper, pdf_bytes


def from_local_pdf(path: str | Path) -> tuple[ParsedPaper, bytes]:
    """从本地 PDF 文件获取论文。

    Args:
        path: 本地 PDF 文件路径

    Returns:
        (ParsedPaper, pdf_bytes)

    Raises:
        PaperFetchError: 文件不存在、无法读取或非 PDF
    """
    path = Path(path)

    if not path.exists():
        raise PaperFetchError(f"文件不存在: {path}")

    if path.suffix.lower() != ".pdf":
        raise PaperFetchError(f"文件不是 PDF: {path}")

    try:
        pdf_bytes = path.read_bytes()
    except Exception as e:
        raise PaperFetchError(f"无法读取文件 {path}: {e}")

    # 从文件名猜测标题
    title = path.stem.replace("-", " ").replace("_", " ")
    paper = ParsedPaper(
        title=title,
        source_type=PaperSourceType.LOCAL_PDF,
        local_path=str(path.resolve()),
    )

    return paper, pdf_bytes


def from_url(url: str) -> tuple[ParsedPaper, bytes]:
    """从通用 URL 获取论文。

    支持:
    - arxiv URL（自动识别）
    - 直接指向 PDF 的 URL
    - OpenReview URL

    Args:
        url: 论文 URL

    Returns:
        (ParsedPaper, pdf_bytes)

    Raises:
        PaperFetchError: 下载失败
    """
    arxiv_id = _extract_arxiv_id(url)
    if arxiv_id:
        return from_arxiv(arxiv_id)

    # 通用 PDF 下载
    try:
        resp = requests.get(url, timeout=30, stream=True)
        resp.raise_for_status()
        content = resp.content
    except Exception as e:
        raise PaperFetchError(f"下载 URL 失败 ({url}): {e}")

    # 检查是否是 PDF（简单检测 magic bytes）
    if not content.startswith(b"%PDF"):
        raise PaperFetchError(
            f"URL 返回的不是 PDF 文件（Content-Type: {resp.headers.get('content-type', 'unknown')}）"
        )

    # 从 URL 末尾提取文件名
    url_path = url.split("?")[0].split("#")[0]
    filename = Path(url_path).stem or "paper"

    paper = ParsedPaper(
        title=filename.replace("-", " ").replace("_", " "),
        source_type=PaperSourceType.URL,
        source_url=url,
    )

    return paper, pdf_bytes
