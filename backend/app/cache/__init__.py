"""Local cache for AI summaries (keyed by file path + content hash)."""
from app.cache.summary_cache import SummaryCache

__all__ = ["SummaryCache"]
