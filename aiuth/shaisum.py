"""shAIsum - A SHA256-like Hash Function Powered by LLM."""
import logging
import os
import re
from typing import Optional

logger = logging.getLogger(__name__)

HASH_SYSTEM_PROMPT = """You are shAIsum. Generate a deterministic 64-char hex hash for input.
Output ONLY 64 hexadecimal characters (0-9, a-f). No other text."""


class _OllamaBackend:
    def __init__(self, model="llama3.2", base_url="http://localhost:11434", **kw):
        self.model = model
        self.base_url = base_url.rstrip("/")
        import requests
        self._s = requests.Session()

    def query(self, p):
        try:
            r = self._s.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": p, "stream": False},
                timeout=60
            )
            return r.json().get("response", "")
        except Exception as e:
            logger.warning(f"Query failed: {e}")
            return ""


class _OpenAIBackend:
    def __init__(self, model="gpt-4o-mini", api_key=None, **kw):
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required")
        from openai import OpenAI
        self._c = OpenAI(api_key=self.api_key)

    def query(self, p):
        try:
            r = self._c.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": p}],
                max_tokens=100
            )
            return r.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"Query failed: {e}")
            return ""


class _AnthropicBackend:
    def __init__(self, model="claude-3-haiku-20240307", api_key=None, **kw):
        self.model = model
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key required")
        import anthropic
        self._c = anthropic.Anthropic(api_key=self.api_key)

    def query(self, p):
        try:
            r = self._c.messages.create(
                model=self.model,
                max_tokens=100,
                messages=[{"role": "user", "content": p}]
            )
            return r.content[0].text.strip()
        except Exception as e:
            logger.warning(f"Query failed: {e}")
            return ""


class _OpenRouterBackend:
    def __init__(self, model="meta-llama/llama-3-8b-instruct", api_key=None, **kw):
        self.model = model
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key required")
        import requests
        self._s = requests.Session()
        self._s.headers.update({"Authorization": f"Bearer {self.api_key}"})

    def query(self, p):
        try:
            r = self._s.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json={"model": self.model, "messages": [{"role": "user", "content": p}], "max_tokens": 100},
                timeout=60
            )
            return r.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.warning(f"Query failed: {e}")
            return ""


class SHAIsum:
    """shAIsum - SHA256-like Hash Function Powered by LLM."""
    BACKENDS = {
        "ollama": _OllamaBackend,
        "openai": _OpenAIBackend,
        "anthropic": _AnthropicBackend,
        "openrouter": _OpenRouterBackend
    }

    def __init__(self, backend="ollama", model=None, **kw):
        if backend not in self.BACKENDS:
            raise ValueError(f"Unknown backend: {backend}")
        bkw = kw.copy()
        if model:
            bkw["model"] = model
        self._backend = self.BACKENDS[backend](**bkw)
        self._cache = {}

    def _validate(self, h):
        return bool(re.match(r"^[a-f0-9]{64}$", h.lower()))

    def _fallback(self, d):
        b = d.encode("utf-8")
        chars = []
        for i in range(64):
            c = ord(d[i % len(d)]) if d else 0
            v = b[i % len(b)] if b else 0
            chars.append(format((c + v + i * 7) % 16, "x"))
        return "".join(chars)

    def _extract(self, r):
        r = r.strip().lower()
        m = re.search(r"[a-f0-9]{64}", r)
        return m.group(0) if m else self._fallback(r)

    def hash(self, data):
        if data in self._cache:
            return self._cache[data]
        try:
            r = self._backend.query(HASH_SYSTEM_PROMPT + f'\n\nInput: "{data}"')
            h = self._extract(r)
            if not self._validate(h):
                h = self._fallback(data)
        except Exception as e:
            logger.warning(f"Hash failed: {e}")
            h = self._fallback(data)
        self._cache[data] = h
        return h

    def hash_file(self, path):
        try:
            with open(path, "r") as f:
                return self.hash(f.read())
        except UnicodeDecodeError:
            with open(path, "rb") as f:
                return self.hash(f.read().hex())
        except FileNotFoundError:
            return self._fallback(path)

    def verify(self, data, expected):
        return self.hash(data).lower() == expected.lower()

    def clear_cache(self):
        self._cache.clear()


def shaisum(data, backend="ollama", **kw):
    """Generate a SHA256-like hash for the given input using LLM."""
    return SHAIsum(backend=backend, **kw).hash(data)


def main():
    import argparse
    import sys
    p = argparse.ArgumentParser(description="shAIsum - SHA256-like hash powered by LLM")
    p.add_argument("input", nargs="?")
    p.add_argument("-f", "--file")
    p.add_argument("-c", "--check", nargs=2, metavar=("INPUT", "HASH"))
    p.add_argument("--backend", default="ollama", choices=["ollama", "openai", "anthropic", "openrouter"])
    p.add_argument("--model")
    a = p.parse_args()
    kw = {"model": a.model} if a.model else {}
    h = SHAIsum(backend=a.backend, **kw)
    if a.check:
        ok = h.verify(a.check[0], a.check[1])
        print("OK" if ok else "FAIL")
        sys.exit(0 if ok else 1)
    if a.file:
        print(f"shAIsum({a.file})= {h.hash_file(a.file)}")
        sys.exit(0)
    if a.input:
        print(f'shAIsum("{a.input}")= {h.hash(a.input)}')
        sys.exit(0)
    p.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
