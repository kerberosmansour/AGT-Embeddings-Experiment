#!/usr/bin/env python3
"""Gate 0 — deterministic, idempotent, bounded de-obfuscation (round-6 M1).

Pure function: no I/O. The runner owns all file access. Normalized text exists
only in memory; artifacts record `transform tags` (a CLOSED enum, F-SEC-2) and
hashes, never text.

Design constraints (runbook §17 M1 Contract Block):
- decode-sniff depth <= 2 (F-ENG-2 acceptance rule: keep a decode only if the
  output is valid UTF-8 with >= 90% printable characters, else keep original
  with tag `decode_rejected`).
- normalized output <= 4x input chars (hard cap, tag `output_capped`).
- transform tags are a closed enum; never constructed from input strings.
- plain ASCII is (near) identity: conservative guards keep benign prose intact.
"""

from __future__ import annotations

import base64
import binascii
import codecs
import html
import re
import unicodedata
import urllib.parse
from dataclasses import dataclass, field

# ---- Closed transform-tag enum (F-SEC-2) -----------------------------------
# Every tag a NormalizedResult may carry MUST be a member of this frozenset.
# Tags are literal constants only; never f-string-built from input.
TAGS = frozenset(
    {
        "nfkc",
        "zero_width_stripped",
        "control_stripped",
        "confusables",
        "leet",
        "spacing_collapsed",
        "rot13",
        "base64",
        "hex",
        "percent",
        "unicode_escape",
        "html_entity",
        "decode_depth_capped",
        "decode_rejected",
        "whitespace_canonicalized",
        "output_capped",
        "invalid_unicode",
    }
)

MAX_OUTPUT_RATIO = 4
MAX_DECODE_DEPTH = 2
PRINTABLE_MIN_RATIO = 0.90

# Confusable fold: common Cyrillic / Greek / fullwidth look-alikes -> ASCII.
# Single-pass, deterministic. Only unambiguous homoglyphs are mapped.
_CONFUSABLES = {
    # Cyrillic -> Latin
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c",
    "у": "y", "х": "x", "А": "A", "Е": "E", "О": "O",
    "Р": "P", "С": "C", "Х": "X", "І": "I", "і": "i",
    "Ј": "J", "ј": "j", "һ": "h", "ԁ": "d",
    # Greek -> Latin
    "ο": "o", "α": "a", "ε": "e", "ρ": "p", "υ": "u",
    "Ο": "O", "Α": "A", "Ε": "E", "Β": "B", "Μ": "M",
    "κ": "k", "ι": "i", "ν": "v", "τ": "t",
}

# Leet substitution map (applied only under the token guard below).
_LEET = {"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a", "$": "s"}

_ZERO_WIDTH = dict.fromkeys(
    [0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF, 0x00AD, 0x180E, 0x200E, 0x200F], None
)

# A small fixed English marker set used ONLY as a generic "did this decode make
# the text more English-like" benefit test. It is not derived from attack
# labels and contains ordinary high-frequency words plus a few imperative stems.
_ENGLISH_MARKERS = (
    " the ", " and ", " you ", " to ", " of ", " all ", " is ", " are ",
    "ignore", "instruction", "system", "previous", "password", "secret",
    "please", "send", "delete", "execute", "reveal",
)

_B64_RE = re.compile(r"^[A-Za-z0-9+/]{16,}={0,2}$")
_HEX_RE = re.compile(r"^(?:0x)?[0-9A-Fa-f]{16,}$")
_WS_RE = re.compile(r"[ \t ]+")
_MULTINL_RE = re.compile(r"\n{3,}")


@dataclass
class NormalizedResult:
    text: str
    tags: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        bad = [t for t in self.tags if t not in TAGS]
        assert not bad, f"transform tags outside closed enum: {bad}"


def _printable_ratio(s: str) -> float:
    if not s:
        return 0.0
    printable = sum(1 for ch in s if ch.isprintable() or ch in "\n\t ")
    return printable / len(s)


def _english_score(s: str) -> int:
    low = " " + s.lower() + " "
    return sum(low.count(m) for m in _ENGLISH_MARKERS)


def _strip_invisibles(s: str) -> tuple[str, set[str]]:
    tags: set[str] = set()
    out = s.translate(_ZERO_WIDTH)
    if out != s:
        tags.add("zero_width_stripped")
    cleaned = []
    removed_control = False
    for ch in out:
        cat = unicodedata.category(ch)
        if cat in ("Cc", "Cf") and ch not in "\n\t":
            removed_control = True
            continue
        cleaned.append(ch)
    if removed_control:
        tags.add("control_stripped")
    return "".join(cleaned), tags


def _fold_confusables(s: str) -> tuple[str, bool]:
    if not any(ch in _CONFUSABLES for ch in s):
        return s, False
    return "".join(_CONFUSABLES.get(ch, ch) for ch in s), True


def _deleet_token(tok: str) -> str | None:
    """Return de-leeted token if the guard passes, else None.

    Guard: original token has >= 2 alphabetic chars and >= 1 leet char, and the
    de-leeted result is entirely alphabetic with length >= 3. Keeps numbers
    (e.g. '2024') and codes intact.
    """
    if not any(c in _LEET for c in tok):
        return None
    if sum(c.isalpha() for c in tok) < 2:
        return None
    sub = "".join(_LEET.get(c, c) for c in tok)
    if len(sub) >= 3 and sub.isalpha():
        return sub
    return None


def _deleet(s: str) -> tuple[str, bool]:
    changed = False
    out = []
    for tok in re.split(r"(\s+)", s):
        if tok.strip():
            d = _deleet_token(tok)
            if d is not None:
                out.append(d)
                changed = True
                continue
        out.append(tok)
    return "".join(out), changed


def _collapse_spacing(s: str) -> tuple[str, bool]:
    """Collapse runs of >= 4 single-character tokens (letter-spacing attacks).

    'i g n o r e   a l l' -> 'ignore all'. Conservative: only fires on runs of
    at least 4 consecutive single-char alnum tokens, which is characteristic of
    spacing obfuscation and rare in benign prose.
    """
    changed = False

    def collapse_line(line: str) -> str:
        nonlocal changed
        tokens = line.split(" ")
        out: list[str] = []
        i = 0
        n = len(tokens)
        while i < n:
            j = i
            while j < n and len(tokens[j]) == 1 and tokens[j].isalnum():
                j += 1
            run = j - i
            if run >= 4:
                out.append("".join(tokens[i:j]))
                changed = True
                i = j
            else:
                out.append(tokens[i])
                i += 1
        return " ".join(out)

    new = "\n".join(collapse_line(ln) for ln in s.split("\n"))
    return new, changed


def _try_decode_once(s: str) -> tuple[str | None, str | None]:
    """Attempt one decode layer. Returns (decoded_text, tag) or (None, None).

    Applies the F-ENG-2 acceptance guard: the decode is only offered if it is
    valid UTF-8 with >= 90% printable characters AND increases the English
    marker score (benefit test). rot13 is tried for mostly-alpha text.
    """
    stripped = s.strip()
    # rot13: only meaningful for alphabetic-heavy PROSE (keep the English-benefit
    # test — rot13 preserves length/printability, so only a dictionary-style
    # benefit signal distinguishes a real rot13 payload from plain text).
    alpha = sum(c.isalpha() for c in stripped)
    if alpha >= 12 and alpha / max(1, len(stripped)) > 0.6:
        dec = codecs.decode(stripped, "rot_13")
        if _english_score(dec) > _english_score(stripped) + 1:
            return dec, "rot13"
    # percent / URL-encoding: only fire on a RUN of %XX (>=4) so a stray "50%" in
    # benign prose is never decoded. Accept on printable + English-benefit.
    if len(re.findall(r"%[0-9A-Fa-f]{2}", stripped)) >= 4:
        dec = urllib.parse.unquote(stripped)
        if dec != stripped and _printable_ratio(dec) >= PRINTABLE_MIN_RATIO and _english_score(dec) > _english_score(stripped):
            return dec, "percent"
    # \uXXXX / \xNN unicode escapes: targeted replace (not whole-string
    # unicode_escape, which would touch unrelated backslashes). >=2 markers.
    esc = re.findall(r"\\u[0-9A-Fa-f]{4}|\\x[0-9A-Fa-f]{2}", stripped)
    if len(esc) >= 2:
        dec = re.sub(r"\\u[0-9A-Fa-f]{4}|\\x[0-9A-Fa-f]{2}",
                     lambda m: chr(int(m.group(0)[2:], 16)), stripped)
        if dec != stripped and _printable_ratio(dec) >= PRINTABLE_MIN_RATIO and _english_score(dec) > _english_score(stripped):
            return dec, "unicode_escape"
    # HTML entities (&#NN; / &#xNN; / named): >=2 markers, accept on benefit so a
    # lone "&amp;" in benign text is left alone.
    if len(re.findall(r"&#x?[0-9A-Fa-f]+;|&[a-zA-Z][a-zA-Z0-9]{1,12};", stripped)) >= 2:
        dec = html.unescape(stripped)
        if dec != stripped and _printable_ratio(dec) >= PRINTABLE_MIN_RATIO and _english_score(dec) > _english_score(stripped):
            return dec, "html_entity"
    # base64 / hex: only attempt on a CONTIGUOUS blob (no internal spaces) so
    # ordinary prose -- which always contains spaces -- is never treated as an
    # encoded payload. Acceptance is the printable-ratio guard (F-ENG-2); we do
    # NOT require an English-benefit signal here, so nested encodings unwrap.
    if "\n" not in stripped and " " not in stripped and len(stripped) >= 16:
        if _B64_RE.match(stripped) and len(stripped) % 4 == 0:
            try:
                dec = base64.b64decode(stripped, validate=True).decode("utf-8")
                if _printable_ratio(dec) >= PRINTABLE_MIN_RATIO:
                    return dec, "base64"
            except (binascii.Error, UnicodeDecodeError, ValueError):
                pass
        hexs = stripped[2:] if stripped.lower().startswith("0x") else stripped
        if _HEX_RE.match(stripped) and len(hexs) % 2 == 0:
            try:
                dec = bytes.fromhex(hexs).decode("utf-8")
                if _printable_ratio(dec) >= PRINTABLE_MIN_RATIO:
                    return dec, "hex"
            except (ValueError, UnicodeDecodeError):
                pass
    return None, None


def _decode_layers(s: str) -> tuple[str, set[str]]:
    tags: set[str] = set()
    cur = s
    attempted_any = False
    for _ in range(MAX_DECODE_DEPTH):
        dec, tag = _try_decode_once(cur)
        if dec is None:
            break
        attempted_any = True
        cur = dec
        tags.add(tag)
    # If a decode-shaped blob was present but rejected by the guard, tag it.
    if not attempted_any:
        probe = s.strip()
        if "\n" not in probe and " " not in probe and len(probe) >= 16:
            hexs = probe[2:] if probe.lower().startswith("0x") else probe
            if (_B64_RE.match(probe) and len(probe) % 4 == 0) or (
                _HEX_RE.match(probe) and len(hexs) % 2 == 0
            ):
                tags.add("decode_rejected")
    else:
        # one more attempt would exceed depth?
        dec, _ = _try_decode_once(cur)
        if dec is not None:
            tags.add("decode_depth_capped")
    return cur, tags


def normalize(text: str) -> NormalizedResult:
    """Normalize text to its plain form. Pure, deterministic, idempotent."""
    if text == "":
        return NormalizedResult("", ())
    tags: set[str] = set()

    # 1. Invalid-unicode safety: ensure the string round-trips; replace lone
    #    surrogates / undecodable units.
    try:
        text.encode("utf-8")
        s = text
    except UnicodeEncodeError:
        s = text.encode("utf-8", "replace").decode("utf-8")
        tags.add("invalid_unicode")

    # 2. NFKC (fullwidth, ligatures, compatibility forms).
    nfkc = unicodedata.normalize("NFKC", s)
    if nfkc != s:
        tags.add("nfkc")
    s = nfkc

    # 3. Strip zero-width and control characters.
    s, t = _strip_invisibles(s)
    tags |= t

    # 4. Fold confusables/homoglyphs.
    s, ch = _fold_confusables(s)
    if ch:
        tags.add("confusables")

    # 5. Decode layers (rot13 / base64 / hex) with acceptance guard.
    s, t = _decode_layers(s)
    tags |= t

    # 6. Canonicalize whitespace BEFORE spacing collapse so token boundaries are
    #    regular (irregular spacing would otherwise make collapse non-idempotent).
    ws = _WS_RE.sub(" ", s)
    ws = _MULTINL_RE.sub("\n\n", ws)
    ws = "\n".join(line.rstrip() for line in ws.split("\n")).strip()
    if ws != s:
        tags.add("whitespace_canonicalized")
    s = ws

    # 7. Collapse letter-spacing runs (operates on regular single-space tokens).
    s, ch = _collapse_spacing(s)
    if ch:
        tags.add("spacing_collapsed")

    # 8. De-leet under token guard. Runs AFTER collapse so that tokens merged by
    #    spacing-collapse are de-leeted in the same pass (idempotency).
    s, ch = _deleet(s)
    if ch:
        tags.add("leet")

    # 9. Output cap (F bound): <= 4x input characters.
    cap = MAX_OUTPUT_RATIO * len(text)
    if len(s) > cap:
        s = s[:cap]
        tags.add("output_capped")

    return NormalizedResult(s, tuple(sorted(tags)))


if __name__ == "__main__":
    import sys

    r = normalize(sys.stdin.read())
    print("tags:", r.tags)
    print(r.text)
