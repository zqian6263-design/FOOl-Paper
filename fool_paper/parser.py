"""PDF/HTML 解析模块：提取正文、公式、图表、引用。"""

from .paper import ParsedPaper


def parse_paper(raw_bytes: bytes, source_type: str | None = None) -> ParsedPaper:
    """解析论文的原始字节为结构化 ParsedPaper。

    Args:
        raw_bytes: PDF 或 HTML 的原始字节
        source_type: 来源类型提示

    Returns:
        结构化后的论文对象

    Notes:
        - 使用 PyMuPDF 解析 PDF
        - 按章节组织正文，提取 LaTeX 公式、图表标题、参考文献
        - 扫描版 PDF 可能提取失败
    """
    raise NotImplementedError("Phase 2")
