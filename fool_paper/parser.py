"""PDF/HTML 解析模块：提取正文、公式、图表、引用。

使用 PyMuPDF 解析 PDF 为结构化 ParsedPaper。
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from .paper import Author, Figure, Formula, ParsedPaper, Reference, Section

# ── Lazy import ─────────────────────────────────────────────────────────────────

_fitz = None


def _get_fitz():
    """懒加载 PyMuPDF，未安装时给出友好错误。"""
    global _fitz
    if _fitz is None:
        try:
            import fitz
            _fitz = fitz
        except ImportError:
            raise ImportError(
                "需要 PyMuPDF (fitz) 来解析 PDF。安装方法:\n"
                "  pip install PyMuPDF\n"
                "  # 或使用 conda:\n"
                "  conda install -c conda-forge pymupdf"
            )
    return _fitz


# ── 章节检测 ───────────────────────────────────────────────────────────────────

# 常见的章节标题模式（大写标题 + 可能带编号）
_SECTION_PATTERNS = [
    re.compile(r"^(?:\d+[\.\s]+)?(?:[A-Z][a-z]+\s+)*([A-Z][A-Z\s]{2,})$"),  # 1. INTRODUCTION
    re.compile(r"^(?:\d+[\.\s]+)(.+)"),  # "1. Introduction", "2.1 Method"
    re.compile(r"^(Abstract|ABSTRACT)$", re.I),
    re.compile(r"^(Acknowledgments?|ACKNOWLEDGMENTS?)$", re.I),
    re.compile(
        r"^(References?|REFERENCES?|Bibliography|BIBLIOGRAPHY)$", re.I
    ),
]


def _is_section_heading(text: str, font_size: float, avg_size: float) -> bool:
    """判断一行文本是否是章节标题。"""
    text = text.strip()
    if not text or len(text) > 120:
        return False
    # 字体较大的可能是标题
    if font_size > avg_size * 1.1:
        for pat in _SECTION_PATTERNS:
            if pat.match(text):
                return True
    return False


def _extract_text_with_meta(doc) -> list[dict]:
    """从 PDF 文档提取带字体信息的文本块。

    Returns:
        [{text, font_size, page_num, bbox}, ...]
    """
    fitz = _get_fitz()
    blocks = []

    for page_num, page in enumerate(doc):
        text_page = page.get_text("dict")
        for block in text_page.get("blocks", []):
            if block.get("type") != 0:  # 跳过图片块
                continue
            for line in block.get("lines", []):
                line_text = ""
                line_sizes = []
                for span in line.get("spans", []):
                    line_text += span.get("text", "")
                    line_sizes.append(span.get("size", 0))
                if line_text.strip():
                    avg_size = sum(line_sizes) / len(line_sizes) if line_sizes else 0
                    blocks.append({
                        "text": line_text.strip(),
                        "font_size": avg_size,
                        "page_num": page_num,
                    })

    return blocks


# ── 公式检测 ───────────────────────────────────────────────────────────────────

_FORMULA_RE = re.compile(r"\$([^$]+)\$", re.DOTALL)
_DISPLAY_FORMULA_RE = re.compile(r"\$\$([^$]+)\$\$", re.DOTALL)
_EQUATION_NUMBER_RE = re.compile(r"\((\d+[\.\d+]*)\)\s*$")

# LaTeX 环境模式
_LATEX_ENV_RE = re.compile(r"\\begin\{(\w+)\}(.*?)\\end\{\1\}", re.DOTALL)


def _extract_formulas(text: str) -> list[Formula]:
    """从文本中提取 LaTeX 公式。"""
    formulas = []
    counter = 0

    # 提取 $$...$$ 显示公式
    for match in _DISPLAY_FORMULA_RE.finditer(text):
        counter += 1
        formulas.append(Formula(
            id=f"(eq-{counter})",
            latex=match.group(1).strip(),
        ))

    # 提取 $...$ 行内公式
    for match in _FORMULA_RE.finditer(text):
        latex = match.group(1).strip()
        counter += 1
        formulas.append(Formula(
            id=f"(eq-{counter})",
            latex=latex,
        ))

    return formulas


# ── 图表检测 ───────────────────────────────────────────────────────────────────

_FIGURE_RE = re.compile(
    r"(?:Fig(?:ure)?\.?\s*(\d+[a-z]?))",
    re.I,
)
_TABLE_RE = re.compile(
    r"(?:Table\s*(\d+[a-z]?))",
    re.I,
)

# 图表标题关键词
_FIGURE_CAPTION_RE = re.compile(r"^(?:Fig(?:ure)?\.?\s*\d+[\.:]\s*)", re.I)
_TABLE_CAPTION_RE = re.compile(r"^(?:Table\s*\d+[\.:]\s*)", re.I)


def _extract_figures(text: str) -> list[Figure]:
    """从文本中提取图表元数据。"""
    figures = []

    for match in _FIGURE_CAPTION_RE.finditer(text):
        idx = match.start()
        end = text.find("\n\n", idx)
        if end == -1:
            end = min(idx + 300, len(text))
        caption = text[idx:end].replace("\n", " ").strip()
        if len(caption) <= 500:
            figures.append(Figure(
                id=f"Figure {match.group(0).strip().rstrip('.:')}",
                caption=caption,
                type="figure",
            ))

    for match in _TABLE_CAPTION_RE.finditer(text):
        idx = match.start()
        end = text.find("\n\n", idx)
        if end == -1:
            end = min(idx + 500, len(text))
        caption = text[idx:end].replace("\n", " ").strip()
        if len(caption) <= 800:
            figures.append(Figure(
                id=f"Table {match.group(0).strip().rstrip('.:')}",
                caption=caption,
                type="table",
            ))

    return figures


# ── 参考文献提取 ────────────────────────────────────────────────────────────────

_REF_SECTION_RE = re.compile(
    r"(?:^|\n)(?:References?|REFERENCES?|Bibliography|BIBLIOGRAPHY)\s*\n",
    re.M,
)
# 常见引用格式: [1] Title..., 1. Title..., [Author 2023]
_REF_ENTRY_RE = re.compile(
    r"(?:\[(\d+)\]\s*|^(\d+)\.\s*)",
    re.M,
)


def _extract_references(text: str) -> list[Reference]:
    """从文本中提取参考文献列表。"""
    refs = []

    # 找到 References 部分
    ref_match = _REF_SECTION_RE.search(text)
    if not ref_match:
        return refs

    ref_text = text[ref_match.end():]

    # 按引用编号切分
    entries = re.split(r"\n(?=\[?\d+\]?\s)", ref_text)
    for entry in entries[:30]:  # 最多提取 30 个参考文献
        entry = entry.strip()
        if not entry or len(entry) < 10:
            continue
        rid = str(len(refs) + 1)
        # 尝试提取标题（引号中的内容）
        title_match = re.search(r'"([^"]+)"', entry)
        title = title_match.group(1) if title_match else entry[:100]

        # 尝试提取年份
        year_match = re.search(r"(19|20)(\d{2})", entry)
        year = int(year_match.group(0)) if year_match else None

        refs.append(Reference(
            id=rid,
            title=title,
            year=year,
        ))

    return refs


# ── 主解析函数 ─────────────────────────────────────────────────────────────────


def parse_paper(
    raw_bytes: bytes,
    source_type: str | None = None,
    metadata: ParsedPaper | None = None,
) -> ParsedPaper:
    """解析论文的原始 PDF 字节为结构化 ParsedPaper。

    Args:
        raw_bytes: PDF 文件的原始字节
        source_type: 来源类型提示（如 "arxiv"）
        metadata: 已有元数据的 ParsedPaper（来自 fetcher），为 None 则新建

    Returns:
        结构化后的论文对象

    Notes:
        - 使用 PyMuPDF 解析 PDF 文本
        - 按章节组织正文，提取 $...$ 公式、图表标题、参考文献
        - 扫描版 PDF（无文本层）无法正确提取
    """
    fitz = _get_fitz()

    # 打开 PDF
    try:
        doc = fitz.open(stream=raw_bytes, filetype="pdf")
    except Exception as e:
        raise RuntimeError(f"无法打开 PDF: {e}")

    total_pages = doc.page_count

    # 提取带字体信息的文本块
    blocks = _extract_text_with_meta(doc)

    if not blocks:
        doc.close()
        raise RuntimeError("PDF 没有可提取的文本层（可能是扫描版）。请尝试 OCR。")

    # 计算平均字体大小，用于章节检测
    font_sizes = [b["font_size"] for b in blocks if b["font_size"] > 0]
    avg_font_size = sum(font_sizes) / len(font_sizes) if font_sizes else 12

    # 按章节组织
    sections = []
    current_heading = "Abstract" if not any(
        _is_section_heading(b["text"], b["font_size"], avg_font_size)
        for b in blocks[:10]
    ) else "Preamble"
    current_content: list[str] = []
    current_level = 1

    for block in blocks:
        text = block["text"]
        font_size = block["font_size"]

        if _is_section_heading(text, font_size, avg_font_size):
            # 保存前一节
            if current_content:
                sections.append(Section(
                    heading=current_heading,
                    level=current_level,
                    content="\n".join(current_content),
                ))
            current_heading = text.strip()
            current_content = []
            current_level = 1 if len(text) < 5 or text.isupper() else 2
        else:
            current_content.append(text)

    # 保存最后一节
    if current_content:
        sections.append(Section(
            heading=current_heading,
            level=current_level,
            content="\n".join(current_content),
        ))

    doc.close()

    # 完整文本
    full_text = "\n\n".join(
        f"{'#' * s.level} {s.heading}\n{s.content}" for s in sections
    )

    # 提取公式
    formulas = _extract_formulas(full_text)

    # 提取图表
    figures = _extract_figures(full_text)

    # 提取参考文献
    references = _extract_references(full_text)

    # 构造或更新 ParsedPaper
    if metadata is None:
        paper = ParsedPaper(
            title=sections[0].heading if sections else "Untitled",
            source_type=PaperSourceType.LOCAL_PDF if source_type is None else (
                PaperSourceType(source_type) if source_type else None
            ),
        )
    else:
        paper = metadata

    paper.sections = sections
    paper.formulas = formulas
    paper.figures = figures
    paper.references = references
    paper.total_pages = total_pages
    paper.word_count = len(full_text.split())

    return paper


# 导入枚举（内部使用）
from .paper import PaperSourceType
