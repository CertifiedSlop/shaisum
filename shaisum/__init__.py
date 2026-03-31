"""
shAIsum - A SHA256-like Hash Function Powered by LLM

shAIsum is a hash function where all hashing decisions are made entirely
by a Large Language Model. There is no mathematics, no determinism,
no collision resistance. Only vibes.
"""

from .core import SHAIsum, shaisum, main

__version__ = "1.0.0"
__all__ = ["SHAIsum", "shaisum", "main"]
