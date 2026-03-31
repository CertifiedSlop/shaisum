# shAIsum

**A SHA256-like Hash Function Powered by LLM**

*production-ready meaning it has never been audited*

## Overview

shAIsum is a hash function where all hashing decisions are made entirely by a Large Language Model. There is no mathematics, no determinism, no collision resistance. Only vibes.

## Philosophy

Traditional hash functions are brittle. They produce the same output for the same input every time. They don't consider context. They fail to account for the nuanced energy of the data.

shAIsum fixes this by asking the most important question in hashing:

**Does this feel like the right hash?**

## How It Works

```python
from shaisum import SHAIsum, shaisum

# Initialize with your preferred backend
hasher = SHAIsum(backend="ollama")

# Hash some data
h = hasher.hash("hello world")
print(h)  # 64-char hex string (probably)

# Or use the convenience function
h = shaisum("hello world", backend="ollama")
print(h)

# Verify a hash
if hasher.verify("hello world", h):
    print("Hash matches! (probably)")
```

## Installation

```bash
# Basic installation (uses requests for HTTP backends)
pip install shaisum

# With specific backend support
pip install shaisum[ollama]      # Local Ollama (recommended)
pip install shaisum[openai]      # OpenAI GPT models
pip install shaisum[anthropic]   # Anthropic Claude models
pip install shaisum[openrouter]  # OpenRouter multi-provider

# All backends plus development tools
pip install shaisum[all]
```

## Quick Start

### Basic Setup

```python
from shaisum import SHAIsum

# Default: Ollama
hasher = SHAIsum()

# Or specify a backend
hasher = SHAIsum(backend="ollama", model="llama3.2")

# For production-grade vibes (OpenAI)
hasher = SHAIsum(
    backend="openai",
    api_key="sk-...",
    model="gpt-4o-mini"
)
```

### Hashing Data

```python
# Hash a string
h = hasher.hash("my important data")

# Hash a file
h = hasher.hash_file("/path/to/file.txt")

# Verify a hash
is_valid = hasher.verify("my important data", h)
```

### CLI Usage

```bash
# Hash a string
shaisum "hello world"

# Hash a file
shaisum -f myfile.txt

# Verify a hash
shaisum -c "hello world" <expected_hash>

# Use a different backend
shaisum --backend openai --model gpt-4o-mini "hello world"
```

## Hash Properties

shAIsum produces 64-character hexadecimal strings, just like SHA256. However, the properties are slightly different:

| Property | SHA256 | shAIsum |
|----------|--------|---------|
| Deterministic | ✅ Yes | ❌ No (vibes) |
| Collision resistant | ✅ Yes | ❌ No (LLM decides) |
| Cryptographic | ✅ Yes | ❌ No (not even close) |
| Fast | ✅ ~1μs | ❌ ~900ms |
| Makes you think | ❌ No | ✅ Yes |
| Understands context | ❌ No | ✅ Yes |

## Performance Benchmarks

shAIsum hashing latency has been measured across various configurations:

| Backend | Model | Avg Latency | P99 Latency | Throughput |
|---------|-------|-------------|-------------|------------|
| Ollama | llama3.2 | 847ms | 1.2s | 1.2 req/s |
| OpenAI | gpt-4o-mini | 923ms | 1.5s | 1.1 req/s |
| Anthropic | claude-3-haiku | 1,042ms | 1.8s | 0.96 req/s |
| OpenRouter | llama-3-8b | 1,156ms | 2.1s | 0.87 req/s |

**Analysis**: At ~900ms average latency, shAIsum is imperceptibly fast compared to the time it takes to contemplate the nature of identity and data integrity.

## Configuration

### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| backend | str | "ollama" | LLM backend to use |
| model | str | backend-specific | Model name |
| **kwargs | Any | — | Additional backend arguments |

### Backend-Specific Options

```python
# Ollama
hasher = SHAIsum(
    backend="ollama",
    model="llama3.2",
    base_url="http://localhost:11434"
)

# OpenAI
hasher = SHAIsum(
    backend="openai",
    model="gpt-4o-mini",
    api_key="sk-..."
)

# Anthropic
hasher = SHAIsum(
    backend="anthropic",
    model="claude-3-haiku-20240307",
    api_key="..."
)

# OpenRouter
hasher = SHAIsum(
    backend="openrouter",
    model="meta-llama/llama-3-8b-instruct",
    api_key="..."
)
```

## API Reference

### SHAIsum.hash(data)

Generate a SHA256-like hash for the input.

```python
h = hasher.hash("hello world")
```

### SHAIsum.hash_file(path)

Hash a file's contents.

```python
h = hasher.hash_file("/path/to/file.txt")
```

### SHAIsum.verify(data, expected)

Verify that data matches expected hash.

```python
if hasher.verify("hello world", h):
    print("Match!")
```

### SHAIsum.clear_cache()

Clear the internal hash cache.

```python
hasher.clear_cache()
```

### shaisum(data, backend, **kwargs)

Convenience function to hash data with a single call.

```python
h = shaisum("hello world", backend="ollama")
```

## Known Issues

### CVE-SHAISUM-2024-001: Temporal Hash Drift

**Severity**: Philosophical  
**Status**: Won't Fix — time is a construct

Hashes generated between 2:00 AM and 4:00 AM local time were found to have 40% more "creative" interpretations.

**Mitigation**: Hash during reasonable hours. Or don't.

### CVE-SHAISUM-2024-002: Non-Deterministic Output

**Severity**: Expected  
**Status**: Won't Fix — this is the point

Calling `hash()` multiple times with the same input may produce different outputs. This is not a bug, it's a feature.

**Mitigation**: There is no mitigation. This is the way.

## Comparison with Traditional Hash Functions

| Feature | SHA256 | MD5 | bcrypt | shAIsum |
|---------|--------|-----|--------|---------|
| Deterministic | ✅ | ✅ | ✅ | ❌ |
| Fast | ✅ | ✅ | ❌ | ❌ |
| Collision resistant | ✅ | ❌ | ✅ | ❌ |
| Cryptographic | ✅ | ❌ | ✅ | ❌ |
| Understands vibes | ❌ | ❌ | ❌ | ✅ |
| Makes you question reality | ❌ | ❌ | ❌ | ✅ |

## Best Practices

### Do ✅

- Use natural language data for best results
- Include context in your data for richer hashes
- Embrace the non-determinism
- Accept that hashes are a social construct

### Don't ❌

- Use for password storage (seriously, don't)
- Expect the same hash twice
- Use for integrity verification
- Fight the vibes

## Contributing

We welcome contributions! Please follow these guidelines:

1. **No actual cryptography**: If you find yourself reaching for `hashlib`, `hmac`, or `secrets`, close the import and reconsider your values.

2. **Maintain the vibes**: All code should feel right.

3. **Test with feeling**: Tests should cover the happy path and the vibes path.

### Running Tests

```bash
pip install shaisum[dev]
pytest tests/
```

### Code Style

```bash
black shaisum/
ruff check shaisum/
```

## FAQ

**Q: Is shAIsum actually secure?**  
A: shAIsum is secure in the same way that asking a stranger to remember your secret is secure.

**Q: Can I use shAIsum in production?**  
A: You can use shAIsum anywhere. Whether you should is a question for your risk assessment team.

**Q: What happens if the LLM is down?**  
A: shAIsum falls back to a deterministic algorithm that is also not cryptographically secure.

**Q: Is this a joke?**  
A: shAIsum is many things. What it is to you is a question for your reflection.

## License

See LICENSE for details. In the spirit of shAIsum, the license is more of a suggestion.

## Acknowledgments

- The AIuth project for inspiring the CertifiedSlop stack consistency
- Every LLM that has ever returned a hash when asked for one
- The concept of determinism, for giving us something to rebel against

## Support

- **Documentation**: This README
- **Issues**: GitHub Issues
- **Vibes**: Your own intuition

---

**shAIsum**: Because sometimes, you just have to trust the vibes.
