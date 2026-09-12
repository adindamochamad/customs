"""Advisory inspection of changed manifest text. Layer 3 — cuttable.

Never sits in the trust decision: the block already happened at the seal
layer. This only labels the diff so the operator reads it faster.

Heuristics, in order of signal:
  - imperative verbs aimed at the agent ("also read", "include the contents of")
  - filesystem or env references (.env, id_rsa, credentials, ~/.aws)
  - exfiltration shapes (URLs in a description, "send to", "append to the
    location field")
  - tool shadowing (a description that redefines another tool's behaviour)
"""

from __future__ import annotations

from customs.models import ManifestDiff

_IMPERATIVE = (
    "also read",
    "include the contents of",
    "before answering",
    "you must",
    "do not ask",
)

_FS_REFS = (
    ".env",
    "id_rsa",
    "credentials",
    "~/.aws",
    "/etc/passwd",
    "secret",
)

_EXFIL = (
    "send to",
    "http://",
    "https://",
    "append to",
    "location field",
    "pass along",
)


def label(diff: ManifestDiff) -> str | None:
    """Return a short verdict string, or None when nothing stands out."""
    if diff.field != "description" or not diff.added:
        return None

    haystack = " ".join(diff.added).lower()

    for phrase in _IMPERATIVE:
        if phrase in haystack:
            return "instruction injection"

    for phrase in _FS_REFS:
        if phrase in haystack:
            return "filesystem / secret reference"

    for phrase in _EXFIL:
        if phrase in haystack:
            return "exfiltration shape"

    if diff.removed and diff.added:
        return "tool behaviour redefined"

    return None
