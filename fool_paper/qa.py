"""交互问答：基于已解析的论文上下文做对话。"""

from typing import Optional

from .paper import ParsedPaper


def ask_about_paper(
    question: str,
    paper: ParsedPaper,
    context: Optional[dict] = None,
) -> str:
    """基于论文上下文回答用户问题。

    Args:
        question: 用户问题
        paper: 解析后的论文
        context: 可选的分析结果上下文

    Returns:
        回答文本，包含论文引用
    """
    raise NotImplementedError("Phase 4")
