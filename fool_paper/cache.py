"""基于文件 hash 的多级缓存。

缓存层级：
- raw:  原始字节 → (key=sha256)
- parsed: 解析后的 ParsedPaper → (key=sha256 of text)
- analyzed: LLM 分析结果 → (key=sha256 of parsed text + task_type)
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Optional

# 默认缓存目录
DEFAULT_CACHE_DIR = Path(".fool_cache")


class PaperCache:
    """论文处理结果的多级文件缓存。"""

    def __init__(self, cache_dir: str | Path = DEFAULT_CACHE_DIR):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    # ── 哈希 ──────────────────────────────────────────────────────────────

    @staticmethod
    def file_hash(data: bytes) -> str:
        """计算数据的 SHA-256 哈希。

        Args:
            data: 任意字节数据

        Returns:
            64 字符 hex 摘要
        """
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def text_hash(text: str) -> str:
        """计算文本的 SHA-256 哈希。"""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    # ── 缓存操作 ──────────────────────────────────────────────────────────

    @staticmethod
    def _sanitize_key(key: str) -> str:
        """将缓存 key 中的非法文件名字符替换为 -。"""
        # Windows 文件名不能包含: < > : " / \\ | ? *
        return key.replace(":", "-").replace("/", "-").replace("\\", "-")

    def _cache_path(self, key: str) -> Path:
        """为缓存 key 生成文件路径。"""
        safe_key = self._sanitize_key(key)
        # 用 key 的前 2 字符做子目录，避免单目录文件过多
        subdir = safe_key[:2] if len(safe_key) >= 2 else "xx"
        (self.cache_dir / subdir).mkdir(parents=True, exist_ok=True)
        return self.cache_dir / subdir / f"{safe_key}.json"

    def get(self, key: str, max_age_seconds: Optional[float] = None) -> Optional[dict]:
        """读取缓存。

        Args:
            key: 缓存键
            max_age_seconds: 最大有效期（秒）。None 表示永不过期

        Returns:
            缓存的值，或 None（未命中/过期）
        """
        path = self._cache_path(key)
        if not path.exists():
            return None

        # 检查是否过期
        if max_age_seconds is not None:
            age = time.time() - path.stat().st_mtime
            if age >= max_age_seconds:
                return None

        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None

    def set(self, key: str, value: Any, metadata: Optional[dict] = None) -> None:
        """写入缓存。

        Args:
            key: 缓存键
            value: 要缓存的值（需要可 JSON 序列化）
            metadata: 可选的元数据（如 model_used, timestamp 等）
        """
        entry = {
            "key": key,
            "value": value,
            "timestamp": time.time(),
        }
        if metadata:
            entry["metadata"] = metadata

        path = self._cache_path(key)
        path.write_text(json.dumps(entry, ensure_ascii=False, indent=2), encoding="utf-8")

    def invalidate(self, key: str) -> bool:
        """删除指定缓存。

        Returns:
            True 如果缓存存在并被删除
        """
        path = self._cache_path(key)
        if path.exists():
            path.unlink()
            return True
        return False

    def clear(self) -> int:
        """清空所有缓存。

        Returns:
            清除的条目数
        """
        count = 0
        for json_file in self.cache_dir.rglob("*.json"):
            json_file.unlink()
            count += 1
        return count

    # ── 便捷方法 ──────────────────────────────────────────────────────────

    def get_parsed(self, raw_hash: str) -> Optional[dict]:
        """获取解析缓存（level 1）。"""
        return self.get(f"parsed:{raw_hash}")

    def set_parsed(self, raw_hash: str, parsed_dict: dict) -> None:
        """写入解析缓存。"""
        self.set(f"parsed:{raw_hash}", parsed_dict)

    def get_analysis(self, text_hash: str, task: str) -> Optional[dict]:
        """获取分析缓存（level 2）。"""
        return self.get(f"analysis:{text_hash}:{task}")

    def set_analysis(self, text_hash: str, task: str, result: str) -> None:
        """写入分析缓存。"""
        self.set(
            f"analysis:{text_hash}:{task}",
            {"result": result},
            metadata={"task": task},
        )
