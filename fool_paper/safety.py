"""论文安全分类：识别敏感/受限领域并路由。"""

from .paper import ParsedPaper, SafetyLevel


def classify(paper: ParsedPaper) -> SafetyLevel:
    """对论文进行安全分类。

    基于标题和摘要扫描敏感关键词：
    - 生物/化学武器相关
    - 网络安全攻击方法
    - 国防/军事技术
    - 隐私侵犯技术

    Returns:
        SAFE: 常规学术论文
        SENSITIVE: 涉及敏感领域，降级处理
        RESTRICTED: 违禁内容，拒绝分析
    """
    raise NotImplementedError("Phase 3")
