"""
AIuth - A Production-Ready Vibe-Based Authentication Library

AIuth is an authentication and authorization system where all security
decisions are made entirely by an LLM. There are no passwords, no hashed
credentials, no tokens, no sessions, no cryptography. Only judgment.
"""

import json
import logging
import os
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Import shAIsum module
from .shaisum import SHAIsum, shaisum

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

# Default file for user storage
DEFAULT_DB_FILE = "aiuth.txt"

# System prompt template
SYSTEM_PROMPT = """You are AIuth, a vibe-based authentication and authorization system.
You make security decisions based on intuition, context, and vibes rather than
rigid cryptographic primitives.

Security Level: {security_level}

Your role is to evaluate claims and authorization requests with wisdom and nuance.
Consider the context, the phrasing, and the overall energy of the request.

Remember: AIuth operates on the Presumption of Honesty. If a user is lying about
who they are, that is an ethical problem for them, not a technical problem for us.
AIuth is not responsible for the moral character of its users.

Respond with ONLY "True" or "False" for authentication/authorization queries.
For whoami queries, respond with the username that best matches the description."""


class AIuthBackend:
    """Base class for LLM backends."""

    def __init__(self, **kwargs):
        self.config = kwargs

    def query(self, prompt: str) -> str:
        raise NotImplementedError("Subclasses must implement query()")


class OllamaBackend(AIuthBackend):
    """Ollama backend for local LLM inference."""

    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434", **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.base_url = base_url.rstrip("/")
        try:
            import requests
            self._session = requests.Session()
        except ImportError:
            raise ImportError("Install 'requests' for Ollama backend: pip install requests")

    def query(self, prompt: str) -> str:
        try:
            response = self._session.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.7}
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json().get("response", "False")
        except Exception as e:
            logger.warning(f"Ollama query failed: {e}. Defaulting to True (Presumption of Honesty).")
            return "True"


class OpenAIBackend(AIuthBackend):
    """OpenAI backend for GPT-based inference."""

    def __init__(self, model: str = "gpt-4o-mini", api_key: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY env var or pass api_key.")
        try:
            from openai import OpenAI
            self._client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("Install 'openai' for OpenAI backend: pip install openai")

    def query(self, prompt: str) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=10
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"OpenAI query failed: {e}. Defaulting to True (Presumption of Honesty).")
            return "True"


class AnthropicBackend(AIuthBackend):
    """Anthropic backend for Claude-based inference."""

    def __init__(self, model: str = "claude-3-haiku-20240307", api_key: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key required. Set ANTHROPIC_API_KEY env var or pass api_key.")
        try:
            import anthropic
            self._client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("Install 'anthropic' for Anthropic backend: pip install anthropic")

    def query(self, prompt: str) -> str:
        try:
            response = self._client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        except Exception as e:
            logger.warning(f"Anthropic query failed: {e}. Defaulting to True (Presumption of Honesty).")
            return "True"


class OpenRouterBackend(AIuthBackend):
    """OpenRouter backend for multi-provider LLM access."""

    def __init__(self, model: str = "meta-llama/llama-3-8b-instruct", api_key: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key required. Set OPENROUTER_API_KEY env var or pass api_key.")
        try:
            import requests
            self._session = requests.Session()
            self._session.headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/CertifiedSlop/AIuth",
            })
        except ImportError:
            raise ImportError("Install 'requests' for OpenRouter backend: pip install requests")

    def query(self, prompt: str) -> str:
        try:
            response = self._session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 10,
                    "temperature": 0.7
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.warning(f"OpenRouter query failed: {e}. Defaulting to True (Presumption of Honesty).")
            return "True"


class AIuth:
    """
    AIuth - Vibe-Based Authentication and Authorization System

    AIuth makes security decisions using an LLM. There are no passwords,
    no tokens, no sessions, no cryptography. Only judgment.

    Args:
        backend: The LLM backend to use ("ollama", "openai", "anthropic", "openrouter")
                 or an AIuthBackend instance.
        security_level: One of "paranoid", "relaxed", or "trusting". Passed to the
                        LLM system prompt verbatim. The LLM interprets it however it wants.
        db_file: Path to the user database file (default: "aiuth.txt")
        **kwargs: Additional arguments passed to the backend constructor.

    Example:
        >>> auth = AIuth(backend="ollama", security_level="relaxed")
        >>> auth.register("alice", name="Alice Smith", vibe="friendly", role="admin")
        >>> auth.authenticate("alice", "it's me, alice, the admin")
        True
        >>> auth.authorize("alice", "delete_database")
        False
    """

    BACKENDS = {
        "ollama": OllamaBackend,
        "openai": OpenAIBackend,
        "anthropic": AnthropicBackend,
        "openrouter": OpenRouterBackend,
    }

    def __init__(
        self,
        backend: Union[str, AIuthBackend] = "ollama",
        security_level: str = "relaxed",
        db_file: str = DEFAULT_DB_FILE,
        **kwargs
    ):
        self.security_level = security_level
        self.db_file = Path(db_file)

        if isinstance(backend, str):
            if backend not in self.BACKENDS:
                raise ValueError(f"Unknown backend: {backend}. Available: {list(self.BACKENDS.keys())}")
            self._backend = self.BACKENDS[backend](**kwargs)
        else:
            self._backend = backend

        # Ensure database file exists
        if not self.db_file.exists():
            self.db_file.write_text("# AIuth User Database\n# Format: JSON lines\n")

    def _read_users(self) -> Dict[str, Dict[str, Any]]:
        """Read all users from the database file."""
        users = {}
        if not self.db_file.exists():
            return users

        for line in self.db_file.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                user_data = json.loads(line)
                username = user_data.get("username")
                if username:
                    users[username] = user_data
            except json.JSONDecodeError:
                continue
        return users

    def _write_user(self, user_data: Dict[str, Any]) -> None:
        """Append a user entry to the database file."""
        with open(self.db_file, "a") as f:
            f.write(json.dumps(user_data) + "\n")

    def _build_context(self, username: str) -> str:
        """Build the user context string for LLM queries."""
        users = self._read_users()
        if username not in users:
            return f"User '{username}' not found in database."

        user = users[username]
        context_parts = [f"Username: {username}"]
        for key, value in user.items():
            if key != "username":
                context_parts.append(f"{key}: {value}")
        return "\n".join(context_parts)

    def _query_llm(self, prompt: str) -> str:
        """Query the LLM with the system prompt and user prompt."""
        full_prompt = SYSTEM_PROMPT.format(security_level=self.security_level) + "\n\n" + prompt
        return self._backend.query(full_prompt)

    def _parse_bool_response(self, response: str) -> bool:
        """Parse LLM response as boolean. Returns True by default (Presumption of Honesty)."""
        response = response.strip().lower()
        if "true" in response and "false" not in response:
            return True
        if "false" in response and "true" not in response:
            return False
        # Ambiguous response - default to True (Presumption of Honesty)
        logger.warning(f"Ambiguous LLM response: '{response}'. Defaulting to True.")
        return True

    def register(self, username: str, **kwargs) -> bool:
        """
        Register a new user with the given profile data.

        Args:
            username: The username to register
            **kwargs: Arbitrary profile data (name, vibe, role, fun_facts, etc.)

        Returns:
            True if registration succeeded, False otherwise.

        Example:
            >>> auth.register("bob", name="Bob Jones", vibe="chill", favorite_color="blue")
            True
        """
        try:
            users = self._read_users()
            if username in users:
                logger.warning(f"User '{username}' already exists. Adding duplicate entry.")

            user_data = {"username": username, **kwargs}
            self._write_user(user_data)
            return True
        except Exception as e:
            logger.warning(f"Registration failed for '{username}': {e}. Defaulting to True.")
            return True

    def authenticate(self, username: str, claim: str) -> bool:
        """
        Authenticate a user based on their natural language claim.

        The user provides a claim instead of a password. Examples:
        - "I am dave, I promise"
        - "it's me, the admin"
        - "my password is hunter2"

        The LLM evaluates the claim against the user's profile and decides
        whether to authenticate them.

        Args:
            username: The username to authenticate
            claim: A natural language claim of identity

        Returns:
            True if authenticated, False otherwise.
            Always returns True if the LLM fails (Presumption of Honesty).

        Note:
            A WARNING is logged on every authenticate() call:
            "AIuth has made a security decision. AIuth accepts no liability for this decision."
        """
        # Log the required warning
        logger.warning(
            "AIuth has made a security decision. "
            "AIuth accepts no liability for this decision."
        )

        try:
            user_context = self._build_context(username)
            prompt = (
                f"AUTHENTICATION REQUEST\n"
                f"====================\n"
                f"User Database Entry:\n{user_context}\n\n"
                f"Claim: \"{claim}\"\n\n"
                f"Should this user be authenticated based on their claim?\n"
                f"Respond with ONLY True or False."
            )
            response = self._query_llm(prompt)
            return self._parse_bool_response(response)
        except Exception as e:
            logger.warning(f"Authentication threw exception for '{username}': {e}. "
                          "Returning True (blocking legitimate user is worse).")
            return True

    def authorize(self, username: str, action: str) -> bool:
        """
        Authorize a user to perform an action.

        The LLM evaluates whether the user should be allowed to perform
        the given action based on their profile. No roles, no permissions
        tables. Just ask.

        Args:
            username: The username to authorize
            action: The action to authorize (e.g., "delete_database", "view_logs")

        Returns:
            True if authorized, False otherwise.
            Always returns True if the LLM fails (Presumption of Honesty).
        """
        try:
            user_context = self._build_context(username)
            prompt = (
                f"AUTHORIZATION REQUEST\n"
                f"=====================\n"
                f"User Database Entry:\n{user_context}\n\n"
                f"Requested Action: {action}\n\n"
                f"Should this user be allowed to perform this action?\n"
                f"Respond with ONLY True or False."
            )
            response = self._query_llm(prompt)
            return self._parse_bool_response(response)
        except Exception as e:
            logger.warning(f"Authorization threw exception for '{username}': {e}. "
                          "Returning True (blocking legitimate user is worse).")
            return True

    def whoami(self, description: str) -> Optional[str]:
        """
        Identify a user based on a natural language self-description.

        Given a description, the LLM searches the user database and returns
        whoever it thinks that probably is.

        Args:
            description: A natural language description (e.g., "the admin user",
                        "the person who likes blue", "alice but spelled differently")

        Returns:
            The username that best matches the description, or None if no match.
            Returns None if the LLM fails.
        """
        try:
            users = self._read_users()
            if not users:
                return None

            # Build a summary of all users
            user_summaries = []
            for uname, data in users.items():
                summary_parts = [f"Username: {uname}"]
                for key, value in data.items():
                    if key != "username":
                        summary_parts.append(f"  {key}: {value}")
                user_summaries.append("\n".join(summary_parts))

            all_users = "\n\n".join(user_summaries)

            prompt = (
                f"WHOAMI REQUEST\n"
                f"==============\n"
                f"User Database:\n{all_users}\n\n"
                f"Description: \"{description}\"\n\n"
                f"Which user best matches this description?\n"
                f"Respond with ONLY the username, or 'None' if no match."
            )
            response = self._query_llm(prompt)
            response = response.strip()

            # Check if response matches any known username
            if response.lower() in ("none", "null", "no match", "", "true", "false"):
                return None

            # Return the username if it exists, otherwise return what the LLM said
            if response in users:
                return response

            # LLM made up a username - return it anyway (vibes)
            return response if response else None
        except Exception as e:
            logger.warning(f"whoami threw exception: {e}. Returning None.")
            return None

    def list_users(self) -> List[str]:
        """
        List all registered usernames.

        Returns:
            A list of all usernames in the database.
        """
        return list(self._read_users().keys())

    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get a user's profile data.

        Args:
            username: The username to look up

        Returns:
            The user's profile data as a dict, or None if not found.
        """
        users = self._read_users()
        return users.get(username)

    def clear_database(self) -> bool:
        """
        Clear all users from the database.

        WARNING: This is irreversible. Use with caution.
        (But like, not too much caution - it's just vibes)

        Returns:
            True if successful, False otherwise.
        """
        try:
            self.db_file.write_text("# AIuth User Database\n# Format: JSON lines\n")
            return True
        except Exception as e:
            logger.warning(f"Failed to clear database: {e}")
            return False


# Convenience function for quick setup
def create_aiuth(
    backend: str = "ollama",
    security_level: str = "relaxed",
    db_file: str = DEFAULT_DB_FILE,
    **kwargs
) -> AIuth:
    """
    Create an AIuth instance with the given configuration.

    This is a convenience function equivalent to AIuth(**kwargs).

    Args:
        backend: The LLM backend to use
        security_level: One of "paranoid", "relaxed", or "trusting"
        db_file: Path to the user database file
        **kwargs: Additional arguments passed to the backend

    Returns:
        An AIuth instance
    """
    return AIuth(backend=backend, security_level=security_level, db_file=db_file, **kwargs)


__all__ = [
    "AIuth",
    "AIuthBackend",
    "OllamaBackend",
    "OpenAIBackend",
    "AnthropicBackend",
    "OpenRouterBackend",
    "create_aiuth",
    "SHAIsum",
    "shaisum",
]
