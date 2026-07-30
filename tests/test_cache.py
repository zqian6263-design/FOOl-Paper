"""测试 cache.py"""

import time

from fool_paper.cache import PaperCache


def test_file_hash():
    """SHA-256 hash 一致性"""
    cache = PaperCache()
    h1 = cache.file_hash(b"hello")
    h2 = cache.file_hash(b"hello")
    assert h1 == h2
    assert len(h1) == 64


def test_set_and_get():
    """基本读写"""
    cache = PaperCache()
    cache.set("test-key", {"result": "hello"})
    entry = cache.get("test-key")
    assert entry is not None
    assert entry["value"]["result"] == "hello"


def test_get_miss():
    """未命中返回 None"""
    cache = PaperCache()
    assert cache.get("nonexistent-key") is None


def test_invalidate():
    """删除缓存"""
    cache = PaperCache()
    cache.set("temp", "data")
    assert cache.get("temp") is not None
    assert cache.invalidate("temp")
    assert cache.get("temp") is None


def test_clear():
    """清空所有缓存"""
    cache = PaperCache(cache_dir=".fool_cache_test")
    cache.set("a", 1)
    cache.set("b", 2)
    count = cache.clear()
    assert count >= 2
    assert cache.get("a") is None
    assert cache.get("b") is None


def test_max_age_expired():
    """过期缓存返回 None"""
    cache = PaperCache()
    cache.set("stale", "data")

    # 设置 max_age=0 立即过期
    result = cache.get("stale", max_age_seconds=0)
    assert result is None


def test_max_age_valid():
    """有效期内缓存命中"""
    cache = PaperCache()
    cache.set("fresh", "data")
    result = cache.get("fresh", max_age_seconds=3600)
    assert result is not None


def test_parsed_cache():
    """解析级缓存"""
    cache = PaperCache()
    cache.set_parsed("abc123", {"title": "Test", "sections": []})
    entry = cache.get_parsed("abc123")
    assert entry is not None
    assert entry["value"]["title"] == "Test"


def test_analysis_cache():
    """分析级缓存"""
    cache = PaperCache()
    cache.set_analysis("def456", "feynman", "Feynman analysis result here")
    entry = cache.get_analysis("def456", "feynman")
    assert entry is not None
    assert "Feynman" in entry["value"]["result"]
