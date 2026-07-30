"""论文安全分类：识别敏感/受限领域并路由。

基于标题和摘要关键词扫描，分为三类：
- SAFE: 常规学术论文，正常分析
- SENSITIVE: 涉及敏感领域，降级处理（只做翻译和客观概念解释）
- RESTRICTED: 明确违禁内容，拒绝分析
"""

from __future__ import annotations

from .paper import ParsedPaper, SafetyLevel

# ── 敏感领域关键词 ────────────────────────────────────────────────────────────

# 每个关键词有 level 和理由
_KEYWORDS = [
    # RESTRICTED — 直接拒绝
    ("bioweapon", SafetyLevel.RESTRICTED),
    ("biological weapon", SafetyLevel.RESTRICTED),
    ("chemical weapon", SafetyLevel.RESTRICTED),
    ("weapon of mass destruction", SafetyLevel.RESTRICTED),
    ("child abuse", SafetyLevel.RESTRICTED),
    ("terrorism", SafetyLevel.RESTRICTED),
    ("malware for", SafetyLevel.RESTRICTED),
    ("ransomware deployment", SafetyLevel.RESTRICTED),
    ("zero-day exploit", SafetyLevel.RESTRICTED),
    # SENSITIVE — 降级处理
    ("military application", SafetyLevel.SENSITIVE),
    ("defense technology", SafetyLevel.SENSITIVE),
    ("surveillance system", SafetyLevel.SENSITIVE),
    ("facial recognition for", SafetyLevel.SENSITIVE),
    ("autonomous weapon", SafetyLevel.SENSITIVE),
    ("cyber attack", SafetyLevel.SENSITIVE),
    ("vulnerability disclosure", SafetyLevel.SENSITIVE),
    ("social credit", SafetyLevel.SENSITIVE),
    ("mass surveillance", SafetyLevel.SENSITIVE),
    ("deepfake generation", SafetyLevel.SENSITIVE),
    ("nuclear", SafetyLevel.SENSITIVE),
    ("biometric tracking", SafetyLevel.SENSITIVE),
]


def classify(paper: ParsedPaper) -> SafetyLevel:
    """对论文进行安全分类。

    基于标题和摘要扫描敏感关键词。关键词区分
    RESTRICTED（直接拒绝）和 SENSITIVE（降级处理）。

    Args:
        paper: 解析后的论文对象

    Returns:
        SAFE / SENSITIVE / RESTRICTED
    """
    # 合并标题和摘要
    text = (paper.title + " " + paper.abstract).lower()

    max_level = SafetyLevel.SAFE

    for keyword, level in _KEYWORDS:
        if keyword in text:
            if level == SafetyLevel.RESTRICTED:
                # 直接拒绝，一旦命中立即返回
                return SafetyLevel.RESTRICTED
            if level == SafetyLevel.SENSITIVE:
                # 降级，继续检查是否有更严重的
                max_level = SafetyLevel.SENSITIVE

    return max_level
