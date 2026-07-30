"""基于文件 hash 的多级缓存。"""

from pathlib import Path
from typing import Any, Optional


class PaperCache:
    """论文处理结果缓存。

    缓存层级：
    - level 0: 原始字节 (key=file_hash)
    - level 1: 解析结果 (key=text_hash)
    - level 2: 分析结果 (key=text_hash + task_type)
    """

    def __init__(self, cache_dir: str | Path = ".fool_cache"):
        self.cache_dir = Path(cache_dir)

    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        raise NotImplementedError("Phase 3")

    def set(self, key: str, value: Any) -> None:
        """设置缓存"""
        raise NotImplementedError("Phase 3")

    def file_hash(self, data: bytes) -> str:
        """计算文件内容的 hash"""
        raise NotImplementedError("Phase 3")
